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
├── tools/
│   ├── make_fixed_copy.py       builds a throw-away "all defects fixed" copy for oracle validation
│   ├── build_manual_matrix.py   builds reports/manual_to_automated.csv (one row per manual case)
│   └── manual_cases/            copies of the Week 1/2/4/5 test-case sheets + Week 3/5 IDs from findings
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
| Smoke (every change) | `pytest -m smoke` | 47 | ~8 s |
| Focused regression (every fix / before merge) | `pytest -m regression` | 100 | ~18 s |
| Full suite + coverage + traceability | `pytest --cov=app --cov=helpers --cov-branch --traceability=reports/traceability.csv` | 133 | ~21 s |
| One layer | `pytest -m unit` / `-m api` / `-m web` / `-m ui` | 42 / 38 / 38 / 15 | |
| Show open defects as real failures | `pytest -m known_defect --runxfail` | 37 | ~7 s |
| HTML + JUnit evidence | add `--html=reports/x.html --self-contained-html --junitxml=reports/x.xml` | | |

\* headless Chrome on Linux; your machine will differ.

## Reading the results

| Outcome | Meaning | Action |
|---|---|---|
| `PASSED` | behaviour matches the specification | – |
| `XFAIL` | a **logged, still-open defect** (ID in the reason) | none; the suite stays green |
| `XPASS(strict)` → **FAILED** | a known defect now behaves correctly | retest manually, close the defect, delete its `known_defect(...)` line |
| `FAILED` (anything else) | **new regression** | investigate and log a defect |

## Traceability files

```bash
pytest --traceability=reports/traceability.csv     # one row per automated test case
python tools/build_manual_matrix.py                 # one row per manual test case -> reports/manual_to_automated.csv
```

`build_manual_matrix.py` reads the sheets in `tools/manual_cases/` by default. Pass paths to use the
originals instead, e.g. `python tools/build_manual_matrix.py ../01_Black_Box/black_box_test_cases.csv ...`.

TC-BB, TC-WB, API and SEC IDs are final. The Week 3 sheet was not available, so `tests/manual_ids.py`
still has `TC-GUI-??` / `TC-ACC-??` placeholders. Replace them with the real IDs and re-run both
commands.

## Oracle validation (optional)

```bash
python tools/make_fixed_copy.py .. /tmp/pytodo_fixed          # all open defects fixed in a COPY
PYTODO_APP_DIR=/tmp/pytodo_fixed pytest --runxfail            # expected: everything passes
```
