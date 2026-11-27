# Web/API Testing – Defect Log

## A. Confirmed Defects

| Defect ID | Test Case | Defect Description | Expected Result | Actual Result | Severity | Status |
|---|---|---|---|---|---|---|
| DEF-API-01 | API Task Input Validation | Submitting a numeric value as a task title causes a server error. | API should validate the input and return HTTP 400. | API returns HTTP 500 Internal Server Error. | Medium | Failed |

**Explanation:**

The API does not handle the numeric task title correctly. Instead of returning a controlled validation response, it produces an internal server error. This indicates insufficient input validation or error handling and may affect API reliability.

## B. Items Requiring Review

| Review ID | Endpoint / Test Case | Observation | Explanation | Classification |
|---|---|---|---|---|
| API-REV-01 | GET `/api/categories` – Authentication | Endpoint returns HTTP 200 without authentication. | The endpoint allows unauthenticated users to retrieve category information. This is not necessarily a security defect because category data may be intended for public access. However, the application's access-control requirements should be reviewed to confirm whether authentication is required. | Needs Review |

## C. Overall Evaluation

Web/API testing identified one confirmed defect involving improper handling of numeric task-title input. One additional observation involving unauthenticated access to the categories endpoint was recorded for review.

The categories endpoint should not automatically be classified as a defect unless the application's requirements specify that authentication is necessary. This distinction prevents intentional public functionality from being incorrectly reported as a security or API failure.
