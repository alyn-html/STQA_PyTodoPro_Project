# Web and API Testing — PyTodo Pro

## 1. Purpose

This folder contains the Web/API testing artefacts for the PyTodo Pro Software Testing and Quality Assurance project. The tests evaluate selected web workflows, API authentication, valid and invalid requests, HTTP status codes, response content, and consistency between API and user-interface behaviour.

## 2. Files in This Folder

| File                        | Purpose                                                             |
| --------------------------- | ------------------------------------------------------------------- |
| `README.md`                 | Overview of the testing scope, environment, execution and artefacts |
| `api_findings.md`           | Detailed observations and actual responses from executed tests      |
| `api_test_cases.csv`        | Structured test cases with expected and actual results              |
| `web_api_testing_report.md` | Consolidated report for Section 5.0 of the group QA report          |

## 3. Test Environment

- **Application:** PyTodo Pro
- **Application type:** Flask-based task-management web application
- **Test interface:** Web browser and HTTP API requests
- **API format:** JSON for the tested API responses
- **Execution environment:** GitHub Codespaces
- **Local application address:** `http://127.0.0.1:5000`
- **Test date:** 27 October 2026
- **Test tools:** `curl`, terminal, web browser and GitHub Codespaces
- **Test account:** Siti

The API requests were sent to the locally running application. Authentication-dependent tests used the session cookie saved locally after logging in as Siti.

## 4. Scope

Testing covered:

- Unauthenticated access to selected web pages and API endpoints.
- Login and authenticated task access.
- Task creation, listing, retrieval and updating.
- Validation of a request with a missing task title.
- Filtering tasks by category.
- Comparison of task data returned by the API with the task displayed in the web interface.
- Review of an authentication-control inconsistency requiring further investigation.

Pagination, task deletion, broader input validation, automated API regression, security penetration testing and performance testing are not claimed as completed by this test suite.

## 5. Execution Summary

Twelve checks were recorded from the available execution evidence. The tested operations behaved as expected for the stated test objectives, with one observation requiring investigation: `/api/categories` returned `200 OK` without authentication, although the project README describes API endpoints other than registration and login as requiring a session cookie.

This observation is not automatically classified as a confirmed security defect because categories may intentionally be publicly accessible. The intended access policy should be confirmed with the project requirements or developer.

## 6. Procedure

1. Start PyTodo Pro using the project's documented startup instructions.
2. Open a second terminal in the repository.
3. Send the HTTP requests listed in `api_findings.md`.
4. Compare actual responses with the records in `api_test_cases.csv`.
5. Review `web_api_testing_report.md` for the consolidated analysis.

Do not commit session-cookie files or local test databases to the repository. Test results should reflect actual observed behaviour rather than assumed outcomes.

