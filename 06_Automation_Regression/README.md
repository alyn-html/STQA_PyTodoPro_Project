# 06_Automation_Regression — how to run

Automated tests for PyTodo Pro (Project Week 6). The application code is **not** modified;
every test creates its own temporary SQLite database.

## Folder layout

```
06_Automation_Regression/
├── REPORT.md                Week 6 write-up (candidate justification, traceability, results, reflection)
├── README.md                this file
├── pytest.ini               markers: smoke, regression, unit, api, web, ui, known_defect, covers
├── requirements-test.txt
├── tests/
│   ├── conftest.py              fixtures + traceability-report plugin
│   ├── manual_ids.py            TC-BB / TC-GUI / TC-ACC ids to fill in (see below)
│   ├── test_unit_helpers.py     AT-U-*   helpers.py (TC-WB cases, urgency/password BVA)
│   ├── test_api.py              AT-A-*   REST API + security (API-xxx, SEC-xxx)
│   ├── test_web.py              AT-W-*   pages/forms, usability & HTML accessibility (TC-BB, TC-USA, TC-ACC)
│   ├── test_ui_selenium.py      AT-UI-*  headless Chrome journeys + axe-core scan (TC-GUI, TC-ACC)
│   └── vendor/axe.min.js        axe-core 4.14.1 (MPL-2.0), same version as the Week 3 scan
├── tools/make_fixed_copy.py  builds a throw-away "all defects fixed" copy for oracle validation
└── reports/                  execution evidence (logs, JUnit XML, HTML reports, coverage, traceability.csv)
```

The tests expect `app.py`, `helpers.py` and `templates/` in the **repository root**
(one level above this folder). Otherwise set `PYTODO_APP_DIR`:

```bash
export PYTODO_APP_DIR=/path/to/pytodo          # PowerShell: $env:PYTODO_APP_DIR="C:\path\to\pytodo"
```

## Setup

```bash
python -m venv venv
source venv/bin/activate                        # Windows: venv\Scripts\activate
pip install -r 06_Automation_Regression/requirements-test.txt
cd 06_Automation_Regression
```

Google Chrome is needed for the `ui` tests. Selenium Manager fetches the matching ChromeDriver
automatically. If it cannot (offline lab, version gap):

```bash
export CHROMEDRIVER_PATH=/path/to/chromedriver
export CHROMEDRIVER_DISABLE_BUILD_CHECK=1       # only if driver and Chrome major versions differ
```

If Chrome cannot start, UI tests are **skipped**, not failed. `SELENIUM_HEADED=1` shows the browser.

## Running the suites

| Purpose | Command | Tests | Time* |
|---|---|---|---|
| Smoke (every change) | `pytest -m smoke` | 47 | ~6 s |
| Focused regression (every fix / before merge) | `pytest -m regression` | 97 | ~16 s |
| Full suite + coverage + traceability | `pytest --cov=app --cov=helpers --cov-branch --traceability=reports/traceability.csv` | 125 | ~21 s |
| One layer | `pytest -m unit` / `-m api` / `-m web` / `-m ui` | 35 / 38 / 37 / 15 | |
| Show open defects as real failures | `pytest -m known_defect --runxfail` | 36 | ~7 s |
| HTML + JUnit evidence | add `--html=reports/x.html --self-contained-html --junitxml=reports/x.xml` | | |

\* headless Chrome on Linux; your machine will differ.

## Reading the results

| Outcome | Meaning | Action |
|---|---|---|
| `PASSED` | behaviour matches the specification | – |
| `XFAIL` | a **logged, still-open defect** (ID in the reason) | none; the suite stays green |
| `XPASS(strict)` → **FAILED** | a known defect now behaves correctly | retest manually, close the defect, delete its `known_defect(...)` line |
| `FAILED` (anything else) | **new regression** | investigate and log a defect |

## Filling in the manual test IDs

`tests/manual_ids.py` holds placeholders such as `"TC-BB-?? Login decision table"` for the black-box
and some Week 3 cases, because the findings reports did not say which ID tests which behaviour.
Replace each value with the real ID, then re-run with `--traceability=reports/traceability.csv`.
The traceability matrix updates itself.

## Oracle validation (optional)

```bash
python tools/make_fixed_copy.py .. /tmp/pytodo_fixed          # all open defects fixed in a COPY
PYTODO_APP_DIR=/tmp/pytodo_fixed pytest --runxfail            # expected: everything passes
```
