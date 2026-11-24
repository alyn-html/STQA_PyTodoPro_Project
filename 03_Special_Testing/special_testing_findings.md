# GUI, Compatibility, Usability & Accessibility Findings — PyTodo Pro Web UI

## 1. Overview of Execution
GUI, usability, accessibility and compatibility testing was carried out on the PyTodo Pro Web UI (`http://127.0.0.1:5000/`) using **Google Chrome 153** at a desktop viewport of 1280×800 and in **mobile emulation** at 375×667 with touch input. Browser actions were scripted with Playwright (`week3_evidence.py`), so every step can be reproduced, and every screenshot carries a header strip with the test-case ID, URL, browser, viewport and timestamp. The accessibility review combined manual checks based on WCAG 2 concepts (labels, names, keyboard access, change of context, reflow) with an automated scan by **axe-core 4.14.1** (rule sets `wcag2a` and `wcag2aa`). Each run used a clean SQLite database, the test account `tester1` / `abcd12345`, and the execution date `2026-11-24` (*T*).

A total of **38 test cases** were planned across five groups:
- 16 GUI (`TC-GUI-001` to `TC-GUI-016`)
- 6 usability (`TC-USA-001` to `TC-USA-006`)
- 11 accessibility (`TC-ACC-001` to `TC-ACC-011`)
- 5 compatibility (`TC-CMP-001` to `TC-CMP-005`)

**33 were executed (86.84%)**: **18 passed (54.55% of executed)** and **15 failed (45.45%)**. **5 were Not Run**: Firefox, Edge and Safari (no installs available in the test environment), plus colour contrast and visual consistency, because `static/style.css` was not in the project files and the pages were therefore tested **unstyled**. Failures were traced to **14 defects**:
- two confirmed earlier defects showing up in the UI (`DEF-002`, `DEF-006`)
- twelve new defects (`DEF-010` to `DEF-021`)

---

## 2. GUI Testing Checklist & Results

| Area | Checks | Result | Evidence |
|---|---|---|---|
| **Forms** | Login, Register, New Task and Edit Task forms show all fields. Due date uses a native date picker. Edit pre-fills values. | Pass, except title validation (`DEF-012`) | `05_new_task_form.png`, `08_edit_task_form.png` |
| **Buttons** | Create Task / Save Changes labels, Filter, toggle ○/✓, Delete with confirmation | Pass | `09_task_toggled_done.png`, `11_after_delete_confirmed.png` |
| **Links & navigation** | The nav changes correctly when logged in or out. Tasks, Dashboard, Log out, Cancel and "+ New Task" go to the right pages. After log out, protected pages redirect to `/login`. | Pass | `01_login_page.png`, `04_empty_task_list.png` |
| **Messages** | Errors for login, invalid username and short password. Empty-state message. | Partly pass (`DEF-006`, `DEF-017`, `DEF-018`) | `02_…`, `03_…`, `15_login_error.png` |
| **Data display** | Titles, categories, due dates, urgency badges, dashboard counters | Fail (`DEF-002`, `DEF-011`, `DEF-012`) | `06_task_list_defects.png`, `07_dashboard_overdue_count.png` |
| **Visual consistency** | Styling, spacing and badge colours across pages | Not Run — no stylesheet | — |

### Finding 1: Task Titles Are Rendered as HTML (`DEF-011`)
A task titled `<b>Bold</b> <i>formatted</i> title` appeared in **bold and italic** in the task list instead of as the literal text the user typed (`06_task_list_defects.png`). The template outputs titles with Jinja's `|safe` filter, which turns off escaping. Besides the display error, this lets stored markup or script run in the browser of anyone viewing the list, so it should be followed up as a stored-XSS threat in Week 5 (STRIDE: Tampering / Elevation of Privilege).

### Finding 2: Whitespace-Only Titles Create Blank Rows (`DEF-012`)
The title field's HTML `required` attribute accepts three spaces. The server then strips them and saves an **empty title**. The result is a task row with no visible title, where only the ○ button and the Edit/Delete links identify it (`06_task_list_defects.png`, first row). Neither the browser nor the server prevents this error.

### Finding 3: Due-Today Tasks Are Shown as Overdue in the UI (`DEF-002`)
This confirms the Week 1 and Week 2 finding at GUI level. *Submit STQA report*, due `2026-11-24` (today), showed a red **Overdue** badge (`06_task_list_defects.png`). The dashboard also counted it under **Overdue = 1** (`07_dashboard_overdue_count.png`). Users see a task as late on the day it is actually due.

### Finding 4: Register Hint Contradicts Behaviour (`DEF-006`)
The registration page says *"(min 8 characters)"*, but `abcd1234` (8 characters) was rejected with *"Password must be at least 8 characters."* (`03_register_8char_password_rejected.png`). The message tells the user they did what it asks and still failed, which is confusing. Root cause: `len(password) > 8`, as shown in Week 2.

---

## 3. Compatibility / Configuration Matrix

| Configuration | Register/Login | Create + date picker | Toggle | Filters | Delete dialog | Dashboard layout | Log out | Result |
|---|---|---|---|---|---|---|---|---|
| Chrome 153, desktop 1280×800 | Pass | Pass | Pass | Pass | Pass | Pass | Pass | **Pass** |
| Firefox (latest) | — | — | — | — | — | — | — | Not Run |
| Edge (latest) | — | — | — | — | — | — | — | Not Run |
| Safari (macOS/iOS) | — | — | — | — | — | — | — | Not Run |
| Chrome mobile emulation 375×667, touch | Pass | Pass | Pass | Pass | Pass | **Fail** | Pass | **Fail** (`DEF-020`) |

### Finding 5: No Mobile Viewport Setting — Pages Render at Desktop Width on Phones (`DEF-020`)
`base.html` has no `<meta name="viewport" content="width=device-width, initial-scale=1">` tag. In 375×667 mobile emulation, every functional step worked by touch, including the date picker, toggle, filter and delete confirmation. However, the browser laid each page out at its default 980 px and then **shrank it to fit the phone screen** (page width 981 px against a 980 px layout viewport), leaving text and tap targets very small (`17_mobile_task_list.png`, `18_mobile_dashboard.png`). Because this comes from the HTML rather than the stylesheet, it will happen whatever `style.css` contains.

---

## 4. Usability Observations
Evaluated against Nielsen's heuristics: visibility of system status, consistency, error prevention, help users recover from errors, and recognition over recall.

| ID | Observation | Heuristic | Result |
|---|---|---|---|
| TC-USA-001 | After a registration error, the **username field is cleared**, so the user must retype it (`02_register_username_error.png`). | Error recovery, user control | Fail — `DEF-013` |
| TC-USA-002 | A brand-new user with no filters sees *"No tasks match your filters."* This suggests a filter problem instead of inviting them to create a first task (`04_empty_task_list.png`). | Match with real world | Fail — `DEF-017` |
| TC-USA-003 | Username and password rules are shown next to the labels **before** the user types. | Error prevention | Pass |
| TC-USA-004 | Opening `/tasks/999/edit` silently returns the user to the list, with **no "task not found" message** (`12_invalid_edit_url_no_message.png`). | Visibility of system status | Fail — `DEF-018` |
| TC-USA-005 | Every page has a distinct tab title (*Log in / Register / Tasks / New Task / Edit Task / Dashboard — PyTodo Pro*). | Consistency | Pass |
| TC-GUI-012 | Delete asks *"Delete this task?"*. Cancel kept the task (4 → 4 rows) and OK removed it (4 → 3) (`11_after_delete_confirmed.png`). | Error prevention | Pass |
| TC-GUI-013 | Category, status and search text are kept after filtering (`10_filters_persist.png`). | Visibility / recognition | Pass |

**Overall:** navigation is simple and predictable, and destructive actions are confirmed. The weak points are **feedback and error recovery**: inputs are cleared, there are silent redirects, the empty-state message is misleading, and the password rule text contradicts the behaviour.

---

## 5. Basic Accessibility Findings (WCAG 2)

**Automated scan (axe-core 4.14.1, WCAG 2 A/AA)** — `19_axe_scan_summary.png`

| Page | Rule | Impact | WCAG | Elements |
|---|---|---|---|---|
| Login | `label` — form elements must have labels | Critical | 4.1.2 (A) | 2 |
| Task list | `select-name` — select must have an accessible name | Critical | 4.1.2 (A) | 2 |
| New Task | `label` | Critical | 4.1.2 (A) | 3 |
| New Task | `select-name` | Critical | 4.1.2 (A) | 1 |
| Dashboard | No violations detected | — | — | — |

### Finding 6: Form Labels Are Not Connected to Their Inputs (`DEF-010`)
Every form uses `<label>Username</label>` followed by an `<input>`, with no `for`/`id` pairing. Clicking the visible word "Username" left focus on the page body instead of moving it to the input (`14_label_not_associated.png`), and `getByLabel("Username")` found **0** matching fields on both Login and Register. Screen-reader users hear unnamed "edit text" fields. This fails **WCAG 1.3.1 and 4.1.2 (Level A)** and was confirmed by axe on the Login and New Task pages.

### Finding 7: Filter Controls Have No Accessible Names (`DEF-016`)
Both filter dropdowns on the task list have no label (axe `select-name`, critical). The search box is named only by its placeholder *"Search title..."*. axe accepts a placeholder as a fallback name, but the placeholder disappears as soon as the user types, which is weak support for **WCAG 3.3.2**.

### Finding 8: Complete/Undo Button Is Announced as a Symbol (`DEF-014`)
The toggle buttons' accessible names are just `○` and `✓`. A screen reader announces "white circle, button" with no indication of the action or which task it affects. This fails **WCAG 4.1.2**. Suggested name: `aria-label="Mark 'Buy groceries' as done"`.

### Finding 9: Choosing a Filter Option Reloads the Page Immediately (`DEF-015`)
Both filter dropdowns submit on `onchange`. With keyboard focus on the category dropdown, a **single ↓ key press** reloaded the page to `?category=Personal`. Keyboard users cannot move through the options without triggering a reload each time, which fails **WCAG 3.2.2 On Input (Level A)**.

### Finding 10: Empty Table Headers (`DEF-019`)
The first column (toggle) and last column (actions) of the task table have empty `<th>` elements, so screen readers give no column context (**WCAG 1.3.1**, best practice).

### Finding 11: Horizontal Scrolling at 320 px (`DEF-021`, provisional)
At 640 px, which is equivalent to 200% zoom, the task list fitted with no horizontal scroll. At 320 px, which is equivalent to 400% zoom and the width WCAG uses for its reflow test, the page measured **337 px wide** and needed horizontal scrolling (`16_reflow_320px.png`), failing **WCAG 1.4.10 Reflow (AA)**. This was measured **without** `style.css` and must be re-checked once the stylesheet is applied.

### Accessibility checks that passed
- `<html lang="en">` is present (WCAG 3.1.1).
- Every page has a descriptive title (2.4.2).
- Urgency badges carry text, not colour alone (1.4.1).
- Errors are described in text (3.3.1).
- Keyboard-only operation (2.1.1 / 2.4.7): all 14 interactive controls on the task list were reached with Tab in a logical order (nav → *+ New Task* → filters → each row's ○, Edit, Delete), and Chrome's default focus ring was visible (`13_keyboard_focus_visible.png`). *Re-check focus visibility with `style.css`, since stylesheets often remove outlines.*

---

## 6. Defects and Improvement Recommendations

| Defect ID | Title | Severity | Priority | Recommendation |
|---|---|---|---|---|
| DEF-002 | Task due today shown as Overdue (list + dashboard) | Major | High | Add a `due == today → "Due Today"` branch in `compute_urgency()` |
| DEF-006 | 8-char password rejected despite "min 8" hint | Major | High | Use `len(password) >= 8` |
| DEF-010 | Form labels not associated with inputs | Moderate | Medium | Add `for`/`id` pairs (or wrap the input inside `<label>`) |
| DEF-011 | Task titles rendered as raw HTML | Major | High | Remove `\|safe` from `index.html`; rely on Jinja auto-escaping |
| DEF-012 | Whitespace-only title creates blank task | Moderate | Medium | Reject an empty title after `strip()` on the server; add `pattern=".*\S.*"` on the input |
| DEF-013 | Register form clears username after error | Minor | Low | Re-render with `value="{{ username }}"` |
| DEF-014 | Toggle button has no descriptive name | Moderate | Medium | Add an `aria-label` naming the action and the task |
| DEF-015 | Filter selects reload page on change | Minor | Low | Remove `onchange` and rely on the Filter button |
| DEF-016 | Filter controls have no accessible names | Moderate | Medium | Add visible or `aria-label` labels to both selects and the search box |
| DEF-017 | Misleading empty-state message | Minor | Low | Show "No tasks yet — create your first task" when no filters are applied |
| DEF-018 | Invalid edit URL redirects without feedback | Minor | Low | Flash a "Task not found" message |
| DEF-019 | Empty table headers | Minor | Low | Use headers such as "Done" and "Actions" (can be visually hidden) |
| DEF-020 | No viewport meta tag; desktop layout on phones | Moderate | Medium | Add `<meta name="viewport" content="width=device-width, initial-scale=1">` to `base.html` |
| DEF-021 | Horizontal scroll at 320 px (provisional) | Minor | Low | Re-check with `style.css`; stack table rows as cards on narrow screens |

**General recommendations**
1. Add **axe-core** (or Lighthouse) to the Week 6 regression suite so missing labels and names are caught automatically.
2. Validate on the **server** as well as with HTML attributes, because `required` alone does not stop empty or whitespace input.
3. Before the final report, repeat `TC-CMP-002` to `004` in Firefox, Edge and Safari, and `TC-ACC-010` and `TC-USA-006` with the real stylesheet.

---

## 7. Limitations
- **The pages were tested unstyled.** `static/style.css` was not in the project files, so the screenshots show default browser styling. Colour contrast (WCAG 1.4.3) and visual consistency are Not Run, and the reflow and focus-visibility results should be re-checked with the stylesheet.
- **Only Chrome was available.** Mobile results come from Chrome's device emulation, not a physical phone. Firefox, Edge and Safari still need to be tested by the group.
- **Automated accessibility scans catch only part of WCAG.** No screen-reader session (NVDA/VoiceOver) was performed. The screen-reader statements above are based on the accessible names exposed in the page.
- **Headless runs do not show native dialogs.** The delete confirmation was verified through the browser's dialog event (message text plus row counts before and after), not a visible screenshot of the dialog.
