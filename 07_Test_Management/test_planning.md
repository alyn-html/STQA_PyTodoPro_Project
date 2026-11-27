# Consolidated Software Test Plan & Strategy — PyTodo Pro

## 1. Objectives & Risk Analysis ("Why are we testing?")
- **Primary Objective:** Conduct an independent, evidence-based Software Quality Assurance (SQA) evaluation of **PyTodo Pro** across functional and non-functional quality dimensions without modifying application source code (`app.py`, `helpers.py`, or HTML templates)[cite: 5].
- **Key Quality Risks:**
  1. **Security & Data Integrity (Critical Risk):** Unparameterized SQL search queries exposing private user tasks, missing user-ownership predicates on task deletion (IDOR), duplicate user registrations overwriting existing records, and unescaped Jinja `|safe` title rendering enabling stored XSS[cite: 5].
  2. **Date-Boundary & Input Validation Defects (High Risk):** Off-by-one relational comparisons in due-date urgency classification (`Overdue` vs. `Due Today`) and 7-day completion counters, strict `> 8` password length checks rejecting valid 8-character passwords, and unhandled `ValueError` / `AttributeError` HTTP 500 crashes on 5-digit years or numeric JSON fields[cite: 5].
  3. **Accessibility, Mobile Viewport & Session Hardening (Moderate Risk):** Missing `<label for>` associations, missing `<meta name="viewport">` tags causing horizontal overflow, missing `static/style.css` assets, and missing `Cache-Control: no-store` headers on authenticated routes[cite: 5].

## 2. Testing Scope & Team Responsibilities ("What are we testing?")
- **In-Scope Across Project Phases:**
  - **Black-Box Web UI Testing (`01_Black_Box` — Member 1: Mohammad Haiqal Firdaus Bin Mad Husni):** Manual browser-based functional testing of `REQ-01` through `REQ-09` using Equivalence Partitioning (EP), Boundary Value Analysis (BVA), Decision-Table Testing, and State-Transition Testing[cite: 5].
  - **White-Box Structural Testing & Test Automation (`02_White_Box_Coverage` & `06_Automation_Regression` — Member 2: Wan Danihaziq bin Wan Adrie):** Control-flow analysis ($V(G)$), statement and branch coverage across six selected units (`TC-WB-001` to `TC-WB-043`), and a 133-test automated PyTest/Selenium suite (`test_unit_helpers.py`, `test_api.py`, `test_web.py`, `test_ui_selenium.py`) including a 100-test regression suite and 47-test smoke suite[cite: 5].
  - **GUI, Usability, Accessibility & Compatibility Testing (`03_Special_Testing` — Member 2: Wan Danihaziq bin Wan Adrie):** Checklist-based GUI testing (`TC-GUI-001` to `TC-GUI-013`), Nielsen's 10 heuristics evaluation (`TC-USA-001` to `TC-USA-006`), WCAG 2.1 Level A/AA review with `axe-core 4.14.1` (`TC-ACC-001` to `TC-ACC-014`), and browser/viewport compatibility testing (`TC-CMP-001` to `TC-CMP-005`)[cite: 5].
  - **Web & REST API Testing (`04_Web_API` — Member 3: Alya Nabihah bt Ahmad Kamarzaman):** Manual HTTP endpoint verification (`API-001` to `API-021`) across 9 REST routes (`/api/register`, `/api/login`, `/api/categories`, `/api/tasks`, `/api/tasks/<id>`, `/api/dashboard`)[cite: 5].
  - **Security & Performance Testing (`05_Security_Performance` — Member 3: Alya Nabihah bt Ahmad Kamarzaman):** STRIDE threat modeling, authentication, authorization, session, and input-validation security testing (`SEC-001` to `SEC-011`), alongside sequential and concurrent API benchmarking (`PERF-001` to `PERF-004`, 80 total requests)[cite: 5].
- **Out-of-Scope:**
  - Modifying or patching PyTodo Pro's application source code (`app.py`, `helpers.py`, templates, or static files)[cite: 5].
  - Third-party browser execution on unavailable browsers (Firefox, Edge, Safari) and unscheduled external participant walkthroughs[cite: 5].

## 3. Test Strategy & Tools ("How will we test?")
- **Manual Testing Techniques:** Equivalence Partitioning, 2-value and 3-value Boundary Value Analysis, Decision Tables, State Transition diagrams, control-flow basis path analysis, heuristic evaluation, WCAG 2.1 accessibility checklists, STRIDE threat modeling, and load/concurrency profiling[cite: 4, 5].
- **Automation Strategy:** Stratified PyTest automation pyramid combining fast unit tests (`helpers.py`), Flask test-client API and Web route tests (`app.py`), and headless Selenium WebDriver UI tests integrated with `axe-core 4.14.1`, marking confirmed open defects with `@pytest.mark.xfail(strict=True)`[cite: 5].
- **Tools Used:** Google Chrome 153 (DevTools viewport emulation), Python 3 / Flask local server (`http://127.0.0.1:5000/`), SQLite (`pytodo_pro.db`), GitHub Codespaces, IntelliJ IDEA / PowerShell, `curl`, PyTest, `pytest-cov`, Selenium, `axe-core 4.14.1`, and GitHub version control[cite: 4, 5].

## 4. Environment, Test Data & Schedule ("When and with what?")
- **Test Environments:** Local Windows 11 environment (Python 3.10.11 / Werkzeug 3.1.9, Google Chrome 153) and GitHub Codespaces Linux container[cite: 5].
- **Test Data Rules:** Clean SQLite database (`pytodo_pro.db`) initialized prior to execution; isolated user accounts (`ayamgoreng`, `security_user_a`, `security_user_b`, and automated ephemeral fixtures); deterministic date boundaries anchored to the test execution date[cite: 4, 5].
- **Schedule:** Progressive execution across Project Weeks 1–8 (`01_Black_Box` through `08_Final_QA_Report` and `09_Presentation`)[cite: 4, 7].

## 5. Entry & Exit Criteria ("How will we know we are done?")
- **Entry Criteria:**
  1. PyTodo Pro launches cleanly on `http://127.0.0.1:5000/` with a freshly initialized SQLite schema[cite: 5].
  2. Isolated virtual/cloud environments and standardized 12-field test-case and defect-report templates are ready[cite: 5, 7].
- **Exit Criteria:**
  1. All executable manual (`133/138`) and automated (`133/133`) test suites are completed, and non-runnable tests (`5` cases) due to missing assets (`static/style.css`) or unavailable browsers are formally documented[cite: 5].
  2. Bidirectional traceability is established in `rtm.csv` across `REQ-01` to `REQ-09` and non-functional quality areas[cite: 5].
  3. All discovered defects are deduplicated and logged in `consolidated_defect_log.csv` (`26` unique defects)[cite: 5].
