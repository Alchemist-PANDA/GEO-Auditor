# Architecture Conformance Report

This report compares the actual implementation in the codebase against the requirements outlined in the architecture documentation under `docs/architecture/`.

---

## 1. System Topology & Infrastructure Conformance

| Requirement | Documented Specification | Codebase Implementation | Status | Evidence |
|---|---|---|---|---|
| **Transactional DB** | PostgreSQL database for configurations, user profiles, actions, and CMS adapters. | SQLAlchemy async engine configured for PostgreSQL, fallback to SQLite. | **IMPLEMENTED** | [database.py](file:///e:/Profound-cloning/backend/app/core/database.py) |
| **Analytical Store** | ClickHouse database cluster for high-volume logs, crawler events, and SOV metrics. | No ClickHouse driver, database configurations, or endpoints exist. | <span style="color:red;font-weight:bold;">MISSING</span> | Grep search for "clickhouse" yielded zero results. |
| **Vector DB** | Qdrant Vector Index Collection for prompt embeddings. | Embedding vectors are stored as `JSON` fields inside standard SQLite/Postgres tables. | <span style="color:red;font-weight:bold;">MISSING</span> | [models.py](file:///e:/Profound-cloning/backend/app/modules/analysis/models.py#L78) |
| **Ingestion Queue** | Message Bus (Kafka/Kinesis) for ingestion spikes and crawler data buffers. | SQLite database transactions and ARQ tasks via Redis. No Kafka/Kinesis. | <span style="color:red;font-weight:bold;">MISSING</span> | Worker settings use Redis. No messaging queue wrappers. |
| **Background Workers** | Celery/Temporal workers for execution loops. | Arq asynchronous worker running tasks via Redis. | **IMPLEMENTED** | [run_worker.py](file:///e:/Profound-cloning/backend/workers/run_worker.py) |
| **Browser Crawlers** | Playwright headless browser fleet with ISP rotating proxy configurations. | Crawler runs via `httpx.AsyncClient` GET requests. No Playwright. | <span style="color:red;font-weight:bold;">MISSING</span> | [service.py](file:///e:/Profound-cloning/backend/app/modules/analysis/service.py#L674) |
| **LLM-as-a-Judge** | LangGraph orchestration loops for automated verification and CMS edits. | Hybrid service utilizing LiteLLM with fallback strategies. No LangGraph. | <span style="color:orange;font-weight:bold;">PARTIALLY IMPLEMENTED</span> | [llm.py](file:///e:/Profound-cloning/backend/app/core/llm.py) |
| **Raw Content Archive** | S3 bucket storage for DOM snapshots and text bodies. | Raw text and parsed HTML stored locally or inside DB tables. No S3. | <span style="color:red;font-weight:bold;">MISSING</span> | Grep search for "boto3" or S3 configurations yielded zero results. |

---

## 2. Database Schema Conformance

The documented relational schema (`docs/architecture/database.md`) differs from the actual SQLAlchemy implementation:

* **Clients & Workspaces Mapping**:
  * **Documented**: `clients` -> `workspaces` -> `brands` (1-to-1 table relations).
  * **Codebase**: `organizations` -> `users` -> `workspaces` -> `projects` -> `brands` -> `competitors`.
  * **Status**: <span style="color:orange;font-weight:bold;">PARTIALLY IMPLEMENTED</span> (The codebase introduces users and projects as intermediate layers to improve agency management structure).
* **Competitor Mapping Table**:
  * **Documented**: A junction table `brand_competitors`.
  * **Codebase**: A flat model table `competitors` where each row has a foreign key `brand_id`.
  * **Status**: <span style="color:orange;font-weight:bold;">PARTIALLY IMPLEMENTED</span>.
* **Extracted Mentions & Runs**:
  * **Documented**: Tables `runs` (referencing S3 bucket keys) and `extracted_mentions`.
  * **Codebase**: Swapped for `responses` (storing raw response text) and `prompt_runs`. Mentions are computed dynamically inside visibility methods.
  * **Status**: <span style="color:orange;font-weight:bold;">PARTIALLY IMPLEMENTED</span>.
* **Topic Clustering**:
  * **Documented**: Table `topic_clusters` holding centroid vector keys mapping to Qdrant.
  * **Codebase**: `TopicCluster` and `Topic` tables are defined where topic records store local model embeddings as float arrays in JSON fields.
  * **Status**: **IMPLEMENTED** (Without Qdrant, using local SQLite/Postgres JSON serialization).

---

## 3. GEO Engine & NLP Pipeline Conformance

* **Topic Extraction & Embeddings**:
  * **Documented**: Real-time Qdrant ANN matching and weekly offline clustering using sentence embeddings.
  * **Codebase**: Dynamic clustering using local `KeyBERT` and `SentenceTransformer` ('all-MiniLM-L6-v2') libraries during response parsing if installed. Falls back gracefully to plain text parsing when keys or modules are missing.
  * **Status**: **IMPLEMENTED**.
* **Visibility Scorer (V2 Algorithm)**:
  * **Documented**: Sentiment weight, relative position weight, domain citation weight, and model engine weights.
  * **Codebase**: Fully matches specification.
  * **Status**: **IMPLEMENTED**.
* **Share of Voice (SOV)**:
  * **Documented**: Percentage tracking based on total panel responses.
  * **Codebase**: Calculated dynamically based on prompt response mentions compared to competitors.
  * **Status**: **IMPLEMENTED**.

---

## 4. Conclusion & Action Items
* **Verdict**: The platform functions successfully at a **Sandbox / MVP level**. It does not use heavy cloud infrastructure (Kafka, ClickHouse, Qdrant, S3, Playwright proxy fleets) described in the conceptual blueprints, using local Python service classes, SQLite, KeyBERT, and httpx crawls instead.
* **Recommendations**:
  1. Update `docs/architecture/` to accurately reflect the Sandbox/MVP architecture.
  2. Implement an S3/Local file hybrid toggle for raw response storage.
  3. Plan Qdrant and ClickHouse integration stages for the Production phase.
