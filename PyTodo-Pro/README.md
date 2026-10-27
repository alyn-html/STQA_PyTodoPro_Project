# PyTodo Pro

A complete, ready-to-test Flask task manager — the target application
for the course testing project. **You do not need to write or modify
any application code.** Your job is to test it.

## Setup

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The app creates `pytodo_pro.db` on first run and serves at
`http://127.0.0.1:5000/`. Register a new account from the web UI (or
via `POST /api/register`) to get started — there is no pre-seeded
login.

## What's here

### Web UI
- `/register`, `/login`, `/logout` — account management
- `/` — task list, with filters for category, status (open/done), and a title search box
- `/tasks/new`, `/tasks/<id>/edit` — create and edit tasks
- `/dashboard` — summary counters (total, open, overdue, due soon, completed in the last 7 days)

### JSON REST API (all under `/api`, session-cookie authenticated except register/login)
- `POST /api/register` — `{"username": ..., "password": ...}`
- `POST /api/login` — `{"username": ..., "password": ...}`
- `GET /api/categories`
- `GET /api/tasks?category=&status=&q=&page=&per_page=`
- `POST /api/tasks` — `{"title": ..., "description": ..., "category_id": ..., "due_date": "YYYY-MM-DD"}`
- `GET /api/tasks/<id>`
- `PUT /api/tasks/<id>` — partial updates accepted
- `DELETE /api/tasks/<id>`
- `GET /api/dashboard`

### Data model
- **users**: id, username, password_hash
- **categories**: id, name (seeded with Work, Personal, Study, Urgent)
- **tasks**: id, user_id, title, description, category_id, due_date, done, completed_at, created_at

### Task urgency
Each task is classified as one of: `No due date`, `Overdue`, `Due Today`,
`Due Soon` (due within 2 days), `Upcoming`, or `Done`. The exact rules
are implemented in `helpers.py` — a good place to start if you're
designing white-box test cases.

## A note on quality

This app was built to be tested, not audited by its author. Treat it
the way you would treat a real, working piece of software handed to a
QA team: it does what it's supposed to do in the common cases — your
job across the testing phases is to find out where that stops being
true.
