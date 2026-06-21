# Codebase Audit Report

This report documents the actual state of the codebase, files, routes, services, models, workers, and tests as of June 20, 2026.

---

## 1. Frontend Subsystem
* **Status**: <span style="color:orange;font-weight:bold;">YELLOW</span>
* **Rationale**: The frontend is a Next.js App Router project utilizing Tailwind CSS and Recharts. While the user-facing pages, interactive dashboard, citations viewer, recommendations manager, and mock portal logs are fully built and integrate with the backend API endpoints, there are no automated tests (unit, integration, or E2E) defined in the `frontend` directory.

### Existing Files
* **Routing Pages**:
  * [landing page](file:///e:/Profound-cloning/frontend/src/app/page.tsx)
  * [login page](file:///e:/Profound-cloning/frontend/src/app/login/page.tsx)
  * [dashboard home](file:///e:/Profound-cloning/frontend/src/app/(dashboard)/dashboard/page.tsx)
  * [prompts page](file:///e:/Profound-cloning/frontend/src/app/(dashboard)/prompts/page.tsx)
  * [recommendations page](file:///e:/Profound-cloning/frontend/src/app/(dashboard)/recommendations/page.tsx)
  * [citations page](file:///e:/Profound-cloning/frontend/src/app/(dashboard)/citations/page.tsx)
  * [explorer page](file:///e:/Profound-cloning/frontend/src/app/(dashboard)/explorer/page.tsx)
  * [agency page](file:///e:/Profound-cloning/frontend/src/app/(dashboard)/agency/page.tsx)
  * [industry page](file:///e:/Profound-cloning/frontend/src/app/(dashboard)/industry/page.tsx)
  * [inbox page](file:///e:/Profound-cloning/frontend/src/app/(dashboard)/inbox/page.tsx)
  * [search page](file:///e:/Profound-cloning/frontend/src/app/(dashboard)/search/page.tsx)
  * [model page](file:///e:/Profound-cloning/frontend/src/app/(dashboard)/model/page.tsx)
* **Layouts**:
  * [dashboard root layout](file:///e:/Profound-cloning/frontend/src/app/(dashboard)/layout.tsx)
  * [dashboard sidebar component](file:///e:/Profound-cloning/frontend/src/components/layout/Sidebar.tsx)
  * [dashboard topbar component](file:///e:/Profound-cloning/frontend/src/components/layout/Topbar.tsx)
* **State Stores (Zustand)**:
  * [geoStore.ts](file:///e:/Profound-cloning/frontend/src/store/geoStore.ts)
  * [workspaceStore.ts](file:///e:/Profound-cloning/frontend/src/store/workspaceStore.ts)
* **Configuration**:
  * [package.json](file:///e:/Profound-cloning/frontend/package.json)
  * [tsconfig.json](file:///e:/Profound-cloning/frontend/tsconfig.json)

### Existing Routes (Next.js client-side)
* `/` — Public Landing Page & Free GEO Auditor Request
* `/login` — Login Screen (JWT Token retrieval)
* `/dashboard` — Visibility score trend and brand rankings
* `/prompts` — Prompt list configuration & model triggering
* `/recommendations` — Rule-based and LLM-powered recommendations lists
* `/citations` — Citation domain authority and impact tracker
* `/explorer` — Conversation Explorer and topic graphs
* `/agency` — Agency client organization lists
* `/industry` — Market vertical baseline rankings
* `/inbox` — Alert notifications

### Existing Services / API Client
* **API functions in [api.ts](file:///e:/Profound-cloning/frontend/src/lib/api.ts)**:
  * `login()`: Sign in user and retrieve access token.
  * `requestAudit()`: Trigger free auditor crawl over target page.
  * `fetchVisibility()`: Load visibility overview metrics.
  * `fetchCitations()`: Load citation sources.
  * `fetchExplorerData()`: Load topic frequency explorer.
  * `fetchRecommendations()`: Retrieve actionable recommendations.
  * `createPrompts()`: Bulk submit tracking prompts.
  * `triggerRun()`: Queue prompt runs on active models.
  * `generateRecommendations()`: Trigger local rule-based generation.
  * `generateAdvancedRecommendations()`: Trigger remote LLM-based analysis.
  * `updateRecommendationStatus()`: Resolve or ignore items.
  * `checkHealth()`: Check API state.

### Existing Models & Workers
* *None (Client-side app only).*

### Existing Tests
* *None.*

---

## 2. Backend Subsystem
* **Status**: <span style="color:green;font-weight:bold;">GREEN</span>
* **Rationale**: The backend is a clean, modular FastAPI codebase. It provides robust database models, transaction routing, API schemas, LiteLLM integrations, rate limiting, and an extensive test suite.

### Existing Files
* **Application Core**:
  * [main.py](file:///e:/Profound-cloning/backend/app/main.py)
  * [core/config.py](file:///e:/Profound-cloning/backend/app/core/config.py)
  * [core/database.py](file:///e:/Profound-cloning/backend/app/core/database.py)
  * [core/security.py](file:///e:/Profound-cloning/backend/app/core/security.py)
  * [core/llm.py](file:///e:/Profound-cloning/backend/app/core/llm.py)
  * [core/rate_limit.py](file:///e:/Profound-cloning/backend/app/core/rate_limit.py)
* **Sub-Modules**:
  * `app/modules/workspaces/` (router, models, schemas, service)
  * `app/modules/prompts/` (router, models, schemas, service)
  * `app/modules/analysis/` (router, models, schemas, service)
  * `app/modules/recommendations/` (router, models, schemas, service)
  * `app/modules/agency/` (router, models, schemas, service)

### Existing Routes (FastAPI endpoints)
* `POST /api/v1/workspaces/token` — Authenticates user, issues JWT token
* `POST /api/v1/workspaces/sync` — Synchronizes user company/tenant structure
* `POST /api/v1/workspaces` — Creates a new workspace
* `POST /api/v1/workspaces/projects` — Creates brand tracking projects
* `POST /api/v1/workspaces/brands` — Creates tracking brands
* `POST /api/v1/workspaces/competitors` — Creates brand competitors
* `GET /api/v1/prompts` — Lists tracking prompts for a project
* `POST /api/v1/prompts` — Adds prompts in batch
* `POST /api/v1/prompts/run` — Enqueues prompt runs across active models (Rate limited)
* `GET /api/v1/analytics/visibility` — Compiles visibility trends & baseline rankings
* `GET /api/v1/analytics/citations` — Lists top cited domains & visibility gains
* `GET /api/v1/analytics/explorer` — Serves local semantic topic clustering data
* `POST /api/v1/audit/request` — Receives and queues public page audits
* `GET /api/v1/recommendations` — Lists recommendations
* `POST /api/v1/recommendations/generate` — Computes rule-based recommendations locally
* `POST /api/v1/recommendations/advanced` — Triggers LLM strategic analysis (Rate limited)
* `PATCH /api/v1/recommendations/{rec_id}/status` — Updates item status
* `GET /api/v1/agency/profile` — Retrieves agency profile metrics
* `GET /api/v1/agency/clients` — Lists clients under agency organization
* `POST /api/v1/agency/clients` — Adds a client organization
* `GET /health` — Simple database / service status ping

### Existing Services
* `WorkspaceService` — Manages tenant sync, org mapping, and brand creation.
* `PromptService` — Handles prompt generation, model updates, and background run queuing.
* `AnalysisService` — Executes heuristic crawler parsing, keyword stuffing checks, citation extraction, visibility calculations, and email reports.
* `RecommendationService` — Compiles rule-based suggestions and calls LiteLLM for strategic insights.
* `AgencyService` — Governs agency tenant configuration.

### Existing Models (SQLAlchemy Declarative)
* `User`, `Organization`, `Workspace`, `Project`, `Brand`, `Competitor`
* `AIModel`, `Prompt`, `PromptRun`
* `Domain`, `CitationSource`, `Response`, `Citation`, `TopicCluster`, `Topic`, `Industry`, `IndustryRanking`, `VisibilityScore`, `VisibilityHistory`, `ShareOfVoice`, `PageAudit`
* `Agency`, `Client`, `Report`, `Notification`, `AuditLog`
* `Recommendation`, `RecommendationAction`

### Existing Workers
* *None directly on FastAPI (routed to workers subsystem).*

### Existing Tests
* **Pytest Suite (`backend/tests/`)**:
  * `test_analysis.py` — Link extraction & base domain validation
  * `test_audit_api.py` — Audit submission router integration
  * `test_auth.py` — Login token generation and verification
  * `test_geo_algorithms.py` — Sentiment, weights, DA, citation, SOV, and visibility formula benchmarks
  * `test_heuristic_auditor.py` — Crawl parser and keyword stuffing mock evaluations
  * `test_readiness_fixes.py` — Rate-limiting bypass and daily scanner scheduling
  * `test_recommendations.py` — Hybrid engine rules verification

---

## 3. Background Workers Subsystem
* **Status**: <span style="color:green;font-weight:bold;">GREEN</span>
* **Rationale**: The asynchronous workers are implemented using the lightweight `arq` queue on top of Redis. Task execution pipelines are structured cleanly and are easy to execute.

### Existing Files
* [run_worker.py](file:///e:/Profound-cloning/backend/workers/run_worker.py) — Defines worker runner daemon and configurations.

### Existing Workers / Tasks
* `run_prompt_execution`: Executes prompt calls via LiteLLM and updates database metrics.
* `run_batch_visibility_update`: Recalculates metrics for a project across all models.
* `run_recommendation_generation`: Triggers rule-based updates.
* `run_heuristic_audit`: Processes crawler audits and fires email report cards.
* `scheduled_daily_scan`: Runs a cron job that triggers active scans daily.

### Existing Tests
* Mock verification is included inside the pytest suite (`test_heuristic_auditor.py` and `test_audit_api.py` patch and mock ARQ enqueues).

---

## 4. Database Subsystem
* **Status**: <span style="color:green;font-weight:bold;">GREEN</span>
* **Rationale**: Fully database-agnostic through SQLAlchemy async engine. It connects to a Postgres instance by default, and falls back gracefully to a local SQLite database (`geo_db.sqlite`) if Postgres is unreachable. Migrations are managed by Alembic.

### Existing Files
* [core/database.py](file:///e:/Profound-cloning/backend/app/core/database.py) — Database sessions and connections.
* [seed.py](file:///e:/Profound-cloning/backend/seed.py) — Seeds default records for local developer setups.
* `alembic/` & `alembic.ini` — Database migration folders.
* [geo_db.sqlite](file:///e:/Profound-cloning/backend/geo_db.sqlite) — Active local SQLite datastore.

### Existing Models & Migrations
* All SQLAlchemy models are mapped.
* Alembic tracking records migrations (e.g., `upgrade 95a121bf2361 -> a6a121bf2362` adding `page_audits`).

---

## 5. Infrastructure
* **Status**: <span style="color:orange;font-weight:bold;">YELLOW</span>
* **Rationale**: The infrastructure files contain a Docker blueprint for the backend API server. However, there are no Docker compose setup configurations, Kubernetes configurations, or configuration pipelines for Redis/Postgres infrastructure.

### Existing Files
* [Dockerfile](file:///e:/Profound-cloning/backend/Dockerfile) — Backend FastAPI Docker container setup.
