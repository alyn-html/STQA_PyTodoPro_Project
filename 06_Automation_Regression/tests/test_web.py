"""
Server-rendered web tests (Flask test client): automate the Week 1 black-box
workflows (TC-BB), the Week 3 GUI/usability checks that have an objective
oracle (TC-GUI, TC-USA), and HTML-level accessibility retests (TC-ACC).

Why here and not only in Selenium: these hit the same routes, forms, redirects
and templates without a browser, so they are fast and never flaky. Selenium
(test_ui_selenium.py) is kept to a thin end-to-end layer plus the axe scan.
"""

import re

import pytest

from conftest import VALID_PASSWORD, day, known_defect
from manual_ids import ACC, BB, GUI

pytestmark = [pytest.mark.web]
REG = pytest.mark.regression
cov = pytest.mark.covers


def task_titles(html):
    return re.findall(r'<td class="title-cell">(.*?)</td>', html, re.S)


def text(resp):
    return resp.get_data(as_text=True)


# ---------------------------------------------------------------------------
# Access control, registration, login, logout
# ---------------------------------------------------------------------------

@REG
@pytest.mark.smoke
@cov("API-001", "TC-WB-036..040", BB["logout"])
@pytest.mark.parametrize("url", ["/", "/dashboard", "/tasks/new", "/tasks/1/edit"])
def test_protected_pages_redirect_to_login_AT_W_001(client, url):
    r = client.get(url)
    assert r.status_code == 302 and r.headers["Location"].endswith("/login")


@REG
@pytest.mark.smoke
@cov(BB["register_valid"], GUI["nav"])
def test_register_form_logs_user_in_AT_W_002(client):
    html = text(client.post("/register", data={"username": "ayamgoreng", "password": "akusukaayam"},
                            follow_redirects=True))
    assert "My Tasks" in html and '<span class="nav-user">ayamgoreng</span>' in html


@cov(BB["register_invalid"], GUI["messages"])
@pytest.mark.parametrize("auto_id, username, password, message", [
    ("AT-W-003", "us", VALID_PASSWORD, "Username must be 3-20 characters (letters, numbers, underscore)."),
    ("AT-W-004", "okuser", "short", "Password must be at least 8 characters."),
])
def test_register_validation_messages(client, auto_id, username, password, message):
    r = client.post("/register", data={"username": username, "password": password})
    assert r.status_code == 200 and message in text(r)


@REG
@cov("TC-USA-001")
@known_defect("DEF-013", "register form clears the username after a validation error")
def test_register_error_keeps_username_AT_W_005(client):
    html = text(client.post("/register", data={"username": "okuser", "password": "short"}))
    assert 'value="okuser"' in html


@cov("TC-USA-003")
def test_rules_shown_before_typing_AT_W_006(client):
    html = text(client.get("/register"))
    assert "(3-20 chars, letters/numbers/underscore)" in html and "(min 8 characters)" in html


@REG
@pytest.mark.smoke
@cov(BB["login"], GUI["messages"])
def test_login_decision_table_AT_W_007(make_client):
    make_client().post("/register", data={"username": "ayamgoreng", "password": "akusukaayam"})
    c = make_client()
    rules = [("ayamgoreng", "wrongpass1", False),   # valid user, wrong password
             ("nobody_xx", "akusukaayam", False),   # unknown user, any password
             ("nobody_xx", "wrongpass1", False),    # both wrong
             ("ayamgoreng", "akusukaayam", True)]   # both right
    for user, pwd, ok in rules:
        r = c.post("/login", data={"username": user, "password": pwd})
        if ok:
            assert r.status_code == 302 and r.headers["Location"].endswith("/")
        else:
            assert "Invalid username or password." in text(r)


@REG
@cov(BB["logout"])
def test_logout_then_protected_pages_redirect_AT_W_008(web_user):
    assert web_user.get("/logout").headers["Location"].endswith("/login")
    assert web_user.get("/").status_code == 302
    assert web_user.get("/dashboard").status_code == 302


@REG
@cov(BB["register_second"])
def test_second_account_same_browser_session_AT_W_009(client):
    """Retest of DEF-004 ('multi-account registration blocked'). Week 2 predicted it is a
    symptom of DEF-006. With 9+ char passwords a second registration from the SAME session works."""
    assert client.post("/register", data={"username": "ayamgoreng", "password": "akusukaayam"}).status_code == 302
    r = client.post("/register", data={"username": "haiqalfirdaus", "password": "haiqal1234"},
                    follow_redirects=True)
    assert '<span class="nav-user">haiqalfirdaus</span>' in text(r)


@REG
@pytest.mark.smoke
@cov(BB["register_second"], GUI["messages"])
@known_defect("DEF-006", "8-character password rejected although the page says '(min 8 characters)'")
def test_register_with_8_char_password_AT_W_010(client):
    r = client.post("/register", data={"username": "username1", "password": "password"})
    assert r.status_code == 302


# ---------------------------------------------------------------------------
# Task lifecycle
# ---------------------------------------------------------------------------

@REG
@pytest.mark.smoke
@cov(BB["create"], GUI["forms"], GUI["data_display"])
def test_create_task_via_form_AT_W_011(web_user, categories):
    html = text(web_user.post("/tasks/new", data={"title": "Buy groceries", "category_id": categories["Personal"],
                                                 "due_date": day(1)}, follow_redirects=True))
    assert task_titles(html) == ["Buy groceries"]
    assert "Personal" in html and "Due Soon" in html


@REG
@cov(BB["toggle"], GUI["buttons"])
def test_toggle_done_and_reopen_AT_W_012(web_user):
    web_user.post("/tasks/new", data={"title": "Toggle"})
    html = text(web_user.post("/tasks/1/toggle", follow_redirects=True))
    assert '<tr class="done">' in html and "✓" in html and ">Done<" in html
    html = text(web_user.post("/tasks/1/toggle", follow_redirects=True))
    assert '<tr class="done">' not in html and "○" in html


@REG
@cov(BB["edit"], GUI["forms"])
def test_edit_prefills_and_saves_AT_W_013(web_user):
    web_user.post("/tasks/new", data={"title": "Old name", "due_date": day(5)})
    form = text(web_user.get("/tasks/1/edit"))
    assert 'value="Old name"' in form and f'value="{day(5)}"' in form and "Save Changes" in form
    assert task_titles(text(web_user.post("/tasks/1/edit", data={"title": "New name"},
                                          follow_redirects=True))) == ["New name"]


@REG
@cov(BB["delete"])
def test_delete_task_AT_W_014(web_user):
    web_user.post("/tasks/new", data={"title": "Temp"})
    assert task_titles(text(web_user.post("/tasks/1/delete", follow_redirects=True))) == []


@REG
@pytest.mark.smoke
@cov("new in Week 6 (web counterpart of SEC-004..006)")
def test_other_user_cannot_edit_toggle_delete_via_web_AT_W_015(make_client):
    a = make_client(); a.post("/register", data={"username": "owner1", "password": VALID_PASSWORD})
    a.post("/tasks/new", data={"title": "Owner task"})
    b = make_client(); b.post("/register", data={"username": "other1", "password": VALID_PASSWORD})
    assert b.get("/tasks/1/edit").headers["Location"].endswith("/")
    b.post("/tasks/1/edit", data={"title": "hijacked"}); b.post("/tasks/1/toggle"); b.post("/tasks/1/delete")
    html = text(a.get("/"))
    assert task_titles(html) == ["Owner task"] and '<tr class="done">' not in html


@REG
@pytest.mark.smoke
@cov(BB["due_5digit"], "TC-WB-043")
@known_defect("DEF-001", "5-digit year (19999-06-14) is stored; task list and dashboard then return HTTP 500")
def test_five_digit_year_does_not_break_pages_AT_W_016(web_user):
    web_user.post("/tasks/new", data={"title": "submit stqa project", "due_date": "19999-06-14"})
    assert web_user.get("/").status_code == 200
    assert web_user.get("/dashboard").status_code == 200


@REG
@cov(BB["filters"], GUI["filters_persist"])
def test_filter_decision_table_and_persistence_AT_W_017(web_user, categories):
    web_user.post("/tasks/new", data={"title": "Study maths", "category_id": categories["Study"]})
    web_user.post("/tasks/new", data={"title": "Work email", "category_id": categories["Work"]})
    web_user.post("/tasks/new", data={"title": "Study notes", "category_id": categories["Study"]})
    web_user.post("/tasks/2/toggle")
    cases = {"/?category=Study": ["Study notes", "Study maths"],
             "/?status=done": ["Work email"],
             "/?q=maths": ["Study maths"],
             "/?category=Study&status=open&q=notes": ["Study notes"],
             "/?category=Work&status=open": []}                       # zero-result combination
    for url, expected in cases.items():
        assert task_titles(text(web_user.get(url))) == expected, url
    html = text(web_user.get("/?category=Study&status=open&q=notes"))   # TC-GUI-013: filters persist
    assert 'value="Study" selected' in html and 'value="open" selected' in html and 'value="notes"' in html


@cov("new in Week 6 (contrast with DEF-023 on the API)")
def test_web_search_with_quote_is_safe_AT_W_018(web_user):
    web_user.post("/tasks/new", data={"title": "O'Brien report"})
    r = web_user.get("/?q=O'Brien")
    assert r.status_code == 200
    assert len(task_titles(text(r))) == 1 and "Brien report" in task_titles(text(r))[0]


@REG
@cov(BB["dashboard"])
def test_dashboard_page_counters_AT_W_019(web_user):
    web_user.post("/tasks/new", data={"title": "late", "due_date": day(-1)})
    web_user.post("/tasks/new", data={"title": "soon", "due_date": day(2)})
    web_user.post("/tasks/new", data={"title": "finished"})
    web_user.post("/tasks/3/toggle")
    values = re.findall(r'<div class="stat-value">(\d+)</div>', text(web_user.get("/dashboard")))
    assert values == ["3", "2", "1", "1", "1"]   # total, open, overdue, due soon, completed (7 days)


@REG
@pytest.mark.smoke
@cov(GUI["data_display"])
@known_defect("DEF-011", "task titles are rendered as raw HTML (|safe): markup and scripts execute")
def test_titles_are_escaped_AT_W_020(web_user):
    web_user.post("/tasks/new", data={"title": "<b>Bold</b> <i>formatted</i> title"})
    html = text(web_user.get("/"))
    assert "<b>Bold</b>" not in html and "&lt;b&gt;Bold&lt;/b&gt;" in html


@REG
@cov(GUI["forms"], GUI["data_display"])
@known_defect("DEF-012", "whitespace-only title passes HTML 'required' and is saved as a blank task")
def test_whitespace_title_rejected_AT_W_021(web_user):
    web_user.post("/tasks/new", data={"title": "   "})
    assert task_titles(text(web_user.get("/"))) == []


# ---------------------------------------------------------------------------
# Usability retests (objective oracles only)
# ---------------------------------------------------------------------------

@REG
@cov("TC-USA-002")
@known_defect("DEF-017", "new user with no filters is told 'No tasks match your filters.'")
def test_empty_state_message_for_new_user_AT_W_022(web_user):
    assert "No tasks match your filters." not in text(web_user.get("/"))


@REG
@cov("TC-USA-004")
@known_defect("DEF-018", "invalid edit URL silently redirects to the list with no 'not found' message")
def test_invalid_edit_url_gives_feedback_AT_W_023(web_user):
    assert "not found" in text(web_user.get("/tasks/999/edit", follow_redirects=True)).lower()


@cov("TC-USA-005")
def test_every_page_has_distinct_title_AT_W_024(client):
    def title(html):
        return re.search(r"<title>(.*?)</title>", html).group(1)
    seen = {title(text(client.get("/login"))), title(text(client.get("/register")))}
    client.post("/register", data={"username": "titles", "password": VALID_PASSWORD})
    client.post("/tasks/new", data={"title": "x"})
    for url in ("/", "/tasks/new", "/tasks/1/edit", "/dashboard"):
        seen.add(title(text(client.get(url))))
    assert seen == {"Log in — PyTodo Pro", "Register — PyTodo Pro", "Tasks — PyTodo Pro",
                    "New Task — PyTodo Pro", "Edit Task — PyTodo Pro", "Dashboard — PyTodo Pro"}


# ---------------------------------------------------------------------------
# HTML-level accessibility & compatibility retests (WCAG 2)
# ---------------------------------------------------------------------------

def unlabelled_controls(html):
    """Return form controls with no programmatic name: no <label for=id>, no wrapping <label>,
    no aria-label / aria-labelledby."""
    label_for = set(re.findall(r'<label[^>]*\bfor="([^"]+)"', html))
    controls = re.findall(r'<(input|select|textarea)\b([^>]*)>', html)
    bad = []
    for tag, attrs in controls:
        if re.search(r'type="(hidden|submit|button)"', attrs):
            continue
        cid = re.search(r'\bid="([^"]+)"', attrs)
        named = (cid and cid.group(1) in label_for) or "aria-label" in attrs
        if not named:
            bad.append(re.search(r'name="([^"]+)"', attrs).group(1))
    return bad


@REG
@cov(ACC["labels"])
@known_defect("DEF-010", "form labels are not associated with their inputs (WCAG 1.3.1 / 4.1.2)")
@pytest.mark.parametrize("page", ["/login", "/register", "/tasks/new"])
def test_form_controls_have_labels_AT_W_025(client, page):
    client.post("/register", data={"username": "a11y_user", "password": VALID_PASSWORD})
    if page != "/tasks/new":
        client.get("/logout")
    assert unlabelled_controls(text(client.get(page))) == []


@REG
@cov(ACC["filter_names"])
@known_defect("DEF-016", "filter selects and search box have no accessible name (WCAG 4.1.2 / 3.3.2)")
def test_filter_controls_have_names_AT_W_026(web_user):
    assert unlabelled_controls(text(web_user.get("/"))) == []


@REG
@cov(ACC["toggle_name"])
@known_defect("DEF-014", "toggle button's accessible name is just '○' / '✓' (WCAG 4.1.2)")
def test_toggle_button_has_descriptive_name_AT_W_027(web_user):
    web_user.post("/tasks/new", data={"title": "Buy groceries"})
    button = re.search(r'<button[^>]*class="check-btn"[^>]*>', text(web_user.get("/"))).group(0)
    assert "aria-label=" in button and "Buy groceries" in button


@REG
@cov(ACC["table_headers"])
@known_defect("DEF-019", "first and last task-table headers are empty (WCAG 1.3.1)")
def test_table_headers_not_empty_AT_W_028(web_user):
    headers = re.findall(r"<th>(.*?)</th>", text(web_user.get("/")), re.S)
    assert all(h.strip() for h in headers)


@REG
@cov(BB["logout"], "SEC-007")
@known_defect("DEF-026", "authenticated pages are sent without Cache-Control: no-store [found in Week 6]")
@pytest.mark.parametrize("url", ["/", "/dashboard", "/tasks/new"])
def test_authenticated_pages_not_cacheable_AT_W_030(web_user, url):
    assert "no-store" in web_user.get(url).headers.get("Cache-Control", "")


@REG
@cov("TC-CMP-005")
@known_defect("DEF-020", "no <meta name=viewport>; phones render the 980 px desktop layout")
def test_viewport_meta_present_AT_W_029(client):
    assert re.search(r'<meta name="viewport" content="width=device-width', text(client.get("/login")))
