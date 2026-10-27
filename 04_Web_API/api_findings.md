# API Findings: PyTodo Pro

**Tester:** Alya Nabihah (22012109)  
**Test Account:** Siti  
**Date:** 27 October 2026  
**Environment:** GitHub Codespaces, Python 3.14.2, Werkzeug 3.1.9  
**Application:** PyTodo Pro (Flask)  
**Testing Method:** Manual HTTP requests using `curl`

## 2. Test Environment and Methodology

PyTodo Pro was executed in GitHub Codespaces and tested using `curl -i`, which displays HTTP response status codes, headers, and response bodies.

The authenticated API tests used Siti's account. The session cookie was saved in `own_cookies.txt` to maintain an authenticated session across requests. Unauthenticated requests were sent without a session cookie.

The application was tested locally at `http://127.0.0.1:5000/`. Passwords and session-cookie values are excluded from this report.

## 3. Test Findings

### API-001: Unauthenticated Request to the Home Page

| Field | Observed result |
|---|---|
| HTTP method | GET |
| Endpoint | `/` |
| Status code | `302 FOUND` |
| Content-Type | `text/html; charset=utf-8` |
| Location header | `/login` |
| Expected behaviour | An unauthenticated user should be redirected to the login page if authentication is required. |
| Actual result | The server redirected the request to `/login`. |
| Test result | Pass — consistent with expected behaviour. |

**Request:**

```bash
curl -i http://127.0.0.1:5000/
```

**Actual response:**

```http
HTTP/1.1 302 FOUND
Location: /login
Content-Type: text/html; charset=utf-8
```

**Finding:** The home page redirected the unauthenticated request to the login page. No defect was observed in this test.

---

### API-002: Unauthenticated Request to the Categories API

| Field | Observed result |
|---|---|
| HTTP method | GET |
| Endpoint | `/api/categories` |
| Status code | `200 OK` |
| Content-Type | `application/json` |
| Location header | Not applicable / no redirect recorded |
| Expected behaviour | According to the project's stated API authentication policy, endpoints other than registration and login should require a session. Confirm whether categories are intended to be public. |
| Actual result | The server returned category data without requiring authentication. |
| Test result | Needs Review — intended access policy requires confirmation. |

**Request:**

```bash
curl -i http://127.0.0.1:5000/api/categories
```

**Actual response body:**

```json
[
  {"id": 2, "name": "Personal"},
  {"id": 3, "name": "Study"},
  {"id": 4, "name": "Urgent"},
  {"id": 1, "name": "Work"}
]
```

**Finding:** The endpoint returned categories without authentication. This is not classified as a confirmed defect until the team verifies whether public access is intended.

---

### API-003: Unauthenticated Request to the Task List API

| Field | Observed result |
|---|---|
| HTTP method | GET |
| Endpoint | `/api/tasks` |
| Status code | `401 UNAUTHORIZED` |
| Content-Type | `application/json` |
| Location header | Not applicable / no redirect recorded |
| Expected behaviour | The server should reject access to the task list when no authenticated session is supplied. |
| Actual result | The server returned an authentication error. |
| Test result | Pass — consistent with expected behaviour. |

**Request:**

```bash
curl -i http://127.0.0.1:5000/api/tasks
```

**Actual response body:**

```json
{
  "error": "authentication required"
}
```

**Finding:** The task list endpoint enforced authentication and rejected the unauthenticated request.

---

### API-004: Unauthenticated Request to the Dashboard API

| Field | Observed result |
|---|---|
| HTTP method | GET |
| Endpoint | `/api/dashboard` |
| Status code | `401 UNAUTHORIZED` |
| Content-Type | `application/json` |
| Location header | Not applicable / no redirect recorded |
| Expected behaviour | The dashboard API should reject requests without an authenticated session. |
| Actual result | The server returned an authentication error. |
| Test result | Pass — consistent with expected behaviour. |

**Request:**

```bash
curl -i http://127.0.0.1:5000/api/dashboard
```

**Actual response body:**

```json
{
  "error": "authentication required"
}
```

**Finding:** The dashboard endpoint rejected unauthenticated access as expected.

---

### API-005: Login with Valid Credentials

| Field | Observed result |
|---|---|
| HTTP method | POST |
| Endpoint | `/api/login` |
| Status code | `200 OK` |
| Content-Type | `application/json` |
| Location header | Not applicable / no redirect recorded |
| Expected behaviour | Valid credentials should authenticate the user and return user information. |
| Actual result | The server returned the user's ID and username in JSON. A session was established for subsequent authenticated requests. |
| Test result | Pass — consistent with expected behaviour. |

**Request:**

```bash
curl -i \
  -H "Content-Type: application/json" \
  -d '{"username":"<valid_test_username>","password":"<valid_test_password>"}' \
  http://127.0.0.1:5000/api/login
```

**Actual response body:**

```json
{
  "id": 1,
  "username": "Siti"
}
```

**Finding:** The login endpoint accepted the valid test credentials and returned user information. Credentials and session-cookie values are omitted from this report.

---

### API-006: Retrieve Tasks Before Creating a Test Task

| Field | Observed result |
|---|---|
| HTTP method | GET |
| Endpoint | `/api/tasks` |
| Status code | `200 OK` |
| Content-Type | `application/json` |
| Location header | Not applicable / no redirect recorded |
| Expected behaviour | An authenticated request should return the current task list. If no tasks exist for the test state, the response should be an empty array. |
| Actual result | The server returned an empty JSON array. |
| Test result | Pass — consistent with the observed test state. |

**Request:**

```bash
curl -i -b own_cookies.txt \
  http://127.0.0.1:5000/api/tasks
```

**Actual response body:**

```json
[]
```

**Finding:** The authenticated task-list endpoint returned an empty array before the test task was created.

---

### API-007: Create a Task with Valid Data

| Field | Observed result |
|---|---|
| HTTP method | POST |
| Endpoint | `/api/tasks` |
| Status code | `201 CREATED` |
| Content-Type | `application/json` |
| Location header | Not recorded |
| Expected behaviour | The server should create a task from valid input and return the created task's information. |
| Actual result | The server created task ID `5` with the submitted title, description, category, and due date. |
| Test result | Pass — consistent with expected behaviour. |

**Request:**

```bash
curl -i -b own_cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"title":"API Test Task","description":"Testing task creation through the API","category_id":1,"due_date":"2026-12-31"}' \
  http://127.0.0.1:5000/api/tasks
```

**Actual response:** `201 CREATED`. The response contained the created task, including task ID `5`, title `API Test Task`, category `Work`, due date `2026-12-31`, and `done: false`.

**Finding:** The endpoint successfully created a task using valid JSON data.

---

### API-008: Retrieve the Task List After Creation

| Field | Observed result |
|---|---|
| HTTP method | GET |
| Endpoint | `/api/tasks` |
| Status code | `200 OK` |
| Content-Type | `application/json` |
| Location header | Not applicable / no redirect recorded |
| Expected behaviour | The newly created task should appear in the authenticated task list. |
| Actual result | Task ID `5` appeared in the response. |
| Test result | Pass — consistent with expected behaviour. |

**Request:**

```bash
curl -i -b own_cookies.txt \
  http://127.0.0.1:5000/api/tasks
```

**Actual response:** `200 OK`. The JSON array included task ID `5`, titled `API Test Task`.

**Finding:** The newly created task was available through the task-list endpoint, confirming that the creation was reflected in subsequent API retrieval.

---

### API-009: Retrieve a Task by ID

| Field | Observed result |
|---|---|
| HTTP method | GET |
| Endpoint | `/api/tasks/5` |
| Status code | `200 OK` |
| Content-Type | `application/json` |
| Location header | Not applicable / no redirect recorded |
| Expected behaviour | The endpoint should return the details of an existing task when a valid task ID is supplied. |
| Actual result | The server returned the details of task ID `5`. |
| Test result | Pass — consistent with expected behaviour. |

**Request:**

```bash
curl -i -b own_cookies.txt \
  http://127.0.0.1:5000/api/tasks/5
```

**Actual response:** `200 OK`. The response contained the details of task ID `5`.

**Finding:** The endpoint successfully retrieved the existing task by ID.

---

### API-010: Update an Existing Task

| Field | Observed result |
|---|---|
| HTTP method | PUT |
| Endpoint | `/api/tasks/5` |
| Status code | `200 OK` |
| Content-Type | `application/json` |
| Location header | Not applicable / no redirect recorded |
| Expected behaviour | The server should update the supplied task field and return the updated task details. |
| Actual result | The task description changed to `Updated through API for verification`. Other task fields remained present in the response. |
| Test result | Pass — consistent with expected behaviour. |

**Request:**

```bash
curl -i -X PUT -b own_cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"description":"Updated through API for verification"}' \
  http://127.0.0.1:5000/api/tasks/5
```

**Actual response:** `200 OK`. The returned task contained the updated description.

**Finding:** The update endpoint successfully updated the task description. This result confirms the API response; a separate UI check of the updated description was not recorded.

---

### API-011: Create a Task Without a Title

| Field | Observed result |
|---|---|
| HTTP method | POST |
| Endpoint | `/api/tasks` |
| Status code | `400 BAD REQUEST` |
| Content-Type | `application/json` |
| Location header | Not applicable / no redirect recorded |
| Expected behaviour | The server should reject a task-creation request when the required title field is missing. |
| Actual result | The server returned a validation error stating that the title is required. |
| Test result | Pass — consistent with expected behaviour. |

**Request:**

```bash
curl -i -b own_cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"description":"Task without a title"}' \
  http://127.0.0.1:5000/api/tasks
```

**Actual response body:**

```json
{
  "error": "title is required"
}
```

**Finding:** The server correctly rejected the request because the required title field was missing.

---

### API-012: Filter Tasks by Category

| Field | Observed result |
|---|---|
| HTTP method | GET |
| Endpoint | `/api/tasks?category=Work` |
| Status code | `200 OK` |
| Content-Type | `application/json` |
| Location header | Not applicable / no redirect recorded |
| Expected behaviour | The endpoint should return tasks matching the specified category. |
| Actual result | The response contained a task in the `Work` category. |
| Test result | Pass — consistent with expected behaviour. |

**Request:**

```bash
curl -i -b own_cookies.txt \
  "http://127.0.0.1:5000/api/tasks?category=Work"
```

**Actual response:** `200 OK`. The returned task list included the matching Work-category task and its updated description.

**Finding:** The category filter returned matching task data for the Work category.

---

### API-013: Create a Task with a Numeric Title

| Field | Observed result |
|---|---|
| HTTP method | POST |
| Endpoint | `/api/tasks` |
| Status code | `500 INTERNAL SERVER ERROR` |
| Content-Type | Not recorded in the saved notes |
| Location header | Not applicable / no redirect recorded |
| Expected behaviour | The server should validate the title's data type and return a controlled client error, preferably `400 BAD REQUEST`, rather than raising an internal server error. |
| Actual result | The server raised an attribute error when attempting to call `.strip()` on the integer `123`. |
| Test result | Fail — confirmed defect. |

**Request:**

```bash
curl -i -b own_cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"title":123,"description":"Testing invalid title type"}' \
  http://127.0.0.1:5000/api/tasks
```

**Actual response:** `500 INTERNAL SERVER ERROR`. The observed error indicated that the integer title did not support the `.strip()` method.

**Finding:** The endpoint did not safely handle an incorrectly typed title. It should validate the input type before performing string operations and return a controlled JSON validation error.

**Defect ID:** `DEF-API-001`

**Severity:** Moderate — proposed.  
**Priority:** Medium — proposed.  
**Status:** Open / observed.

---

### API-014: Create a Task with an Empty Title

| Field | Observed result |
|---|---|
| HTTP method | POST |
| Endpoint | `/api/tasks` |
| Status code | `400 BAD REQUEST` |
| Content-Type | `application/json` |
| Location header | Not applicable / no redirect recorded |
| Expected behaviour | The server should reject a task when its title is an empty string. |
| Actual result | The server returned the `title is required` validation message. |
| Test result | Pass — consistent with expected behaviour. |

**Request:**

```bash
curl -i -b own_cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"title":"","description":"Testing empty title"}' \
  http://127.0.0.1:5000/api/tasks
```

**Actual response body:**

```json
{
  "error": "title is required"
}
```

**Finding:** The server correctly rejected an empty task title with `400 BAD REQUEST`.

---

### API-015: Retrieve the First Pagination Page

| Field | Observed result |
|---|---|
| HTTP method | GET |
| Endpoint | `/api/tasks?page=0&per_page=1` |
| Status code | `200 OK` |
| Content-Type | `application/json` |
| Location header | Not applicable / no redirect recorded |
| Expected behaviour | With zero-based pagination and a page size of one, page `0` should return the first task in the ordered result set. |
| Actual result | The response returned task ID `7`. |
| Test result | Pass — consistent with the observed pagination implementation. |

**Request:**

```bash
curl -i -b own_cookies.txt \
  "http://127.0.0.1:5000/api/tasks?page=0&per_page=1"
```

**Actual response:** `200 OK`. The response contained task ID `7`, titled `Pagination Test B`.

**Finding:** Page `0` returned one task as expected. The endpoint uses zero-based pagination.

---

### API-016: Retrieve the Second Pagination Page

| Field | Observed result |
|---|---|
| HTTP method | GET |
| Endpoint | `/api/tasks?page=1&per_page=1` |
| Status code | `200 OK` |
| Content-Type | `application/json` |
| Location header | Not applicable / no redirect recorded |
| Expected behaviour | With zero-based pagination and a page size of one, page `1` should return the next task after page `0`. |
| Actual result | The response returned task ID `6`. |
| Test result | Pass — consistent with the observed pagination implementation. |

**Request:**

```bash
curl -i -b own_cookies.txt \
  "http://127.0.0.1:5000/api/tasks?page=1&per_page=1"
```

**Actual response:** `200 OK`. The response contained task ID `6`, titled `Pagination Test A`.

**Finding:** Page `1` returned the next task after page `0`. No pagination defect was observed in these two checks.

---

### API-017: Delete an Existing Task

| Field | Observed result |
|---|---|
| HTTP method | DELETE |
| Endpoint | `/api/tasks/5` |
| Status code | `200 OK` |
| Content-Type | `application/json` |
| Location header | Not applicable / no redirect recorded |
| Expected behaviour | The server should delete the specified existing task and return a successful result. |
| Actual result | The server returned `{"result":"ok"}`. |
| Test result | Pass — consistent with expected behaviour. |

**Request:**

```bash
curl -i -X DELETE -b own_cookies.txt \
  http://127.0.0.1:5000/api/tasks/5
```

**Actual response body:**

```json
{
  "result": "ok"
}
```

**Finding:** The server reported successful deletion of task ID `5`.

---

### API-018: Retrieve a Task After Deletion

| Field | Observed result |
|---|---|
| HTTP method | GET |
| Endpoint | `/api/tasks/5` |
| Status code | `404 NOT FOUND` |
| Content-Type | `application/json` |
| Location header | Not applicable / no redirect recorded |
| Expected behaviour | A deleted task should no longer be retrievable and should return a not-found response. |
| Actual result | The server returned a not-found error. |
| Test result | Pass — consistent with expected behaviour. |

**Request:**

```bash
curl -i -b own_cookies.txt \
  http://127.0.0.1:5000/api/tasks/5
```

**Actual response body:**

```json
{
  "error": "not found"
}
```

**Finding:** The deleted task was no longer available through the task-detail endpoint. The `404 NOT FOUND` response matched the expected post-condition.

---

### API-019: Login with Invalid Credentials

| Field | Observed result |
|---|---|
| HTTP method | POST |
| Endpoint | `/api/login` |
| Status code | `401 UNAUTHORIZED` |
| Content-Type | `application/json` |
| Location header | Not applicable / no redirect recorded |
| Expected behaviour | The server should reject invalid credentials and return an authentication error. |
| Actual result | The server returned `invalid credentials`. |
| Test result | Pass — consistent with expected behaviour. |

**Request:**

```bash
curl -i \
  -H "Content-Type: application/json" \
  -d '{"username":"invalid_test_user","password":"wrong_password"}' \
  http://127.0.0.1:5000/api/login
```

**Actual response body:**

```json
{
  "error": "invalid credentials"
}
```

**Finding:** The server rejected the invalid login credentials with `401 UNAUTHORIZED`. No successful authentication was reported.

---

### API-020: Login Request with a Missing Password

| Field | Observed result |
|---|---|
| HTTP method | POST |
| Endpoint | `/api/login` |
| Status code | `401 UNAUTHORIZED` |
| Content-Type | `application/json` |
| Location header | Not applicable / no redirect recorded |
| Expected behaviour | The server should reject a login request when the password is missing and should not authenticate the user. |
| Actual result | The server returned `invalid credentials`. |
| Test result | Pass — request rejected as expected. |

**Request:**

```bash
curl -i \
  -H "Content-Type: application/json" \
  -d '{"username":"invalid_test_user"}' \
  http://127.0.0.1:5000/api/login
```

**Actual response body:**

```json
{
  "error": "invalid credentials"
}
```

**Finding:** The server rejected the request with a missing password using `401 UNAUTHORIZED`. The response was consistent with rejecting an incomplete login request.

---

### API-021: Attempt to Create a Task Without Authentication

| Field | Observed result |
|---|---|
| HTTP method | POST |
| Endpoint | `/api/tasks` |
| Status code | `401 UNAUTHORIZED` |
| Content-Type | `application/json` |
| Location header | Not applicable / no redirect recorded |
| Expected behaviour | The server should reject task creation when no authenticated session is supplied. |
| Actual result | The server returned `authentication required`. |
| Test result | Pass — consistent with expected behaviour. |

**Request:**

```bash
curl -i \
  -H "Content-Type: application/json" \
  -d '{"title":"Unauthenticated Test","description":"Should not be created"}' \
  http://127.0.0.1:5000/api/tasks
```

**Actual response body:**

```json
{
  "error": "authentication required"
}
```

**Finding:** The server rejected unauthenticated task creation with `401 UNAUTHORIZED`. The request was not accepted for task creation.

---

## 4. Summary of Findings

| Result | Count |
|---|---:|
| Pass | 19 |
| Fail | 1 |
| Needs Review | 1 |
| **Total** | **21** |

### Confirmed defect

- **DEF-API-001:** A numeric task title causes `500 INTERNAL SERVER ERROR` instead of a controlled validation response.

### Item requiring clarification

- **API-002:** `/api/categories` returns category data without authentication. Confirm whether this endpoint is intended to be public.

### UI/API consistency

A task created through the API was confirmed to appear in the web UI. This provides limited evidence of consistency between the API and interface; it does not establish that all browser workflows have been tested.

## 5. Evidence and Limitations

The evidence consists of actual terminal outputs from HTTP requests to the local PyTodo Pro application. Testing was performed manually using `curl` in GitHub Codespaces.

Passwords and session-cookie values are excluded from the report. The categories endpoint's authentication behaviour remains under investigation. No claim is made that the application is free from defects, and untested behaviour is not presented as a confirmed finding.
