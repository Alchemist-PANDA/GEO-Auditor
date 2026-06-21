# MSP Pre-Implementation Gap Analysis & Audit

This document audits the existing repository codebase against the approved Minimum Sellable Product (MSP) specifications. The goal is to maximize code reuse, avoid rebuilding existing features, and isolate missing components.

---

## 1. Subsystem Readiness & Traceability Audit

For every MSP requirement, we classify its state as:
* **GREEN**: Fully implemented.
* **YELLOW**: Partially implemented (needs minor edits, upgrades, or routing alignment).
* **RED**: Missing.

### 1.1 Database Layer (PostgreSQL / SQLite)
* **Status**: <span style="color:green;font-weight:bold;">GREEN</span> (90% Complete)
* **Existing Database Tables**:
  - `organizations` (client tenant orgs)
  - `workspaces` (workspace setups)
  - `projects` (project containers)
  - `brands` (tracked brand entities)
  - `competitors` (competitor domains)
  - `prompts` (tracking search queries)
  - `prompt_runs` (execution runs status)
  - `responses` (raw LLM return texts)
  - `citations` (parsed source citations)
  - `citation_sources` (source URL maps)
  - `domains` (root domains authority ratings)
* **Missing Database Tables**:
  - `page_audits` (to track submitted prospect URLs, computed scores, and email dispatches).
* **Existing Files**:
  - [analysis/models.py](file:///e:/Profound-cloning/backend/app/modules/analysis/models.py)
  - [prompts/models.py](file:///e:/Profound-cloning/backend/app/modules/prompts/models.py)
  - [workspaces/models.py](file:///e:/Profound-cloning/backend/app/modules/workspaces/models.py)

---

### 1.2 Ingestion & Analytics Services
* **Status**: <span style="color:green;font-weight:bold;">GREEN</span> (90% Complete)
* **Description**: The mathematical scoring engines and database rollup routines are fully operational.
* **Calculations Implemented**:
  - Visibility Score (weighting model IDs, positions, and citation parameters: `AnalysisService.update_visibility_metrics`).
  - Share of Voice (SoV) percentages across tracked competitor domains.
  - Citation Impact ratings (evaluating position weights and domain authority).
  - Monthly model weighted blended visibility rollups.
* **Existing Files**:
  - [analysis/service.py](file:///e:/Profound-cloning/backend/app/modules/analysis/service.py)
  - [core/llm.py](file:///e:/Profound-cloning/backend/app/core/llm.py) (LiteLLM query interface with mock fallback strategies).

---

### 1.3 Background Workers
* **Status**: <span style="color:gold;font-weight:bold;">YELLOW</span> (62.5% Complete)
* **Existing Workers**:
  - `run_prompt_execution` (ARQ task running LiteLLM completions).
  - `run_batch_visibility_update` (recalculating visibility scores).
  - `run_recommendation_generation` (runs rules recommendation engine).
  - `scheduled_daily_scan` (ARQ daily scan cron).
* **Existing Files**:
  - [workers/run_worker.py](file:///e:/Profound-cloning/backend/workers/run_worker.py) (ARQ-based Redis worker system).
* **Blockers & Missing Tasks**:
  - **Missing**: The crawling and heuristic page audit worker task is absent.
  - **Missing**: Celery is not used in the repository; the background worker framework is **ARQ** running over Redis. `phase1_tasks.md` must be updated to align worker configurations with **ARQ** instead of Celery.
  - **Adjustment**: The NLP Judge structured extraction currently runs locally via regex string parsers inside `AnalysisService.process_raw_response` rather than a secondary `gpt-4o-mini` JSON call. To optimize latency and API credits for the MSP, the regex parser should remain the primary method, with the LLM-as-judge model added as a validation fallback.

---

### 1.4 REST API Endpoints
* **Status**: <span style="color:gold;font-weight:bold;">YELLOW</span> (75% Complete)
* **Existing API Endpoints**:
  - `POST /api/v1/workspaces` (Create workspace/project).
  - `POST /api/v1/workspaces/brands` (Create brand).
  - `POST /api/v1/workspaces/competitors` (Create competitor).
  - `POST /api/v1/prompts` (GET and POST prompt batches).
  - `POST /api/v1/prompts/run` (Trigger prompts execution runs).
  - `GET /api/v1/analytics/visibility` (Dashboard visibility trends).
  - `GET /api/v1/analytics/citations` (Cited domains/pages tables).
  - `GET /api/v1/recommendations` (Action recommendations).
* **Missing API Endpoints**:
  - `POST /api/v1/audit/request` (Accepting URL/email audits).
* **Existing Files**:
  - [analysis/router.py](file:///e:/Profound-cloning/backend/app/modules/analysis/router.py)
  - [prompts/router.py](file:///e:/Profound-cloning/backend/app/modules/prompts/router.py)
  - [workspaces/router.py](file:///e:/Profound-cloning/backend/app/modules/workspaces/router.py)

---

### 1.5 Frontend Dashboard (Next.js / TypeScript)
* **Status**: <span style="color:gold;font-weight:bold;">YELLOW</span> (60% Complete)
* **Existing UI Pages**:
  - `/dashboard` ([dashboard/page.tsx](file:///e:/Profound-cloning/frontend/src/app/%28dashboard%29/dashboard/page.tsx) rendering visibility charts and brand rankings).
  - `/prompts` (Prompt setup and execution launch console).
  - `/citations` (Citations leaderboard list).
  - `/recommendations` (Action priority checklist page).
* **Missing UI Pages**:
  - **Missing**: Sign-in/Auth screen (currently directly redirects to `/dashboard`).
  - **Missing**: Public Page Auditor crawler submission portal.
  - **Missing**: Streamlined brand onboarding setup wizard.
* **Existing Files**:
  - [frontend/src/app/page.tsx](file:///e:/Profound-cloning/frontend/src/app/page.tsx)
  - [frontend/src/app/(dashboard)/dashboard/page.tsx](file:///e:/Profound-cloning/frontend/src/app/%28dashboard%29/dashboard/page.tsx)
  - [frontend/src/lib/api.ts](file:///e:/Profound-cloning/frontend/src/lib/api.ts)

---

## 2. MSP Completion Indexes

Based on the audit of existing files, routing structures, and background task scripts:

1. **Database Completion**: **90%** (10 tables exist; only `page_audits` is missing).
2. **Backend Completion**: **75%** (Boilerplate, configuration REST APIs, scoring logic, and analytics routers exist; audit controller and mail integrations are missing).
3. **Worker Completion**: **62.5%** (ARQ service, query runners, and regex parsing judges are functional; page-auditing crawler is missing).
4. **Frontend Completion**: **60%** (Next.js layout, visibility pages, and API hooks are functional; login screens and public auditor portal form pages are missing).
5. **Overall MSP Completion**: **72%**

---

## 3. Revised Implementation Sequence (Delta Only)

To reach the launch target in the shortest time, the revised implementation focus is restricted **strictly to missing and partially integrated items**:

```
Step 1: Database DDL ──> Step 2: Heuristic Auditor Service ──> Step 3: API Endpoint
(Create page_audits)      (Crawling & score parser)             (POST /audit/request)
                                                                          │
                                                                          ▼
Step 6: Login Views  <──  Step 5: Public Portal UI  <──  Step 4: Email Dispatcher
(Sign-in page flow)       (Crawling request forms)              (Resend/SMTP hook)
```

### Sprint 1: Audit Engine & Email Dispatcher
* **Database**:
  - Create the `page_audits` schema in PostgreSQL (SQLite for local sandbox testing).
* **Workers**:
  - Add the `page_audit_parser` job in `backend/workers/run_worker.py` (crawls the URL, parses HTML headings/schemas, and computes the heuristic score).
* **Services**:
  - Integrate a simple email dispatcher (Resend client wrapper or SMTP mailer) to construct and send HTML audit reports.

### Sprint 2: API Integration & Frontend Auditor Portal
* **Backend**:
  - Deploy the `POST /api/v1/audit/request` endpoint to accept auditing submissions and queue ARQ tasks.
* **Frontend**:
  - Build the public audit submission portal page (form requesting crawl URL and email address).
  - Connect the client API connector to trigger audit requests.

### Sprint 3: Client Access Controls
* **Frontend**:
  - Create the Sign-in UI login page.
  - Implement access token storage (`localStorage.setItem('auth_token', token)`) to authenticate requests.
