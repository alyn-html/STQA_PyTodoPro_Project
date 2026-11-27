# Security Testing – Defect Log

| Defect ID | Test Case | Defect Description | Expected Result | Actual Result | Severity | Status |
|---|---|---|---|---|---|---|
| DEF-SEC-01 | Cross-User Task Access | The API does not properly enforce task ownership when deleting tasks. | Users should only be able to delete tasks belonging to their own accounts. | A user may be able to delete another user's task using its task ID. | High | Failed |

**Note:** Retain this defect only if the cross-user deletion test successfully demonstrated the issue. Otherwise, mark it as *Needs Verification*.
