"""
Unit tests for helpers.py: the regression subset of the Week 2 white-box
cases (TC-WB-xxx) and the Week 1 black-box boundary cases.

Why automate: pure functions, deterministic (the clock is injectable), run in
milliseconds, and the urgency / password / 7-day rules are where four of the
logged defects live (DEF-002, DEF-006, DEF-007, DEF-008). Same fixed clock as
Week 2: today = 2026-11-24, now = 2026-11-24 12:00:00.
"""

from datetime import date, datetime, timedelta

import pytest

from conftest import defect_marks, known_defect
from helpers import compute_urgency, completed_in_last_n_days, is_valid_password, is_valid_username
from manual_ids import BB, GUI

pytestmark = [pytest.mark.unit]
REG = pytest.mark.regression
cov = pytest.mark.covers

TODAY = date(2026, 11, 24)
NOW = datetime(2026, 11, 24, 12, 0, 0)


def d(offset):
    return (TODAY + timedelta(days=offset)).isoformat()


def ago(**kw):
    return (NOW - timedelta(**kw)).strftime("%Y-%m-%d %H:%M:%S")


# ---------------------------------------------------------------------------
# compute_urgency (TC-WB-001..009, black-box urgency BVA)
# Same BVA points as the Week 1 run: -2, -1, 0, +1, +2, +3, blank.
# ---------------------------------------------------------------------------

@REG
@pytest.mark.smoke
@cov("TC-WB-001..009", BB["urgency"])
@pytest.mark.parametrize("auto_id, due, expected", [
    ("AT-U-001", None, "No due date"),
    ("AT-U-002", "", "No due date"),
    ("AT-U-003", d(-2), "Overdue"),
    ("AT-U-004", d(-1), "Overdue"),
    ("AT-U-006", d(1), "Due Soon"),
    ("AT-U-007", d(2), "Due Soon"),
    ("AT-U-008", d(3), "Upcoming"),
    ("AT-U-009", d(365), "Upcoming"),
])
def test_compute_urgency_partitions(auto_id, due, expected):
    assert compute_urgency(due, today=TODAY) == expected


@REG
@cov("TC-WB-004", BB["urgency_today"], GUI["data_display"])
@known_defect("DEF-002", "due date == today is labelled 'Overdue'; no 'Due Today' path exists")
def test_due_today_is_labelled_due_today_AT_U_005():
    # Exact label, not just "not Overdue": changing <= to < alone would give "Due Soon" (Week 2, Finding 2)
    assert compute_urgency(d(0), today=TODAY) == "Due Today"


@cov("TC-WB-009")
def test_five_digit_year_raises_in_helper_AT_U_010():
    """Characterisation: the helper itself does not validate; the callers must.
    This is the root cause of DEF-001 (retested end-to-end in AT-W-016 and AT-A-016)."""
    with pytest.raises(ValueError):
        compute_urgency("19999-06-14", today=TODAY)


@cov("TC-WB-008")
def test_default_clock_branch_AT_U_011():
    assert compute_urgency((date.today() + timedelta(days=10)).isoformat()) == "Upcoming"


# ---------------------------------------------------------------------------
# is_valid_password (TC-WB-010..015)
# ---------------------------------------------------------------------------

@REG
@pytest.mark.smoke
@cov("TC-WB-010..015")
@pytest.mark.parametrize("auto_id, pwd, expected", [
    ("AT-U-012", "", False),
    ("AT-U-013", "a" * 7, False),      # just below the minimum
    ("AT-U-015", "a" * 9, True),       # just above
    ("AT-U-016", "akusukaayam", True),  # the Week 1 baseline password (11 chars)
    ("AT-U-017", None, False),
    ("AT-U-018", 12345678, False),
])
def test_is_valid_password(auto_id, pwd, expected):
    assert is_valid_password(pwd) is expected


@REG
@pytest.mark.smoke
@cov("TC-WB-013")
@known_defect("DEF-006", "an 8-character password is rejected (len > 8 instead of >= 8)")
def test_password_of_exactly_8_chars_is_valid_AT_U_014():
    assert is_valid_password("abcd1234") is True


# ---------------------------------------------------------------------------
# is_valid_username (TC-WB-016..024)
# ---------------------------------------------------------------------------

@cov("TC-WB-016..023", BB["register_invalid"])
@pytest.mark.parametrize("auto_id, name, expected", [
    ("AT-U-019", "us", False),          # 2 chars (Week 1 value)
    ("AT-U-020", "abc", True),          # 3
    ("AT-U-021", "a" * 20, True),       # 20
    ("AT-U-022", "a" * 21, False),      # 21
    ("AT-U-023", "user_01", True),      # loop: no failing character
    ("AT-U-024", "user-01", False),     # loop: failing character in the middle
    ("AT-U-025", "user name", False),
    ("AT-U-026", None, False),
])
def test_is_valid_username(auto_id, name, expected):
    assert is_valid_username(name) is expected


@cov("TC-WB-024")
@known_defect("DEF-009", "non-ASCII letters (e.g. 'jöhn') are accepted [needs spec clarification]")
def test_username_rejects_non_ascii_AT_U_033():
    # Kept OUT of the regression suite until the team confirms the intended rule.
    assert is_valid_username("jöhn") is False


# ---------------------------------------------------------------------------
# completed_in_last_n_days (TC-WB-025..035)
# ---------------------------------------------------------------------------

@REG
@cov("TC-WB-025..035")
@pytest.mark.parametrize("auto_id, completed_at, expected", [
    ("AT-U-027", None, False),
    pytest.param("AT-U-028", ago(seconds=1), True, marks=cov("TC-WB-027")),
    pytest.param("AT-U-029", ago(days=6, hours=23), True, marks=cov("TC-WB-028")),
    pytest.param("AT-U-031", ago(days=7, hours=1), False, marks=cov("TC-WB-030")),
    pytest.param("AT-U-032", (NOW + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"), False,
                 marks=cov("TC-WB-032")),
    pytest.param("AT-U-030", ago(days=7), True,
                 marks=[cov("TC-WB-029")] + defect_marks(
                     "DEF-007", "completion exactly 7 days ago is excluded (age.days < n; spec says inclusive)")),
    pytest.param("AT-U-034", ago(seconds=0), True,
                 marks=[cov("TC-WB-033")] + defect_marks(
                     "DEF-008", "completion in the same second is excluded (total_seconds() > 0)")),
])
def test_completed_in_last_7_days(auto_id, completed_at, expected):
    assert completed_in_last_n_days(completed_at, n=7, now=NOW) is expected


@cov("TC-WB-034")
def test_completed_default_clock_branch_AT_U_035():
    recent = (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    assert completed_in_last_n_days(recent) is True
