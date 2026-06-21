# Architectural Decision Traceability Audit

This document records the traceability audit for all major design decisions in the GEO/AEO Platform architecture package. It maps each decision back to its source: **Reverse Engineering Document**, **Inference**, or **Recommendation**.

---

## 1. GEO/AEO Scoring Engine

### Visibility Score Formula
* **Decision**: Raw count ratio of mentions to total response runs:
  $$\text{VisibilityScore} = \frac{\text{Runs where brand is mentioned}}{\text{Total runs}} \times 100$$
* **Source Type**: Reverse Engineering Document
* **Evidence**: Stated in `geo_aeo_scoring_engine_spec.md#L16-L23` where it describes the Raw mention frequency design choice: *"Profound's Visibility Score measures the percentage of mentions out of the total responses tracked."*
* **Confidence**: High

### Share of Voice (SoV) Formula
* **Decision**: Target brand mentions divided by the sum of mentions across the defined competitor set, sorted ordinally for ranking.
* **Source Type**: Reverse Engineering Document
* **Evidence**: Stated in `geo_aeo_scoring_engine_spec.md#L37-L47`: *"Profound's Share of Voice score compares your brand mentions to competitors' mentions..."*
* **Confidence**: High

### Intent-Weighted Visibility Score
* **Decision**: Weighting mentions in high-commercial-intent prompts higher (0.5 to 2.0) than low-intent informational queries.
* **Source Type**: Recommendation
* **Evidence**: Added in `product.md` and `intelligence.md` as an enhancement to raw visibility to address the limitation of treating all user prompts identically.
* **Confidence**: High

### Citation Impact Score
* **Decision**: Decaying, position-adjusted word count, and domain-authority weighted sum:
  $$\text{CitationImpact} = \sum \left( \frac{1}{\text{Position}} \times \text{AuthorityScore} \times e^{-\lambda t} \right)$$
* **Source Type**: Inference
* **Evidence**: Reconstructed in `geo_aeo_scoring_engine_spec.md#L48-L68` and `intelligence.md` from KDD 2024 Princeton/Georgia Tech GEO papers confirming citation placement and domain authority influence.
* **Confidence**: High

### Blended Visibility (Model Weighting)
* **Decision**: Blending per-engine visibility metrics using monthly-refreshed consumer traffic market shares (e.g., ChatGPT 62%, Gemini 19%).
* **Source Type**: Inference
* **Evidence**: Reconstructed in `geo_aeo_scoring_engine_spec.md#L70-L83` based on platform UI packaging filters and external market-share metrics.
* **Confidence**: High

---

## 2. Topic & Prompt Discovery

### 4-Stage Discovery Pipeline
* **Decision**: System resolves taxonomy via: 1) Semantic Retrieval, 2) Relevance Reranking, 3) HDBSCAN Clustering, 4) Centroid Canonical Selection.
* **Source Type**: Reverse Engineering Document
* **Evidence**: Outlined in the prompt research reports blog post referenced in `geo-aeo-part3-remaining-gaps.md.pdf` (Page 2, Stage 1 to 4).
* **Confidence**: High

### Joint Clustering of Prompts and Fan-Outs
* **Decision**: Embedding and clustering original parent queries together with their search-grounding sub-queries (fan-outs) using HDBSCAN.
* **Source Type**: Reverse Engineering Document
* **Evidence**: Confirmed in `geo-aeo-part3-remaining-gaps.md.pdf` (Page 2, Stage 3): *"clustering uses the original prompts' embeddings AND their corresponding query fan-outs jointly."*
* **Confidence**: High

### Centroid-Based Canonical Selection
* **Decision**: Selecting a canonical query representing each cluster using centroid proximity and query volume weights.
* **Source Type**: Inference
* **Evidence**: Reconstructed in `geo-aeo-part3-remaining-gaps.md.pdf` (Page 2, Stage 4) to explain the deduplication criteria.
* **Confidence**: High

---

## 3. Crawler & Log Analytics

### CDN Log Ingest (No JavaScript)
* **Decision**: Telemetry logs are collected at the server level via CDN log forwarding (Cloudflare Workers, CloudFront Firehose, Fastly connectors) without JS execution.
* **Source Type**: Reverse Engineering Document
* **Evidence**: Confirmed in `geo-aeo-part3-remaining-gaps.md.pdf` (Pages 12-13): *"No JavaScript required. The CDN sees every request before any application logic."*
* **Confidence**: High

### IP Range & DNS Bot Verification
* **Decision**: User-agents claiming to be RAG scrapers (GPTBot, ClaudeBot) are verified against provider IP registries and reverse DNS records.
* **Source Type**: Reverse Engineering Document
* **Evidence**: Confirmed in `geo-aeo-part3-remaining-gaps.md.pdf` (Page 13, Section 9C): *"Profound explicitly confirms IP-range cross-checking against provider-published ranges."*
* **Confidence**: High

### Profound Network Benchmarking
* **Decision**: Page crawl, latency, and citation rates are compared against a pooled median of 800,000+ benchmarked network pages.
* **Source Type**: Reverse Engineering Document
* **Evidence**: Confirmed in `geo-aeo-part3-remaining-gaps.md.pdf` (Page 13, Section 9B) and `geo-aeo-part4-final-gaps.md` (Page 10, Section 7B).
* **Confidence**: High

---

## 4. AI Readiness Audits

### Supervised AEO Content Score Model
* **Decision**: Supervised classification/regression model predicting citation probability, trained on the crawling database.
* **Source Type**: Reverse Engineering Document
* **Evidence**: Confirmed in `geo-aeo-part4-final-gaps.md` (Page 20, Section 1C): *"A predictive ML model (not a checklist scorer) trained on millions of top-cited pages."*
* **Confidence**: High

### Five Primary Feature Categories
* **Decision**: Predictors segment into: 1) Semantic Alignment, 2) Schema JSON-LD, 3) Structural balance, 4) Fan-out coverage, 5) Freshness.
* **Source Type**: Reverse Engineering Document
* **Evidence**: Confirmed in `geo-aeo-part4-final-gaps.md` (Page 20, Section 1C, Feature Table).
* **Confidence**: High

### Emailed HTML Audits (Ternary Rating)
* **Decision**: Free lead-gen audits are delivered via structured HTML email containing overall ratings (Good / Fair / Poor) across 6 sections.
* **Source Type**: Reverse Engineering Document
* **Evidence**: Confirmed in `geo-aeo-part4-final-gaps.md` (Page 30, Section 1A): *"The report is a purpose-built email template... delivered as HTML."*
* **Confidence**: High

---

## 5. System Architecture & Databases

### PostgreSQL Transactional Store
* **Decision**: PostgreSQL manages users, RBAC, workspaces, configurations, actions, prompts, and run metadata.
* **Source Type**: Recommendation
* **Evidence**: Defined in `system.md` and `database.md` as the standard, ACID-compliant transactional datastore.
* **Confidence**: High

### ClickHouse Columnar Store
* **Decision**: ClickHouse stores raw high-volume crawler telemetry logs, extrapolated prompt volumes, and Share of Voice time-series aggregates.
* **Source Type**: Recommendation
* **Evidence**: Defined in `system.md` and `database.md` to handle high-throughput log ingestion and speed up dashboard aggregations.
* **Confidence**: High

### Qdrant Vector DB
* **Decision**: Qdrant stores prompt and document embeddings to run ANN query clustering.
* **Source Type**: Recommendation
* **Evidence**: Defined in `system.md` and `database.md` as a dedicated vector database supporting HNSW indexing.
* **Confidence**: High

### LangGraph Agent Orchestrator
* **Decision**: Orchestrates optimization loops using LangGraph StateGraphs, forcing a human-in-the-loop (HITL) gate before publication.
* **Source Type**: Recommendation
* **Evidence**: Defined in `system.md` and `workers.md` to support stateful workflow pausing and checkpoint persistence.
* **Confidence**: High

---

## 6. Actions & Integrations

### CMS Adapter Drafting Rule
* **Decision**: CMS publishing adapters (WordPress, Contentful, Sanity) mutate posts in a staged "draft" state, never publishing live directly.
* **Source Type**: Reverse Engineering Document
* **Evidence**: Confirmed in `geo_aeo_scoring_engine_spec.md#L633-L670` and `integrations.md`.
* **Confidence**: High

### HubSpot & Salesforce ROI Bridge
* **Decision**: Appending UTM and session parameters to user intake forms to tie AI visibility referrals to closed-won CRM opportunities.
* **Source Type**: Recommendation
* **Evidence**: Added in `integrations.md` and `reporting.md` to resolve customer complaints regarding the organic revenue attribution gap.
* **Confidence**: High

### Hierarchical Workspace Support
* **Decision**: Reconfiguring the workspace database schema to support parent (Agency) and children (Client) profiles.
* **Source Type**: Recommendation
* **Evidence**: Added in `product.md` and `future-enhancements.md` to address single-workspace limitations highlighted by agency reviews.
* **Confidence**: High

### EWMA-Based Alerts
* **Decision**: Using Exponentially Weighted Moving Average control charts (SPC) instead of flat deltas to trigger alarms.
* **Source Type**: Inference
* **Evidence**: Reconstructed in `geo_aeo_scoring_engine_spec.md#L120-L135` to avoid alerting on sampling noise.
* **Confidence**: High

---

## 7. Audit Summary Matrix

| Design Decision | Source Type | Key Document Location | Confidence |
|---|---|---|---|
| **Visibility Score** | Reverse Engineering | [product.md](file:///e:/Profound-cloning/docs/architecture/product.md#L14) | High |
| **Share of Voice** | Reverse Engineering | [intelligence.md](file:///e:/Profound-cloning/docs/architecture/intelligence.md#L24) | High |
| **Intent-Weighted Visibility** | Recommendation | [intelligence.md](file:///e:/Profound-cloning/docs/architecture/intelligence.md#L18) | High |
| **Citation Impact** | Inference | [intelligence.md](file:///e:/Profound-cloning/docs/architecture/intelligence.md#L35) | High |
| **Blended Visibility** | Inference | [intelligence.md](file:///e:/Profound-cloning/docs/architecture/intelligence.md#L48) | High |
| **4-Stage Discovery** | Reverse Engineering | [roadmap.md](file:///e:/Profound-cloning/docs/architecture/roadmap.md#L14) | High |
| **Joint Clustering** | Reverse Engineering | [intelligence.md](file:///e:/Profound-cloning/docs/architecture/intelligence.md#L83) | High |
| **Centroid Selection** | Inference | [intelligence.md](file:///e:/Profound-cloning/docs/architecture/intelligence.md#L89) | High |
| **CDN Ingestion** | Reverse Engineering | [analytics.md](file:///e:/Profound-cloning/docs/architecture/analytics.md#L7) | High |
| **IP Bot Verification** | Reverse Engineering | [analytics.md](file:///e:/Profound-cloning/docs/architecture/analytics.md#L19) | High |
| **Profound Network** | Reverse Engineering | [analytics.md](file:///e:/Profound-cloning/docs/architecture/analytics.md#L71) | High |
| **AEO Content Score** | Reverse Engineering | [audits.md](file:///e:/Profound-cloning/docs/architecture/audits.md#L7) | High |
| **5 Feature Categories** | Reverse Engineering | [audits.md](file:///e:/Profound-cloning/docs/architecture/audits.md#L19) | High |
| **HTML Email Audits** | Reverse Engineering | [reporting.md](file:///e:/Profound-cloning/docs/architecture/reporting.md#L19) | High |
| **PostgreSQL Datastore** | Recommendation | [database.md](file:///e:/Profound-cloning/docs/architecture/database.md#L7) | High |
| **ClickHouse Datastore** | Recommendation | [database.md](file:///e:/Profound-cloning/docs/architecture/database.md#L120) | High |
| **Qdrant Vector DB** | Recommendation | [database.md](file:///e:/Profound-cloning/docs/architecture/database.md#L170) | High |
| **LangGraph Orchestrator**| Recommendation | [workers.md](file:///e:/Profound-cloning/docs/architecture/workers.md#L60) | High |
| **CMS Draft State** | Reverse Engineering | [integrations.md](file:///e:/Profound-cloning/docs/architecture/integrations.md#L7) | High |
| **CRM Revenue Bridge** | Recommendation | [integrations.md](file:///e:/Profound-cloning/docs/architecture/integrations.md#L70) | High |
| **Hierarchical Workspaces**| Recommendation | [product.md](file:///e:/Profound-cloning/docs/architecture/product.md#L24) | High |
| **EWMA Alerting** | Inference | [open-questions.md](file:///e:/Profound-cloning/docs/decisions/open-questions.md#L19) | High |
