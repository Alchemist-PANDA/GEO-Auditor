# MSP Phase 1 Implementation Tasks

This document maps all Phase 1 Minimum Sellable Product (MSP) tasks. Tasks are ordered strictly by dependency.

---

## 1. Database Tasks (DB)

These tasks must be executed first to establish storage dependencies for all backend and worker systems.

- [ ] **DB-1: Initialize PostgreSQL Migrations Pipeline**
  - Setup migration utility (e.g., Alembic / SQL scripts repository) to track schema changes.
- [ ] **DB-2: Migration 001 - Tenancy & Core Entities**
  - Create tables: `clients`, `workspaces`, `brands`, `brand_competitors`.
- [ ] **DB-3: Migration 002 - Prompts & Model Runs**
  - Create tables: `prompts`, `runs`.
- [ ] **DB-4: Migration 003 - Extracted Mentions & Citations**
  - Create tables: `extracted_mentions`, `citations`, `domain_authority`.
- [ ] **DB-5: Migration 004 - Heuristic Page Audits**
  - Create table: `page_audits` (to store submitted URLs, email addresses, computed scores, signal metrics, and status).
- [ ] **DB-6: Database Seed Script**
  - Build seed scripts to populate a mock client profile, brand, competitors, and default query seeds for local developer sandboxes.

---

## 2. Backend Tasks (BE)

Provides the REST API endpoints and data services queried by the frontend and triggered by the workers.

- [ ] **BE-1: FastAPI Application Boilerplate**
  - Set up directory structures, configure CORS, and deploy unified error handling middleware.
- [ ] **BE-2: Authentication & Token Middleware**
  - Verify workspace API tokens in headers (`Authorization: Bearer <token>`) against database records.
- [ ] **BE-3: Brand & Competitor Management Controller**
  - Endpoint `POST /api/v1/brands` to configure domain and competitors.
- [ ] **BE-4: Prompt Seed Management Controller**
  - Endpoint `POST /api/v1/prompts` to upload target search keywords.
- [ ] **BE-5: Core Scoring & Aggregation Service**
  - Write SQL/ORM queries calculating Visibility scores and Share of Voice percentages from runs.
- [ ] **BE-6: Dashboard Analytics Endpoints**
  - Endpoints `GET /api/v1/dashboard/overview` and `GET /api/v1/dashboard/competitors` returning formatted data payloads.
- [ ] **BE-7: Heuristic Audit Request Controller**
  - Endpoint `POST /api/v1/audit/request` to validate URL structures, insert audit records, and queue parser tasks.
- [ ] **BE-8: Email Dispatch Connector**
  - Integrate a mailing library (SMTP / Resend client wrapper) to dispatch HTML-rendered emails.

---

## 3. Worker Tasks (WK)

Runs the asynchronous processing jobs, query execution loops, and content auditing heuristics.

- [ ] **WK-1: Celery Service Setup**
  - Configure Redis broker connection settings and define task schedules.
- [ ] **WK-2: Active Query Runner Task**
  - Connect Celery task executing target prompts against official OpenAI ChatGPT (with search) and Perplexity APIs.
  - Implement async token buckets (semaphores) to respect vendor rate limits.
  - Store raw responses in local storage buckets and write metadata records in the database.
- [ ] **WK-3: NLP Judge Structured Extractor Task**
  - Celery task feeding raw response texts to `gpt-4o-mini` using the structured JSON extraction prompt.
  - Parse JSON arrays and persist brand mentions and citations records.
- [ ] **WK-4: Crawling & Heuristic Page Audit Task**
  - Crawl submitted URL, parse DOM structures, and evaluate:
    - JSON-LD schemas presence (FAQPage, HowTo).
    - Paragraph structures (identifying direct answers).
    - Heading distribution balances.
    - Keyword stuffing densities.
  - Generate HTML audit reports and dispatch email reports.

---

## 4. Frontend Tasks (FE)

Builds the user views, configuration setups, and analytics dashboards.

- [ ] **FE-1: Next.js Boilerplate & Core Design System**
  - Initialize directory, establish standard vanilla CSS colors/fonts, and build common components (buttons, text inputs, headers).
- [ ] **FE-2: Sign-In View**
  - Secure credential submission form checking API tokens.
- [ ] **FE-3: Brand & Prompts Configuration Wizard**
  - Form inputs to configure domains, list competitors, and upload prompt seeds.
- [ ] **FE-4: Overview Analytics Dashboard**
  - Dashboard panels: Visibility scores grids, SoV comparison bar charts, and cited pages grids.
- [ ] **FE-5: Public Page Audit Submission Portal**
  - Form permitting visitors to submit target URLs and email addresses to trigger audit dispatches.

---

## 5. Testing Tasks (TE)

Verifies the correctness and reliability of the platform prior to deployment.

- [ ] **TE-1: Database Schema Integration Tests**
  - Test constraints, cascading deletions, and uniqueness configurations.
- [ ] **TE-2: Query Runner Mock Unit Tests**
  - Test query loops against mock HTTP model responses, checking concurrency rate limits.
- [ ] **TE-3: NLP Judge Extraction Parser Tests**
  - Verify JSON formatting correctness and check sentiment classification ranges using mock model payloads.
- [ ] **TE-4: Heuristic Auditor Scoring Tests**
  - Verify computed score correctness against mock HTML templates (e.g., check FAQ schema increases, stuffing deductions).
- [ ] **TE-5: REST API Endpoint Integration Tests**
  - Validate response payloads against JSON schemas across all endpoints.
- [ ] **TE-6: End-to-End User Flow Verification**
  - Run Playwright test script validating navigation flow (Login → Setup Wizard → Dashboard Overview).
