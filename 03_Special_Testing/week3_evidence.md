"""Week 3 evidence capture for PyTodo Pro (Chrome via Playwright)."""
import json, datetime, os
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont

BASE = "http://127.0.0.1:5000"
OUT = "/home/claude/w3/screenshots/"
os.makedirs(OUT, exist_ok=True)
TODAY = datetime.date.today()
TOMORROW = TODAY + datetime.timedelta(days=1)
AXE = open("/home/claude/axe/node_modules/axe-core/axe.min.js").read()
LOG = {}
FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
FONTB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
BROWSER = "Chrome 153 (headless, Linux)"


def shot(page, name, tc, note="", full=True):
    """Screenshot + header strip with test ID, URL, browser, viewport and time."""
    path = OUT + name + ".png"
    page.screenshot(path=path, full_page=full)
    im = Image.open(path)
    vp = page.viewport_size
    head = Image.new("RGB", (im.width, 58), (31, 56, 100))
    d = ImageDraw.Draw(head)
    d.text((12, 8), f"{tc}", font=FONTB, fill="white")
    d.text((12 + d.textlength(tc, font=FONTB) + 14, 8), note, font=FONT, fill=(255, 230, 150))
    d.text((12, 32), f"URL: {page.url}   |   {BROWSER}   |   viewport {vp['width']}x{vp['height']}   |   "
           f"{datetime.datetime.now():%Y-%m-%d %H:%M}", font=FONT, fill=(210, 220, 235))
    out = Image.new("RGB", (im.width, im.height + 58), "white")
    out.paste(head, (0, 0)); out.paste(im, (0, 58))
    out.save(path)


def add_task(page, title, cat=None, due=None):
    page.goto(BASE + "/tasks/new")
    page.fill("input[name=title]", title)
    if cat:
        page.select_option("select[name=category_id]", label=cat)
    if due:
        page.fill("input[name=due_date]", due.isoformat())
    page.click("button[type=submit]")


with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    ctx = b.new_context(viewport={"width": 1280, "height": 800})
    page = ctx.new_page()

    # --- logged-out pages
    page.goto(BASE + "/login")
    shot(page, "01_login_page", "TC-GUI-001 / TC-GUI-002", "Login page & logged-out navigation")
    LOG["login_title"] = page.title()

    page.goto(BASE + "/register")
    page.fill("input[name=username]", "ab"); page.fill("input[name=password]", "Passw0rd123")
    page.click("button[type=submit]")
    LOG["register_username_value_after_error"] = page.input_value("input[name=username]")
    shot(page, "02_register_username_error", "TC-GUI-005 / TC-USA-001", "Error shown; username field cleared (DEF-013)")

    page.fill("input[name=username]", "tester1"); page.fill("input[name=password]", "abcd1234")
    page.click("button[type=submit]")
    LOG["register_8char_error"] = page.inner_text(".error")
    shot(page, "03_register_8char_password_rejected", "TC-GUI-006", "8-char password rejected despite '(min 8 characters)' hint (DEF-006)")

    page.fill("input[name=username]", "tester1"); page.fill("input[name=password]", "abcd12345")
    page.click("button[type=submit]")
    shot(page, "04_empty_task_list", "TC-GUI-003 / TC-USA-002", "New user, no filters: 'No tasks match your filters.' (DEF-017)")

    page.goto(BASE + "/tasks/new")
    shot(page, "05_new_task_form", "TC-GUI-007", "New Task form")

    add_task(page, "Submit STQA report", "Study", TODAY)
    add_task(page, "Buy groceries", "Personal", TOMORROW)
    add_task(page, "<b>Bold</b> <i>formatted</i> title", "Work")
    add_task(page, "   ")  # whitespace-only title passes HTML 'required'
    LOG["rows_after_create"] = page.locator("tbody tr").count()
    shot(page, "06_task_list_defects", "TC-GUI-009 / 010 / 014",
         "Blank-title row (DEF-012) · HTML rendered in title (DEF-011) · due today = 'Overdue' (DEF-002)")

    page.goto(BASE + "/dashboard")
    LOG["dashboard"] = page.locator(".stat-card").all_inner_texts()
    shot(page, "07_dashboard_overdue_count", "TC-GUI-015", "Overdue = 1 although only task is due TODAY (DEF-002)")

    page.goto(BASE + "/")
    page.locator("tbody tr", has_text="Buy groceries").get_by_role("link", name="Edit").click()
    shot(page, "08_edit_task_form", "TC-GUI-008", "Edit form pre-filled; 'Save Changes' + Cancel")
    page.click("a.btn-secondary")
    LOG["cancel_url"] = page.url

    page.locator("tbody tr", has_text="Buy groceries").locator(".check-btn").click()
    LOG["toggled_row_class"] = page.locator("tbody tr", has_text="Buy groceries").get_attribute("class")
    shot(page, "09_task_toggled_done", "TC-GUI-011", "'Buy groceries' marked done: ✓ and 'Done' badge")

    # --- filters: count reloads triggered by keyboard selection (WCAG 3.2.2)
    navs = []
    page.on("framenavigated", lambda f: navs.append(f.url) if f == page.main_frame else None)
    page.focus("select[name=category]")
    try:
        with page.expect_navigation(timeout=3000):
            page.keyboard.press("ArrowDown")
    except Exception:
        pass
    LOG["reload_after_one_arrow_key"] = list(navs)
    page.goto(BASE + "/?category=Study&status=open&q=STQA")
    shot(page, "10_filters_persist", "TC-GUI-013", "Category, status and search text retained after filtering")

    # --- delete confirm dialog
    page.goto(BASE + "/")
    msgs = []
    before = page.locator("tbody tr").count()
    page.once("dialog", lambda d: (msgs.append(d.message), d.dismiss()))
    page.locator("tbody tr", has_text="Submit STQA").get_by_role("button", name="Delete").click()
    page.wait_for_timeout(300)
    after_dismiss = page.locator("tbody tr").count()
    page.once("dialog", lambda d: (msgs.append(d.message), d.accept()))
    page.locator("tbody tr", has_text="Submit STQA").get_by_role("button", name="Delete").click()
    page.wait_for_load_state()
    after_accept = page.locator("tbody tr").count()
    LOG["delete_dialog"] = {"messages": msgs, "rows_before": before, "after_cancel": after_dismiss, "after_ok": after_accept}
    shot(page, "11_after_delete_confirmed", "TC-GUI-012",
         f"Dialog '{msgs[0] if msgs else ''}' — Cancel kept task ({before}→{after_dismiss}); OK deleted it ({after_dismiss}→{after_accept})")

    page.goto(BASE + "/tasks/999/edit")
    shot(page, "12_invalid_edit_url_no_message", "TC-USA-004", "/tasks/999/edit silently redirected to list — no 'not found' message (DEF-018)")

    # --- accessibility checks
    a11y = {}
    page.goto(BASE + "/")
    a11y["toggle_button_names"] = [page.locator(".check-btn").nth(i).evaluate("e => e.textContent.trim()")
                                   for i in range(page.locator(".check-btn").count())]
    a11y["empty_th"] = page.locator("thead th").all_inner_texts()
    a11y["search_by_label_count"] = page.get_by_label("Search").count()
    a11y["search_attrs"] = page.locator("input[name=q]").evaluate("e => ({id:e.id, ariaLabel:e.getAttribute('aria-label'), placeholder:e.placeholder})")
    # keyboard focus order
    page.goto(BASE + "/")
    order = []
    for i in range(14):
        page.keyboard.press("Tab")
        order.append(page.evaluate("""() => {const e=document.activeElement;
            return e.tagName.toLowerCase() + (e.name? '[name='+e.name+']':'') + ' "' + (e.innerText||e.value||e.placeholder||'').trim().slice(0,25) + '"'}"""))
        if i == 9:
            shot(page, "13_keyboard_focus_visible", "TC-ACC-009", f"Keyboard-only: Tab #{i+1} focus on {order[-1]} (default focus ring visible)", full=False)
    a11y["tab_order"] = order
    for url in ["/login", "/register"]:
        page.goto(BASE + "/logout"); page.goto(BASE + url)
        a11y[f"getByLabel_Username_{url}"] = page.get_by_label("Username").count()
    page.goto(BASE + "/login")
    page.click("text=Username")
    a11y["focus_after_clicking_label"] = page.evaluate("document.activeElement.tagName")
    shot(page, "14_label_not_associated", "TC-ACC-002",
         f"Clicked the 'Username' label → focus stays on {a11y['focus_after_clicking_label']} (not the input): labels lack for/id (DEF-010)")
    page.fill("input[name=username]", "tester1"); page.fill("input[name=password]", "wrongpass1")
    page.click("button[type=submit]")
    shot(page, "15_login_error", "TC-GUI-004 / TC-ACC-008", "Invalid credentials message")
    page.fill("input[name=username]", "tester1"); page.fill("input[name=password]", "abcd12345")
    page.click("button[type=submit]")

    # --- axe-core automated scan
    axe = {}
    for name, url in [("Login", "/login"), ("Task list", "/"), ("New task", "/tasks/new"), ("Dashboard", "/dashboard")]:
        if name == "Login":
            page.goto(BASE + "/logout")
        page.goto(BASE + url)
        page.add_script_tag(content=AXE)
        res = page.evaluate("async () => await axe.run(document, {runOnly:['wcag2a','wcag2aa']})")
        axe[name] = [{"id": v["id"], "impact": v["impact"], "help": v["help"], "nodes": len(v["nodes"]),
                      "wcag": [t for t in v["tags"] if t.startswith("wcag") and t[4:5].isdigit()]} for v in res["violations"]]
        if name == "Login":
            page.fill("input[name=username]", "tester1"); page.fill("input[name=password]", "abcd12345")
            page.click("button[type=submit]")
    LOG["axe"] = axe
    LOG["a11y"] = a11y

    # --- reflow / zoom (320 CSS px ≈ 1280 px at 400%; WCAG 1.4.10)
    for w, tag in [(640, "200pct"), (320, "320px")]:
        page.set_viewport_size({"width": w, "height": 700})
        page.goto(BASE + "/")
        sw = page.evaluate("[document.documentElement.scrollWidth, document.documentElement.clientWidth]")
        LOG[f"reflow_{tag}"] = sw
        shot(page, f"16_reflow_{tag}", "TC-ACC-011",
             f"Width {w}px: scrollWidth {sw[0]} vs viewport {sw[1]} → {'horizontal scroll' if sw[0] > sw[1] else 'no horizontal scroll'}")
    ctx.close()

    # --- mobile viewport smoke flow (TC-CMP-005)
    m = b.new_context(viewport={"width": 375, "height": 667}, is_mobile=True, has_touch=True, device_scale_factor=2,
                      user_agent="Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0 Mobile Safari/537.36")
    mp = m.new_page()
    BROWSER = "Chrome 153 mobile emulation (Pixel-class UA, touch)"
    mob = {}
    mp.goto(BASE + "/register"); mp.fill("input[name=username]", "mobile_user"); mp.fill("input[name=password]", "abcd12345")
    
    with mp.expect_navigation(): mp.tap("button[type=submit]")
    mob["register"] = mp.url.endswith("/")
    add_task(mp, "Mobile task", "Work", TOMORROW); mob["create"] = mp.locator("tbody tr", has_text="Mobile task").count() == 1
    shot(mp, "17_mobile_task_list", "TC-CMP-005", "375x667 mobile: no viewport meta → page laid out at 980px and shrunk (DEF-020)", full=False)
    
    with mp.expect_navigation(): mp.locator(".check-btn").first.tap()
    mob["toggle"] = "done" in (mp.locator("tbody tr").first.get_attribute("class") or "")
    mp.goto(BASE + "/?status=done"); mob["filter"] = mp.locator("tbody tr", has_text="Mobile task").count() == 1
    mp.once("dialog", lambda d: d.accept())
    with mp.expect_navigation(): mp.get_by_role("button", name="Delete").first.tap()
    mob["delete"] = mp.locator("tbody tr", has_text="Mobile task").count() == 0
    mp.goto(BASE + "/dashboard"); shot(mp, "18_mobile_dashboard", "TC-CMP-005", "375x667 mobile: dashboard rendered at desktop width (DEF-020)", full=False)
    mob["dash_scroll"] = mp.evaluate("[document.documentElement.scrollWidth, document.documentElement.clientWidth]")
    mp.goto(BASE + "/logout"); mob["logout"] = mp.url.endswith("/login")
    LOG["mobile"] = mob
    b.close()

# axe summary image
rows = "".join(f"<tr><td>{pg}</td><td><code>{v['id']}</code></td><td>{v['impact']}</td><td>{v['help']}</td><td>{', '.join(v['wcag'])}</td><td>{v['nodes']}</td></tr>"
               for pg, vs in LOG["axe"].items() for v in vs) + "".join(f"<tr><td>{pg}</td><td colspan=5 style='color:#2e7d32'>No WCAG 2 A/AA violations detected</td></tr>" for pg, vs in LOG["axe"].items() if not vs)
html = f"""<html><body style='font-family:DejaVu Sans,sans-serif;margin:0'><div style='background:#1F3864;color:#fff;padding:10px 14px'>
<b>TC-ACC-002 / TC-ACC-003</b> &nbsp; axe-core {json.load(open('/home/claude/axe/node_modules/axe-core/package.json'))['version']} automated scan · rules: wcag2a + wcag2aa · {BROWSER.split(' mobile')[0]} · {datetime.datetime.now():%Y-%m-%d %H:%M}</div>
<table style='border-collapse:collapse;margin:14px;font-size:14px' border=1 cellpadding=7><tr style='background:#D9E1F2'><th>Page</th><th>Rule</th><th>Impact</th><th>Description</th><th>WCAG</th><th>Elements</th></tr>{rows}</table>
<p style='margin:0 14px 14px;font-size:12px;color:#555'>Automated tools find only a subset of WCAG issues; manual checks are recorded separately in the test cases.</p></body></html>"""
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": 1100, "height": 100}); pg.set_content(html)
    pg.screenshot(path=OUT + "19_axe_scan_summary.png", full_page=True); b.close()

json.dump(LOG, open("/home/claude/w3/evidence_log.json", "w"), indent=2, ensure_ascii=False)
print(json.dumps(LOG, indent=1, ensure_ascii=False))
