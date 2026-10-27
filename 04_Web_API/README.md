# Web and API Testing — PyTodo Pro

## 1. Purpose

This folder contains the Web/API testing artefacts prepared for the STQA group project. The tests evaluate selected PyTodo Pro web routes and REST API endpoints, including authentication, task creation and retrieval, task updates, deletion, filtering, pagination, input validation, and HTTP responses.

## 2. Test environment

| Item | Details |
|---|---|
| Project | PyTodo Pro |
| Test area | Web and REST API |
| Environment | GitHub Codespaces |
| Application | Flask |
| Base URL | `http://127.0.0.1:5000` |
| Execution date | 27 October 2026 |
| Test tools | `curl`, HTTP response inspection, browser UI comparison |
| Test data | Test tasks and login requests; credentials and session-cookie values are excluded from reports |

## 3. Contents

| File | Purpose |
|---|---|
| `README.md` | Scope, environment, and execution summary |
| `api_findings.md` | Observed endpoint responses and API findings |
| `api_test_cases.csv` | Test cases, expected results, actual results, and statuses |
| `web_api_testing_report.md` | Summary, coverage, defect, and limitations |

## 4. Test coverage

The tests cover:
- Authentication and access control for selected web routes and API endpoints.
- Valid login and invalid or incomplete login requests.
- Task creation, listing, filtering, retrieval, updating, and deletion.
- Missing, empty, and incorrectly typed task-title inputs.
- HTTP status codes and JSON response bodies.
- Zero-based pagination.
- A basic UI/API consistency check confirming that a task created through the API appeared in the web UI.

## 5. Execution summary

| Result | Count |
|---|---:|
| Pass | 19 |
| Fail | 1 |
| Needs Review | 1 |
| **Total checks** | **21** |

The failed test concerns a numeric task title. The endpoint returns `500 INTERNAL SERVER ERROR` rather than a controlled input-validation response. The unauthenticated categories endpoint is marked Needs Review because its observed behaviour may conflict with the project's stated authentication policy.

## 6. Running the tests

Start the application from the project directory using the project's documented startup command, then run the relevant `curl` requests in the terminal. Use a valid test session only for authenticated tests. Requests without `-b own_cookies.txt` are unauthenticated.

Example: test whether unauthenticated task creation is rejected.

```bash
curl -i \
  -H "Content-Type: application/json" \
  -d '{"title":"Unauthenticated Test","description":"Should not be created"}' \
  http://127.0.0.1:5000/api/tasks
```

Expected result: `401 UNAUTHORIZED` with an authentication error.

## 8. Scope limitations

This is a scoped test of selected web and API behaviours, not exhaustive testing of the entire application. The UI/API comparison is limited to confirming that an API-created task appeared in the web interface. Additional end-to-end browser workflows and the intended authentication policy for `/api/categories` require further verification.
