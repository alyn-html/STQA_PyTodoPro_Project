# Test Execution Summary & Planned-vs-Actual Report

## 1. Consolidated Manual Test Execution Metrics (Sections 2.0 – 6.0)
| Testing Area (Repo Folder) | Planned | Executed | Passed | Failed | Needs Review | Not Run | Pass Rate (Executed) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Black-Box Web UI (`01_Black_Box`)** | 21 | 21 | 17 | 4 | 0 | 0 | 80.95% |
| **White-Box Structural (`02_White_Box_Coverage`)** | 43 | 43 | 34 | 9 | 0 | 0 | 79.07% |
| **GUI, Usability, Accessibility & Compatibility (`03_Special_Testing`)** | 38 | 33 | 19 | 14 | 0 | 5 | 57.58% |
| **Web & REST API (`04_Web_API`)** | 21 | 21 | 19 | 1 | 1 | 0 | 90.48% |
| **Security & Performance (`05_Security_Performance`)** | 15 | 15 | 13 | 2 | 0 | 0 | 86.67% |
| **Total Consolidated Manual Suite** | **138** | **133** | **102** | **30** | **1** | **5** | **76.69%** |

## 2. Automated Regression Suite Metrics (`06_Automation_Regression`)
| Automated Suite Layer | Test Count | Runtime | Key Verification Outcome |
| :--- | :---: | :---: | :--- |
| **Unit Tests (`test_unit_helpers.py`)** | 42 | 0.3 s | 100% statement and 100% branch coverage on `helpers.py` |
| **REST API Tests (`test_api.py`)** | 38 | ~3.5 s | Uncovered 4 new API defects (`DEF-022` to `DEF-025`) |
| **Web Route Tests (`test_web.py`)** | 38 | ~3.6 s | Uncovered post-logout caching defect (`DEF-026`) |
| **Selenium Browser UI (`test_ui_selenium.py`)** | 15 | 13.9 s | Verified UI flows and `axe-core 4.14.1` accessibility rules |
| **Total Automated Suite (`pytest`)** | **133** | **~21.3 s** | **99% stmt / 99% branch coverage on `app.py`; 37 strict `xfail` defect oracles** |

- **Manual-to-Automated Conversion Rate:** 105 of 113 automatable manual test cases automated (**92.92%**), with **99.05%** oracle consistency (104/105 matching manual outcomes).

## 3. Consolidated Defect Summary (26 Unique Defects)
- **Deduplication Reconciliation:** 28 total defect IDs were logged across all folders (`DEF-001`–`DEF-026`, `DEF-API-001`, `SEC-DEF-001`, `SEC-DEF-002`). Root-cause verification confirmed two duplicates: `DEF-004` (same-browser registration block) is a symptom of `DEF-006` (`len(password) > 8`), and `SEC-DEF-002` duplicates `DEF-API-001` (numeric title HTTP 500 on `POST /api/tasks`), leaving **26 unique confirmed defects** (all maintained in `Open` status per non-modification rules).
- **Severity Breakdown:** **4 Critical** (15.4% — `DEF-001`, `DEF-003`, `SEC-DEF-001`, `DEF-023`), **3 Major** (11.5% — `DEF-002`, `DEF-006`, `DEF-011`), **10 Moderate** (38.5%), and **9 Minor** (34.6%).

## 4. Planned-versus-Actual Variance Analysis
- **Manual Execution Variance (`133 / 138 = 96.38%`):** Five planned tests in `03_Special_Testing` were marked `Not Run` due to environment constraints: unavailable Firefox, Edge, and Safari browsers (`TC-CMP-002` to `TC-CMP-004`), missing `static/style.css` returning HTTP 404 for contrast verification (`TC-ACC-014`), and an unscheduled moderated participant walkthrough (`TC-USA-006`).
- **Automation Expansion:** Alongside the 105 automated tests converted from manual cases, 28 additional automated tests were added in `06_Automation_Regression` to cover SQL injection on `/api/tasks`, non-string JSON payloads, and `Cache-Control` response headers, uncovering `DEF-022` through `DEF-026`.
