# Project Week 6 — Test Automation and Regression

**Application under test:** PyTodo Pro (Flask 3.0.3, SQLite)
**Course:** TEB3433 / TFB3433 Software Testing and Quality Assurance
**Artefact location:** `/06_Automation_Regression` (how to run: `README.md`)

> **Traceability sources:** TC-BB, TC-WB, API and SEC IDs come from the group's test-case sheets
> (copied into `tools/manual_cases/`). TC-USA, TC-GUI-012/013, TC-CMP and PERF IDs come from the Week 3
> and Week 5 findings reports. The Week 3 sheet was not available, so the remaining TC-GUI / TC-ACC
> references are still `TC-GUI-??` / `TC-ACC-??` with a description. Fill them in once in
> `tests/manual_ids.py` and re-run; both traceability files regenerate.

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
| 1 | Black-box (EP, BVA, decision table, state transition) | 21 in the sheet (TC-BB-001…021)¹ | 17 pass / 4 fail | DEF-001…005 | Manual, Chrome, Windows 11 |
| 2 | White-box (statement, branch, boundary, data flow) | 43 (TC-WB-001…043) | 35 pass / 8 fail | DEF-006…009 | **Already in PyTest** (`test_whitebox.py`) |
| 3 | GUI / usability / accessibility / compatibility | 38 planned, 33 run | 18 pass / 15 fail / 5 not run | DEF-010…021 | Playwright evidence script + axe-core |
| 4 | API | 21 (API-001…021) | 19 pass / 1 fail / 1 needs review | DEF-API-001 | Manual `curl`, Codespaces |
| 5 | Security | 11 (SEC-001…011) | 9 pass / 2 fail | SEC-DEF-001, 002 | Manual `curl` + PowerShell, 2 environments |
| 5 | Performance | 4 (PERF-001…004) | 4 pass | – | PowerShell timing, 20 requests each |

¹ The black-box findings report says 28 cases were executed (23 pass / 5 fail), but the sheet holds 21
(17 pass / 4 fail; DEF-005 is linked to a passing case). **Reconcile before Week 7** (the RTM and metrics must match the sheet).

**What the review showed:**
- **The same areas keep failing across weeks:** date handling (DEF-001/002), registration (DEF-003/004/006),
  input validation (DEF-012, DEF-API-001) and output encoding (DEF-011). These need re-checking after
  every fix, so they are the strongest regression candidates.
- **Weeks 4–5 were run by hand in two environments** (Codespaces and Windows) with shared, hand-made
  accounts and fixed task IDs (`5`, `6`, `7`, `8`). They are slow to repeat and hard to reproduce exactly.
- **Week 2 was already in PyTest.** All 43 TC-WB cases are re-expressed one-to-one, using the same data
  and the same fixed clock (`today = 2026-11-24`).
- **Some areas were flagged but never tested:** Week 2 flagged the f-string SQL in `api_list_tasks()`
  as a Week 5 target, but Week 5 did not test it. Week 2 also predicted the API route to DEF-001 ("to be
  confirmed in Week 4"), which Week 4 did not test either. Both are automated now (§8).
- **Defect records need consolidating:** SEC-DEF-002 and DEF-API-001 are the same defect. TC-BB-001 links
  DEF-005, which Week 2 reclassified as an improvement. DEF-004 was already marked *Retest* by Week 2.

## 3. Automation candidate justification

Each manual test group was scored 1 (low) – 3 (high) on the brief's four criteria. **Feasibility**
(can a tool decide pass/fail without human judgement?) was used as a gate.

| Manual test group | Repetition | Stability | Criticality | Regression value | Objective oracle? | Decision |
|---|---|---|---|---|---|---|
| Urgency BVA (TC-BB-006…011, TC-WB-001…009) | 3 | 3 | 3 | 3 | Yes, exact label | **Automate: unit** |
| Password / username rules (TC-WB-010…024, TC-BB-001/003) | 3 | 3 | 3 | 3 | Yes | **Automate: unit + web** |
| 7-day completion window (TC-WB-025…035) | 2 | 3 | 2 | 3 | Yes, injectable clock | **Automate: unit** |
| App glue code (TC-WB-036…040) | 1 | 3 | 1 | 2 | Yes | **Automate: unit** (full suite only) |
| Registration, login decision table, logout (TC-BB-001…003, 012…015, 021; API-005/019/020; SEC-007) | 3 | 3 | 3 | 3 | Yes, status/redirect | **Automate: API + web + UI** |
| Create / complete / reopen / delete (TC-BB-004, 018…020; API-006…018) | 3 | 3 | 3 | 3 | Yes | **Automate: API + web** |
| Bad due date (TC-BB-005, TC-WB-043) | 2 | 3 | 3 | 3 | Yes, HTTP 200 vs 500 | **Automate: web + API** |
| Filters, search, pagination (TC-BB-016/017, TC-GUI-013, API-012/015/016) | 2 | 3 | 2 | 2 | Yes | **Automate: API + web** |
| Authentication & cross-user access (SEC-001…006, API-001/003/004/021) | 3 | 3 | 3 | 3 | Yes | **Automate: API + web** |
| Input validation & error handling (API-011/013/014, SEC-008…011) | 3 | 3 | 3 | 3 | Yes | **Automate: API** |
| Browser-only GUI behaviour (TC-GUI-012 confirm dialog, date input, auto-submit select, HTML5 `required`) | 2 | 2 | 2 | 2 | Yes | **Automate: thin Selenium layer** |
| Accessibility with objective rules (labels, names, headers, viewport; axe scan) | 2 | 3 | 2 | 3 | Yes, DOM rules | **Automate: web HTML checks + axe in Selenium** (the Week 3 recommendation) |
| Usability items with a fixed oracle (TC-USA-001…005) | 1 | 3 | 1 | 2 | Yes, text present/absent | **Automate: web** |
| Usability needing judgement, visual consistency, TC-USA-006 | 1 | 1 | 2 | 1 | No | Keep manual |
| Keyboard behaviour of filter selects (DEF-015) | 1 | 1 | 1 | 1 | OS-dependent (macOS opens the list, Windows/Linux change value) | Keep manual |
| Reflow at 320 px / colour contrast (DEF-021, not-run items) | 1 | 1 | 1 | 1 | Depends on missing `style.css` | Keep manual until stylesheet available |
| Firefox / Edge / Safari (TC-CMP-002…004) | 1 | 2 | 2 | 1 | Yes, but browsers unavailable | Not automated. The Selenium suite can run in other browsers once installed |
| Performance (PERF-001…004) | 1 | 1 | 2 | 1 | Needs controlled load environment | Keep separate (load tool), not functional regression |
| STRIDE analysis, exploratory sessions | 1 | – | 3 | 1 | No | Keep manual |

**Layering (test pyramid).** Each rule is checked at the **lowest layer that can observe it**. Only
behaviour that needs a real browser goes through Selenium. As a result, 89 % of the tests run in about
7 seconds without a browser.

| Layer | File | Tests | Share | Runtime |
|---|---|---|---|---|
| Unit (`helpers.py` + app glue) | `test_unit_helpers.py` | 42 | 32 % | 0.3 s |
| API + security | `test_api.py` | 38 | 29 % | 3.4 s |
| Web pages, usability, HTML accessibility | `test_web.py` | 38 | 29 % | 3.6 s |
| UI end-to-end + axe scan (Selenium) | `test_ui_selenium.py` | 15 | 11 % | 13.9 s |
| **Total** | | **133** (83 test functions; parametrised cases count separately) | | **~21 s** |

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
| `tests/manual_ids.py` | – | TC-BB IDs (filled in from the sheet) and the remaining TC-GUI / TC-ACC placeholders |
| `tests/test_unit_helpers.py` | AT-U-001…042 | All 43 TC-WB cases except TC-WB-040–043, which run at web/API level, plus TC-BB-006…011. Same data and clock as the Week 2 sheet |
| `tests/test_api.py` | AT-A-001…033 | API-001…021, SEC-001…011, the white-box risk routes, and new negative cases |
| `tests/test_web.py` | AT-W-001…031 | TC-BB workflows (incl. the 4-rule login decision table with the sheet's data), TC-USA checks, HTML-level WCAG checks, caching headers |
| `tests/test_ui_selenium.py` | AT-UI-001…011 | Browser journeys (TC-GUI-012/013, TC-CMP-001), axe-core WCAG 2 A/AA scan of 5 pages, Back-after-logout |
| `tools/make_fixed_copy.py` | – | Builds a throw-away copy of the app with every open defect fixed, used to validate the tests (§6.4) |
| `tools/build_manual_matrix.py` + `tools/manual_cases/` | – | Builds `reports/manual_to_automated.csv` from the manual test-case sheets and the latest run |

Test data mirrors the manual sheets: `ayamgoreng` / `akusukaayam`, `us`, `unknown` / `wrongpassword`,
`haiqalfirdaus`, `security_user_a/b`, due date `19999-06-14`, title `submit stqa project`, search
`nonexistent999`, passwords `abc1234` / `abcd1234` / `abcd12345`, usernames `john_doe1` / `john-doe` /
`jöhn`, title `123`.

## 5. Manual-to-automated traceability

Two files, both regenerated on every run:

| File | One row per | Use |
|---|---|---|
| **`reports/manual_to_automated.csv`** | **manual test case** (113 rows) | Which automated tests re-execute each manual case, the automated result, whether it is in the regression suite, and whether it agrees with the manual result. Cases not automated have a reason |
| `reports/traceability.csv` | automated test case (133 rows) | Which manual cases each automated test covers, its defect, its suites, and its result |

### 5.1 Coverage of the manual test cases

| Source | Manual cases | Automated | In regression suite | Not automated (reason) |
|---|---|---|---|---|
| Week 1 black-box (TC-BB) | 21 | **21** | 21 | – |
| Week 2 white-box (TC-WB) | 43 | **43** | 26 | – |
| Week 3 GUI (TC-GUI-012/013) | 2 | **2** | 2 | Other TC-GUI IDs: sheet not provided |
| Week 3 usability (TC-USA) | 6 | **5** | 3 | TC-USA-006 (not run in Week 3, judgement-based) |
| Week 3 compatibility (TC-CMP) | 5 | **2** | 2 | TC-CMP-002…004 (Firefox, Edge, Safari unavailable) |
| Week 4 API | 21 | **21** | 18 | – |
| Week 5 security (SEC) | 11 | **11** | 10 | – |
| Week 5 performance (PERF) | 4 | 0 | – | Load testing needs a controlled environment and tool (Locust suggested for Week 9) |
| **Total** | **113** | **105 (93 %)** | **82** | **8** |

**Comparison with the manual results.** For 104 of the 105 automated cases, the automated result
agrees with the manual one: same pass/fail, same defect.
- **TC-BB-021** (Back after logout) passed manually and still passes on what it checked: actions after
  Back are blocked. Automation also showed that Back **displays the cached task list** (DEF-026, new).
- **TC-BB-003** failed manually under DEF-004. Automation shows the failure only happens with an
  8-character password (DEF-006). With 10 characters a second account in the same browser works, so
  DEF-004 is a duplicate of DEF-006.
- **SEC-008** (SEC-DEF-002) and **API-013** (DEF-API-001) are re-executed by the same test with the same
  failure, which confirms they are one defect.

### 5.2 Week 1 black-box → automated tests

| Manual case | Technique | Automated | Result | Defect |
|---|---|---|---|---|
| TC-BB-001 valid registration | EP | AT-W-002, AT-A-001, AT-UI-001, AT-U-016 | Pass | (DEF-005 → improvement) |
| TC-BB-002 duplicate username | EP invalid | AT-W-031 ✗, AT-A-006 ✗ | Fail | DEF-003 |
| TC-BB-003 short inputs + second account | EP/BVA | AT-W-003/004, AT-A-002…004 pass; AT-W-009 pass (10-char pwd); AT-W-010 ✗ (8-char) | Partly failing | DEF-006 (DEF-004 duplicate) |
| TC-BB-004 create task | EP | AT-W-011, AT-UI-004 | Pass | |
| TC-BB-005 5-digit year | EP invalid | AT-W-016 ✗, AT-A-017 ✗ | Fail | DEF-001 |
| TC-BB-006 T-1, T-2 | BVA | AT-U-003, AT-U-004 | Pass | |
| TC-BB-007 T (today) | BVA | AT-U-005 ✗ | Fail | DEF-002 |
| TC-BB-008 / 009 / 010 T+1 / T+2 / T+3 | BVA | AT-U-006 / 007 / 008 | Pass | |
| TC-BB-011 blank due date | BVA/EP | AT-U-001 | Pass | |
| TC-BB-012…015 login rules 1–4 | Decision table | AT-W-007 (all 4 rules, sheet data); AT-UI-002 (rule 4) | Pass | |
| TC-BB-016 Urgent + Open + "stqa" | Decision table | AT-W-017 | Pass | |
| TC-BB-017 "nonexistent999" | Decision table | AT-W-017 | Pass | |
| TC-BB-018 Open → Done + dashboard | State transition | AT-W-012 (Open −1, Completed +1), AT-A-033, AT-UI-005, AT-W-019 | Pass | |
| TC-BB-019 Done → Open | State transition | AT-W-012, AT-A-022 | Pass | |
| TC-BB-020 delete + deleted edit URL | State transition | AT-W-014, AT-UI-007 | Pass | |
| TC-BB-021 logout + Back | State transition | AT-W-001, AT-W-008, AT-UI-009 pass; AT-W-030 ✗, AT-UI-011 ✗ | Partly failing | DEF-026 (new) |

### 5.3 Week 2 white-box → unit / web / API tests

| Manual cases | Automated | Result | Defect |
|---|---|---|---|
| TC-WB-001, 002, 003, 005, 006, 007 | AT-U-001, 002, 004, 006, 007, 008 | Pass | |
| TC-WB-004 | AT-U-005 ✗ | Fail | DEF-002 |
| TC-WB-008, 009 | AT-U-011, AT-U-010 | Pass | (009 = root cause of DEF-001) |
| TC-WB-010, 011, 012, 014, 015 | AT-U-017, 018, 013, 015, 012 | Pass | |
| TC-WB-013 | AT-U-014 ✗ (+ AT-W-010 ✗ at web level) | Fail | DEF-006 |
| TC-WB-016…023 | AT-U-026, 019, 020, 021, 022, 023, 025, 024 | Pass | |
| TC-WB-024 | AT-U-033 ✗ (outside regression: spec pending) | Fail | DEF-009 |
| TC-WB-025, 026, 027, 028, 030, 031, 032 | AT-U-027, 036, 028, 029, 031, 037, 032 | Pass | |
| TC-WB-029 / TC-WB-033 | AT-U-030 ✗ / AT-U-034 ✗ | Fail | DEF-007 / DEF-008 |
| TC-WB-034, 035 | AT-U-035, AT-U-038 | Pass | |
| TC-WB-036, 037, 038, 039 | AT-U-039, 040, 041, 042 | Pass | |
| TC-WB-040 | AT-W-001 (`/dashboard`) | Pass | |
| TC-WB-041 / TC-WB-042 | AT-W-031 ✗, AT-A-006 ✗ / AT-A-006 ✗ | Fail | DEF-003 |
| TC-WB-043 | AT-W-016 ✗ (+ API route AT-A-017/018 ✗) | Fail | DEF-001 |

### 5.4 Week 3 GUI / usability / accessibility / compatibility

| Manual case | Automated | Result | Defect |
|---|---|---|---|
| TC-GUI-012 delete confirm (cancel keeps, OK deletes) | AT-UI-007 | Pass | |
| TC-GUI-013 filters persist | AT-W-017, AT-UI-006 | Pass | |
| TC-GUI-?? navigation, forms, buttons, messages | AT-UI-001…005, 008, 009; AT-W-002…004, 007, 011…013 | Pass | |
| TC-GUI-?? data display: HTML in titles | AT-W-020 ✗ | Fail | DEF-011 |
| TC-GUI-?? data display: whitespace title | AT-W-021 ✗ | Fail | DEF-012 |
| TC-USA-001 / 002 / 004 | AT-W-005 ✗ / AT-W-022 ✗ / AT-W-023 ✗ | Fail | DEF-013 / DEF-017 / DEF-018 |
| TC-USA-003 / 005 | AT-W-006 / AT-W-024 | Pass | |
| TC-ACC-?? labels associated | AT-W-025 ✗ (×3 pages) + axe AT-UI-010 ✗ (Login, Register, New Task) | Fail | DEF-010 |
| TC-ACC-?? filter controls named | AT-W-026 ✗ + axe AT-UI-010 ✗ (task list) | Fail | DEF-016 |
| TC-ACC-?? toggle button name / table headers | AT-W-027 ✗ / AT-W-028 ✗ | Fail | DEF-014 / DEF-019 |
| TC-ACC-?? axe scan, Dashboard | AT-UI-010 | Pass (no violations, as in Week 3) | |
| TC-CMP-001 Chrome desktop | AT-UI-001, 004 (1280×800) | Pass | |
| TC-CMP-005 mobile viewport | AT-W-029 ✗ | Fail | DEF-020 |

### 5.5 Week 4 API and Week 5 security

| Manual case(s) | Automated | Result | Defect |
|---|---|---|---|
| API-001 | AT-W-001 (`/`) | Pass | |
| API-002 categories public (*Needs Review*) | AT-A-010 | Pass (records current behaviour; flip if the team decides "private") | |
| API-003, API-004, API-021, SEC-001, SEC-002, SEC-003 | AT-A-008 (6 endpoints) | Pass | |
| API-005, API-019, API-020 | AT-A-007 | Pass | |
| API-006, 007, 008 | AT-A-012 | Pass | |
| API-009, SEC-010 | AT-A-019 | Pass | |
| API-010 | AT-A-021 | Pass | |
| API-011 + SEC-009 / API-014 | AT-A-013 / AT-A-014 | Pass | |
| API-012 | AT-A-029 | Pass | |
| API-013, SEC-008 | AT-A-016 ✗ | Fail | DEF-API-001 (= SEC-DEF-002) |
| API-015, API-016 | AT-A-032 | Pass | |
| API-017, API-018 | AT-A-024 | Pass | |
| SEC-004, SEC-005 | AT-A-020 (+ list isolation AT-A-028) | Pass | |
| SEC-006 | AT-A-026 ✗ | Fail | SEC-DEF-001 |
| SEC-007 | AT-A-009 | Pass | |
| SEC-011 | AT-A-011 | Pass | |

### 5.6 New automated cases (no manual equivalent)

| Automated | Purpose | Result | Defect |
|---|---|---|---|
| AT-A-005 | numeric `username` in `/api/register` (data-type EP, cf. API-013) | Fail | **DEF-022** |
| AT-A-015 | whitespace title via API | Pass (API rejects it; web does not → DEF-012) | |
| AT-A-017, AT-A-018 | Week 2's predicted API route to DEF-001 | Fail | DEF-001 (confirmed on API) |
| AT-A-023 | `PUT` with empty title | Fail | **DEF-024** |
| AT-A-025 | `DELETE` non-existent id | Fail | **DEF-025** |
| AT-A-027 | SQL injection in `GET /api/tasks?q=` (Week 2 risk note) | Fail | **DEF-023** |
| AT-A-030, AT-A-031 | API status filter, API title search | Pass | |
| AT-U-009 | far-future due date (EP) | Pass | |
| AT-W-013 | edit task (no Week 1 case; Week 3 edit pre-fill) | Pass | |
| AT-W-015 | cross-user edit/toggle/delete through the **web** routes | Pass | |
| AT-W-018 | apostrophe in web search | Pass | |
| AT-W-030, AT-UI-011 | caching of authenticated pages; Back after logout | Fail | **DEF-026** |

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
| Full | `pytest` | 133 | 96 | 0 | 37 | 21.3 s |
| Regression | `pytest -m regression` | 100 | 64 | 0 | 36 | 17.7 s |
| Smoke | `pytest -m smoke` | 47 | 39 | 0 | 8 | 7.8 s |
| Open defects shown as failures | `pytest -m known_defect --runxfail` | 37 | 0 | 37 | – | 7.0 s |

### 6.2 Results by layer (full run)

| Layer | Executed | Passed | XFAIL | In regression | In smoke |
|---|---|---|---|---|---|
| Unit | 42 | 37 | 5 | 25 | 15 |
| API | 38 | 29 | 9 | 31 | 17 |
| Web | 38 | 20 | 18 | 33 | 11 |
| UI (Selenium + axe) | 15 | 10 | 5 | 11 | 4 |
| **Total** | **133** | **96** | **37** | **100** | **47** |

- **Conformance to specification:** 96 / 133 = **72.2 %**. The other 37 test cases are retests for 24
  open defects. This is lower than the manual pass rates (81 % black-box sheet, 81 % white-box, 82 %
  security) because the automated suite deliberately includes a retest for every open defect, including
  the Week 3 accessibility ones.
- **New regressions: 0.**
- **Stability:** 10 consecutive full runs with coverage on gave identical results
  (96 passed / 37 xfailed, 19.3–21.8 s; `reports/stability_10_runs.log`).

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
- **Real app** (`known_defects_as_failures.log`): all 37 retests fail, each with the expected-vs-actual
  difference that matches its finding, e.g. `'Overdue' == 'Due Today'`, `500 == 400`,
  `axe label critical ×2`.
- **Throw-away copy with every open defect fixed** (`tools/make_fixed_copy.py`,
  `oracle_validation_all_fixed.log`): **all 133 tests pass** with `--runxfail`.

So every retest checks the right behaviour, and every other test still passes on a corrected app.

### 6.5 Demonstration: a fix being detected

Only DEF-006 was fixed in a throw-away copy (`> 8` → `>= 8`), and the non-UI regression suite was run
(`demo_after_fixing_DEF-006.log`):

```
FAILED tests/test_unit_helpers.py::test_password_of_exactly_8_chars_is_valid_AT_U_014   [XPASS(strict)]
FAILED tests/test_web.py::test_register_with_8_char_password_AT_W_010                   [XPASS(strict)]
2 failed, 58 passed, 44 deselected, 29 xfailed
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
| AT-UI-005 failed in about 1 of 10 runs | **Test flakiness:** the assertion read the page before the form-post reload finished | Explicit wait for the expected state (`tr.done`). Stable since |
| Selenium session would not start | ChromeDriver 147 vs Chrome 153 on the test machine | Driver path and version check configurable by environment variable. UI tests skip, not fail, without Chrome |
| Python errors raised inside pytest instead of HTTP 500 | Flask `TESTING` propagates exceptions | `PROPAGATE_EXCEPTIONS=False`, so tests see the status a real client gets |
| Patch order clash in the fixed-copy script | Two fixes edit the same function | Reordered. Script now fails loudly if a patch doesn't apply |

## 7. Regression suite

**Membership** (`-m regression`, 100 of 133: 64 behaviour checks + 36 open-defect retests). It re-executes
82 of the 105 automated manual cases (§5.1). A test is included if it meets at least one of these criteria:
1. **Critical path:** every smoke test (register, log in, create, view, complete, delete, protect data).
   Smoke ⊂ regression.
2. **Open-defect retest:** every `known_defect` test, so each fix is verified and cannot silently come
   back. The exception is DEF-009, which stays out until the username rule is confirmed.
3. **Rules that broke before:** urgency, password and 7-day boundaries, and due-date handling.
4. **Data protection:** authentication, ownership, isolation, injection, escaping and caching.
5. **State and calculations:** done/reopen transitions, partial update, dashboard counters.
6. **Code next to a planned fix:** e.g. AT-A-031 title search, because the DEF-023 fix rewrites that query.

**Deliberately excluded** (33; still in the full suite): checks repeated at a cheaper layer (username
rules TC-WB-016…023 are also covered by AT-A-002 / AT-W-003; four Selenium journeys repeat web-layer
checks), low-risk internal or static behaviour (TC-WB-036…039 glue code, seeded categories, page titles,
405 on unsupported methods, status filter, pagination), characterisation and default-clock tests
(TC-WB-008, 009, 034, 035) and the spec-pending DEF-009 test.

**Run frequency** (to be linked with CI/CD in Week 9):

| Trigger | Suite | Time |
|---|---|---|
| Every commit / push | Smoke (`-m smoke`) | ~8 s |
| Every defect fix, before merge | Regression (`-m regression`) | ~18 s |
| Nightly / before release | Full suite + coverage + HTML + both traceability files | ~21 s |

## 8. Defect outcomes from automation (input to the Week 7 consolidated log)

| Defect | Title | Severity / Priority (from source week) | Week 6 automated retest | Recommended status |
|---|---|---|---|---|
| DEF-001 | Unvalidated due date → persistent HTTP 500 on list & dashboard | Critical / High | AT-W-016, **AT-A-017/018 confirm the API route** predicted in Week 2 | Open (scope widened to API) |
| DEF-002 | Due today shown as Overdue; no "Due Today" path | Major / High | AT-U-005 | Open |
| DEF-003 | Duplicate usernames; second account hides the first | Major / High | AT-W-031 (web), AT-A-006 (API) | Open |
| DEF-004 | Second registration in same browser blocked | – | **AT-W-009 passes** with a 10-char password in the same session; AT-W-010 fails with 8 chars | **Close as duplicate of DEF-006** |
| DEF-005 | No password complexity | – | not automated | Reclassify as improvement (spec = length only); remove from TC-BB-001 |
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
| **DEF-026** *(new)* | Authenticated pages cacheable: Back after logout shows task list | Moderate / Medium | AT-W-030 ×3, AT-UI-011 | Open. TC-BB-021 tested refresh/edit after Back (still blocked) but not what Back displays |

Severity scales also need aligning in Week 7: the security log uses High/Medium, while the brief uses
Critical/Major/Moderate/Minor.

## 9. Automation reflection

**Benefits observed**
- **Repeatable in seconds:** the 105 automatable manual cases from five weeks, run across Windows,
  Codespaces and two shells, are re-executed in about 21 s with identical results each time. Tests use
  their own databases, so there are no shared accounts or hard-coded task IDs (`5`, `8`) to set up.
- **Found what manual testing missed:** five new defects (DEF-022…026), including a Critical SQL
  injection that Week 2 flagged but Week 5 never tested. It also confirmed Week 2's prediction that
  DEF-001 is reachable through the API.
- **Settled open questions with evidence:** DEF-004 can be closed as a duplicate of DEF-006, and
  SEC-DEF-002 as a duplicate of DEF-API-001. API-002 is now recorded as current behaviour pending the
  team's decision.
- **Every open defect has an automatic retest,** and the suite proved it detects a fix (§6.5).
- **The Week 3 accessibility scan is now repeatable:** the same axe-core version reproduced the manual
  results exactly and checked one more page.
- **Traceability stays current:** both matrices are generated from the tests and sheets on every run,
  so they cannot drift from the code.

**Limitations**
- **Automation checks only what we asserted.** It cannot judge whether a message is helpful or a layout
  clear. Usability heuristics, visual consistency and screen-reader experience stay manual. Axe also
  catches only part of WCAG.
- **High coverage is not high quality:** 99–100 % coverage with 24 open defects.
- **The UI layer is the expensive part:** 11 % of tests but about 65 % of runtime. It also had the only
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
- **Week 7:**
  - reconcile the black-box count (21 vs 28);
  - fill in the remaining TC-GUI / TC-ACC IDs in `manual_ids.py`;
  - use `manual_to_automated.csv` for the RTM's automation column;
  - apply §8 to the consolidated defect log (merge duplicates, add DEF-022…026, align severity scales).
- **Week 8:** use §5.1 and §6 figures for metrics (automation coverage, pass rates, defects by
  severity/module, coverage before vs after).
- **Week 9:** run smoke on every push and regression on every pull request in CI (e.g. GitHub Actions),
  publishing `regression_junit.xml`. Add a small Locust job for the PERF baseline.

## 10. Evidence index (`reports/`)

| File | Content |
|---|---|
| `manual_to_automated.csv` | **One row per manual test case** (113): automated tests, result, regression membership, agreement with manual result, reason if not automated |
| `traceability.csv` | One row per automated test case (133): manual cases covered, defect, smoke/regression, actual result |
| `full_run.log`, `full_run_report.html`, `full_run_junit.xml` | Full suite (verbose log with coverage table, HTML report, JUnit XML) |
| `coverage_html/index.html` | Line/branch coverage with annotated source |
| `regression_run.log`, `regression_report.html`, `regression_junit.xml` | Focused regression suite |
| `smoke_run.log` | Smoke suite |
| `known_defects_as_failures.log` | Every open-defect retest with expected vs actual |
| `oracle_validation_all_fixed.log` | Whole suite passing against an all-fixed copy (§6.4) |
| `demo_after_fixing_DEF-006.log` | Regression suite detecting a single fix (§6.5) |
| `stability_10_runs.log` | 10 consecutive full runs |
| `manual_to_automated_summary.txt` | Automated / total per manual source |
