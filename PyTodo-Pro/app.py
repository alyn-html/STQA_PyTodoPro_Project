"""
PyTodo Pro — a complete, ready-to-test Flask task manager.

Features: user accounts, categorized tasks with due dates, an urgency
dashboard, and a full JSON REST API — all already implemented. This
app is the target of the course testing project; nothing here needs
to be built, only tested.

Run:
    pip install -r requirements.txt
    python app.py

Web UI:  http://127.0.0.1:5000/
API base: http://127.0.0.1:5000/api
"""

import os
import sqlite3
from datetime import datetime
from functools import wraps

from flask import Flask, g, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import compute_urgency, completed_in_last_n_days, is_valid_password, is_valid_username

app = Flask(__name__)
app.config["SECRET_KEY"] = "pytodo-pro-dev-secret"

DATABASE = os.path.join(os.path.dirname(__file__), "pytodo_pro.db")
DEFAULT_CATEGORIES = ["Work", "Personal", "Study", "Urgent"]


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password_hash TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                category_id INTEGER,
                due_date TEXT,
                done INTEGER NOT NULL DEFAULT 0,
                completed_at TEXT,
                created_at TEXT NOT NULL
            );
            """
        )
        for name in DEFAULT_CATEGORIES:
            db.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (name,))
        db.commit()


def row_to_task(row, category_name=None):
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "category_id": row["category_id"],
        "category": category_name,
        "due_date": row["due_date"],
        "done": bool(row["done"]),
        "urgency": compute_urgency(row["due_date"]) if not row["done"] else "Done",
        "completed_at": row["completed_at"],
        "created_at": row["created_at"],
    }


def get_category_name(db, category_id):
    if not category_id:
        return None
    row = db.execute("SELECT name FROM categories WHERE id = ?", (category_id,)).fetchone()
    return row["name"] if row else None


def get_category_id_by_name(db, name):
    row = db.execute("SELECT id FROM categories WHERE name = ?", (name,)).fetchone()
    return row["id"] if row else None


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def login_required_web(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return wrapper


def login_required_api(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"error": "authentication required"}), 401
        return f(*args, **kwargs)
    return wrapper


# ---------------------------------------------------------------------------
# Web UI — auth pages
# ---------------------------------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register_page():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not is_valid_username(username):
            error = "Username must be 3-20 characters (letters, numbers, underscore)."
        elif not is_valid_password(password):
            error = "Password must be at least 8 characters."
        else:
            db = get_db()
            # NOTE: no uniqueness check against existing usernames here.
            password_hash = generate_password_hash(password)
            cur = db.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash),
            )
            db.commit()
            session["user_id"] = cur.lastrowid
            session["username"] = username
            return redirect(url_for("index"))
    return render_template("register.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login_page():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("index"))
        error = "Invalid username or password."
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))


# ---------------------------------------------------------------------------
# Web UI — tasks & dashboard
# ---------------------------------------------------------------------------

@app.route("/")
@login_required_web
def index():
    db = get_db()
    category_filter = request.args.get("category", "").strip()
    status_filter = request.args.get("status", "").strip()
    q = request.args.get("q", "").strip()

    query = "SELECT * FROM tasks WHERE user_id = ?"
    params = [session["user_id"]]

    cat_id = get_category_id_by_name(db, category_filter) if category_filter else None
    if cat_id:
        query += " AND category_id = ?"
        params.append(cat_id)

    if status_filter == "done":
        query += " AND done = 1"
    elif status_filter == "open":
        query += " AND done = 0"

    if q:
        query += " AND title LIKE ?"
        params.append(f"%{q}%")

    query += " ORDER BY id DESC"
    rows = db.execute(query, params).fetchall()
    tasks = [row_to_task(r, get_category_name(db, r["category_id"])) for r in rows]
    categories = db.execute("SELECT * FROM categories ORDER BY name").fetchall()

    return render_template(
        "index.html", tasks=tasks, categories=categories,
        category_filter=category_filter, status_filter=status_filter, q=q,
    )


@app.route("/tasks/new", methods=["GET", "POST"])
@login_required_web
def new_task():
    db = get_db()
    categories = db.execute("SELECT * FROM categories ORDER BY name").fetchall()
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category_id = request.form.get("category_id") or None
        due_date = request.form.get("due_date") or None
        db.execute(
            "INSERT INTO tasks (user_id, title, description, category_id, due_date, done, created_at) "
            "VALUES (?, ?, ?, ?, ?, 0, ?)",
            (session["user_id"], title, description, category_id, due_date, datetime.now().isoformat()),
        )
        db.commit()
        return redirect(url_for("index"))
    return render_template("task_form.html", categories=categories, task=None)


@app.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
@login_required_web
def edit_task(task_id):
    db = get_db()
    categories = db.execute("SELECT * FROM categories ORDER BY name").fetchall()
    task = db.execute(
        "SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, session["user_id"])
    ).fetchone()
    if task is None:
        return redirect(url_for("index"))
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category_id = request.form.get("category_id") or None
        due_date = request.form.get("due_date") or None
        db.execute(
            "UPDATE tasks SET title = ?, description = ?, category_id = ?, due_date = ? WHERE id = ?",
            (title, description, category_id, due_date, task_id),
        )
        db.commit()
        return redirect(url_for("index"))
    return render_template("task_form.html", categories=categories, task=task)


@app.route("/tasks/<int:task_id>/toggle", methods=["POST"])
@login_required_web
def toggle_task(task_id):
    db = get_db()
    task = db.execute(
        "SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, session["user_id"])
    ).fetchone()
    if task is not None:
        new_done = 0 if task["done"] else 1
        completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if new_done else None
        db.execute("UPDATE tasks SET done = ?, completed_at = ? WHERE id = ?", (new_done, completed_at, task_id))
        db.commit()
    return redirect(url_for("index"))


@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required_web
def delete_task_web(task_id):
    db = get_db()
    db.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, session["user_id"]))
    db.commit()
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required_web
def dashboard():
    db = get_db()
    rows = db.execute("SELECT * FROM tasks WHERE user_id = ?", (session["user_id"],)).fetchall()

    total = len(rows)
    open_tasks = sum(1 for r in rows if not r["done"])
    overdue = sum(1 for r in rows if not r["done"] and compute_urgency(r["due_date"]) == "Overdue")
    due_soon = sum(1 for r in rows if not r["done"] and compute_urgency(r["due_date"]) == "Due Soon")
    completed_this_week = sum(1 for r in rows if completed_in_last_n_days(r["completed_at"], n=7))

    return render_template(
        "dashboard.html", total=total, open_tasks=open_tasks,
        overdue=overdue, due_soon=due_soon, completed_this_week=completed_this_week,
    )


# ---------------------------------------------------------------------------
# JSON REST API
# ---------------------------------------------------------------------------

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if not is_valid_username(username):
        return jsonify({"error": "invalid username"}), 400
    if not is_valid_password(password):
        return jsonify({"error": "invalid password"}), 400
    db = get_db()
    password_hash = generate_password_hash(password)
    cur = db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
    db.commit()
    session["user_id"] = cur.lastrowid
    session["username"] = username
    return jsonify({"id": cur.lastrowid, "username": username}), 201


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if user and check_password_hash(user["password_hash"], password):
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        return jsonify({"id": user["id"], "username": user["username"]})
    return jsonify({"error": "invalid credentials"}), 401


@app.route("/api/categories", methods=["GET"])
def api_categories():
    db = get_db()
    rows = db.execute("SELECT * FROM categories ORDER BY name").fetchall()
    return jsonify([{"id": r["id"], "name": r["name"]} for r in rows])


@app.route("/api/tasks", methods=["GET"])
@login_required_api
def api_list_tasks():
    db = get_db()
    page = request.args.get("page", default=0, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    category = request.args.get("category", "").strip()
    status = request.args.get("status", "").strip()
    q = request.args.get("q", "").strip()

    query = "SELECT * FROM tasks WHERE user_id = ?"
    params = [session["user_id"]]

    cat_id = get_category_id_by_name(db, category) if category else None
    if cat_id:
        query += " AND category_id = ?"
        params.append(cat_id)

    if status == "done":
        query += " AND done = 1"
    elif status == "open":
        query += " AND done = 0"

    if q:
        # Search is intentionally simple: build the LIKE pattern directly.
        query += f" AND title LIKE '%{q}%'"

    query += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([per_page, page * per_page])

    rows = db.execute(query, params).fetchall()
    tasks = [row_to_task(r, get_category_name(db, r["category_id"])) for r in rows]
    return jsonify(tasks)


@app.route("/api/tasks/<int:task_id>", methods=["GET"])
@login_required_api
def api_get_task(task_id):
    db = get_db()
    row = db.execute(
        "SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, session["user_id"])
    ).fetchone()
    if row is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(row_to_task(row, get_category_name(db, row["category_id"])))


@app.route("/api/tasks", methods=["POST"])
@login_required_api
def api_create_task():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "title is required"}), 400
    description = data.get("description", "")
    category_id = data.get("category_id")
    due_date = data.get("due_date")

    db = get_db()
    cur = db.execute(
        "INSERT INTO tasks (user_id, title, description, category_id, due_date, done, created_at) "
        "VALUES (?, ?, ?, ?, ?, 0, ?)",
        (session["user_id"], title, description, category_id, due_date, datetime.now().isoformat()),
    )
    db.commit()
    row = db.execute("SELECT * FROM tasks WHERE id = ?", (cur.lastrowid,)).fetchone()
    return jsonify(row_to_task(row, get_category_name(db, row["category_id"]))), 201


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
@login_required_api
def api_update_task(task_id):
    db = get_db()
    row = db.execute(
        "SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, session["user_id"])
    ).fetchone()
    if row is None:
        return jsonify({"error": "not found"}), 404

    data = request.get_json(silent=True) or {}
    title = data.get("title", row["title"])
    description = data.get("description", row["description"])
    category_id = data.get("category_id", row["category_id"])
    due_date = data.get("due_date", row["due_date"])
    done = data.get("done", bool(row["done"]))
    completed_at = row["completed_at"]
    if bool(done) and not row["done"]:
        completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elif not bool(done):
        completed_at = None

    db.execute(
        "UPDATE tasks SET title=?, description=?, category_id=?, due_date=?, done=?, completed_at=? WHERE id=?",
        (title, description, category_id, due_date, int(bool(done)), completed_at, task_id),
    )
    db.commit()
    updated = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return jsonify(row_to_task(updated, get_category_name(db, updated["category_id"])))


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
@login_required_api
def api_delete_task(task_id):
    db = get_db()
    # NOTE: deletes by id only — does not scope to session["user_id"].
    db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    db.commit()
    return jsonify({"result": "ok"})


@app.route("/api/dashboard", methods=["GET"])
@login_required_api
def api_dashboard():
    db = get_db()
    rows = db.execute("SELECT * FROM tasks WHERE user_id = ?", (session["user_id"],)).fetchall()
    total = len(rows)
    open_tasks = sum(1 for r in rows if not r["done"])
    overdue = sum(1 for r in rows if not r["done"] and compute_urgency(r["due_date"]) == "Overdue")
    due_soon = sum(1 for r in rows if not r["done"] and compute_urgency(r["due_date"]) == "Due Soon")
    completed_this_week = sum(1 for r in rows if completed_in_last_n_days(r["completed_at"], n=7))
    return jsonify({
        "total": total, "open": open_tasks, "overdue": overdue,
        "due_soon": due_soon, "completed_this_week": completed_this_week,
    })


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
