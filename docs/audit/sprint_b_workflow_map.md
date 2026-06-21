# Sprint B: Audit Workflow Map

## 1. Landing Page -> Submit URL
* **Component**: Frontend Landing Page form (React)
* **Action**: User enters URL and Email, submits form.
* **API Call**: `POST /api/v1/audit/request`

## 2. API Endpoint
* **Files Involved**: `app/modules/analysis/router.py`
* **Functions Involved**: `request_page_audit`
* **Action**: Validates the URL payload, then invokes the database model.

## 3. Database Record Creation
* **Files Involved**: `app/modules/analysis/models.py`, `app/modules/analysis/router.py`
* **Database Tables Involved**: `page_audits`
* **Action**: Creates a `PageAudit` record with ID, URL, Email, and sets `status` to `"PENDING"`.

## 4. ARQ Queue
* **Files Involved**: `app/modules/analysis/router.py` (enqueue)
* **Dependencies Involved**: Redis, ARQ (`create_pool`, `enqueue_job`)
* **Action**: Pushes the job `"run_heuristic_audit"` along with `audit_id` to the Redis queue.

## 5. Worker
* **Files Involved**: `workers/run_worker.py`
* **Functions Involved**: `run_heuristic_audit`
* **Action**: The background worker process consumes the job from Redis and executes `AnalysisService.perform_heuristic_audit`.

## 6. Heuristic Audit
* **Files Involved**: `app/modules/analysis/service.py`
* **Functions Involved**: `perform_heuristic_audit`
* **Dependencies Involved**: `httpx` (for crawler), `html.parser.HTMLParser`
* **Action**: Fetches HTML from the target URL, parses tags/meta, and computes schema, structure, stuffing, and semantic scores out of 100.

## 7. Database Update
* **Files Involved**: `app/modules/analysis/service.py`
* **Database Tables Involved**: `page_audits`
* **Action**: Sets `status` to `"RUNNING"`, updates the scores, populates recommendations, and then sets `status` to `"COMPLETED"`.

## 8. Email Generation
* **Files Involved**: `app/modules/analysis/service.py`
* **Functions Involved**: `send_audit_email`
* **Dependencies Involved**: `httpx` (to Resend API)
* **Action**: Sends HTML email report via Resend API, or falls back to writing a local HTML file under `docs/implementation/logs/emails/`.

## 9. Dashboard Retrieval
* **Files Involved**: `app/modules/analysis/router.py` (Assuming an endpoint exists, e.g., `/api/v1/audit/{audit_id}` or similar)
* **Functions Involved**: `get_audit_result` (if implemented)
* **Action**: Frontend polls or requests the completed audit status and displays the recommendations.
