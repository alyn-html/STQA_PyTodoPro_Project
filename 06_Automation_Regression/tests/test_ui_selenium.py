"""
Selenium end-to-end tests (headless Chrome): automate the Week 3 GUI cases that
need a real browser (native date input, JS confirm() dialog, auto-submitting
<select>, HTML5 'required') and re-run the Week 3 axe-core WCAG scan
(same engine version, 4.14.1, vendored in tests/vendor/axe.min.js).

Deliberately a THIN layer: business rules are covered faster by test_api /
test_web. The app runs on a free local port in a background thread with its own
temporary database. If Chrome/Selenium is unavailable the module is SKIPPED.
Set SELENIUM_HEADED=1 to watch the browser.
"""

import json
import os
import threading
import uuid
from pathlib import Path

import pytest

from conftest import VALID_PASSWORD, app_module, day, defect_marks
from manual_ids import ACC, BB, GUI

pytest.importorskip("selenium")
from selenium import webdriver  # noqa: E402
from selenium.common.exceptions import WebDriverException  # noqa: E402
from selenium.webdriver.chrome.service import Service  # noqa: E402
from selenium.webdriver.common.by import By  # noqa: E402
from selenium.webdriver.support import expected_conditions as EC  # noqa: E402
from selenium.webdriver.support.ui import Select, WebDriverWait  # noqa: E402
from werkzeug.serving import make_server  # noqa: E402

pytestmark = [pytest.mark.ui]
REG = pytest.mark.regression
cov = pytest.mark.covers
AXE_JS = (Path(__file__).parent / "vendor" / "axe.min.js").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def live_server(tmp_path_factory):
    db = tmp_path_factory.mktemp("ui") / "ui_pytodo.db"
    original = app_module.DATABASE
    app_module.DATABASE = str(db)
    app_module.init_db()
    server = make_server("127.0.0.1", 0, app_module.app, threaded=True)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    app_module.DATABASE = original


@pytest.fixture(scope="module")
def driver():
    opts = webdriver.ChromeOptions()
    if not os.environ.get("SELENIUM_HEADED"):
        opts.add_argument("--headless=new")
    for arg in ("--no-sandbox", "--disable-dev-shm-usage", "--window-size=1280,800"):
        opts.add_argument(arg)
    # Selenium Manager normally finds the right driver. CHROMEDRIVER_PATH points at a specific
    # one (CI / offline lab); CHROMEDRIVER_DISABLE_BUILD_CHECK=1 tolerates a version gap.
    args = ["--disable-build-check"] if os.environ.get("CHROMEDRIVER_DISABLE_BUILD_CHECK") else []
    path = os.environ.get("CHROMEDRIVER_PATH")
    service = Service(executable_path=path, service_args=args) if path else Service(service_args=args)
    try:
        drv = webdriver.Chrome(options=opts, service=service)
    except WebDriverException as exc:
        pytest.skip(f"Chrome WebDriver not available: {exc.msg}")
    drv.implicitly_wait(2)
    yield drv
    drv.quit()


@pytest.fixture
def logged_in(driver, live_server):
    """Register a fresh unique user through the real form."""
    driver.delete_all_cookies()
    username = "ui_" + uuid.uuid4().hex[:8]
    driver.get(live_server + "/register")
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(VALID_PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
    WebDriverWait(driver, 5).until(EC.title_contains("Tasks"))
    return username


def create_task(driver, base, title, category=None, due=None):
    driver.get(base + "/tasks/new")
    driver.find_element(By.NAME, "title").send_keys(title)
    if category:
        Select(driver.find_element(By.NAME, "category_id")).select_by_visible_text(category)
    if due:  # set via JS: typing into <input type=date> depends on the OS locale
        driver.execute_script("arguments[0].value = arguments[1];", driver.find_element(By.NAME, "due_date"), due)
    driver.find_element(By.XPATH, "//button[text()='Create Task']").click()
    WebDriverWait(driver, 5).until(EC.title_contains("Tasks"))


def click_and_wait_for(driver, element, css):
    """Click something that posts a form, then wait for the EXPECTED new state.
    Asserting before the reload finishes reads the old page (a classic flaky-test cause)."""
    element.click()
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, css)))


def row_titles(driver):
    return [e.text for e in driver.find_elements(By.CSS_SELECTOR, "td.title-cell")]


# ---------------------------------------------------------------------------
# GUI journeys
# ---------------------------------------------------------------------------

@REG
@pytest.mark.smoke
@cov(GUI["nav"], BB["register_valid"], "TC-CMP-001")
def test_register_and_nav_AT_UI_001(driver, logged_in):
    assert driver.find_element(By.CSS_SELECTOR, ".nav-user").text == logged_in
    links = [a.text for a in driver.find_elements(By.CSS_SELECTOR, ".nav-links a")]
    assert links == ["Tasks", "Dashboard", "Log out"]


@cov(GUI["messages"], BB["login"])
def test_invalid_login_message_AT_UI_002(driver, live_server):
    driver.delete_all_cookies()
    driver.get(live_server + "/login")
    driver.find_element(By.NAME, "username").send_keys("invalid_test_user")
    driver.find_element(By.NAME, "password").send_keys("wrong_password")
    driver.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
    assert driver.find_element(By.CSS_SELECTOR, "p.error").text == "Invalid username or password."


@cov(GUI["forms"])
def test_html5_required_blocks_empty_title_AT_UI_003(driver, live_server, logged_in):
    driver.get(live_server + "/tasks/new")
    driver.find_element(By.XPATH, "//button[text()='Create Task']").click()
    assert driver.title.startswith("New Task")
    assert driver.execute_script("return document.querySelector('input[name=title]').checkValidity();") is False


@REG
@pytest.mark.smoke
@cov(GUI["forms"], GUI["data_display"], BB["create"], "TC-CMP-001")
def test_create_task_end_to_end_AT_UI_004(driver, live_server, logged_in):
    create_task(driver, live_server, "Selenium task", category="Work", due=day(2))
    row = driver.find_element(By.XPATH, "//tr[td[@class='title-cell' and text()='Selenium task']]")
    assert "Work" in row.text and "Due Soon" in row.text


@cov(GUI["buttons"], BB["toggle"])
def test_toggle_updates_row_AT_UI_005(driver, live_server, logged_in):
    create_task(driver, live_server, "Toggle via UI")
    click_and_wait_for(driver, driver.find_element(By.CSS_SELECTOR, "button.check-btn"), "tbody tr.done")
    assert "Done" in driver.find_element(By.CSS_SELECTOR, "tbody tr").text


@REG
@cov(GUI["filters_persist"], BB["filters"])
def test_status_filter_autosubmits_and_persists_AT_UI_006(driver, live_server, logged_in):
    create_task(driver, live_server, "Open one")
    create_task(driver, live_server, "Closed one")
    click_and_wait_for(driver, driver.find_element(By.CSS_SELECTOR, "button.check-btn"), "tbody tr.done")
    Select(driver.find_element(By.NAME, "status")).select_by_value("open")
    WebDriverWait(driver, 5).until(EC.url_contains("status=open"))
    assert row_titles(driver) == ["Open one"]
    assert Select(driver.find_element(By.NAME, "status")).first_selected_option.text == "Open"


@REG
@pytest.mark.smoke
@cov(GUI["delete_confirm"], BB["delete"])
def test_delete_confirm_cancel_then_ok_AT_UI_007(driver, live_server, logged_in):
    create_task(driver, live_server, "Delete me")
    driver.find_element(By.CSS_SELECTOR, "button.link-btn").click()
    alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
    assert alert.text == "Delete this task?"
    alert.dismiss()                                   # Cancel keeps the task
    assert row_titles(driver) == ["Delete me"]
    driver.find_element(By.CSS_SELECTOR, "button.link-btn").click()
    WebDriverWait(driver, 5).until(EC.alert_is_present()).accept()
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "td.empty")))


@cov(GUI["nav"], BB["dashboard"])
def test_dashboard_navigation_AT_UI_008(driver, live_server, logged_in):
    create_task(driver, live_server, "Late", due=day(-3))
    driver.find_element(By.LINK_TEXT, "Dashboard").click()
    WebDriverWait(driver, 5).until(EC.title_contains("Dashboard"))
    assert [e.text for e in driver.find_elements(By.CSS_SELECTOR, ".stat-value")] == ["1", "1", "1", "0", "0"]


@REG
@pytest.mark.smoke
@cov(GUI["nav"], BB["logout"])
def test_logout_and_protected_pages_AT_UI_009(driver, live_server, logged_in):
    driver.find_element(By.LINK_TEXT, "Log out").click()
    WebDriverWait(driver, 5).until(EC.title_contains("Log in"))
    driver.get(live_server + "/dashboard")
    assert driver.title.startswith("Log in")          # session really ended


@REG
@cov(BB["logout"], "SEC-007")
@pytest.mark.parametrize("dummy", [pytest.param(0, marks=defect_marks(
    "DEF-026", "after logout, browser Back shows the cached task list (no Cache-Control: no-store) [found in Week 6]"))])
def test_back_after_logout_does_not_show_tasks_AT_UI_011(driver, live_server, logged_in, dummy):
    create_task(driver, live_server, "private cached task")
    driver.find_element(By.LINK_TEXT, "Log out").click()
    WebDriverWait(driver, 5).until(EC.title_contains("Log in"))
    driver.back()
    assert "private cached task" not in driver.page_source


# ---------------------------------------------------------------------------
# axe-core accessibility scan (re-runs the Week 3 automated WCAG 2 A/AA scan)
# ---------------------------------------------------------------------------

def axe_violations(driver):
    driver.execute_script(AXE_JS)
    result = driver.execute_async_script(
        "const done = arguments[arguments.length - 1];"
        "axe.run(document, {runOnly: {type: 'tag', values: ['wcag2a', 'wcag2aa']}})"
        "   .then(r => done(JSON.stringify(r.violations))).catch(e => done(JSON.stringify([{id: 'axe-error: ' + e}])));")
    return [(v["id"], v.get("impact"), len(v.get("nodes", []))) for v in json.loads(result)]


@REG
@cov(ACC["axe"])
@pytest.mark.parametrize("page, needs_login, seed_task", [
    pytest.param("/login", False, False, marks=[cov(ACC["labels"])] + defect_marks(
        "DEF-010", "axe 'label' violations on Login")),
    pytest.param("/register", False, False, marks=[cov(ACC["labels"])] + defect_marks(
        "DEF-010", "axe 'label' violations on Register")),
    pytest.param("/", True, True, marks=[cov(ACC["filter_names"])] + defect_marks(
        "DEF-016", "axe 'select-name' violations on the task list")),
    pytest.param("/tasks/new", True, False, marks=[cov(ACC["labels"])] + defect_marks(
        "DEF-010", "axe 'label' + 'select-name' violations on New Task")),
    pytest.param("/dashboard", True, False),
])
def test_axe_wcag2_no_serious_violations_AT_UI_010(driver, live_server, page, needs_login, seed_task, request):
    driver.delete_all_cookies()
    if needs_login:
        request.getfixturevalue("logged_in")
        if seed_task:
            create_task(driver, live_server, "axe sample task", category="Work", due=day(1))
    driver.get(live_server + page)
    bad = [v for v in axe_violations(driver) if v[1] in ("critical", "serious")]
    print(f"axe violations on {page}: {bad}")
    assert bad == []
