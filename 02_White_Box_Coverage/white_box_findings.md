# White-Box Testing Findings — PyTodo Pro

## 1. Overview of White-Box Execution
White-box testing was carried out on the PyTodo Pro source code (`helpers.py` and selected units of `app.py`). Following the project brief, the whole application was not tested exhaustively. Instead, the group chose the units that decide what users see on the task list and dashboard, and the units behind the defects found during black-box testing (`DEF-001` to `DEF-005`). Tests were written to achieve statement and branch coverage, with boundary values added where branch coverage alone would miss off-by-one errors. They were automated in PyTest (`test_whitebox.py`) and coverage was measured with `pytest-cov` in branch mode.

Fixed dates were injected wherever the functions allow it (`today = 2026-11-24`, `now = 2026-11-24 12:00:00`), so the results do not depend on the day the suite is run. Each test's name contains its test-case ID (for example `test_TC_WB_004_urgency_today` is `TC-WB-004`).

A total of **43 white-box test cases** (`TC-WB-001` to `TC-WB-043`) were executed: **35 passed (81.40%)** and **8 failed (18.60%)**. The failures confirmed the root causes of two black-box defects (`DEF-001`, `DEF-002`), explained two others (`DEF-003`, `DEF-004`), and exposed **four new defects** (`DEF-006` to `DEF-009`). Coverage of `helpers.py` reached **100% of statements and 100% of branches**, which shows clearly that full coverage does not mean the code is correct.

**Command used:**
```bash
pytest test_whitebox.py -v --cov=helpers --cov=app --cov-branch --cov-report=term-missing --cov-report=html
```

---

## 2. Selected Code Units and Justification

| Unit | Why it was selected | Test cases |
|---|---|---|
| `helpers.compute_urgency()` | Produces the urgency badge on every task row and the Overdue / Due Soon dashboard counters. Its date boundaries are classic defect sources, and black-box testing had already found `DEF-001` and `DEF-002` here. | TC-WB-001 to 009 |
| `helpers.is_valid_password()` | Gatekeeper for every new account (web and API). A one-line rule, but an off-by-one error here blocks valid users. | TC-WB-010 to 015 |
| `helpers.is_valid_username()` | Gatekeeper for every new account. Controls which characters reach the database and the UI. Contains a loop and compound conditions. | TC-WB-016 to 024 |
| `helpers.completed_in_last_n_days()` | Feeds the "Completed (last 7 days)" counter. Time arithmetic with an inclusive boundary and a two-condition decision. | TC-WB-025 to 035 |
| `app.row_to_task()`, `get_category_name()`, `login_required_web` | Glue code where the helpers feed the UI. Selected to show that branches in the application layer are reached. | TC-WB-036 to 040 |
| `app.register_page()` / `login_page()` | Root-cause analysis of black-box defects `DEF-003` and `DEF-004` (registration and login). | TC-WB-041, 042 |
| `app.new_task()` → `index()` | Root-cause analysis of black-box defect `DEF-001` (server crash on a 5-digit year). | TC-WB-043 |

The rest of the route handlers in `app.py` (the API in particular) were left out on purpose. They are covered by black-box testing (Week 1) and will be covered by API testing (Week 4).

---

## 3. Control-Flow Analysis

Cyclomatic complexity (CC) was calculated as *number of decisions + 1*. A compound condition (`A and B`) was counted as two decisions, so that each condition is tested on its own.

**`compute_urgency(due_date_str, today)` — CC = 5**
- D1 `today is None` → use `date.today()`
- D2 `not due_date_str` → return `"No due date"`
- *(`strptime` parses the date and raises `ValueError` if the format is wrong)*
- D3 `due <= today` → return `"Overdue"`
- D4 `delta_days <= 2` → return `"Due Soon"`, otherwise `"Upcoming"`

The specification lists **five** outcomes, but the flow graph has only **four** return statements. There is no path that returns `"Due Today"`.

**`is_valid_password(password)` — CC = 3**
- D1 `not isinstance(password, str)` → `False`
- D2 `len(password) > 8` → result

**`is_valid_username(username)` — CC = 6**
- D1 `not isinstance(username, str)` → `False`
- D2 `not (3 <= len <= 20)`, which is two conditions → `False`
- D3 loop inside `all()`: `c.isalnum() or c == "_"`, which is two conditions, checked for every character

**`completed_in_last_n_days(completed_at_str, n, now)` — CC = 5**
- D1 `not completed_at_str` → `False`
- D2 `now is None` → use `datetime.now()`
- D3 `age.total_seconds() > 0 and age.days < n`, which is two conditions → result

**`register_page()` (POST) — CC = 4**
- `if not is_valid_username` → error; `elif not is_valid_password` → error; `else` → INSERT and log in
- There is **no decision node that checks whether the username already exists** before the INSERT.

---

## 4. Detailed Defect & Behavioural Findings

### Finding 1: Root Cause of the Server Crash on Non-Standard Years Confirmed (`DEF-001`)
`TC-WB-009` showed that `compute_urgency("19999-06-14")` raises an unhandled `ValueError` from `datetime.strptime`. `TC-WB-043` traced the full path. `new_task()` saves `due_date` **with no server-side validation**, and then every later request to `/` and `/dashboard` calls `compute_urgency()` on the stored value, through `row_to_task()` or the dashboard counters. Both pages return **HTTP 500**, while `/tasks/new` still loads (HTTP 200).

This explains the black-box observation that navigation "stopped functioning". The crash is not a one-off: the bad task is stored in the database, so the user's task list and dashboard stay broken until that record is removed. Because the list page cannot load, the user cannot even reach the Delete button for it. The `POST /api/tasks` and `PUT /api/tasks/<id>` endpoints also store `due_date` without checking it, so the same crash can be triggered through the API (to be confirmed in Week 4).

### Finding 2: Root Cause of the Current-Date Urgency Defect Confirmed (`DEF-002`)
`TC-WB-004` (due date = today) returned `"Overdue"` instead of `"Due Today"`. The control-flow analysis shows two separate faults in `compute_urgency()`:
1. The comparison `due <= today` captures today's date in the Overdue branch.
2. **No statement anywhere in the function returns `"Due Today"`.** Changing `<=` to `<` alone would make today's tasks show as `"Due Soon"`, which is still wrong.

The fix needs a new branch (`if due == today: return "Due Today"`). This matters for retesting: the retest must check the exact label, not just that the badge is no longer "Overdue".

### Finding 3: Duplicate Registration Creates a Second Account; Tasks Are Hidden, Not Deleted (`DEF-003` — root cause clarified)
`TC-WB-041` registered `ayamgoreng` twice and then checked the `users` table. It held **two rows with the same username** (ids 1 and 2). The original task was still in the `tasks` table, owned by user 1. The cause is structural: the `users` table has no `UNIQUE` constraint on `username`, and `register_page()` has no duplicate check. The code even carries the comment `# NOTE: no uniqueness check against existing usernames here.`

After the duplicate registration, the session points to the new, empty account 2, which is why the tasks *appeared* to be wiped during black-box testing. When the user logged out and back in with the same password, `login_page()` matched the first row (user 1) and the original tasks came back.

`TC-WB-042` showed a worse case. If the second registration uses a **different** password, that new account can never be logged into, because login only checks the first matching row. Login returns the error page (HTTP 200) instead of the success redirect (HTTP 302).

**Recommended update to the defect log:** `DEF-003` should be described as *"duplicate usernames allowed; the second account hides the first and may be impossible to log into"*. It should not be described as data deletion. The severity should stay high, because the user experiences data loss and is left with an account they cannot use.

### Finding 4: "Multi-Account Registration Blocked" Is Caused by the Password Length Defect (`DEF-004` → see `DEF-006`)
The code was inspected, and `register_page()` has **no check of any kind** on whether the browser already has a session or an account. A second registration from the same browser session was tested directly:
- `username1` with an 8-character password (`password`) was **rejected** with "Password must be at least 8 characters."
- `haiqalfirdaus` with a 9-character password was **accepted** (redirected to `/`).

The black-box evidence (`register_password_error.png`) matches this message. `DEF-004` is therefore very likely a symptom of `DEF-006` below, not a one-browser-one-account rule. **Recommended action:** set `DEF-004` to *Retest*, repeat it with a password of 9 or more characters, and close it as a duplicate of `DEF-006` if it passes.

### Finding 5: Exactly-8-Character Passwords Are Rejected (`DEF-006` — new)
Boundary tests on `is_valid_password()` gave these results: 7 characters → `False` (correct), **8 characters → `False` (`TC-WB-013`, fail)**, 9 characters → `True`. The code uses `len(password) > 8`, which contradicts both its own docstring ("at least 8 characters") and the hint on the registration page ("min 8 characters"). The black-box tests checked passwords shorter than 8 and the 11-character `akusukaayam`, so this exact boundary was not tested in Week 1.

This finding also shows that branch coverage alone is not enough. Testing only 7 and 9 characters already gives 100% branch coverage of this function, but misses the defect. Only a test at the boundary value of 8 catches it.

### Finding 6: Task Completed Exactly 7 Days Ago Is Not Counted (`DEF-007` — new)
The docstring of `completed_in_last_n_days()` says the window is *"inclusive of exactly N days ago"*. `TC-WB-029`, a task completed at `2026-11-17 12:00:00` with `now = 2026-11-24 12:00:00`, returned `False`. The cause is the condition `age.days < n`, which should be `<=`. The cases just inside the boundary (6 days 23 hours, `TC-WB-028`) and just outside it (7 days 1 hour, `TC-WB-030`) behaved correctly, which isolates the fault to the boundary itself.

### Finding 7: Task Completed in the Same Second Is Not Counted (`DEF-008` — new)
`TC-WB-033` (`completed_at == now`) returned `False`, because the first condition is `age.total_seconds() > 0` instead of `>= 0`. `completed_at` is stored to the second, so a dashboard request in the same second as marking a task done will not count it. The impact is low, since the next page load corrects it, but it is a real boundary error on the second condition.

### Finding 8: Username Validation Accepts Non-ASCII Letters (`DEF-009` — needs spec clarification)
`TC-WB-024` showed that `is_valid_username("jöhn")` returns `True`. This is because Python's `str.isalnum()` accepts Unicode letters and digits. The registration hint ("letters/numbers/underscore") suggests A–Z, a–z, 0–9 and `_` only. This is logged as a minor defect pending confirmation of the intended rule.

### Note on Black-Box `DEF-005` (password complexity)
The white-box review confirmed that `is_valid_password()` checks length only. However, the documented specification (the docstring and the registration hint) **only requires a minimum length**, so the code meets its specification on this point. The group may want to reclassify `DEF-005` as a security **improvement recommendation** (to revisit under STRIDE in Week 5), rather than a functional defect.

---

## 5. Path and Data-Flow Considerations
- **Missing paths cannot be covered.** The most important defect (`DEF-002`) is a path that does not exist. Coverage tools only measure code that is present, so the only way to find this was to derive expected results from the specification.
- **Compound conditions were tested one condition at a time.** In `completed_in_last_n_days()`, D3 was exercised as True/True (`TC-WB-027`), False/– (`TC-WB-032`, future timestamp) and True/False (`TC-WB-030`), so each condition independently changes the outcome. This is MC/DC-style coverage.
- **Loop coverage.** The `all()` loop in `is_valid_username()` was exercised with no failing characters (`TC-WB-021`) and with a failing character in the middle of the string (`TC-WB-022`, `TC-WB-023`).
- **Data flow of `due_date` (define → store → use).** The value is *defined* by user input in `new_task()`, `edit_task()` and the API. It is *stored* without validation, and then *used* by `strptime` in `compute_urgency()` on every page load. The missing validation between definition and use is what turns one bad input into a persistent crash (`DEF-001`).
- **Data flow of `username`.** The value is *defined* at registration and *used* by `login_page()` through `SELECT ... fetchone()`. Because duplicates can be stored, the use only ever sees the first row (`DEF-003`).
- **Injected clock values.** `today` and `now` can be passed in, which makes the date logic testable without waiting for real dates. The default-clock branches were still covered (`TC-WB-008`, `TC-WB-034`).

---

## 6. Coverage Report and Interpretation

| Module | Statements | Missed | Branches | Partial | Combined coverage |
|---|---|---|---|---|---|
| `helpers.py` | 31 | 0 | 18 | 0 | **100%** |
| `app.py` | 299 | 154 | 64 | 12 | **45%** |
| **Total** | 330 | 154 | 82 | 12 | **52%** |

*(Statement counts depend on the exact file. Re-running the command above on the group's copy will give the authoritative figures, and the HTML report in `htmlcov/index.html` should be included as evidence.)*

**Interpretation**
- **`helpers.py` (100%):** every statement and branch was executed, yet five helper tests failed. Coverage shows what was run, not whether it was right.
- **`app.py` (45%):** this figure is low by design and should not be read as a quality score for the module. The uncovered code is mainly:
  - the JSON API routes (`/api/*`), planned for Week 4 API testing
  - `edit_task()`, `toggle_task()` and `delete_task_web()`, already exercised manually in Week 1 state-transition tests
  - the filter branches in `index()`, already covered by Week 1 EP and decision-table tests
- **Uncovered code that carries risk:**
  - `api_list_tasks()` builds the `q` search with an f-string straight into SQL (an SQL injection risk, for Week 5 security testing).
  - `api_delete_task()` deletes by `id` without checking `user_id`, so one user may be able to delete another user's tasks (Week 4/5).
  - `POST`/`PUT /api/tasks` store `due_date` without validation (the API route to `DEF-001`).

  These should be the first targets when coverage of `app.py` is extended.

---

## 7. Summary
White-box testing confirmed the code-level root causes of `DEF-001` and `DEF-002`, gave a more accurate explanation of `DEF-003` and `DEF-004`, and found four new defects (`DEF-006` to `DEF-009`) that black-box testing had not reached. Three of the four new defects are off-by-one comparisons (`>` vs `>=`, `<` vs `<=`). This suggests a recurring coding pattern that code review and boundary-focused unit tests in CI could prevent.

The most useful lesson for the final QA evaluation is that 100% statement and branch coverage of `helpers.py` sat alongside a missing "Due Today" path and three boundary defects. Coverage is a guide to what has not been tested, not proof that what has been tested is correct.

| Defect ID | Title | Severity | Priority | Status |
|---|---|---|---|---|
| DEF-001 | Unvalidated due date causes persistent HTTP 500 on task list and dashboard | Critical | High | Confirmed — root cause found |
| DEF-002 | Task due today shows "Overdue"; no "Due Today" path exists | Major | High | Confirmed — root cause found |
| DEF-003 | Duplicate usernames allowed; second account hides the first | Major | High | Confirmed — description updated |
| DEF-004 | Second registration in same browser blocked | — | — | Retest (likely duplicate of DEF-006) |
| DEF-006 | 8-character password rejected (`> 8` instead of `>= 8`) | Major | High | Open |
| DEF-007 | Task completed exactly 7 days ago not counted | Moderate | Medium | Open |
| DEF-008 | Task completed in the same second not counted | Minor | Low | Open |
| DEF-009 | Username accepts non-ASCII letters | Minor | Low | Open — needs spec clarification |
