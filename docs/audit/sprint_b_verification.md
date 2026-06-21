# Sprint B Verification Report

**Date**: 2026-06-20


## Phase 2 — Runtime Verification


### Step 1: Landing page submission works.
* **Request**: `POST /api/v1/audit/request`
* **Payload**:
```json
{
  "url": "https://example.com",
  "email": "test@example.com"
}
```
* **Status Code**: **500**
* **Response**:
```json
{
  "detail": "Failed to queue background audit task: Timeout connecting to server"
}
```

> **Failure Detected**: Redis connection failed, preventing queueing.

### Step 2: PageAudit record created.
Database record likely rolled back or left in PENDING due to queue failure.

### Step 3: ARQ queue receives job.
FAILED. `ConnectionRefusedError: [WinError 10061]`

### Step 4-7: Worker execution, Email generation, Database Update.
FAILED due to earlier failure.

### Step 8: Dashboard retrieves results.
FAILED. No endpoint (`GET /api/v1/audit/{id}`) exists in the router!

## Phase 3 — Reliability Testing


### 1. Invalid URL
* **Request**: `POST /api/v1/audit/request`
* **Payload**:
```json
{
  "url": "not-a-url",
  "email": "test@example.com"
}
```
* **Status Code**: **400**
* **Response**:
```json
{
  "detail": "URL must start with http:// or https://"
}
```

### 5. Queue unavailable
Tested in Step 1. Result: **500**. Silent failure? No, proper 500 error returned but the system is broken when queue is down.

### 6. Database unavailable
Skipping db unbind test manually, but would result in 500.

## Final Verdict

**C. Audit Workflow Failed**

The workflow fails at Step 3 (Queue Unavailable) and Step 8 (Retrieval Endpoint Missing).