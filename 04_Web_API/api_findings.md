# API Findings: PyTodo Pro

**Tester:** Alya Nabihah (22012109)  
**Test Account:** Siti  
**Date:** 27 October 2026  
**Environment:** GitHub Codespaces, Python 3.14.2, Werkzeug 3.1.9  
**Application:** PyTodo Pro (Flask)  
**Testing Method:** Manual HTTP requests using `curl`

## 1. Objective

The objective of this testing activity is to evaluate the web application's HTTP responses, API authentication controls, login functionality, and task management operations. The testing compares observed results against the application's documented behaviour.

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
| Test result | Consistent with expected behaviour. |

**Request:**

```bash
curl -i http://127.0.0.1:5000/
```

**Actual response:**

```http
HTTP/1.1 302 FOUND
Server: Werkzeug/3.1.9 Python/3.14.2
Date: Tue, 27 Oct 2026 14:07:58 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 199
Location: /login
Vary: Cookie
Connection: close
```

**Finding:** The home page redirected the unauthenticated request to the login page. No defect was observed in this test.

### API-002: Unauthenticated Request to the Categories API

| Field | Observed result |
|---|---|
| HTTP method | GET |
| Endpoint | `/api/categories` |
| Status code | `200 OK` |
| Content-Type | `application/json` |
| Expected behaviour | The README states that API endpoints other than registration and login require session-cookie authentication. |
| Actual result | The endpoint returned category data without a session cookie being explicitly supplied. |
| Test result | Requires further investigation. |

**Request:**

```bash
curl -i http://127.0.0.1:5000/api/categories
```

**Actual response:**

```http
HTTP/1.1 200 OK
Server: Werkzeug/3.1.9 Python/3.14.2
Date: Tue, 27 Oct 2026 14:09:04 GMT
Content-Type: application/json
Content-Length: 174
Connection: close
```

**Actual response body:**

```json
[
  {
    "id": 2,
    "name": "Personal"
  },
  {
    "id": 3,
    "name": "Study"
  },
  {
    "id": 4,
    "name": "Urgent"
  },
  {
    "id": 1,
    "name": "Work"
  }
]
```

**Source-code analysis:** Inspection of `PyTodo-Pro/app.py` showed that the `api_categories()` route does not use the `@login_required_api` decorator, unlike the `/api/tasks` route.

**Finding:** The categories endpoint returned category names and IDs without authentication. This appears inconsistent with the README's documented authentication requirement. Further investigation is needed to confirm whether this endpoint is intentionally public.

**Recommendation:** Confirm the intended access-control requirements. If authentication is required, apply the appropriate control and add a regression test.

### API-003: Unauthenticated Request to the Tasks API

| Field | Observed result |
|---|---|
| HTTP method | GET |
| Endpoint | `/api/tasks` |
| Status code | `401 UNAUTHORIZED` |
| Content-Type | `application/json` |
| Expected behaviour | Unauthenticated requests should be rejected. |
| Actual result | The server returned HTTP 401 and an authentication-required error. |
| Test result | Consistent with expected behaviour. |

**Request:**

```bash
curl -i http://127.0.0.1:5000/api/tasks
```

**Actual response:**

```http
HTTP/1.1 401 UNAUTHORIZED
Server: Werkzeug/3.1.9 Python/3.14.2
Date: Tue, 27 Oct 2026 14:14:40 GMT
Content-Type: application/json
Content-Length: 41
Vary: Cookie
Connection: close
```

**Actual response body:**

```json
{
  "error": "authentication required"
}
```

**Finding:** The tasks endpoint rejected the unauthenticated request with HTTP 401, consistent with the documented authentication requirement.

### API-004: Unauthenticated Request to the Dashboard API

| Field | Observed result |
|---|---|
| HTTP method | GET |
| Endpoint | `/api/dashboard` |
| Status code | `401 UNAUTHORIZED` |
| Content-Type | `application/json` |
| Expected behaviour | Unauthenticated requests should be rejected. |
| Actual result | The server returned HTTP 401 and an authentication-required error. |
| Test result | Consistent with expected behaviour. |

**Request:**

```bash
curl -i http://127.0.0.1:5000/api/dashboard
```

**Actual response:**

```http
HTTP/1.1 401 UNAUTHORIZED
Server: Werkzeug/3.1.9 Python/3.14.2
Date: Tue, 27 Oct 2026 14:15:03 GMT
Content-Type: application/json
Content-Length: 41
Vary: Cookie
Connection: close
```

**Actual response body:**

```json
{
  "error": "authentication required"
}
```

**Finding:** The dashboard API rejected the unauthenticated request with HTTP 401, consistent with the documented authentication requirement.

### API-005: Login Through the API Using Siti's Account

| Field | Observed result |
|---|---|
| HTTP method | POST |
| Endpoint | `/api/login` |
| Status code | `200 OK` |
| Content-Type | `application/json` |
| Username | Siti |
| User ID | `1` |
| Test result | Successful login. |

**Request:**

```bash
curl -i -c own_cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"username":"Siti","password":"[redacted]"}' \
  http://127.0.0.1:5000/api/login
```

**Actual response:**

```http
HTTP/1.1 200 OK
Server: Werkzeug/3.1.9 Python/3.14.2
Date: Tue, 27 Oct 2026 14:42:35 GMT
Content-Type: application/json
Content-Length: 36
Vary: Cookie
Connection: close
```

**Actual response body:**

```json
{
  "id": 1,
  "username": "Siti"
}
```

**Finding:** The API accepted Siti's login credentials and returned the associated user ID and username. A session cookie was saved in `own_cookies.txt` for subsequent authenticated requests.

### API-006: Retrieve Tasks Using Siti's Session

| Field | Observed result |
|---|---|
| HTTP method | GET |
| Endpoint | `/api/tasks` |
| Session | Siti |
| Status code | `200 OK` |
| Content-Type | `application/json` |
| Actual response body | `[]` |
| Test result | Successful request; no tasks returned at the time of this test. |

**Request:**

```bash
curl -i -b own_cookies.txt \
  http://127.0.0.1:5000/api/tasks
```

**Actual response:**

```http
HTTP/1.1 200 OK
Server: Werkzeug/3.1.9 Python/3.14.2
Date: Tue, 27 Oct 2026 14:44:03 GMT
Content-Type: application/json
Content-Length: 3
Vary: Cookie
Connection: close
```

**Actual response body:**

```json
[]
```

**Finding:** Siti's authenticated session was accepted, and the API returned an empty task list before the subsequent task-creation test.

### API-007: Create a Task Using Siti's Session

| Field | Observed result |
|---|---|
| HTTP method | POST |
| Endpoint | `/api/tasks` |
| Session | Siti |
| Status code | `201 CREATED` |
| Content-Type | `application/json` |
| Task title | `API Test Task` |
| Category | Work |
| Due date | `2026-12-31` |
| Task ID | `5` |
| Urgency | Upcoming |
| Test result | Successful task creation. |

**Request:**

```bash
curl -i -b own_cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"title":"API Test Task","description":"Testing task creation through the API","category_id":1,"due_date":"2026-12-31"}' \
  http://127.0.0.1:5000/api/tasks
```

**Actual response:**

```http
HTTP/1.1 201 CREATED
Server: Werkzeug/3.1.9 Python/3.14.2
Date: Tue, 27 Oct 2026 14:45:28 GMT
Content-Type: application/json
Content-Length: 282
Vary: Cookie
Connection: close
```

**Actual response body:**

```json
{
  "category": "Work",
  "category_id": 1,
  "completed_at": null,
  "created_at": "2026-10-27T14:45:28.117833",
  "description": "Testing task creation through the API",
  "done": false,
  "due_date": "2026-12-31",
  "id": 5,
  "title": "API Test Task",
  "urgency": "Upcoming"
}
```

**Finding:** The API successfully created a task under Siti's authenticated session and returned HTTP 201 with the task details. The task was subsequently visible in Siti's web application.

## 4. Summary of Findings

Seven test cases were documented. The home page redirected unauthenticated requests to the login page, while the tasks and dashboard API endpoints rejected unauthenticated requests with HTTP 401. The categories endpoint returned HTTP 200 without a session cookie, which appears inconsistent with the README's authentication statement and requires further investigation.

Siti's API login was successful. The authenticated task-list request initially returned an empty JSON array, and a subsequent task-creation request returned HTTP 201. The newly created task was visible in Siti's web application, confirming that the API operation succeeded under the intended account.

These findings are limited to the requests executed. Additional tests are needed to assess task updates and deletion, input validation, filtering, pagination, error handling, and data isolation.

## 5. Evidence and Limitations

The evidence consists of actual terminal outputs from HTTP requests to the local PyTodo Pro application. Testing was performed manually using `curl` in GitHub Codespaces.

Passwords and session-cookie values are excluded from the report. The categories endpoint's authentication behaviour remains under investigation. No claim is made that the application is free from defects, and untested behaviour is not presented as a confirmed finding.
