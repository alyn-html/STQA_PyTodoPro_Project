# Test Management, Traceability & Defect Consolidation Findings — PyTodo Pro

- **Coordinator:** [Mohammad Haiqal Firdaus Bin Mad Husni (22006428)]
- **Role:** Member 1 — Test Planning, Black-Box & Test Management
- **Date:** 21 November 2026
- **Environment:** Local Windows 11 environment, PowerShell (`venv`), Google Chrome, Python 3 / Flask (`http://127.0.0.1:5000/`), GitHub Repository (`STQA_PyTodoPro_Project`)
- **Application:** PyTodo Pro (Flask + SQLite `pytodo_pro.db`)
- **Scope:** Project Week 7 — Test Plan Alignment, Requirements Traceability Matrix (RTM), Consolidated Defect Management, and Planned-vs-Actual Execution Evaluation
- **Baseline Test Account:** `ayamgoreng` (Password: `akusukaayam`)

---

## 1. Overview of Test Management & Consolidation
As part of Project Week 7 test management activities, all testing artifacts produced during manual black-box execution (`01_Black_Box`) were consolidated into a unified traceability and defect-tracking framework inside `07_Test_Management/`. Rather than treating test planning as a static pre-execution document, the formal Software Test Plan (`test_plan.md`) and Requirements Traceability Matrix (`rtm.csv`) were updated using empirical evidence gathered during browser execution. Every requirement (`REQ-01` through `REQ-09`) was mapped to its corresponding test cases (`TC-BB-001` through `TC-BB-028`), execution outcomes, visual screenshot references, and defect records (`DEF-001` through `DEF-005`) so that cross-artifact consistency is maintained for the final quality evaluation (`08_Final_QA_Report`).

---

## 2. Key Test Management & Governance Findings

### Finding 1: Requirements Traceability Coverage & Failure Concentration (`rtm.csv`)
Mapping all 28 black-box test cases against the nine functional Web UI requirements (`REQ-01` to `REQ-09`) confirmed 100% forward and backward traceability across every user-facing feature. Six of the nine requirements (`REQ-02` User Login, `REQ-03` User Logout, `REQ-04` Task Listing/Filter/Search, `REQ-07` Delete Task, and `REQ-09` Summary Dashboard) achieved a 100% pass rate with zero confirmed functional defects. In contrast, all five confirmed defects clustered around three specific functional areas: User Registration (`REQ-01`), Task Creation/Editing (`REQ-05` and `REQ-06`), and Task Urgency Classification (`REQ-08`). This distribution validates the Pareto defect-clustering principle and confirms that input validation and date-boundary logic represent the primary stability risks in PyTodo Pro.

### Finding 2: Consolidated Defect Severity & Prioritization Analysis (`consolidated_defect_log.csv`)
All five defects discovered during manual black-box testing were standardized under the 12-field ISTQB-aligned defect schema and classified by both technical **Severity** and remediation **Priority**. Two defects were classified as **Critical Severity / High Priority**: `DEF-001` (an unhandled Python `ValueError` HTTP 500 traceback crash when submitting a five-digit year such as `19999-06-14` in `/tasks/new` or `/tasks/<id>/edit`, which also disrupts return navigation) and `DEF-003` (duplicate account registration with existing credentials silently overwriting prior user records and wiping saved tasks). Two defects were classified as **Major Severity**: `DEF-002` (High Priority — tasks due on the exact current date $T$ are mislabeled as `Overdue` instead of `Due Today`) and `DEF-004` (Medium Priority — registering a second unique account within the same browser instance is blocked). One defect was classified as **Minor Severity / Low Priority**: `DEF-005` (registration accepts purely lowercase passwords without alphanumeric or symbol complexity rules).

### Finding 3: Defect Lifecycle Governance Under Non-Modification Constraints
In accordance with the course quality evaluation guidelines prohibiting modification of PyTodo Pro's application source code (`app.py`, `helpers.py`, and HTML templates), no code patches were applied during testing. Consequently, all five confirmed defects (`DEF-001` through `DEF-005`) remain formally tracked in `Open` status within `consolidated_defect_log.csv` with full reproduction steps and screenshot links (`01_Black_Box/screenshots/...`) so that downstream phases (`08_Final_QA_Report` and `09_Presentation`) can accurately report unresolved residual risks. Additionally, the consolidated log structure is aligned with teammate findings in `04_Web_API` and `05_Security_Performance` to prevent duplicate numbering across repository branches.

### Finding 4: Planned-versus-Actual Execution Variance (`execution_summary.md`)
During initial test planning, 21 core black-box test cases (`TC-BB-001` to `TC-BB-021`) were designed across Equivalence Partitioning, Boundary Value Analysis, Decision Tables, and State Transitions. During execution, seven additional exploratory and boundary-refinement test cases (`TC-BB-022` to `TC-BB-028`) were added to verify exact three-value character length boundaries on registration (`3–20` username characters, `min 8` password characters), special-character rejection, whitespace-only task titles, edit-form date crashes, and dashboard metric updates upon task deletion. Across all 28 executed test cases (100% execution rate), 23 passed (82.14%), 5 failed (17.86%), and 0 were blocked.

---

## 3. Summary of Cross-Artifact Alignment & Readiness
All required Week 7 test management deliverables—`test_plan.md`, `rtm.csv`, `consolidated_defect_log.csv`, `execution_summary.md`, and `test_management_findings.md`—are synchronized with `01_Black_Box/`. Every Test Case ID (`TC-BB-001` to `TC-BB-028`), Defect ID (`DEF-001` to `DEF-005`), severity label (`Critical`, `Major`, `Moderate`, `Minor`), status value (`Open`), and screenshot path resolves consistently across both folders, providing a complete audit trail for final SQA reporting.
```[cite: 21, 22, 23, 25]

### How to Add This to GitHub
1. Open the **`07_Test_Management`** folder in your GitHub repository[cite: 21].
2. Click **Add file** → **Create new file**.
3. Name the file `test_management_findings.md`, paste the Markdown content above (after adding your full name and student ID), and click **Commit changes**.
4. *(Optional)* Add `- test_management_findings.md — Narrative summary of traceability coverage, defect severity/lifecycle governance, and planned-versus-actual execution findings.` to `07_Test_Management/README.md`[cite: 21].
