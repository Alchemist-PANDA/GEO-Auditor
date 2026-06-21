# Minimum Sellable Product (MSP) Execution Plan

This document defines the execution plan to implement the **Minimum Sellable Product (MSP)** for the GEO/AEO Platform. The goal is to reach a sellable, value-generating GEO Audit Platform in the shortest possible time.

---

## 1. Smallest Product Definition

The MSP is a **GEO Audit & Share of Voice Dashboard**. It provides immediate value to SEO and marketing teams by answering: *Where does my brand stand in AI search answers, who is winning our keywords, and how do we improve our site's citation probability?*

### 1.1 Mapped Scope
* **Active Ingestion**: Executes prompt queries directly via official API endpoints (OpenAI ChatGPT & Perplexity API), bypassing Playwright browser scraping.
* **Visibility & SOV Analytics**: Reports raw brand mention rates, competitor presence rates, and sentiment categories across tracked queries.
* **Heuristic AEO Page Auditor**: Scores a single submitted URL against key on-page SEO/AEO signals (header tags, FAQ schemas, keyword stuffing, and direct answers).
* **Audit PDF/Email**: Renders the audit report inside an HTML email sent to prospects.

---

## 2. Component Scoping Matrix

```
┌────────────────────────────────────────────────────────────────────────┐
│                              MSP SCOPING                               │
├────────────────────────────────────────────────────────────────────────┤
│ MANDATORY (MSP Phase)                                                  │
│  - Postgres transactional DB & config schemas                          │
│  - Active query runners (OpenAI/Perplexity API, no proxy pools)        │
│  - NLP Judge text extraction & SQL aggregations                        │
│  - Heuristic page auditor (HTML tag & schema parse)                    │
│  - Dashboard UI (Visibility, SOV leaderboard, Page audit form)         │
│  - HTML email generator                                                │
│                                                                        │
│ DEFERRED (Phase 2 - Core GEO)                                          │
│  - Playwright browser scraping fleets                                  │
│  - ClickHouse telemetry & Qdrant vector spaces                         │
│  - CDN edge log analytics & IP bot verification                        │
│  - LangGraph optimization loop workflows & CMS adapters                │
│                                                                        │
│ DEFERRED (Phase 3 - Enterprise)                                        │
│  - Panel-based search volume discovery & extrapolation                 │
│  - Salesforce/HubSpot ROI revenue attribution                          │
│  - SAML/OIDC SSO & SCIM directory integrations                         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Implementation Sequence

The development sequence is ordered to ensure each component builds on verified, functioning dependencies:

```
Step 1: PostgreSQL Schema ──> Step 2: API Query Runner Worker ──> Step 3: NLP Judge Worker
                                                                          │
                                                                          ▼
Step 6: Dashboard UIs  <──  Step 5: API Endpoints  <──  Step 4: Heuristic Audit Engine
```

1. **Step 1: Database Migration**: Run DDL scripts to provision PostgreSQL.
2. **Step 2: API Query Runner**: Implement the async job query runner executing prompts via OpenAI/Perplexity APIs.
3. **Step 3: NLP judge**: Deploy the extractor worker parsing responses into structured JSON arrays.
4. **Step 4: Heuristic Audit Engine**: Build the page crawling and parsing parser to score URLs.
5. **Step 5: REST API Controller**: Deploy endpoints exposing dashboard analytics, configurations, and audit targets.
6. **Step 6: UI Frontend Pages**: Build the Next.js application screens.
7. **Step 7: Email Client Integration**: Set up email integrations (e.g., Resend/SendGrid) to deliver HTML audits.

---

## 4. PostgreSQL DDL Migrations

Run these tables in a single migration block to initialize the MSP database:

```sql
-- Accounts & Tenancies
CREATE TABLE clients (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name    TEXT NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE workspaces (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id       UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE brands (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    domain          TEXT NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE brand_competitors (
    brand_id        UUID NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    competitor_id   UUID NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    PRIMARY KEY (brand_id, competitor_id)
);

-- Prompts & Active Runs
CREATE TABLE prompts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id        UUID NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    text            TEXT NOT NULL,
    prompt_type     TEXT NOT NULL CHECK (prompt_type IN ('branded', 'unbranded', 'comparison')),
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE runs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prompt_id       UUID NOT NULL REFERENCES prompts(id) ON DELETE CASCADE,
    engine          TEXT NOT NULL CHECK (engine IN ('chatgpt', 'perplexity')),
    raw_text_s3_key TEXT NOT NULL,
    run_at          TIMESTAMPTZ DEFAULT now()
);

-- Parsed Mentions & Citations
CREATE TABLE extracted_mentions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id          UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    entity_name     TEXT NOT NULL,
    entity_type     TEXT NOT NULL CHECK (entity_type IN ('target_brand', 'competitor')),
    sentiment       FLOAT NOT NULL CHECK (sentiment >= -1.0 AND sentiment <= 1.0),
    is_recommended  BOOLEAN DEFAULT FALSE
);

CREATE TABLE citations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id          UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    url             TEXT NOT NULL,
    root_domain     TEXT NOT NULL
);
```

---

## 5. API Endpoints

All endpoints require standard token authentication: `Authorization: Bearer <token>`.

* **`POST /api/v1/brands`**: Configures tracked brands and competitors.
* **`POST /api/v1/prompts`**: Adds prompts to the brand profile.
* **`GET /api/v1/dashboard/overview`**: Returns raw visibility and sentiment percentages:
  ```json
  {
    "brand_name": "Acme",
    "visibility_score": 12.5,
    "sentiment_positive_pct": 78.2,
    "engines": [
      { "engine": "chatgpt", "visibility": 15.0 },
      { "engine": "perplexity", "visibility": 10.0 }
    ]
  }
  ```
* **`GET /api/v1/dashboard/competitors`**: Exposes SoV leaderboard rankings.
* **`POST /api/v1/audit/request`**: Submits a page URL to trigger a heuristic audit and email delivery:
  ```json
  {
    "url": "https://acme.com/blog/running-shoes",
    "email": "user@acme.com"
  }
  ```

---

## 6. Workers Implementation

### 6.1 API Query Runner
Executed daily via Celery schedules:
1. Reads all tracked prompts.
2. Calls model APIs concurrently using HTTP clients with timeout retries (OpenAI API with search enabled, Perplexity search API).
3. Saves raw text response files to local files or storage buckets.
4. Triggers the NLP Judge parser task.

### 6.2 NLP Judge Extractor
Processes raw texts using `gpt-4o-mini`:
1. Submits raw responses with structured system prompt formatting constraints.
2. Extracts JSON data containing mentions and source URLs.
3. Persists parsed entities into `extracted_mentions` and `citations` tables.

### 6.3 Page Auditor
Scores prospect URLs:
1. Crawls the target URL page using standard HTTP request clients.
2. Evaluates elements:
   - Structured JSON-LD schema (FAQ schemas add +20 points).
   - Paragraph structure (+20 points if direct answers exist).
   - Heading checks (+20 points for header tag distributions).
   - Keyword counts (deducts -10 points if stuffing density exceeds 5%).
3. Generates HTML summary template and queues email dispatch.

---

## 7. Mandatory UI Screens

* **Sign-in Screen**: standard login credentials page.
* **Configuration Wizard**: Forms to add brand domains and set target prompt queries.
* **Dashboard Panel**:
  - Top Metrics (Visibility index, Positive sentiment percentage, Top citing domain).
  - SoV Leaderboard (Simple bar charts showing brand vs. competitors).
  - Cited Pages Table (List of URLs cited for tracked prompts).
* **Audit Request Page**: Simple page permitting visitors to submit a URL and email address to trigger audit reports.

---

## 8. Acceptance Criteria

Development is complete when:
1. A configuration payload can be submitted to setup brand profiles.
2. The Celery worker triggers query runner jobs that successfully execute prompts via OpenAI/Perplexity APIs.
3. The NLP judge extracts structured records, populating mentions and citations in PostgreSQL.
4. The Dashboard UI displays Visibility and SoV aggregates computed from PostgreSQL.
5. The public auditor crawled a URL, calculated heuristic scores, generated an HTML report, and successfully delivered it via email.
