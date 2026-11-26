"""
REST API tests: automate the Week 4 API cases (API-001..021) and the Week 5
security cases (SEC-001..011), plus the API routes that the white-box
analysis flagged as untested risks (Week 2, section 6).

Why automate: API checks are stable (no layout churn), fast through the
Flask test client, and the authorisation / input-validation checks are the
ones that must be re-run after every change. Week 4/5 ran them by hand with
curl and PowerShell across two environments; here they run identically in ~3 s.
"""

import pytest

from conftest import VALID_PASSWORD, api_create, api_login, api_register, day, known_defect
from manual_ids import BB

pytestmark = [pytest.mark.api]
REG = pytest.mark.regression
cov = pytest.mark.covers


# ---------------------------------------------------------------------------
# Registration & login
# ---------------------------------------------------------------------------

@REG
@pytest.mark.smoke
@cov(BB["register_valid"])
def test_register_valid_returns_201_AT_A_001(client):
    r = api_register(client, "newuser")
    assert r.status_code == 201
    assert r.get_json()["username"] == "newuser"


@cov(BB["register_invalid"])
@pytest.mark.parametrize("auto_id, payload, error", [
    ("AT-A-002", {"username": "us", "password": VALID_PASSWORD}, "invalid username"),
    ("AT-A-003", {"username": "gooduser", "password": "short"}, "invalid password"),
    ("AT-A-004", {}, "invalid username"),
])
def test_register_invalid_input_rejected(client, auto_id, payload, error):
    r = client.post("/api/register", json=payload)
    assert r.status_code == 400 and r.get_json()["error"] == error


@REG
@cov("new in Week 6 (API data-type EP, cf. API-013)")
@known_defect("DEF-022", "non-string username in /api/register causes HTTP 500 (.strip() on int) [found in Week 6]")
def test_register_numeric_username_rejected_AT_A_005(client):
    assert client.post("/api/register", json={"username": 123, "password": VALID_PASSWORD}).status_code == 400


@REG
@cov("TC-WB-041", "TC-WB-042", BB["register_dup"])
@known_defect("DEF-003", "duplicate usernames accepted; second account hides the first and may be impossible to log into")
def test_duplicate_username_rejected_AT_A_006(make_client):
    assert api_register(make_client(), "ayamgoreng").status_code == 201
    second = api_register(make_client(), "ayamgoreng", password="Different999")
    assert second.status_code in (400, 409)


@REG
@pytest.mark.smoke
@cov("API-005", "API-019", "API-020", BB["login"])
def test_login_valid_invalid_missing_password_AT_A_007(make_client):
    api_register(make_client(), "Siti_api")
    c = make_client()
    assert api_login(c, "Siti_api", "wrong_password").status_code == 401             # API-019
    assert c.post("/api/login", json={"username": "Siti_api"}).status_code == 401    # API-020
    r = api_login(c, "Siti_api")                                                     # API-005
    assert r.status_code == 200 and r.get_json()["username"] == "Siti_api"


# ---------------------------------------------------------------------------
# Authentication enforcement & session
# ---------------------------------------------------------------------------

@REG
@pytest.mark.smoke
@pytest.mark.parametrize("method, url", [
    pytest.param("get", "/api/tasks", marks=cov("API-003", "SEC-001")),
    pytest.param("post", "/api/tasks", marks=cov("API-021", "SEC-003")),
    pytest.param("get", "/api/tasks/1", marks=cov("new in Week 6")),
    pytest.param("put", "/api/tasks/1", marks=cov("new in Week 6")),
    pytest.param("delete", "/api/tasks/1", marks=cov("new in Week 6")),
    pytest.param("get", "/api/dashboard", marks=cov("API-004", "SEC-002")),
])
def test_protected_endpoints_require_login_AT_A_008(client, method, url):
    r = getattr(client, method)(url, json={"title": "Unauthorised Task"})
    assert r.status_code == 401 and r.get_json()["error"] == "authentication required"


@REG
@pytest.mark.smoke
@cov("SEC-007", BB["logout"])
def test_logout_invalidates_api_session_AT_A_009(make_client):
    c = make_client()
    api_register(c, "sess_user")
    assert c.get("/api/tasks").status_code == 200
    assert c.get("/logout").status_code == 302
    assert c.get("/api/tasks").status_code == 401


@cov("API-002")
def test_categories_are_public_and_seeded_AT_A_010(client):
    """Documents CURRENT behaviour flagged 'Needs Review' in API-002: categories are served
    without a session. If the team decides they must be private, flip this assertion to 401."""
    r = client.get("/api/categories")
    assert r.status_code == 200
    assert sorted(c["name"] for c in r.get_json()) == ["Personal", "Study", "Urgent", "Work"]


@cov("SEC-011")
def test_unsupported_method_returns_405_AT_A_011(client):
    assert client.put("/api/categories", json={"name": "Test Category"}).status_code == 405


# ---------------------------------------------------------------------------
# Task CRUD
# ---------------------------------------------------------------------------

@REG
@pytest.mark.smoke
@cov("API-006", "API-007", "API-008", "TC-WB-036..040")
def test_create_task_then_listed_AT_A_012(user_a, categories):
    assert user_a.get("/api/tasks").get_json() == []                         # API-006
    r = api_create(user_a, title="API Test Task", description="Testing task creation through the API",
                   category_id=categories["Work"], due_date=day(10))
    assert r.status_code == 201                                              # API-007
    t = r.get_json()
    assert (t["title"], t["category"], t["done"], t["urgency"]) == ("API Test Task", "Work", False, "Upcoming")
    assert [x["id"] for x in user_a.get("/api/tasks").get_json()] == [t["id"]]   # API-008


@REG
@pytest.mark.parametrize("auto_id, payload", [
    pytest.param("AT-A-013", {"description": "Task without a title"}, marks=cov("API-011", "SEC-009")),
    pytest.param("AT-A-014", {"title": "", "description": "Testing empty title"}, marks=cov("API-014")),
    pytest.param("AT-A-015", {"title": "   "}, marks=cov("new in Week 6 (cf. DEF-012 on web)")),
])
def test_create_task_requires_title(user_a, auto_id, payload):
    r = user_a.post("/api/tasks", json=payload)
    assert r.status_code == 400 and r.get_json()["error"] == "title is required"


@REG
@pytest.mark.smoke
@cov("API-013", "SEC-008")
@known_defect("DEF-API-001", "numeric task title causes HTTP 500 instead of 400 (same defect as SEC-DEF-002)")
def test_numeric_title_rejected_AT_A_016(user_a):
    r = api_create(user_a, title=123, description="Testing invalid title type")
    assert r.status_code == 400


@REG
@cov("TC-WB-043 (API route)", BB["due_5digit"])
@known_defect("DEF-001", "malformed due_date accepted by POST /api/tasks -> HTTP 500")
def test_api_malformed_due_date_rejected_AT_A_017(user_a):
    assert api_create(user_a, title="Bad date", due_date="19999-06-14").status_code == 400


@REG
@pytest.mark.smoke
@cov("TC-WB-043 (API route)")
@known_defect("DEF-001", "the bad due_date is stored, so list and dashboard return HTTP 500 permanently")
def test_bad_due_date_does_not_break_list_AT_A_018(user_a):
    api_create(user_a, title="Bad date", due_date="19999-06-14")
    assert user_a.get("/api/tasks").status_code == 200
    assert user_a.get("/api/dashboard").status_code == 200


@REG
@cov("API-009", "API-018", "SEC-010")
def test_get_by_id_and_not_found_AT_A_019(user_a):
    tid = api_create(user_a, title="Find me").get_json()["id"]
    assert user_a.get(f"/api/tasks/{tid}").get_json()["title"] == "Find me"     # API-009
    assert user_a.get("/api/tasks/999999").status_code == 404                  # SEC-010


@REG
@pytest.mark.smoke
@cov("SEC-004", "SEC-005")
def test_cannot_view_or_update_other_users_task_AT_A_020(user_a, user_b):
    tid = api_create(user_b, title="User B task").get_json()["id"]
    assert user_a.get(f"/api/tasks/{tid}").status_code == 404                                   # SEC-004
    assert user_a.put(f"/api/tasks/{tid}", json={"title": "Modified by User A"}).status_code == 404  # SEC-005
    assert user_b.get(f"/api/tasks/{tid}").get_json()["title"] == "User B task"


@REG
@cov("API-010")
def test_partial_update_keeps_other_fields_AT_A_021(user_a, categories):
    tid = api_create(user_a, title="Orig", description="old", category_id=categories["Work"]).get_json()["id"]
    t = user_a.put(f"/api/tasks/{tid}", json={"description": "Updated through API for verification"}).get_json()
    assert t["description"] == "Updated through API for verification"
    assert (t["title"], t["category"]) == ("Orig", "Work")


@REG
@pytest.mark.smoke
@cov(BB["toggle"])
def test_done_then_reopen_state_transition_AT_A_022(user_a):
    tid = api_create(user_a, title="Toggle me", due_date=day(5)).get_json()["id"]
    done = user_a.put(f"/api/tasks/{tid}", json={"done": True}).get_json()
    assert done["done"] is True and done["urgency"] == "Done" and done["completed_at"]
    reopened = user_a.put(f"/api/tasks/{tid}", json={"done": False}).get_json()
    assert reopened["done"] is False and reopened["completed_at"] is None and reopened["urgency"] == "Upcoming"


@REG
@cov("new in Week 6 (API negative)")
@known_defect("DEF-024", "PUT /api/tasks/<id> accepts an empty title although POST requires one [found in Week 6]")
def test_update_with_empty_title_rejected_AT_A_023(user_a):
    tid = api_create(user_a, title="Has title").get_json()["id"]
    assert user_a.put(f"/api/tasks/{tid}", json={"title": ""}).status_code == 400


@REG
@cov("API-017", "API-018")
def test_delete_own_task_AT_A_024(user_a):
    tid = api_create(user_a, title="Bye").get_json()["id"]
    assert user_a.delete(f"/api/tasks/{tid}").get_json() == {"result": "ok"}
    assert user_a.get(f"/api/tasks/{tid}").status_code == 404


@REG
@cov("new in Week 6 (cf. SEC-010)")
@known_defect("DEF-025", "DELETE of a non-existent task returns 200 'ok' instead of 404 [found in Week 6]")
def test_delete_nonexistent_returns_404_AT_A_025(user_a):
    assert user_a.delete("/api/tasks/999999").status_code == 404


# ---------------------------------------------------------------------------
# Security retests
# ---------------------------------------------------------------------------

@REG
@pytest.mark.smoke
@cov("SEC-006")
@known_defect("SEC-DEF-001", "DELETE /api/tasks/<id> does not check ownership (BOLA): user A deletes user B's task")
def test_cannot_delete_other_users_task_AT_A_026(user_a, user_b):
    tid = api_create(user_b, title="User B keeps this").get_json()["id"]
    user_a.delete(f"/api/tasks/{tid}")
    assert user_b.get(f"/api/tasks/{tid}").status_code == 200


@REG
@pytest.mark.smoke
@cov("new in Week 6 (white-box risk note, Week 2 s.6)")
@known_defect("DEF-023", "search 'q' is concatenated into SQL: injection returns other users' tasks [found in Week 6]")
def test_search_is_not_injectable_AT_A_027(user_a, user_b):
    api_create(user_b, title="User B secret")
    r = user_a.get("/api/tasks", query_string={"q": "zzz' OR user_id != 0 OR title LIKE '"})
    assert r.status_code in (200, 400)
    if r.status_code == 200:
        assert all(t["title"] != "User B secret" for t in r.get_json())


@REG
@cov("SEC-004 (list endpoint)")
def test_task_list_isolated_per_user_AT_A_028(user_a, user_b):
    api_create(user_b, title="Only B")
    assert user_a.get("/api/tasks").get_json() == []


# ---------------------------------------------------------------------------
# Filters, pagination, dashboard
# ---------------------------------------------------------------------------

@pytest.fixture
def seeded(user_a, categories):
    ids = {}
    ids["w1"] = api_create(user_a, title="Work alpha", category_id=categories["Work"]).get_json()["id"]
    ids["w2"] = api_create(user_a, title="Work beta", category_id=categories["Work"]).get_json()["id"]
    ids["p1"] = api_create(user_a, title="Personal gamma", category_id=categories["Personal"]).get_json()["id"]
    user_a.put(f"/api/tasks/{ids['w2']}", json={"done": True})
    return user_a


def titles(resp):
    return {t["title"] for t in resp.get_json()}


@REG
@cov("API-012", BB["filters"])
def test_filter_by_category_AT_A_029(seeded):
    assert titles(seeded.get("/api/tasks?category=Work")) == {"Work alpha", "Work beta"}


@cov(BB["filters"])
def test_filter_by_status_AT_A_030(seeded):
    assert titles(seeded.get("/api/tasks?status=done")) == {"Work beta"}
    assert titles(seeded.get("/api/tasks?status=open")) == {"Work alpha", "Personal gamma"}


@REG
@cov(BB["filters"])
def test_search_by_title_AT_A_031(seeded):
    # In regression because the fix for DEF-023 will rewrite this query.
    assert titles(seeded.get("/api/tasks?q=gamma")) == {"Personal gamma"}


@cov("API-015", "API-016")
def test_pagination_zero_based_newest_first_AT_A_032(user_a):
    a = api_create(user_a, title="Pagination Test A").get_json()["id"]
    b = api_create(user_a, title="Pagination Test B").get_json()["id"]
    assert [t["id"] for t in user_a.get("/api/tasks?page=0&per_page=1").get_json()] == [b]
    assert [t["id"] for t in user_a.get("/api/tasks?page=1&per_page=1").get_json()] == [a]


@REG
@pytest.mark.smoke
@cov(BB["dashboard"])
def test_dashboard_counters_AT_A_033(user_a):
    api_create(user_a, title="overdue", due_date=day(-2))
    api_create(user_a, title="soon", due_date=day(1))
    api_create(user_a, title="later", due_date=day(10))
    done_id = api_create(user_a, title="done", due_date=day(3)).get_json()["id"]
    user_a.put(f"/api/tasks/{done_id}", json={"done": True})
    assert user_a.get("/api/dashboard").get_json() == {
        "total": 4, "open": 3, "overdue": 1, "due_soon": 1, "completed_this_week": 1,
    }
