# Execution Roadmap

This document outlines the actionable roadmap of engineering tasks required to move the platform from its current state to a hardened production release.

---

## Sprint 1 — Launch Blockers

### Task 1.1: Remove Authentication Gate for Public URL Audits
* **Priority**: P0 (Launch Blocker)
* **Target Files**:
  - `backend/app/modules/analysis/router.py` (Modify `/audit/request` or implement public variant)
  - `frontend/src/app/page.tsx`
* **Dependencies**: None.
* **Estimated Effort**: 4 hours.
* **Expected Outcome**: Anonymous landing page visitors can submit URLs for heuristic auditing.
* **Implementation Plan**:
  1. Create a public API endpoint `/api/v1/audit/public-request` in [analysis/router.py](file:///e:/Profound-cloning/backend/app/modules/analysis/router.py) that does not inject `current_user: UserSession = Depends(get_current_user)`.
  2. Implement IP-based rate limiting on this public route using the existing `RateLimiter` dependency.
  3. Modify the landing page client code [page.tsx](file:///e:/Profound-cloning/frontend/src/app/page.tsx) to target this new public endpoint.

---

## Sprint 2 — Beta Readiness

### Task 2.1: Hide Mock Sub-Pages from Main Navigation
* **Priority**: P1 (Critical)
* **Target Files**:
  - `frontend/src/app/(dashboard)/agency/page.tsx`
  - `frontend/src/app/(dashboard)/inbox/page.tsx`
  - `frontend/src/app/(dashboard)/industry/page.tsx`
  - `frontend/src/app/(dashboard)/model/page.tsx`
  - `frontend/src/app/(dashboard)/search/page.tsx`
* **Dependencies**: None.
* **Estimated Effort**: 2 hours.
* **Expected Outcome**: Users cannot navigate to disconnected mock pages.
* **Implementation Plan**:
  Hide or comment out these routes in the Next.js router or redirect them to `/dashboard` until their backend integrations are fully developed.

### Task 2.2: Restrict CORS Wildcard Origin Configurations
* **Priority**: P1 (Critical)
* **Target Files**:
  - `backend/app/main.py`
  - `backend/app/core/config.py`
* **Dependencies**: None.
* **Estimated Effort**: 2 hours.
* **Expected Outcome**: The API blocks origins not matching authorized domains in production.
* **Implementation Plan**:
  Add `CORS_ORIGINS: list[str] = ["http://localhost:3000"]` to `Settings` in [core/config.py](file:///e:/Profound-cloning/backend/app/core/config.py). Update [main.py](file:///e:/Profound-cloning/backend/app/main.py) to read from this array.

### Task 2.3: Convert Absolute Path Email Logs to Relative Path Workspace Logs
* **Priority**: P1 (Critical)
* **Target Files**:
  - `backend/app/modules/analysis/service.py`
* **Dependencies**: None.
* **Estimated Effort**: 2 hours.
* **Expected Outcome**: Running the crawler in Linux or Docker container will not crash when writing files.
* **Implementation Plan**:
  Update [analysis/service.py:975](file:///e:/Profound-cloning/backend/app/modules/analysis/service.py#L975) to resolve paths using `os.path.join(os.getcwd(), "tmp", "emails")` or similar relative layout inside the workspace.

---

## Sprint 3 — Production Hardening

### Task 3.1: Add Rate Limiting to Auditing Requests
* **Priority**: P2 (Important)
* **Target Files**:
  - `backend/app/modules/analysis/router.py`
* **Dependencies**: None.
* **Estimated Effort**: 2 hours.
* **Expected Outcome**: Multiple rapid submissions from the same IP yield HTTP `429 Too Many Requests`.
* **Implementation Plan**:
  Apply `Depends(RateLimiter(2, 3600))` to `/audit/public-request` to prevent abuse.

### Task 3.2: Strict JWT Secret Validation
* **Priority**: P2 (Important)
* **Target Files**:
  - `backend/app/core/config.py`
  - `backend/app/main.py`
* **Dependencies**: None.
* **Estimated Effort**: 1 hour.
* **Expected Outcome**: App refuses to boot if configuration is insecure in production.
* **Implementation Plan**:
  Add validation in `main.py` startup events to ensure `SUPABASE_JWT_SECRET` does not match the default placeholder if `ENVIRONMENT == "production"`.
