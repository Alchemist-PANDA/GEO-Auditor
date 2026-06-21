# End-to-End System Map

This document traces the data flow from the frontend to the backend service, database, worker, and final outputs.

---

## 1. Primary Workflows

### 1.1 User Registration & Default Seeding
```
Frontend: register/page.tsx
  ↓
API: POST /api/v1/workspaces/register
  ↓
Service: WorkspaceService.sync_user (hashes password, inserts structures)
  ↓
Database: Insert records into `users`, `organizations`, `workspaces`, `projects` tables
  ↓
Result: Organization and default workspace/project seeded; user can now login
```

### 1.2 User Login & Session
```
Frontend: login/page.tsx
  ↓
API: POST /api/v1/workspaces/token
  ↓
Service: Verifies password via CryptContext, signs and issues HS256 JWT
  ↓
Database: Read check against `users` table
  ↓
Result: Token stored in localStorage as `auth_token`; redirects to /dashboard
```

### 1.3 Generative Engine Insights Execution (Prompt Runs)
```
Frontend: (dashboard)/prompts/page.tsx (Launch Analysis button)
  ↓
API: POST /api/v1/prompts/run
  ↓
Service: PromptService.trigger_run (Creates run records, enqueues ARQ Redis job)
  ↓
Database: Writes to `prompt_runs` (status: PENDING)
  ↓
Worker: run_prompt_execution (ARQ worker task)
  ↓ [Executes LLM call (LiteLLM) ────> AnalysisService.process_raw_response]
Service: Parses text for mentions, sentiments, and markdown links
  ↓
Database: Writes `responses`, `citations`, `domains`, `citation_sources`, `visibility_scores`, `share_of_voice`
  ↓
Result: Dashboard charts and citations lists populate dynamically with fresh values
```

### 1.4 GEO Page Readiness Audit
```
Frontend: page.tsx (Public portal) / (dashboard)/audits/page.tsx
  ↓
API: POST /api/v1/audit/request
  ↓
Service: Creates audit record, enqueues ARQ Redis job
  ↓
Database: Writes to `page_audits` (status: PENDING)
  ↓
Worker: run_heuristic_audit (ARQ worker task)
  ↓ [Executes crawler ────> AnalysisService.perform_heuristic_audit]
Service: Crawls URL, runs heuristic parses on schemas, headers, word counts
  ↓
Database: Updates `page_audits` (status: COMPLETED/FAILED, stores score & tips)
  ↓
Result: HTML email dispatched via Resend (or local log fallback) and rendered in Audits dashboard
```

---

## 2. Interface Realities (Gaps, Mocks & Unused Elements)

### 2.1 Static Mock / Dead Routes
The following routes are present in the frontend router directories but are **entirely static mockups** with no dynamic backend API hooks:
- **`/agency`** ([agency/page.tsx](file:///e:/Profound-cloning/frontend/src/app/%28dashboard%29/agency/page.tsx)): Displays a static "Premium Feature" card. The backend endpoints inside [agency/router.py](file:///e:/Profound-cloning/backend/app/modules/agency/router.py) (fetching client records, adding client tenants) are completely unused.
- **`/inbox`** ([inbox/page.tsx](file:///e:/Profound-cloning/frontend/src/app/%28dashboard%29/inbox/page.tsx)): Renders static notifications listing mock alerts.
- **`/industry`** ([industry/page.tsx](file:///e:/Profound-cloning/frontend/src/app/%28dashboard%29/industry/page.tsx)): Displays static leaderboard rankings for mock domains.
- **`/model`** ([model/page.tsx](file:///e:/Profound-cloning/frontend/src/app/%28dashboard%29/model/page.tsx)): Displays a hardcoded Radar SVG chart and Line chart comparing LLMs with dummy stats.
- **`/search`** ([search/page.tsx](file:///e:/Profound-cloning/frontend/src/app/%28dashboard%29/search/page.tsx)): Displays mockup list for Search engines.

### 2.2 Broken/Missing Connections
- **Public Audit Submission Failure**: The landing page public form ([page.tsx](file:///e:/Profound-cloning/frontend/src/app/page.tsx)) triggers `requestAudit` without an auth token. However, the backend router `/audit/request` endpoint requires authentication and enforces `payload.email == current_user.email`. This results in a `401 Unauthorized` block on public landing page audit submissions.
- **Mail Host Dependency**: No email SMTP configuration exists, and the Resend API client relies on the `RESEND_API_KEY` environment variable. In local setups, this fails and falls back to writing local HTML files under `docs/implementation/logs/emails`.
