# 03 — GUI, Compatibility, Usability & Accessibility Testing (Project Week 3)

## Role & Scope
- **Owner:** Member 3 — GUI, Usability, Accessibility & Compatibility Testing
- **Target System:** PyTodo Pro Web UI (`http://127.0.0.1:5000/`)
- **Testing Approach:** Checklist-based GUI testing of forms, buttons, links, labels, navigation, messages and data display. Usability evaluation against Nielsen's heuristics. A basic WCAG 2 (A/AA) accessibility review combining manual checks with an automated axe-core scan. Compatibility testing across the browser and viewport configurations available to the group. Browser steps were scripted with Playwright so that every screenshot is reproducible.
- **Out of Scope:** Functional black-box testing (`01_Black_Box`), white-box unit/coverage testing (`02_White_Box_Coverage`), REST `/api/` endpoints (`04_Web_API`), security/STRIDE & performance testing (`05_Security_Performance`), and the automated regression suite (`06_Automation_Regression`).

## Folder Contents
- `README.md` — Summary of scope, technique justifications, how to reproduce the evidence, and execution overview.
- `special_testing_findings.md` — GUI checklist results, compatibility matrix, usability observations, accessibility findings, defects with recommendations, and limitations.
- `Week3_GUI_Usability_Accessibility_TestCases.xlsx` — Complete 38-case suite (`TC-GUI`, `TC-USA`, `TC-ACC`, `TC-CMP`) with expected/actual results, status, evidence file and defect IDs. It also has these sheets:
  - `Summary`: execution metrics
  - `Compatibility Matrix`
  - `Defects`: defect log
- `week3_evidence.py` — Playwright script that drives Chrome through every scenario, takes the screenshots and runs the axe-core scan.
- `evidence_log.json` — Raw values recorded during the run, such as dialog messages, row counts, tab order, accessible names, reflow widths and axe results.
- `screenshots/` — Visual execution evidence. Each image has a header strip with the test-case ID, URL, browser, viewport and timestamp:
  - `01_login_page.png`
  - `02_register_username_error.png`
  - `03_register_8char_password_rejected.png`
  - `04_empty_task_list.png`
  - `05_new_task_form.png`
  - `06_task_list_defects.png`
  - `07_dashboard_overdue_count.png`
  - `08_edit_task_form.png`
  - `09_task_toggled_done.png`
  - `10_filters_persist.png`
  - `11_after_delete_confirmed.png`
  - `12_invalid_edit_url_no_message.png`
  - `13_keyboard_focus_visible.png`
  - `14_label_not_associated.png`
  - `15_login_error.png`
  - `16_reflow_200pct.png`
  - `16_reflow_320px.png`
  - `17_mobile_task_list.png`
  - `18_mobile_dashboard.png`
  - `19_axe_scan_summary.png`

## How to Reproduce the Evidence
The app must be running at `http://127.0.0.1:5000/` with a fresh database (delete `pytodo_pro.db`, then run `python app.py`):
```bash
pip install playwright pillow
python -m playwright install chromium
npm install axe-core          # creates node_modules/axe-core/axe.min.js
python 03_Special_Testing/week3_evidence.py
```
> Before running, edit the paths at the top of `week3_evidence.py`:
> - `OUT`: where screenshots are saved
> - the `axe.min.js` path
> - the font paths
> - the `executable_path` of Chrome (on Windows, remove it to use Playwright's own Chromium, or point it to `C:\Program Files\Google\Chrome\Application\chrome.exe`)

## Technique Justification
1. **GUI Checklist Testing:** Every form, button, link, message and data display on the six pages was checked against its expected appearance and behaviour. A checklist makes sure no element is skipped, and it maps directly to the "evaluate forms, buttons, links, labels, navigation, messages" requirement.
2. **Heuristic Usability Evaluation (Nielsen):** Applied to feedback, error prevention, error recovery and consistency. It gives a recognised, repeatable basis for usability judgements without needing a full user study.
3. **WCAG 2 Accessibility Review:** Applied at Level A/AA, using manual checks (label association, accessible names, keyboard-only navigation, change on input, reflow at 200%/400% zoom) and an **axe-core 4.14.1** automated scan of the Login, Task list, New Task and Dashboard pages. The automated scan finds common failures quickly; the manual checks cover what tools cannot judge.
4. **Configuration / Compatibility Testing:** The same seven-step smoke flow (register, create with date picker, toggle, filter, delete with confirmation, dashboard, log out) was run on each configuration, so that results can be compared cell by cell in the matrix.

## Execution Summary
- **Environment:** Google Chrome 153 (desktop 1280×800 and mobile emulation 375×667 with touch), driven by Playwright; Flask 3.1.3; clean SQLite DB; test account `tester1` / `abcd12345`
- **Total Planned:** 38 test cases
- **Executed:** 33 (86.84%)
- **Passed:** 18 (54.55% of executed)
- **Failed:** 15 (45.45% of executed) — `TC-GUI-006`, `009`, `010`, `014`, `015`; `TC-USA-001`, `002`, `004`; `TC-ACC-002`, `003`, `004`, `005`, `006`, `011`; `TC-CMP-005`
- **Not Run:** 5 — `TC-CMP-002` (Firefox), `TC-CMP-003` (Edge), `TC-CMP-004` (Safari), `TC-ACC-010` (colour contrast), `TC-USA-006` (visual consistency). The last two need `static/style.css`, which was not in the project files, so the pages were tested unstyled.
- **Defects:**
  - 2 earlier defects confirmed in the UI (`DEF-002`, `DEF-006`)
  - 12 new defects (`DEF-010` to `DEF-021`)
  - All consolidated in `07_Test_Management/consolidated_defect_log.csv`
- **Key Observation:** Every user workflow worked in both desktop and mobile Chrome. The quality problems are in **presentation, feedback and accessibility**:
  - task titles render as HTML
  - blank titles are accepted
  - form fields are unlabeled for assistive technology
  - there is no mobile viewport setting

  These are cheap to fix and should be added to the regression suite in Week 6.
