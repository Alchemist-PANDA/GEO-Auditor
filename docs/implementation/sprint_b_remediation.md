# Sprint B Remediation Plan

## Root Causes Identified
1. **Missing Retrieval Endpoint**: There is no API endpoint (e.g., `GET /api/v1/audit/{audit_id}`) for the dashboard to retrieve the completed audit results. The router only contains `POST /api/v1/audit/request`.
2. **Queue Unavailability Causes HTTP 500**: If the ARQ Redis queue is unavailable, the user receives an unhandled 500 Internal Server Error when submitting a URL. While this is not a silent failure, it is poor UX and indicates a lack of resilient queueing fallback or proper error messaging.

## Severities
* **Retrieval Endpoint Missing**: **RED / HIGH** (Critical blocking issue; users cannot view results).
* **Queue Unavailability**: **YELLOW / MEDIUM** (Throws 500 rather than gracefully informing the user of service disruption).

## Files Affected
* `app/modules/analysis/router.py` (Missing GET endpoint, Queue error handling)
* `app/modules/analysis/schemas.py` (Need response schema for full audit data)

## Fix Plan
1. **Implement Audit Retrieval Endpoint**: 
   * Add a `GET /api/v1/audit/{audit_id}` route to `analysis/router.py`.
   * Implement the `get_audit_by_id` logic to fetch the `PageAudit` row by ID, returning status, scores, and recommendations.
2. **Graceful Queue Error Handling**:
   * Catch Redis connection errors and return a `503 Service Unavailable` with a user-friendly message rather than a raw `500`.

## Acceptance Criteria
* `GET /api/v1/audit/{audit_id}` returns a 200 OK with `PageAudit` data if the audit exists, and 404 if not found.
* The frontend or any client can successfully poll the GET endpoint to transition from `PENDING` -> `RUNNING` -> `COMPLETED`.
* Disconnecting Redis results in a 503 instead of a 500 during audit requests.
