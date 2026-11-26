"""
Shared fixtures and reporting hooks for the PyTodo Pro automated suite (Week 6).

* The application code is NOT modified. Each test gets its own throw-away
  SQLite database by pointing app.DATABASE at a temp file.
* Every test declares the manual test cases it automates with
  @pytest.mark.covers("TC-WB-013", "API-007", ...). A run with
  --traceability=reports/traceability.csv writes the manual-to-automated
  traceability matrix together with each test's actual result.
* Tests that assert the SPECIFIED behaviour for an open defect use
  known_defect("DEF-xxx", "...") -> strict xfail.

Location of the app: by default the repository root (two levels above this
file). Override with the PYTODO_APP_DIR environment variable.
"""

import csv
import os
import re
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

APP_DIR = Path(os.environ.get("PYTODO_APP_DIR", Path(__file__).resolve().parents[2]))
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import app as app_module  # noqa: E402  (PyTodo Pro's app.py)


# ---------------------------------------------------------------------------
# Known-defect helpers
# ---------------------------------------------------------------------------

def defect_marks(defect_id, summary):
    """Marks for a test (or pytest.param) that checks an OPEN defect."""
    return [pytest.mark.known_defect,
            pytest.mark.xfail(strict=True, reason=f"{defect_id}: {summary}")]


def known_defect(defect_id, summary):
    def deco(fn):
        for m in defect_marks(defect_id, summary):
            fn = m(fn)
        return fn
    return deco


# ---------------------------------------------------------------------------
# Test data helpers
# ---------------------------------------------------------------------------

def day(offset):
    """ISO date string `offset` days from today (negative = past)."""
    return (date.today() + timedelta(days=offset)).isoformat()


VALID_PASSWORD = "Passw0rd123"  # 11 chars: stays clear of the 8-char boundary defect (DEF-006)


def api_register(c, username, password=VALID_PASSWORD):
    return c.post("/api/register", json={"username": username, "password": password})


def api_login(c, username, password=VALID_PASSWORD):
    return c.post("/api/login", json={"username": username, "password": password})


def api_create(c, **fields):
    fields.setdefault("title", "Sample task")
    return c.post("/api/tasks", json=fields)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def flask_app(tmp_path, monkeypatch):
    monkeypatch.setattr(app_module, "DATABASE", str(tmp_path / "test_pytodo.db"))
    # TESTING on, but let unhandled errors become real HTTP 500 responses
    # (what a browser / API client sees) instead of raising inside pytest.
    app_module.app.config.update(TESTING=True, PROPAGATE_EXCEPTIONS=False)
    app_module.init_db()
    yield app_module.app


@pytest.fixture
def client(flask_app):
    return flask_app.test_client()


@pytest.fixture
def make_client(flask_app):
    """Factory for independent clients (separate session cookies) for multi-user tests."""
    return flask_app.test_client


@pytest.fixture
def user_a(make_client):
    c = make_client()
    assert api_register(c, "security_user_a").status_code == 201
    return c


@pytest.fixture
def user_b(make_client):
    c = make_client()
    assert api_register(c, "security_user_b").status_code == 201
    return c


@pytest.fixture
def web_user(client):
    """Client registered + logged in through the HTML form."""
    r = client.post("/register", data={"username": "ayamgoreng", "password": VALID_PASSWORD})
    assert r.status_code == 302
    return client


@pytest.fixture
def categories(client):
    return {c["name"]: c["id"] for c in client.get("/api/categories").get_json()}


# ---------------------------------------------------------------------------
# Traceability report plugin
# ---------------------------------------------------------------------------

def pytest_addoption(parser):
    parser.addoption("--traceability", default=None,
                     help="write the manual-to-automated traceability matrix (CSV) to this path")


_ROWS = {}
_AUTO_ID = re.compile(r"AT[-_](U|A|W|UI)[-_](\d{3})")


def pytest_collection_modifyitems(config, items):
    for item in items:
        marks = {m.name for m in item.iter_markers()}
        covers = []
        for m in item.iter_markers("covers"):
            covers.extend(a for a in m.args if a not in covers)
        reason = ""
        for m in item.iter_markers("xfail"):
            reason = m.kwargs.get("reason", "")
        mid = _AUTO_ID.search(item.nodeid)
        layer = next((l for l in ("unit", "api", "web", "ui") if l in marks), "")
        _ROWS[item.nodeid] = {
            "auto_id": f"AT-{mid.group(1)}-{mid.group(2)}" if mid else "",
            "test": item.nodeid.split("::", 1)[1],
            "layer": layer,
            "manual_tests_covered": "; ".join(covers),
            "defect": reason.split(":", 1)[0] if reason else "",
            "smoke": "Y" if "smoke" in marks else "",
            "regression": "Y" if "regression" in marks else "",
            "result": "not run",
        }


def pytest_runtest_logreport(report):
    row = _ROWS.get(report.nodeid)
    if row is None:
        return
    if report.when == "call" or (report.when == "setup" and report.outcome != "passed"):
        if hasattr(report, "wasxfail"):
            row["result"] = "XFAIL (defect open)" if report.skipped else "XPASS"
        else:
            row["result"] = report.outcome.upper()


def pytest_sessionfinish(session):
    path = session.config.getoption("--traceability")
    if not path:
        return
    selected = [r for r in _ROWS.values() if r["result"] != "not run"]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(next(iter(_ROWS.values())).keys()))
        w.writeheader()
        w.writerows(sorted(selected, key=lambda r: (r["auto_id"], r["test"])))
