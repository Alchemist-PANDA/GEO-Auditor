# Database Schema & Storage Blueprint

This document details the database architecture, including PostgreSQL (transactional schemas), ClickHouse (analytical time-series), and Qdrant (vector index storage configurations).

---

## 1. PostgreSQL Schema (Transactional Store)

PostgreSQL manages client configurations, tracked brand entities, metadata prompts, agent runs, raw logs pointers, and user workflow actions.

```sql
-- Core Accounts & Brands Taxonomy
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
    domain          TEXT NOT NULL, -- e.g., 'example.com' (root domain)
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- Competitor Mapping Table
CREATE TABLE brand_competitors (
    brand_id        UUID NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    competitor_id   UUID NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    PRIMARY KEY (brand_id, competitor_id),
    CONSTRAINT no_self_competition CHECK (brand_id != competitor_id)
);

-- Topic Clustering Metadata
CREATE TABLE topic_clusters (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id       UUID REFERENCES topic_clusters(id) ON DELETE SET NULL, -- Hierarchical clustering support
    label           TEXT NOT NULL, -- LLM-assigned cluster name
    centroid_vector_id TEXT NOT NULL, -- UUID mapping to vector store payload
    vertical        TEXT NOT NULL, -- Industry sector
    sample_query_ids UUID[] NOT NULL DEFAULT '{}', -- Auditing sample set
    created_at      TIMESTAMPTZ DEFAULT now(),
    last_reclustered_at TIMESTAMPTZ
);

-- Prompt Management
CREATE TABLE prompts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id        UUID NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    text            TEXT NOT NULL,
    prompt_type     TEXT NOT NULL CHECK (prompt_type IN ('branded', 'unbranded', 'comparison')),
    cluster_id      UUID REFERENCES topic_clusters(id) ON DELETE SET NULL,
    prompt_intent_weight FLOAT NOT NULL DEFAULT 1.0, -- Intent multiplier (0.5 to 2.0)
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- Execution Tracking Runs
CREATE TABLE runs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prompt_id       UUID NOT NULL REFERENCES prompts(id) ON DELETE CASCADE,
    engine          TEXT NOT NULL CHECK (engine IN ('chatgpt', 'claude', 'gemini', 'perplexity', 'copilot', 'meta_ai')),
    capture_method  TEXT NOT NULL CHECK (capture_method IN ('api', 'browser_ui')),
    region          TEXT NOT NULL,
    persona         TEXT,
    raw_text_s3_key TEXT NOT NULL, -- Raw response text stored in S3
    dom_snapshot_s3_key TEXT, -- DOM structure file stored in S3
    screenshot_s3_key TEXT, -- Visual screenshot stored in S3
    run_at          TIMESTAMPTZ DEFAULT now()
);

-- NLP Judge Extraction
CREATE TABLE extracted_mentions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id          UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    entity_name     TEXT NOT NULL,
    entity_type     TEXT NOT NULL CHECK (entity_type IN ('target_brand', 'competitor')),
    position_in_text INT, -- Character offset or segment index
    sentiment       FLOAT NOT NULL CHECK (sentiment >= -1.0 AND sentiment <= 1.0),
    is_recommended  BOOLEAN DEFAULT FALSE,
    extractor_model TEXT NOT NULL, -- Tracking extractor performance metrics
    extractor_confidence FLOAT NOT NULL
);

CREATE TABLE citations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id          UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    url             TEXT NOT NULL,
    root_domain     TEXT NOT NULL, -- Extracted eTLD+1 domain
    anchor_text     TEXT,
    position_in_text INT,
    domain_authority_score FLOAT NOT NULL DEFAULT 0.0
);

-- Domain Authority Reference (Refreshed via API feeds or crawlers)
CREATE TABLE domain_authority (
    root_domain     TEXT PRIMARY KEY,
    authority_score FLOAT NOT NULL CHECK (authority_score >= 0.0 AND authority_score <= 100.0),
    last_recrawled_at TIMESTAMPTZ DEFAULT now()
);

-- Actions Center Workflow Tasks
CREATE TABLE actions (
    action_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id        UUID NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    action_type     TEXT NOT NULL CHECK (action_type IN ('outreach', 'reddit', 'content_creation', 'content_optimization')),
    status          TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'complete', 'skipped')),
    priority_score  FLOAT NOT NULL, -- Computed GapScore
    generated_at    TIMESTAMPTZ DEFAULT now(),
    assigned_to     UUID, -- User ID mapping (RBAC support)
    completed_at    TIMESTAMPTZ,
    gap_cluster_id  UUID REFERENCES topic_clusters(id) ON DELETE SET NULL,
    target_domain   TEXT, -- Population for 'outreach' action
    target_url      TEXT, -- Population for 'content_optimization' action
    brief_content   JSONB -- Content outlines, outline briefs, and factual sources
);
```

---

## 2. ClickHouse Schema (Analytical Time-Series Store)

ClickHouse handles raw high-volume datasets, log-forwarder telemetry streams, and analytical aggregates.

```sql
-- Client Bot Logs Telemetry
CREATE TABLE crawler_events
(
    client_site_id   UUID,
    timestamp        DateTime,
    path              String,
    bot_family        LowCardinality(String),    -- 'GPTBot', 'ClaudeBot', 'PerplexityBot', etc.
    bot_purpose       LowCardinality(String),     -- 'training' | 'search_index' | 'live_retrieval'
    bot_verified      UInt8,                      -- 0 (No/Unverified) or 1 (Yes/IP Range confirmed)
    source_ip         IPv4,
    response_code     UInt16,
    response_time_ms  UInt32
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (client_site_id, bot_family, timestamp);

-- Daily Rollup of Crawler events
CREATE MATERIALIZED VIEW crawl_frequency_daily
ENGINE = SummingMergeTree()
ORDER BY (client_site_id, path, bot_family, day)
AS SELECT
    client_site_id, path, bot_family,
    toDate(timestamp) AS day,
    count() AS crawl_count
FROM crawler_events
GROUP BY client_site_id, path, bot_family, day;

-- Panel-Based Extrapolated Volumes
CREATE TABLE prompt_volume_ts
(
    cluster_id       UUID,
    engine            LowCardinality(String),
    region            LowCardinality(String),
    date              Date,
    panel_count       UInt32,
    estimated_volume  UInt64,
    ci_low            UInt64,
    ci_high           UInt64,
    is_synthetic_pct  Float32
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (cluster_id, engine, region, date);

-- Daily Metric Rollups for Share of Voice
CREATE TABLE share_of_voice_ts
(
    brand_id        UUID,
    competitor_id   Nullable(UUID),
    engine          LowCardinality(String),
    cluster_id      UUID,
    date            Date,
    sov_pct         Float32,
    sentiment_avg   Float32,
    citation_authority_avg Float32,
    sample_size     UInt32
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (brand_id, engine, cluster_id, date);
```

---

## 3. Qdrant Collection (Vector Space Configuration)

Vector configurations for embedding text queries (using `text-embedding-3-large` or equivalent model, size `1536`).

```python
COLLECTION_CONFIG = {
    "collection_name": "query_embeddings",
    "vectors_config": {
        "size": 1536,
        "distance": "Cosine"
    },
    "payload_schema": {
        "raw_text_hash":      "Keyword",   -- SHA256 hashed signature of text query (PII scrubbed)
        "engine":              "Keyword",   -- chatgpt | gemini | claude | perplexity
        "region":               "Keyword",   -- US | UK | DE | JP
        "detected_brand_ids":   "Keyword",   -- Arrays of UUID strings matching resolved brands
        "cluster_id":           "Keyword",   -- PostgreSQL cluster foreign key
        "is_synthetic":         "Bool",      -- Synthetic prompt variant identification
        "captured_at":          "Datetime"
    }
}
```

---

## 4. Architectural Summary Table

| Dimension | [CONFIRMED] Findings | [INFERRED] Systems Behavior | [ASSUMPTION] System Limits | [RECOMMENDATION] Optimization |
|---|---|---|---|---|
| **PostgreSQL Partitioning** | Runs require detailed S3 file keys and metadata indexes. | Direct queries against PG for aggregates lead to scale locks. | Aggregate joins over thousands of rows slow dashboard performance. | Keep PostgreSQL for CRUD/Configs; partition `runs` and `citations` by month. |
| **ClickHouse Aggregations** | SOV metrics are computed based on distinct runs per cluster. | Multi-dimensional group-bys (engine, date, cluster) belong in ClickHouse. | Dynamic rollup joins run slower over million-row scales. | Use Materialized Views (`SummingMergeTree` & `AggregatingMergeTree`) in ClickHouse. |
| **Vector DB Moat** | Joint clustering leverages parent prompts + query fan-outs. | Vector payloads map to cluster centroids managed by PostgreSQL. | Qdrant collections run out of memory when caching massive payloads. | Store vectors as 16-bit floats (FP16 quantization) with payload indexes. |
| **GDPR Compliance** | Licensed panel data is double-opt-in, GDPR-compliant. | Raw user chats must have all PII stripped prior to vector embedding. | IP addresses in edge logs count as personal data. | Hash IPs (`SHA256`) in database; clean logs via PII regex filters before queueing. |
