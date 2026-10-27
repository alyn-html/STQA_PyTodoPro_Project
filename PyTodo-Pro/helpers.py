"""
helpers.py — pure, framework-free logic for PyTodo Pro.

Kept separate from app.py deliberately: everything here can be unit
tested (e.g. with pytest) without a running Flask app, a database, or
an HTTP client.
"""

from datetime import date, datetime


def compute_urgency(due_date_str, today=None):
    """
    Classify a task's due date into an urgency label.

    Spec:
      - No due date supplied         -> "No due date"
      - due date is in the past      -> "Overdue"
      - due date is today            -> "Due Today"
      - due date is 1-2 days away    -> "Due Soon"
      - due date is 3+ days away     -> "Upcoming"

    due_date_str: "YYYY-MM-DD" string, or falsy for "no due date".
    today: optional date object, defaults to date.today() (injectable for testing).
    """
    if today is None:
        today = date.today()
    if not due_date_str:
        return "No due date"

    due = datetime.strptime(due_date_str, "%Y-%m-%d").date()

    if due <= today:
        return "Overdue"

    delta_days = (due - today).days
    if delta_days <= 2:
        return "Due Soon"
    return "Upcoming"


def is_valid_password(password):
    """
    Spec: passwords must be at least 8 characters long.
    Returns True if valid, False otherwise.
    """
    if not isinstance(password, str):
        return False
    return len(password) > 8


def is_valid_username(username):
    """Spec: usernames must be 3-20 characters, letters/numbers/underscore only."""
    if not isinstance(username, str):
        return False
    if not (3 <= len(username) <= 20):
        return False
    return all(c.isalnum() or c == "_" for c in username)


def completed_in_last_n_days(completed_at_str, n=7, now=None):
    """
    Spec: a task counts toward the "completed in the last N days" total
    if it was completed within the last N days, inclusive of exactly N
    days ago.

    completed_at_str: "YYYY-MM-DD HH:MM:SS" string, or falsy if not completed.
    """
    if not completed_at_str:
        return False
    if now is None:
        now = datetime.now()
    completed_at = datetime.strptime(completed_at_str, "%Y-%m-%d %H:%M:%S")
    age = now - completed_at
    return age.total_seconds() > 0 and age.days < n
