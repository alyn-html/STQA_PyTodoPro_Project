# Test Management, Traceability & Defect Consolidation Findings — PyTodo Pro

- **Coordinator:** Mohammad Haiqal Firdaus Bin Mad Husni
- **Role:** Member 1 — Test Planning, Black-Box & Test Management
- **Environment:** Local Windows 11 environment, PowerShell (`venv`), Google Chrome 153, Python 3 / Flask (`http://127.0.0.1:5000/`), GitHub Codespaces, GitHub Repository (`STQA_PyTodoPro_Project`)[cite: 4, 5]
- **Application:** PyTodo Pro (Flask + SQLite `pytodo_pro.db`)[cite: 4]
- **Scope:** Project Week 7 — Consolidated Test Plan Alignment, Cross-Phase Requirements Traceability Matrix (RTM), Defect Deduplication & Lifecycle Management, and Planned-vs-Actual Execution Evaluation[cite: 5, 7]

---

## 1. Overview of Cross-Phase Consolidation
As part of Project Week 7 test management activities, all manual and automated testing artifacts produced across the entire project—Black-Box Web UI (`01_Black_Box`), White-Box Coverage (`02_White_Box_Coverage`), Special Testing (`03_Special_Testing`), Web & REST API (`04_Web_API`), Security & Performance (`05_Security_Performance`), and Automated Regression (`06_Automation_Regression`)—were consolidated into `07_Test_Management/`[cite: 5, 7]. The formal Software Test Plan (`test_planning.md`), cross-phase Requirements Traceability Matrix (`rtm.csv`), Consolidated Defect Log (`consolidated_defect_log.csv`), and Test Execution Summary (`execution_summary.md`) were reconciled using empirical execution evidence so that every requirement, test case ID, and defect ID aligns consistently for the final QA evaluation report (`08_Final_QA_Report`)[cite: 4, 5].

---

## 2. Key Test Management & Governance Findings

### Finding 1: Cross-Phase Requirements Traceability & Defect Clustering (`rtm.csv`)
Mapping all 138 planned manual test cases and 133 automated PyTest cases across the nine functional Web UI requirements (`REQ-01` through `REQ-09`) and cross-cutting Accessibility/Compatibility criteria confirmed complete forward and backward traceability[cite: 5]. Only `REQ-02` (User Login) passed across all manual and automated test layers with zero defects[cite: 5]. Every other requirement exhibited at least one functional, structural, security, or accessibility defect, with heavy defect clustering in `REQ-01` User Registration (6 unique defects), `REQ-05` Create Task (4 unique defects), and Accessibility/Viewport Compatibility (7 unique defects)[cite: 5].

### Finding 2: Defect Deduplication & Master Register Reconciliation (`consolidated_defect_log.csv`)
Across all testing phases, 28 defect identifiers were initially logged (`DEF-001` through `DEF-026`, `DEF-API-001`, `SEC-DEF-001`, and `SEC-DEF-002`)[cite: 5]. Cross-phase root-cause verification identified two exact duplicates: `DEF-004` (where registering a second account in the same browser was blocked) was confirmed as a symptom of `DEF-006` (`is_valid_password()` enforcing strict `len(password) > 8` and rejecting valid 8-character passwords), and `SEC-DEF-002` was confirmed as a duplicate of `DEF-API-001` (submitting a numeric task title to `POST /api/tasks` causing an unhandled HTTP 500 error)[cite: 5]. Removing these two duplicates yielded **26 unique confirmed defects**, distributed as **4 Critical** (15.4%), **3 Major** (11.5%), **10 Moderate** (38.5%), and **9 Minor** (34.6%)[cite: 5].

### Finding 3: Defect Lifecycle Governance Under Non-Modification Rules
In accordance with course evaluation rules prohibiting modification of PyTodo Pro's source code (`app.py`, `helpers.py`, and templates), no code patches were applied during testing[cite: 5]. Consequently, all 26 unique defects remain formally tracked in `Open` status in `consolidated_defect_log.csv` with reproducible steps and evidence links, while automated regression tests in `06_Automation_Regression` encode these open defects using `@pytest.mark.xfail(strict=True)` so that any future fix will immediately surface as an unexpected pass (`XPASS`)[cite: 4, 5].

### Finding 4: Planned-versus-Actual Execution & Automation Coverage (`execution_summary.md`)
Out of **138 planned manual test cases**, **133 were executed (96.38%)**, yielding **102 passed (76.69%)**, **30 failed (22.56%)**, **1 needing policy review (`API-002`, 0.75%)**, and **5 marked `Not Run`** due to environment constraints (unavailable Firefox, Edge, and Safari browsers for `TC-CMP-002` to `TC-CMP-004`, missing `static/style.css` returning HTTP 404 for `TC-ACC-014`, and an unscheduled moderated walkthrough for `TC-USA-006`)[cite: 5]. In addition, **105 of 113 automatable manual test cases (92.92%)** were converted into the 133-test automated PyTest suite with **99.05% oracle consistency**, uncovering five additional API and session-caching defects (`DEF-022` through `DEF-026`)[cite: 5].

---

## 3. Summary of Cross-Artifact Alignment & Readiness
All Week 7 test management files—`README.md`, `test_planning.md`, `rtm.csv`, `consolidated_defect_log.csv`, `execution_summary.md`, and `test_management_findings.md`—are now synchronized across all repository branches (`01_Black_Box` through `06_Automation_Regression`) and aligned with Section 7.0 of the Final QA Report (`08_Final_QA_Report`)[cite: 4, 5].
