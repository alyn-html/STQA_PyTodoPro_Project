"""
Week 2 - White-box tests for PyTodo Pro.
Each test name carries its Test Case ID (TC-WB-xxx) so results map to the spreadsheet.
Run:  pytest test_whitebox.py -v --cov=helpers --cov-branch --cov-report=term-missing
"""
from datetime import date, datetime, timedelta

import pytest

import app as app_module
from helpers import compute_urgency, completed_in_last_n_days, is_valid_password, is_valid_username

TODAY = date(2026, 11, 24)
NOW = datetime(2026, 11, 24, 12, 0, 0)


def d(offset):
    return (TODAY + timedelta(days=offset)).strftime("%Y-%m-%d")


def ts(delta):
    return (NOW - delta).strftime("%Y-%m-%d %H:%M:%S")


# ---------------- compute_urgency ----------------
def test_TC_WB_001_urgency_none():
    assert compute_urgency(None, today=TODAY) == "No due date"

def test_TC_WB_002_urgency_empty_string():
    assert compute_urgency("", today=TODAY) == "No due date"

def test_TC_WB_003_urgency_past():
    assert compute_urgency(d(-1), today=TODAY) == "Overdue"

def test_TC_WB_004_urgency_today():
    assert compute_urgency(d(0), today=TODAY) == "Due Today"

def test_TC_WB_005_urgency_plus1():
    assert compute_urgency(d(1), today=TODAY) == "Due Soon"

def test_TC_WB_006_urgency_plus2():
    assert compute_urgency(d(2), today=TODAY) == "Due Soon"

def test_TC_WB_007_urgency_plus3():
    assert compute_urgency(d(3), today=TODAY) == "Upcoming"

def test_TC_WB_008_urgency_default_today():
    future = (date.today() + timedelta(days=10)).strftime("%Y-%m-%d")
    assert compute_urgency(future) == "Upcoming"

def test_TC_WB_009_urgency_bad_format():
    with pytest.raises(ValueError):
        compute_urgency("24/11/2026", today=TODAY)


# ---------------- is_valid_password ----------------
def test_TC_WB_010_pw_none():
    assert is_valid_password(None) is False

def test_TC_WB_011_pw_int():
    assert is_valid_password(12345678) is False

def test_TC_WB_012_pw_7():
    assert is_valid_password("abc1234") is False

def test_TC_WB_013_pw_8():
    assert is_valid_password("abcd1234") is True

def test_TC_WB_014_pw_9():
    assert is_valid_password("abcd12345") is True

def test_TC_WB_015_pw_empty():
    assert is_valid_password("") is False


# ---------------- is_valid_username ----------------
def test_TC_WB_016_user_nonstr():
    assert is_valid_username(123) is False

def test_TC_WB_017_user_2():
    assert is_valid_username("ab") is False

def test_TC_WB_018_user_3():
    assert is_valid_username("abc") is True

def test_TC_WB_019_user_20():
    assert is_valid_username("a" * 20) is True

def test_TC_WB_020_user_21():
    assert is_valid_username("a" * 21) is False

def test_TC_WB_021_user_valid_mix():
    assert is_valid_username("john_doe1") is True

def test_TC_WB_022_user_space():
    assert is_valid_username("john doe") is False

def test_TC_WB_023_user_hyphen():
    assert is_valid_username("john-doe") is False

def test_TC_WB_024_user_non_ascii():
    assert is_valid_username("jöhn") is False


# ---------------- completed_in_last_n_days ----------------
def test_TC_WB_025_comp_none():
    assert completed_in_last_n_days(None, now=NOW) is False

def test_TC_WB_026_comp_empty():
    assert completed_in_last_n_days("", now=NOW) is False

def test_TC_WB_027_comp_1h():
    assert completed_in_last_n_days(ts(timedelta(hours=1)), now=NOW) is True

def test_TC_WB_028_comp_6d23h():
    assert completed_in_last_n_days(ts(timedelta(days=6, hours=23)), now=NOW) is True

def test_TC_WB_029_comp_exact_7d():
    assert completed_in_last_n_days(ts(timedelta(days=7)), now=NOW) is True

def test_TC_WB_030_comp_7d1h():
    assert completed_in_last_n_days(ts(timedelta(days=7, hours=1)), now=NOW) is False

def test_TC_WB_031_comp_8d():
    assert completed_in_last_n_days(ts(timedelta(days=8)), now=NOW) is False

def test_TC_WB_032_comp_future():
    assert completed_in_last_n_days(ts(timedelta(hours=-1)), now=NOW) is False

def test_TC_WB_033_comp_now():
    assert completed_in_last_n_days(ts(timedelta(0)), now=NOW) is True

def test_TC_WB_034_comp_default_now():
    one_min_ago = (datetime.now() - timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S")
    assert completed_in_last_n_days(one_min_ago) is True

def test_TC_WB_035_comp_n1():
    assert completed_in_last_n_days(ts(timedelta(hours=23)), n=1, now=NOW) is True


# ---------------- app.py units ----------------
def _row(done, due):
    return {"id": 1, "title": "t", "description": "", "category_id": None, "due_date": due,
            "done": done, "completed_at": None, "created_at": "x"}

def test_TC_WB_036_row_to_task_done():
    assert app_module.row_to_task(_row(1, d(-5)))["urgency"] == "Done"

def test_TC_WB_037_row_to_task_open():
    assert app_module.row_to_task(_row(0, None))["urgency"] == "No due date"


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(app_module, "DATABASE", str(tmp_path / "t.db"))
    app_module.init_db()
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()

def test_TC_WB_038_category_name_none(client):
    with app_module.app.app_context():
        assert app_module.get_category_name(app_module.get_db(), None) is None

def test_TC_WB_039_category_name_unknown(client):
    with app_module.app.app_context():
        assert app_module.get_category_name(app_module.get_db(), 999) is None

def test_TC_WB_040_login_required_redirect(client):
    r = client.get("/dashboard")
    assert r.status_code == 302 and "/login" in r.headers["Location"]
