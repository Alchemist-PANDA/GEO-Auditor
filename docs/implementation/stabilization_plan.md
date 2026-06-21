# Product Stabilization Plan

## Sprint A - Authentication & Authorization
**Goal:** Secure the platform's entry points and ensure data isolation.

### Issue 1: Hardcoded Authentication & Plaintext Passwords
- **Root Cause:** `POST /token` uses a hardcoded check `if payload.password != "password123":` and does not query the database. Passwords are not hashed.
- **Files Affected:** `backend/app/modules/workspaces/router.py`, `backend/app/modules/workspaces/schemas.py`, `backend/app/modules/workspaces/models.py`.
- **Severity:** CRITICAL
- **Fix Plan:** Add `passlib` with `bcrypt`. Implement a secure login mechanism that checks the `users` table for the email and verifies the hashed password. Add a basic `/register` endpoint to allow users to sign up securely.
- **Acceptance Criteria:** Users can securely register and log in with hashed passwords. The hardcoded "password123" logic is entirely removed.

### Issue 2: Missing User Records (500 Error on Dashboard)
- **Root Cause:** Logging in with `password123` assigns a JWT, but the user doesn't exist in the database. Subsequent calls requiring the user fail when `user_res.scalar_one()` throws a `NoResultFound` exception.
- **Files Affected:** `backend/app/modules/workspaces/router.py` (`create_workspace` endpoint).
- **Severity:** CRITICAL
- **Fix Plan:** Add logic during registration to ensure a `User` and their parent `Organization` are seeded. Replace `.scalar_one()` with `.scalar_one_or_none()` and return clean 404s/403s instead of 500s.
- **Acceptance Criteria:** A user successfully logging in has an underlying database record, and attempting to fetch missing relations yields a 404 instead of a 500 error.

### Issue 3: Missing IDOR Protection
- **Root Cause:** Analytics endpoints extract `project_id` from the query parameter and fetch data blindly, without verifying if the `current_user` actually belongs to the workspace that owns the project.
- **Files Affected:** `backend/app/modules/analysis/router.py`, `backend/app/modules/analysis/service.py`.
- **Severity:** CRITICAL
- **Fix Plan:** Implement an authorization check that joins `Project -> Workspace -> Organization -> User` to ensure the `current_user` has permission to view the requested `project_id`.
- **Acceptance Criteria:** Users attempting to access `project_id`s that do not belong to their organization receive a 403 Forbidden.

---

## Sprint B - Audit Workflow Reliability
**Goal:** Ensure background tasks run predictably and fail gracefully.

### Issue 1: Redis Dependency Crash
- **Root Cause:** Requesting an audit blindly attempts to connect to Redis. If Redis is down, it raises a raw 500 error, crashing the request.
- **Files Affected:** `backend/app/modules/analysis/router.py` (`request_page_audit` endpoint).
- **Severity:** HIGH
- **Fix Plan:** Add a try/except block around the ARQ enqueue logic. If Redis is unavailable, fallback to synchronously executing the audit logic or cleanly notifying the user of temporary queue unavailability.
- **Acceptance Criteria:** The app does not return a 500 error when Redis is down; it degrades gracefully.

### Issue 2: Endless Worker Retries
- **Root Cause:** Exceptions caught in `run_prompt_execution` update the DB to `FAILED` but then re-raise the exception, causing `arq` to trigger automatic retries for deterministic failures (e.g., bad API keys).
- **Files Affected:** `backend/workers/run_worker.py`.
- **Severity:** MEDIUM
- **Fix Plan:** Catch exceptions, mark the job as `FAILED` in the database, log the error, and return normally instead of re-raising the exception.
- **Acceptance Criteria:** Deterministic failures are logged as `FAILED` once, without triggering redundant `arq` retries.

---

## Sprint C - Customer Onboarding
**Goal:** Ensure the database models correctly align and support the user flow.

### Issue 1: Client Mapping Issue (InvalidRequestError)
- **Root Cause:** In `app.modules.workspaces.models`, the `Workspace` model attempts to create a relationship to `Client`, but the `Client` class is never imported, causing SQLAlchemy initialization to fail.
- **Files Affected:** `backend/app/modules/workspaces/models.py`.
- **Severity:** HIGH
- **Fix Plan:** Add the correct import `from app.modules.agency.models import Client` or resolve the string-based relationship lookup by ensuring models are registered in the correct order.
- **Acceptance Criteria:** The application boots without throwing an `InvalidRequestError` for the `Client` mapper.

### Issue 2: Empty Dashboard
- **Root Cause:** Due to lack of data seeding tied to authenticated users, the frontend dashboard remains empty.
- **Files Affected:** `backend/app/modules/workspaces/router.py`.
- **Severity:** HIGH
- **Fix Plan:** Ensure that the registration flow optionally seeds a default workspace and project so the dashboard has something to show.
- **Acceptance Criteria:** A newly registered user sees a default workspace on their dashboard.

---

## Sprint D - Production Readiness
**Goal:** Secure infrastructure and prepare for scale.

### Issue 1: Open CORS Configuration
- **Root Cause:** `allow_origins=["*"]` is hardcoded.
- **Files Affected:** `backend/app/main.py`.
- **Severity:** HIGH
- **Fix Plan:** Bind `allow_origins` to a setting variable (`settings.CORS_ORIGINS`) and restrict it to trusted frontend URLs.
- **Acceptance Criteria:** The API rejects cross-origin requests from unauthorized domains.

### Issue 2: Missing Rate Limiting
- **Root Cause:** No rate limiting middleware exists, exposing expensive LLM routes to abuse.
- **Files Affected:** `backend/app/main.py`.
- **Severity:** HIGH
- **Fix Plan:** Implement `slowapi` or basic Redis-based rate limiting on sensitive routes (like `/analytics/audit/request`).
- **Acceptance Criteria:** Repeated rapid requests to expensive endpoints return 429 Too Many Requests.

### Issue 3: Insecure JWT Default
- **Root Cause:** `SUPABASE_JWT_SECRET` defaults to an insecure string.
- **Files Affected:** `backend/app/core/config.py`.
- **Severity:** MEDIUM
- **Fix Plan:** Enforce that `SUPABASE_JWT_SECRET` is set in production by removing the default or adding startup validation.
- **Acceptance Criteria:** The app refuses to boot in `production` mode if the JWT secret is the default placeholder.
