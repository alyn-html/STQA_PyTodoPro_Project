# Project Week 6 — Test Automation and Regression

**Application under test:** PyTodo Pro (Flask 3.0.3, SQLite)
**Course:** TEB3433 / TFB3433 Software Testing and Quality Assurance
**Artefact location:** `/06_Automation_Regression` (how to run: `README.md`)

> **Before submitting:** the Week 1 findings list `TC-BB-001…028` but not which ID tests which behaviour,
> and the Week 3 findings name only some `TC-GUI` / `TC-ACC` IDs. Those references appear below as
> `TC-BB-??` / `TC-GUI-??` / `TC-ACC-??` with a description. Fill them in once in `tests/manual_ids.py`
> and re-run to regenerate `reports/traceability.csv`. All other IDs (TC-WB, TC-USA, TC-GUI-012/013,
> TC-CMP-001/005, API, SEC, DEF) come straight from the Week 1–5 findings.

---

## 1. Objective and scope

Week 6 re-uses the manual and partly-automated tests from Weeks 1–5 to build:
1. a repeatable automated suite;
2. a **focused regression suite** that is re-run after every change;
3. an **automated retest for every open defect** that has an objective pass/fail rule.

**Tools:** PyTest 9 (prescribed framework), Flask test client (API and server-rendered pages),
Selenium 4 with headless Chrome 153 (approved browser tool), axe-core 4.14.1 (the same engine and
version as the Week 3 scan), pytest-cov, pytest-html and JUnit XML for evidence.

## 2. Review of manual tests from Weeks 1–5

| Week | Activity | Cases | Result | Defects logged | How it was run |
|---|---|---|---|---|---|
| 1 | Black-box (EP, BVA, decision table, state transition) | 28 (TC-BB-001…028) | 23 pass / 5 fail | DEF-001…005 | Manual, Chrome, Windows 11 |
| 2 | White-box (statement, branch, boundary) | 43 (TC-WB-001…043) | 35 pass / 8 fail | DEF-006…009 | **Already in PyTest** (`test_whitebox.py`) |
| 3 | GUI / usability / accessibility / compatibility | 38 planned, 33 run | 18 pass / 15 fail / 5 not run | DEF-010…021 | Playwright evidence script + axe-core |
| 4 | API | 21 (API-001…021) | 19 pass / 1 fail / 1 needs review | DEF-API-001 | Manual `curl`, Codespaces |
| 5 | Security | 11 (SEC-001…011) | 9 pass / 2 fail | SEC-DEF-001, 002 | Manual `curl` + PowerShell, 2 environments |
| 5 | Performance | 4 (PERF-001…004) | 4 pass | – | PowerShell timing, 20 requests each |
| | **Total** | **140 executed** | | **24 defect IDs** | |

**What the review showed:**
- **The same areas keep failing across weeks:** date handling (DEF-001/002), registration (DEF-003/004/006),
  input validation (DEF-012, DEF-API-001) and output encoding (DEF-011). These need re-checking after
  every fix, so they are the strongest regression candidates.
- **Weeks 4–5 were run by hand in two environments** (Codespaces and Windows) with shared, hand-made
  accounts and task IDs (e.g. task `8`). They are slow to repeat and hard to reproduce exactly.
- **Week 2 was already in PyTest.** Its boundary cases are kept, but only the regression-worthy subset is
  re-expressed here with the same fixed clock (`today = 2026-11-24`).
- **Some areas were flagged but never tested:** Week 2 flagged the f-string SQL in `api_list_tasks()`
  as a Week 5 target, but Week 5 did not test it. Week 2 also predicted the API route to DEF-001 ("to be
  confirmed in Week 4"), which Week 4 did not test either. Both are automated now (§8).
- **Defect records need consolidating:** SEC-DEF-002 and DEF-API-001 are the same defect.
  DEF-004 was already marked *Retest* by Week 2.

## 3. Automation candidate justification

Each manual test group was scored 1 (low) – 3 (high) on the brief's four criteria. **Feasibility**
(can a tool decide pass/fail without human judgement?) was used as a gate.

| Manual test group | Repetition | Stability | Criticality | Regression value | Objective oracle? | Decision |
|---|---|---|---|---|---|---|
| Urgency BVA (TC-BB urgency, TC-WB-001…009) | 3 | 3 | 3 | 3 | Yes, exact label | **Automate: unit** |
| Password / username rules (TC-WB-010…024, TC-BB registration) | 3 | 3 | 3 | 3 | Yes | **Automate: unit + web** |
| 7-day completion window (TC-WB-025…035) | 2 | 3 | 2 | 3 | Yes, injectable clock | **Automate: unit** |
| Registration, login decision table, logout (TC-BB, API-005/019/020, SEC-007) | 3 | 3 | 3 | 3 | Yes, status/redirect | **Automate: API + web + UI** |
| Task CRUD + done/reopen state transitions (TC-BB, API-006…018) | 3 | 3 | 3 | 3 | Yes | **Automate: API + web** |
| Filters, search, pagination (TC-BB decision table, TC-GUI-013, API-012/015/016) | 2 | 3 | 2 | 2 | Yes | **Automate: API + web** |
| Dashboard counters (TC-BB state transition) | 2 | 3 | 2 | 3 | Yes, exact numbers | **Automate: API + web** |
| Authentication & cross-user access (SEC-001…006, API-003/004/021) | 3 | 3 | 3 | 3 | Yes | **Automate: API + web** |
| Input validation & error handling (API-011/013/014, SEC-008…011) | 3 | 3 | 3 | 3 | Yes | **Automate: API** |
| Browser-only GUI behaviour (confirm dialog, date input, auto-submit select, HTML5 `required`) | 2 | 2 | 2 | 2 | Yes | **Automate: thin Selenium layer** |
| Accessibility with objective rules (labels, names, headers, viewport; axe scan) | 2 | 3 | 2 | 3 | Yes, DOM rules | **Automate: web HTML checks + axe in Selenium** (the Week 3 recommendation) |
| Usability items with a fixed oracle (TC-USA-001…005) | 1 | 3 | 1 | 2 | Yes, text present/absent | **Automate: web** |
| Usability heuristics needing judgement, visual consistency | 1 | 1 | 2 | 1 | No | Keep manual |
| Keyboard behaviour of filter selects (DEF-015) | 1 | 1 | 1 | 1 | OS-dependent (macOS opens the list, Windows/Linux change value) | Keep manual |
| Reflow at 320 px / colour contrast (DEF-021, not-run items) | 1 | 1 | 1 | 1 | Depends on missing `style.css` | Keep manual until stylesheet available |
| Compatibility: Firefox / Edge / Safari (TC-CMP-002…004) | 1 | 2 | 2 | 1 | Yes, but browsers unavailable | Not automated. The Selenium suite can run in other browsers once installed |
| Performance (PERF-001…004) | 1 | 1 | 2 | 1 | Needs controlled load environment | Keep separate (load tool), not functional regression |
| STRIDE analysis, exploratory sessions | 1 | – | 3 | 1 | No | Keep manual |
| Password complexity (DEF-005) | – | – | – | – | Spec requires length only | Not a defect (Week 2). Recommend as improvement |

**Layering (test pyramid).** Each rule is checked at the **lowest layer that can observe it**. Only
behaviour that needs a real browser goes through Selenium. As a result, 88 % of the tests run in about
7 seconds without a browser.

| Layer | File | Tests | Share | Runtime |
|---|---|---|---|---|
| Unit (`helpers.py`) | `test_unit_helpers.py` | 35 | 28 % | 0.3 s |
| API + security | `test_api.py` | 38 | 30 % | 3.6 s |
| Web pages, usability, HTML accessibility | `test_web.py` | 37 | 30 % | 3.5 s |
| UI end-to-end + axe scan (Selenium) | `test_ui_selenium.py` | 15 | 12 % | 13.7 s |
| **Total** | | **125** (79 test functions; parametrised cases count separately) | | **~21 s** |

**How open defects are handled.** Every test asserts the **specified** behaviour, never the buggy one.
A test that hits an open defect carries `known_defect("DEF-xxx", ...)`, which marks it
`xfail(strict=True)`. As a result:
- the suite stays green while defects are open, so any **new** failure stands out;
- each open defect has an automatic retest. When a developer fixes it, the test turns `XPASS(strict)`
  and pytest reports it as a failure, which prompts the team to retest, close the defect and remove the
  marker (demonstrated in §6.5).

## 4. Automated scripts

| File | IDs | Contents |
|---|---|---|
| `tests/conftest.py` | – | Temp-DB fixture; independent sessions for `security_user_a` / `security_user_b`; `known_defect` helper; **traceability plugin** that writes `reports/traceability.csv` from each test's `@covers(...)` marker and its real outcome |
| `tests/manual_ids.py` | – | Placeholders for the TC-BB / TC-GUI / TC-ACC IDs (fill in once) |
| `tests/test_unit_helpers.py` | AT-U-001…035 | `compute_urgency`, `is_valid_password`, `is_valid_username`, `completed_in_last_n_days`, using the Week 1 BVA values and Week 2 clock |
| `tests/test_api.py` | AT-A-001…033 | API-001…021, SEC-001…011, the white-box risk routes, and new negative cases |
| `tests/test_web.py` | AT-W-001…030 | Black-box workflows, TC-USA checks, HTML-level WCAG checks, caching headers |
| `tests/test_ui_selenium.py` | AT-UI-001…011 | Browser journeys (TC-GUI-012/013, TC-CMP-001), axe-core WCAG 2 A/AA scan of 5 pages, Back-after-logout |
| `tools/make_fixed_copy.py` | – | Builds a throw-away copy of the app with every open defect fixed, used to validate the tests (§6.4) |

Test data mirrors the earlier weeks where useful: accounts `ayamgoreng`, `security_user_a/b` and `Siti`;
date `19999-06-14`; title `<b>Bold</b> <i>formatted</i> title`; passwords `abcd1234` / `password`
(8 characters); title `123`.

## 5. Manual-to-automated traceability

Full matrix with per-test results: **`reports/traceability.csv`** (125 rows, generated by the run).
Summary by source (S = smoke, R = regression, ✗ = open-defect retest, XFAIL while open):

### 5.1 Week 2 white-box → unit layer

| Manual case(s) | Automated | Result | Defect | Suites |
|---|---|---|---|---|
| TC-WB-001…009 urgency (+ TC-BB urgency BVA −2, −1, +1, +2, +3, blank) | AT-U-001…004, 006…009 | 8 pass | | S R |
| TC-WB-004 due today (+ TC-BB urgency = 0) | AT-U-005 ✗ | XFAIL | DEF-002 | R |
| TC-WB-009 5-digit year in helper | AT-U-010 | pass (characterisation) | root cause of DEF-001 | – |
| TC-WB-008 default clock | AT-U-011 | pass | | – |
| TC-WB-010…015 password: 0, 7, 9, 11 chars, None, int | AT-U-012, 013, 015…018 | 6 pass | | S R |
| TC-WB-013 password = 8 chars | AT-U-014 ✗ | XFAIL | DEF-006 | S R |
| TC-WB-016…023 username: 2/3/20/21 chars, loop pass/fail, type | AT-U-019…026 | 8 pass | | – |
| TC-WB-024 non-ASCII username | AT-U-033 ✗ | XFAIL | DEF-009 (spec pending) | – |
| TC-WB-025…035 completed window: none, 1 s, 6d23h (028), 7d1h (030), future (032) | AT-U-027…029, 031, 032 | 5 pass | | R |
| TC-WB-029 exactly 7 days | AT-U-030 ✗ | XFAIL | DEF-007 | R |
| TC-WB-033 same second | AT-U-034 ✗ | XFAIL | DEF-008 | R |
| TC-WB-034 default clock | AT-U-035 | pass | | – |
| TC-WB-036…040 app glue (`row_to_task`, `get_category_name`, `login_required_web`) | AT-A-012, AT-W-001 | pass | | S R |
| TC-WB-041/042 duplicate registration | AT-A-006 ✗ | XFAIL | DEF-003 | R |
| TC-WB-043 bad due date path (web) | AT-W-016 ✗ | XFAIL | DEF-001 | S R |

### 5.2 Week 1 black-box → web / API / UI layers

| Manual case (fill in ID) | Automated | Result | Defect |
|---|---|---|---|
| TC-BB-?? Registration EP valid | AT-W-002, AT-A-001, AT-UI-001 | pass | |
| TC-BB-?? Registration EP/BVA invalid (`us`, short password) | AT-W-003/004, AT-A-002…004, AT-U-019…026 | pass | |
| TC-BB-?? Duplicate username | AT-A-006 ✗ | XFAIL | DEF-003 |
| TC-BB-?? Second account in same browser | AT-W-009 (9+ chars) / AT-W-010 ✗ (8 chars) | **pass** / XFAIL | DEF-004 → DEF-006 (§8) |
| TC-BB-?? Login decision table (4 rules) | AT-W-007, AT-A-007, AT-UI-002 | pass | |
| TC-BB-?? Logout / protected routes / Back button | AT-W-001, AT-W-008, AT-A-009, AT-UI-009 pass; AT-W-030 ✗, AT-UI-011 ✗ | pass / XFAIL | DEF-026 (new) |
| TC-BB-?? Create task EP | AT-W-011, AT-UI-004 | pass | |
| TC-BB-?? Due date 5-digit year | AT-W-016 ✗, AT-A-017 ✗ | XFAIL | DEF-001 |
| TC-BB-?? Urgency BVA | AT-U-001…009 (AT-U-005 ✗) | pass / XFAIL | DEF-002 |
| TC-BB-?? Edit task | AT-W-013 | pass | |
| TC-BB-?? Done/reopen state transition | AT-W-012, AT-A-022, AT-UI-005 | pass | |
| TC-BB-?? Delete task | AT-W-014, AT-UI-007 | pass | |
| TC-BB-?? Filter decision table (incl. zero-result) | AT-W-017, AT-A-029…031, AT-UI-006 | pass | |
| TC-BB-?? Dashboard counters | AT-W-019, AT-A-033, AT-UI-008 | pass | |

### 5.3 Week 3 GUI / usability / accessibility / compatibility

| Manual case | Automated | Result | Defect |
|---|---|---|---|
| TC-GUI-012 delete confirm (cancel keeps, OK deletes) | AT-UI-007 | pass | |
| TC-GUI-013 filters persist | AT-W-017, AT-UI-006 | pass | |
| TC-GUI-?? navigation, forms, buttons, messages | AT-UI-001…005, 008, 009; AT-W-002…004, 007, 011…013 | pass | |
| TC-GUI-?? data display: HTML in titles | AT-W-020 ✗ | XFAIL | DEF-011 |
| TC-GUI-?? data display: whitespace title | AT-W-021 ✗ | XFAIL | DEF-012 |
| TC-USA-001 username kept after error | AT-W-005 ✗ | XFAIL | DEF-013 |
| TC-USA-002 empty-state message | AT-W-022 ✗ | XFAIL | DEF-017 |
| TC-USA-003 rules shown before typing | AT-W-006 | pass | |
| TC-USA-004 invalid edit URL feedback | AT-W-023 ✗ | XFAIL | DEF-018 |
| TC-USA-005 distinct page titles | AT-W-024 | pass | |
| TC-ACC-?? labels associated | AT-W-025 ✗ (×3 pages) + axe AT-UI-010 ✗ (Login, Register, New Task) | XFAIL | DEF-010 |
| TC-ACC-?? filter controls named | AT-W-026 ✗ + axe AT-UI-010 ✗ (task list) | XFAIL | DEF-016 |
| TC-ACC-?? toggle button name | AT-W-027 ✗ | XFAIL | DEF-014 |
| TC-ACC-?? table headers | AT-W-028 ✗ | XFAIL | DEF-019 |
| TC-ACC-?? axe scan, Dashboard | AT-UI-010 | pass (no violations, as in Week 3) | |
| TC-CMP-001 Chrome desktop | AT-UI-001, 004 (1280×800) | pass | |
| TC-CMP-005 mobile viewport | AT-W-029 ✗ | XFAIL | DEF-020 |

### 5.4 Week 4 API and Week 5 security

| Manual case(s) | Automated | Result | Defect |
|---|---|---|---|
| API-001 | AT-W-001 | pass | |
| API-002 categories public (*needs review*) | AT-A-010 | pass (documents current behaviour; flip if the team decides "private") | |
| API-003, API-004, API-021, SEC-001, SEC-002, SEC-003 | AT-A-008 (6 endpoints) | pass | |
| API-005, API-019, API-020 | AT-A-007 | pass | |
| API-006, 007, 008 | AT-A-012 | pass | |
| API-009, API-018, SEC-010 | AT-A-019 | pass | |
| API-010 | AT-A-021 | pass | |
| API-011, SEC-009 / API-014 | AT-A-013 / AT-A-014 | pass | |
| API-012 | AT-A-029 | pass | |
| API-013, SEC-008 | AT-A-016 ✗ | XFAIL | DEF-API-001 (= SEC-DEF-002) |
| API-015, API-016 | AT-A-032 | pass | |
| API-017, API-018 | AT-A-024 | pass | |
| SEC-004, SEC-005 | AT-A-020 (+ list isolation AT-A-028) | pass | |
| SEC-006 | AT-A-026 ✗ | XFAIL | SEC-DEF-001 |
| SEC-007 | AT-A-009 | pass | |
| SEC-011 | AT-A-011 | pass | |

### 5.5 New automated cases (no manual equivalent)

| Automated | Purpose | Result | Defect |
|---|---|---|---|
| AT-A-005 | numeric `username` in `/api/register` (data-type EP, cf. API-013) | XFAIL | **DEF-022** |
| AT-A-015 | whitespace title via API | pass (API rejects it; web does not → DEF-012) | |
| AT-A-017, AT-A-018 | Week 2's predicted API route to DEF-001 | XFAIL | DEF-001 (confirmed on API) |
| AT-A-023 | `PUT` with empty title | XFAIL | **DEF-024** |
| AT-A-025 | `DELETE` non-existent id | XFAIL | **DEF-025** |
| AT-A-027 | SQL injection in `GET /api/tasks?q=` (Week 2 risk note) | XFAIL | **DEF-023** |
| AT-W-015 | cross-user edit/toggle/delete through the **web** routes | pass | |
| AT-W-018 | apostrophe in web search | pass | |
| AT-W-030, AT-UI-011 | caching of authenticated pages; Back after logout | XFAIL | **DEF-026** |

**Defect coverage:** of the 24 defect IDs logged in Weeks 1–5, **21 now have an automated check**:
19 open-defect retests, the DEF-004 retest, and SEC-DEF-002, which is checked by the same test as its
duplicate DEF-API-001. The 3 without one stay manual: DEF-005 (not a defect per spec), DEF-015
(OS-dependent keyboard behaviour) and DEF-021 (needs the stylesheet).

## 6. Execution report

Environment: Linux, Python 3.13, Flask 3.0.3, pytest 9.1.1, Selenium 4.54, headless Chrome 153,
axe-core 4.14.1. Run 26 Nov 2026. All evidence is in `reports/`.

### 6.1 Results by suite

| Suite | Command | Executed | Passed | Failed | XFAIL (open defect) | Time |
|---|---|---|---|---|---|---|
| Full | `pytest` | 125 | 89 | 0 | 36 | 20.9 s |
| Regression | `pytest -m regression` | 97 | 62 | 0 | 35 | 15.7 s |
| Smoke | `pytest -m smoke` | 47 | 39 | 0 | 8 | 6.4 s |
| Open defects shown as failures | `pytest -m known_defect --runxfail` | 36 | 0 | 36 | – | 6.6 s |

### 6.2 Results by layer (full run)

| Layer | Executed | Passed | XFAIL | In regression | In smoke |
|---|---|---|---|---|---|
| Unit | 35 | 30 | 5 | 23 | 15 |
| API | 38 | 29 | 9 | 31 | 17 |
| Web | 37 | 20 | 17 | 32 | 11 |
| UI (Selenium + axe) | 15 | 10 | 5 | 11 | 4 |
| **Total** | **125** | **89** | **36** | **97** | **47** |

- **Conformance to specification:** 89 / 125 = **71.2 %**. The other 36 test cases are retests for 24
  open defects. This is lower than the manual pass rates (82 % black-box, 82 % security) because the
  automated suite deliberately includes a retest for every open defect, including the Week 3
  accessibility ones.
- **New regressions: 0.**
- **Stability:** 10 consecutive full runs with coverage on gave identical results
  (89 passed / 36 xfailed, 19.6–21.3 s; `reports/stability_10_runs.log`).

### 6.3 Code coverage (full suite, branch mode)

| Module | Statements | Missed | Branches | Partial | Week 2 (white-box only) | **Week 6** |
|---|---|---|---|---|---|---|
| `helpers.py` | 31 | 0 | 18 | 0 | 100 % | **100 %** |
| `app.py` | 299 | 2 | 64 | 3 | 45 % | **99 %** |

The only lines not run are the `if __name__ == "__main__"` start-up lines. The three partial branches
are the cached `get_db()` path and one `elif` in the `PUT` handler. The API routes that Week 2 left
uncovered on purpose (and listed as "uncovered code that carries risk") are now covered, and **all
three risks it named turned out to be real defects** (DEF-023, SEC-DEF-001, DEF-001 via the API).
As in Week 2, coverage is close to 100 % while 24 defects are open, so coverage shows what ran, not
whether it was right.

### 6.4 Test-oracle validation

A strict xfail only proves a test *fails*, not that it fails for the intended reason. Each open-defect
retest was therefore checked in both directions:
- **Real app** (`known_defects_as_failures.log`): all 36 retests fail, each with the expected-vs-actual
  difference that matches its finding, e.g. `'Overdue' == 'Due Today'`, `500 == 400`,
  `axe label critical ×2`.
- **Throw-away copy with every open defect fixed** (`tools/make_fixed_copy.py`,
  `oracle_validation_all_fixed.log`): **all 125 tests pass** with `--runxfail`.

So every retest checks the right behaviour, and every other test still passes on a corrected app.

### 6.5 Demonstration: a fix being detected

Only DEF-006 was fixed in a throw-away copy (`> 8` → `>= 8`), and the regression suite was run
(`demo_after_fixing_DEF-006.log`):

```
FAILED tests/test_unit_helpers.py::test_password_of_exactly_8_chars_is_valid_AT_U_014   [XPASS(strict)]
FAILED tests/test_web.py::test_register_with_8_char_password_AT_W_010                   [XPASS(strict)]
2 failed, 56 passed, 39 deselected, 28 xfailed
```

Exactly the two DEF-006 retests flagged the change, and nothing else changed. DEF-006 would move to
*Retest → Closed*, and its two markers would be removed.

### 6.6 Axe-core results compared with Week 3

| Page | Week 3 scan (axe 4.14.1) | Week 6 regression test (same engine) |
|---|---|---|
| Login | `label` critical, 2 elements | `label` critical, 2 ✓ |
| Task list | `select-name` critical, 2 | `select-name` critical, 2 ✓ |
| New Task | `label` 3 + `select-name` 1 | `label` 3 + `select-name` 1 ✓ |
| Dashboard | none | none ✓ |
| Register | not reported | `label` critical, 2 (**additional evidence for DEF-010**) |

### 6.7 Issues met during automation

| Issue | Cause | Resolution |
|---|---|---|
| AT-A-005 failed on first run | **Real defect:** `/api/register` crashes on a numeric username | Logged as DEF-022. Kept as a retest |
| Back after logout showed task titles | **Real defect:** no `Cache-Control: no-store` on authenticated pages | Logged as DEF-026. Header retest + browser retest |
| AT-UI-005 failed in about 1 of 10 runs | **Test flakiness:** the assertion read the page before the form-post reload finished | Explicit wait for the expected state (`tr.done`). 10/10 stable since |
| Selenium session would not start | ChromeDriver 147 vs Chrome 153 on the test machine | Driver path and version check configurable by environment variable. UI tests skip, not fail, without Chrome |
| Python errors raised inside pytest instead of HTTP 500 | Flask `TESTING` propagates exceptions | `PROPAGATE_EXCEPTIONS=False`, so tests see the status a real client gets |
| Patch order clash in the fixed-copy script | Two fixes edit the same function | Reordered. Script now fails loudly if a patch doesn't apply |

## 7. Regression suite

**Membership** (`-m regression`, 97 of 125: 62 behaviour checks + 35 open-defect retests). A test is
included if it meets at least one of these criteria:
1. **Critical path:** every smoke test (register, log in, create, view, complete, delete, protect data).
   Smoke ⊂ regression.
2. **Open-defect retest:** every `known_defect` test, so each fix is verified and cannot silently come
   back. The exception is DEF-009, which stays out until the username rule is confirmed.
3. **Rules that broke before:** urgency, password and 7-day boundaries, and due-date handling.
4. **Data protection:** authentication, ownership, isolation, injection, escaping and caching.
5. **State and calculations:** done/reopen transitions, partial update, dashboard counters.
6. **Code next to a planned fix:** e.g. AT-A-031 title search, because the DEF-023 fix rewrites that query.

**Deliberately excluded** (28; still in the full suite): checks repeated at a cheaper layer (username
BVA is also covered by AT-A-002 / AT-W-003; four Selenium journeys repeat web-layer checks), low-risk
or static behaviour (seeded categories, page titles, 405 on unsupported methods, status filter and
pagination), characterisation
tests (AT-U-010/011/035) and the spec-pending DEF-009 test.

**Run frequency** (to be linked with CI/CD in Week 9):

| Trigger | Suite | Time |
|---|---|---|
| Every commit / push | Smoke (`-m smoke`) | ~6 s |
| Every defect fix, before merge | Regression (`-m regression`) | ~16 s |
| Nightly / before release | Full suite + coverage + HTML + traceability | ~21 s |

## 8. Defect outcomes from automation (input to the Week 7 consolidated log)

| Defect | Title | Severity / Priority (from source week) | Week 6 automated retest | Recommended status |
|---|---|---|---|---|
| DEF-001 | Unvalidated due date → persistent HTTP 500 on list & dashboard | Critical / High | AT-W-016, **AT-A-017/018 confirm the API route** predicted in Week 2 | Open (scope widened to API) |
| DEF-002 | Due today shown as Overdue; no "Due Today" path | Major / High | AT-U-005 | Open |
| DEF-003 | Duplicate usernames; second account hides the first | Major / High | AT-A-006 | Open |
| DEF-004 | Second registration in same browser blocked | – | **AT-W-009 passes** with a 10-char password in the same session; AT-W-010 fails with 8 chars | **Close as duplicate of DEF-006** |
| DEF-005 | No password complexity | – | not automated | Reclassify as improvement (spec = length only) |
| DEF-006 | 8-char password rejected | Major / High | AT-U-014, AT-W-010 | Open |
| DEF-007 | Completed exactly 7 days ago not counted | Moderate / Medium | AT-U-030 | Open |
| DEF-008 | Completed same second not counted | Minor / Low | AT-U-034 | Open |
| DEF-009 | Non-ASCII username accepted | Minor / Low | AT-U-033 (outside regression) | Open, spec pending |
| DEF-010 | Labels not associated | Moderate / Medium | AT-W-025 ×3, axe ×3 (**incl. Register**) | Open |
| DEF-011 | Titles rendered as HTML (stored XSS) | Major / High | AT-W-020 | Open. Not covered by Week 5 security testing; add to STRIDE |
| DEF-012 | Whitespace title saved (web) | Moderate / Medium | AT-W-021; API rejects it (AT-A-015) | Open (web/API inconsistency) |
| DEF-013 | Register clears username | Minor / Low | AT-W-005 | Open |
| DEF-014 | Toggle button name is a symbol | Moderate / Medium | AT-W-027 | Open |
| DEF-015 | Filter selects reload on keyboard change | Minor / Low | manual only | Open |
| DEF-016 | Filter controls unnamed | Moderate / Medium | AT-W-026, axe | Open |
| DEF-017 | Misleading empty-state message | Minor / Low | AT-W-022 | Open |
| DEF-018 | Invalid edit URL, no feedback | Minor / Low | AT-W-023 | Open |
| DEF-019 | Empty table headers | Minor / Low | AT-W-028 | Open |
| DEF-020 | No viewport meta tag | Moderate / Medium | AT-W-029 | Open |
| DEF-021 | Reflow at 320 px (provisional) | Minor / Low | manual only | Re-check with stylesheet |
| DEF-API-001 | Numeric title → HTTP 500 | Moderate / Medium | AT-A-016 | Open. **Merge SEC-DEF-002 into it** |
| SEC-DEF-001 | Cross-user delete (BOLA) | "High" / High → use **Critical** on the brief's scale | AT-A-026 | Open |
| SEC-DEF-002 | Numeric title → HTTP 500 | "Medium" | same test as DEF-API-001 | **Close as duplicate** |
| **DEF-022** *(new)* | Numeric username in `/api/register` → HTTP 500 | Moderate / Low | AT-A-005 | Open |
| **DEF-023** *(new)* | SQL injection in `GET /api/tasks?q=`: returns other users' tasks | **Critical / High** | AT-A-027 | Open |
| **DEF-024** *(new)* | `PUT` accepts empty title (`POST` rejects it) | Moderate / Medium | AT-A-023 | Open |
| **DEF-025** *(new)* | `DELETE` non-existent task → 200 `ok` | Minor / Low | AT-A-025 | Open |
| **DEF-026** *(new)* | Authenticated pages cacheable: Back after logout shows task list | Moderate / Medium | AT-W-030 ×3, AT-UI-011 | Open. Conflicts with the Week 1 note that Back did not expose protected pages; please re-check manually |

Severity scales also need aligning in Week 7: the security log uses High/Medium, while the brief uses
Critical/Major/Moderate/Minor.

## 9. Automation reflection

**Benefits observed**
- **Repeatable in seconds:** 140 test cases executed in Weeks 1–5, across Windows, Codespaces and two
  shells, are replaced for regression purposes by 125 automated checks in about 21 s with identical
  results each time. Tests use their own databases, so there are no shared accounts or hard-coded task
  IDs (e.g. `8`) to set up.
- **Found what manual testing missed:** five new defects (DEF-022…026), including a Critical SQL
  injection that Week 2 flagged but Week 5 never tested. It also confirmed Week 2's prediction that
  DEF-001 is reachable through the API.
- **Settled open questions with evidence:** DEF-004 can be closed as a duplicate of DEF-006, and
  SEC-DEF-002 as a duplicate of DEF-API-001. API-002 is now recorded as current behaviour pending the
  team's decision.
- **Every open defect has an automatic retest,** and the suite proved it detects a fix (§6.5).
- **The Week 3 accessibility scan is now repeatable:** the same axe-core version reproduced the manual
  results exactly and checked one more page.
- **Traceability stays current:** the matrix is generated from the tests on every run, so it cannot
  drift from the code.

**Limitations**
- **Automation checks only what we asserted.** It cannot judge whether a message is helpful or a layout
  clear. Usability heuristics, visual consistency and screen-reader experience stay manual. Axe also
  catches only part of WCAG.
- **High coverage is not high quality:** 99–100 % coverage with 24 open defects.
- **The UI layer is the expensive part:** 12 % of tests but about 65 % of runtime. It also had the only
  flaky test and the only environment failure (driver version). This supports keeping it thin.
- **One environment:** Linux and Chrome only. Firefox, Edge, Safari and a real phone are still untested
  (TC-CMP-002…004), and Week 1 used Windows 11.
- **Strict xfail can hide a change in failure reason.** This was mitigated by the oracle validation
  (§6.4), which should be repeated whenever a known-defect test is edited.
- **Not yet automated:** performance regression (PERF baseline), CSRF (the app has no CSRF tokens),
  session hardening (hard-coded `SECRET_KEY`, `debug=True`), DEF-015, DEF-021, and audit logging
  (STRIDE "Repudiation", not tested).
- **Maintenance:** template changes will need selector or regex updates, mainly in `test_web.py` and
  `test_ui_selenium.py`.

**Next steps**
- **Week 7:** fill in `manual_ids.py`; add AT-IDs to the master test repository and RTM; apply §8 to the
  consolidated defect log (merge duplicates, add DEF-022…026, align severity scales).
- **Week 8:** use §6 figures for metrics (pass rates, defects by severity/module, coverage before vs after).
- **Week 9:** run smoke on every push and regression on every pull request in CI (e.g. GitHub Actions),
  publishing `regression_junit.xml`. Add a small Locust job for the PERF baseline.

## 10. Evidence index (`reports/`)

| File | Content |
|---|---|
| `traceability.csv` | Manual-to-automated matrix: auto ID, manual IDs covered, defect, smoke/regression, **actual result** |
| `full_run.log`, `full_run_report.html`, `full_run_junit.xml` | Full suite (verbose log with coverage table, HTML report, JUnit XML) |
| `coverage_html/index.html` | Line/branch coverage with annotated source |
| `regression_run.log`, `regression_report.html`, `regression_junit.xml` | Focused regression suite |
| `smoke_run.log` | Smoke suite |
| `known_defects_as_failures.log` | Every open-defect retest with expected vs actual |
| `oracle_validation_all_fixed.log` | Whole suite passing against an all-fixed copy (§6.4) |
| `demo_after_fixing_DEF-006.log` | Regression suite detecting a single fix (§6.5) |
| `stability_10_runs.log` | 10 consecutive full runs |
