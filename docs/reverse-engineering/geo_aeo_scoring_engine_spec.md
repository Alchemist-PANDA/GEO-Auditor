GEO/AEO Decision Logic & Scoring Engine Specification

Part 2 of the reverse-engineering series — the formulas, weights, and rules behind the dashboard

How to read this document. Every subsection is tagged:

✅ CONFIRMED — stated directly in Profound's own product blog, help docs, or marketing pages, with a source. These are facts, not inference.
⚙️ RECONSTRUCTED — not publicly disclosed by Profound or any competitor (nobody publishes their exact proprietary weights — that would let competitors game it). This is the best-practice version, built from the underlying academic research, convergent industry checklist behavior across a dozen-plus competing tools, and sound first-principles design. Treat it as "what the best possible version should do," not "what Profound's code literally does."

Mixing those two without labels is how reverse-engineering write-ups turn into confident fiction. This one won't do that.

Tier 1 — Core Scoring Engine

1. Visibility Score

✅ CONFIRMED. Profound's own walkthrough states it plainly: "Profound's Visibility Score measures the percentage of mentions out of the total responses tracked." Their worked example: a brand appearing in 0.1% of relevant AI-generated answers, ranked 339th against other tracked brands in that category.

VisibilityScore(brand, topic, period) =
    COUNT(runs WHERE brand_mentioned = true AND topic = topic AND period = period)
    ────────────────────────────────────────────────────────────────────────────  × 100
    COUNT(runs WHERE topic = topic AND period = period)

This is not a multi-factor weighted score. No position weighting, no sentiment weighting, no citation weighting baked in — it's raw mention frequency. That's a deliberate simplicity choice: a metric three people in a board meeting can sanity-check beats a metric only the data team can explain. Position, sentiment, and citations are surfaced as separate, parallel metrics (Average Position, Sentiment, Citation Share) rather than folded into one composite number — which is the correct design choice, and the one most "AI Visibility Score" competitors skip in favor of an opaque single number that sounds more impressive on a sales call.

⚙️ RECONSTRUCTED enhancement, if you were building a better version: weight each run by the commercial intent of the prompt before averaging, so a mention in a high-intent comparison prompt ("X vs Y pricing") counts more than a mention in a low-intent informational one ("what is X"). Simple implementation: multiply each run's contribution by a prompt_intent_weight (0.5–2.0) set at prompt-creation time, default 1.0.

```sql
SELECT
    SUM(CASE WHEN brand_mentioned THEN prompt_intent_weight ELSE 0 END)
    / SUM(prompt_intent_weight) * 100 AS weighted_visibility_score
FROM runs JOIN prompts USING (prompt_id)
WHERE topic_id = :topic AND run_at >= :period_start;
```

2. Share of Voice

✅ CONFIRMED. Profound's own description: "Profound's Share of Voice score compares your brand mentions to competitors' mentions across all responses tracked." Worked example: a brand at 0% SoV, rank 344, with the note that "across the top 10 brands, share of voice varies by only about 2%."

ShareOfVoice(brand, topic, period) =
    mention_count(brand, topic, period)
    ──────────────────────────────────────────────────────  × 100
    Σ mention_count(every entity in tracked_competitor_set, topic, period)

That "top 10 varies by only 2%" data point is the single most practically useful fact in this whole document, and it's worth sitting with: in a competitive category, AI share of voice is not winner-take-all at the top — it's a tight cluster of leaders followed by a steep cliff to "0% / unranked." The highest-leverage move for almost any brand isn't fighting for position #1 against #2 through #10 (a 2-point swing), it's getting off 0% entirely. That's a far cheaper problem to solve (one good citation-worthy page can do it) than displacing a category leader.

Share of Voice Rank is simply RANK() OVER (PARTITION BY topic, period ORDER BY share_of_voice DESC) — an ordinal sort, nothing more exotic.

3. Citation Impact Engine

✅ CONFIRMED — what exists: Profound's Citations dashboard tracks Citation Share (how often the brand is cited vs. tracked competitors), Citation Rank (ordinal), Top Citation Domains (leaderboard of which external domains AI engines cite most for a topic), and Top Citation Pages (specific URLs). The product explicitly frames two levers: become the top-cited domain yourself (on-page content strategy), or get listed among the top-cited domains via outreach (off-page/PR strategy).

⚙️ RECONSTRUCTED — how authority weighting almost certainly works, since exact weights aren't published. The closest thing to ground truth here is the peer-reviewed Princeton/Georgia Tech GEO paper (KDD 2024), which found that citing external sources improved visibility by up to 115% for lower-ranked content specifically, and which introduced Position-Adjusted Word Count as its core metric — citations earlier in an answer matter more than citations buried at the end. A defensible Citation Impact formula, built on that validated research rather than guesswork:

CitationImpact(domain, topic, period) =
    Σ over each citation event i:
        ( 1 / position_in_answer_i )         -- earlier citation = more weight (Princeton finding)
        × domain_authority_score(domain)      -- backlink-graph-derived, e.g. Ahrefs DR / Moz DA equivalent
        × recency_decay(citation_age_i)        -- exponential decay, half-life ~90 days

```sql
CREATE TABLE domain_authority (
    root_domain        TEXT PRIMARY KEY,
    authority_score     FLOAT NOT NULL,        -- 0-100, from a self-crawled backlink graph or licensed feed
    last_recrawled_at   TIMESTAMPTZ
);
```

The honest gap here: nobody outside Profound knows whether "Forbes counts more than a random blog" in their actual system, but every competitor's public marketing copy and every independent AEO checker tool converges on authority-weighting citations as standard practice — so assume yes, and build it that way, while being clear with customers about which dataset backs the authority score (self-crawled vs. licensed) since that materially changes how trustworthy the number is.

4. Model Weighting

✅ CONFIRMED — and the finding is interesting: Profound does not appear to compute one secretly-weighted blended score across engines. The product surfaces per-engine breakdowns (Topics/Platforms filters) and explicitly tells the marketer to look at their own referral-traffic data to decide which engine matters most: "Seeing an uptick in traffic from Google AI Overviews or Perplexity? Consider prioritizing mentions and citations on those platforms instead of dividing your AI visibility efforts across answer engines." Engine access is also tiered by plan (ChatGPT on all plans; Growth adds Perplexity + AI Overviews; Enterprise unlocks all 10) rather than weighted — which is a packaging decision, not a scoring decision.

⚙️ RECONSTRUCTED — for a best-possible build: rather than equal-weighting all engines into one blended number (which silently overweights low-usage engines like Copilot relative to ChatGPT), weight by real-world usage share, refreshed regularly since this shifts fast — public traffic-panel data put ChatGPT's share of generative-AI web traffic anywhere from roughly 57% to 80% depending on the measurement source and month in question, with Gemini in the 21–25% range and Claude single-to-low-double digits and rising. The rule that matters more than the exact split: never show only the blended number. Always pair it with the per-engine breakdown, exactly as Profound does — because a brand that's strong on Perplexity and invisible on ChatGPT looks identical to one that's evenly mediocre everywhere if you only look at the blend, and those are completely different strategic situations.

```python
ENGINE_USAGE_WEIGHTS = {  # refresh monthly from a traffic panel — do not hardcode in production
    "chatgpt": 0.62, "gemini": 0.19, "perplexity": 0.08, "claude": 0.07, "copilot": 0.04,
}

def blended_visibility(per_engine_scores: dict[str, float]) -> float:
    return sum(score * ENGINE_USAGE_WEIGHTS.get(engine, 0) for engine, score in per_engine_scores.items())
```

Tier 2 — GEO Intelligence

5. Prompt Discovery

✅ CONFIRMED — two distinct mechanisms, not one.

Mechanism A — seeded/manual. The brand inputs topics and seed prompts (Profound suggests sourcing these from customer intake forms and internal sales/CS/marketing polling), and Profound estimates search volume for each before tracking begins — this feeds the same Prompt Volumes pipeline detailed in Part 1 of this series.

Mechanism B — passive/reactive, the more interesting one. The "Relevant Prompts" feature surfaces AI responses where the brand or a competitor gets cited even for prompts the brand never explicitly chose to track. Mechanically, this has to work by reverse-indexing the conversation panel and citation log: scan all captured responses across all tracked categories for the brand's domain or name appearing anywhere, regardless of which specific prompt triggered it, then surface those as discoverable additions. This solves the cold-start problem of "I don't know what to track yet" — you don't need a complete prompt list on day one, the system finds you.

Query Fanouts — a separate, confirmed feature: tracks the sub-queries an answer engine internally generates when expanding a parent prompt (e.g., "best content operations platform" fans out into "content operations software for enterprise," "essential features for content ops software," etc.), plus a "word transformation" view showing what terms the engine added during expansion. This is plausibly captured by either (a) directly reading intermediate search queries some engines expose in their UI/DOM during a live session (Perplexity and AI Overviews both surface visible sub-query chips at points), or (b) running the same parent prompt many times and statistically clustering the citation/source patterns that emerge, then diffing vocabulary against the original prompt.

6. Content Gap Analysis

⚙️ RECONSTRUCTED — not described as a named standalone feature in Profound's own materials, but it's the necessary intersection of data Profound already confirms it has: Prompt Volumes (demand) × Answer Engine Insights share-of-voice (current presence) × Citations (what's already winning). The gap score is the product of three signals, not any one alone:

GapScore(brand, cluster) =
    estimated_volume(cluster)                         -- is anyone even asking this?
    × (1 - share_of_voice(brand, cluster))              -- how much room is there?
    × competitor_dominance(cluster)                     -- is someone else already winning it cleanly?

A cluster with huge volume but where SoV is already split evenly across 15 brands (the "varies by only 2%" scenario from section 2) is a much harder, lower-ROI target than one with moderate volume where one competitor has run away with 70%+ citation share off a single outdated blog post — the gap is real but the bar to clear is low. Sort by GapScore descending, but display competitor-dominance separately so a marketer isn't chasing the biggest number blindly.

7. AI Readiness Audit ("Content AEO")

✅ CONFIRMED — the free /aeo-report tool exists and scores four named dimensions: AI Visibility, Source Citations, Brand Sentiment, and Content AEO — generated by running brand-relevant prompts against three consumer engines (ChatGPT, Perplexity, Google AI Overviews), explicitly captured "directly from the consumer experience, not API outputs."

⚙️ RECONSTRUCTED — the underlying Content AEO sub-factors. Profound doesn't publish the exact per-page scoring weights (no AEO vendor does — as of mid-2026 there's no industry standardization body for this, which every independent comparison piece on the category notes explicitly). But cross-referencing a dozen-plus independently built AEO checker tools converges on essentially the same checklist, which also happens to align with what the Princeton GEO paper validated empirically:

FactorWhy it's in every checklistResearch backingSchema markup (FAQPage, HowTo, Article, Organization, AggregateRating)Gives the engine explicit structure instead of forcing it to inferIndustry-convergent, not yet academically isolatedDirect-answer-first paragraph structureMatches how RAG systems extract passagesMatches Princeton's "fluency optimization" finding (+28% lift)Statistics/citation density on the pagePages citing sources and stats get cited more themselvesPrinceton: statistics +32–41%, citations +30%QuotationsDirectly tested and validatedPrinceton: +28–41% depending on study citedHeading-as-question formatting, FAQ sectionsMirrors actual user query phrasingIndustry-convergentCrawlability (robots.txt AI-bot permissions, llms.txt presence)A page can't be cited if it can't be fetched — see Section 4 of Part 1 of this seriesDirect mechanical prerequisiteFreshness / last-modified signalsEngines deprioritize stale sources for fast-moving topicsIndustry-convergentE-E-A-T signals (author bios, About page, credentials)Carried over from Google's own ranking guidance; AI engines lean on similar trust heuristicsInherited from search SEO, not GEO-specific researchAvoidance of keyword stuffingActively penalized, not neutralPrinceton: keyword stuffing decreased visibility ~10%

A reasonable weighted score: 30% statistics/citations/quotations (the most empirically validated lever), 20% schema/structured data, 20% direct-answer structure, 15% crawlability, 15% E-E-A-T/freshness. Treat these weights as a starting hypothesis to A/B test against your own citation-rate outcomes, not gospel — this is exactly the kind of number that should be continuously recalibrated against real citation data rather than set once and trusted forever.

Tier 3 — Operational Intelligence

8. Alert Logic

⚙️ RECONSTRUCTED — not publicly disclosed, and this is the one place where getting it wrong actively hurts the product. Given everything established in Part 1 about LLM non-determinism, a naive "alert if visibility dropped" rule will fire constantly on pure sampling noise and train users to ignore every alert within a week. The correct approach is a statistical process control pattern, not a raw threshold:

```python
def should_alert(metric_history: list[float], current_value: float, z_threshold: float = 2.5) -> bool:
    """EWMA-based control chart, not raw delta. Only fires when current_value
    falls outside the metric's OWN historical variance band — the same logic
    production monitoring systems (Datadog, etc.) use for noisy time series."""
    mean = ewma(metric_history, alpha=0.3)
    std = ewma_std(metric_history, alpha=0.3)
    z_score = abs(current_value - mean) / max(std, 1e-6)
    return z_score > z_threshold and len(metric_history) >= MIN_SAMPLE_SIZE  # don't alert on day-2 data
```

MIN_SAMPLE_SIZE matters as much as the z-score — alerting off three days of data on a metric with inherent run-to-run variance is how you generate a false "competitor surge" alert that's actually just noise, and burn the trust the rest of the product worked to earn with its confidence-interval transparency.

9. Recommendation Engine

✅ CONFIRMED — this is genuinely well-documented. The feature ("Actions," launched July 2025, later folded into "Agents") explicitly combines three data streams — AI search responses/citations, real user prompts, and AI-referred site traffic — and generates four categories of recommendation, rate-limited to roughly four per week on the Growth plan:

Outreach — get cited on an important third-party domain/page; Profound provides rationale, implementation steps, and a suggested contact.
Reddit marketing — post in specific identified subreddits/threads to boost citation share, with suggested prompts to address.
Content creation — net-new page targeting a topic with no current owned content, with a step-by-step brief and reference inspiration.
Content optimization — update an existing page that's underperforming relative to what gets cited for that prompt.

This is a rules/decision-table system, not an exotic black-box model — and that's a feature, not a limitation, because it's auditable:

```python
def generate_action(gap: dict) -> dict:
    if gap["top_competitor_citation_domain"] and gap["brand_owns_no_competing_content"]:
        return {"type": "outreach", "target": gap["top_competitor_citation_domain"],
                "rationale": f"This domain is the top cited source for '{gap['cluster_label']}' "
                              f"and you have no content competing for it."}
    if gap["reddit_threads_cited_in_answers"]:
        return {"type": "reddit_marketing", "threads": gap["reddit_threads_cited_in_answers"]}
    if not gap["brand_has_owned_page_for_topic"]:
        return {"type": "content_creation", "brief": generate_brief(gap)}
    if gap["brand_owned_page_missing_validated_factors"]:  # see Section 7 checklist
        return {"type": "content_optimization", "page": gap["brand_owned_page"],
                "missing_factors": gap["brand_owned_page_missing_validated_factors"]}
```

Note Profound's own framing, stated directly in their launch post: "We don't generate content for you. Instead, we generate content briefs." That was the explicit boundary in mid-2025 — full draft generation came later (the "Agents" feature, alongside the Series C). That sequencing is itself the most useful Tier 4 finding — see below.

10. Competitor Intelligence

✅ CONFIRMED, mechanism inferable from the UI behavior described: competitors appear as a large, ranked, checkbox-toggleable list (the worked examples reference ranks like #339 and #344 out of an apparently large tracked universe per category), with the brand able to include/exclude specific competitors from comparison views.

⚙️ RECONSTRUCTED — how that universe gets populated automatically, since manually curating hundreds of ranked entities per category isn't realistic: named-entity recognition over the full corpus of captured AI responses for a topic, building a co-occurrence graph of every brand/product entity mentioned alongside the tracked brand's category, then surfacing any entity above a frequency threshold as an auto-discovered competitor candidate, which the user can then confirm or dismiss. This is the same entity-resolution technique used in social-listening and PR monitoring tools — nothing GEO-specific about the underlying method, just applied to a new text corpus (LLM answers instead of news/social posts).

Tier 4 — Agent Layer

11. Workflow Automation

✅ CONFIRMED, and the timeline is the actual insight. Profound shipped pure analysis first (Answer Engine Insights, Prompt Volumes, Agent Analytics), then in July 2025 added insight-to-brief (Actions: "we generate content briefs," explicitly not full drafts), and only by the February 2026 Series C did it expand into full autonomous draft generation and CMS execution under the "Agents" brand — with the company's own stated reason being that customers were exporting Profound's data into separate orchestration tools and Profound wanted to own that last step.

The practical lesson for anyone building a competing or adjacent product: the sequencing was analyze → brief → draft → execute, over roughly 18 months, not all four shipped at once. Each stage had to earn enough customer trust in the data quality before the next stage's automation was credible — nobody hands an AI agent unsupervised publishing rights to their brand's content based on a visibility score they don't yet trust. Building the full Section 3 LangGraph pipeline from Part 1 of this series on day one, before the underlying Tier 1 scoring has a track record with real customers, is building the riskiest layer first. If you're sequencing a build, monitoring credibility is the prerequisite for automation adoption, not a parallel workstream.

What's still genuinely unknown

In the interest of not overstating what triangulating public blog posts can tell you: the literal backend implementation details — the specific embedding model, the exact domain-authority data source, the precise alert z-score threshold, whether there's any ML model involved in opportunity ranking versus pure rules-table logic, the exact composition of the consented conversation panel — are not disclosed anywhere public, by Profound or by any direct competitor, because that's the layer every vendor in this category guards as differentiation. Anyone who claims to know those numbers without an engineering-blog citation or a documented source is guessing and presenting it as fact — which is exactly the failure mode this document was written to avoid.

GEO/AEO Platform Backend Architecture

A reverse-engineered blueprint, built from observable product behavior — not insider knowledge

This document treats "a platform like tryprofound.com" as a system design problem. Every component below is buildable with off-the-shelf infrastructure; none of it requires anything proprietary that isn't either (a) standard data-engineering practice, (b) publicly documented vendor behavior (bot user agents, IP ranges), or (c) well-known LLM-orchestration patterns. Where the real-world product almost certainly diverges from "pure engineering" — panel acquisition, ToS gray zones, statistical extrapolation dressed up as hard numbers — it's called out explicitly, because pretending otherwise would make this blueprint useless to actually build from.

0. System-Level Architecture

┌──────────────────────────────────────────────────────────────────────────────────┐
│                                INGESTION LAYER                                     │
│  ┌────────────────┐ ┌─────────────────┐ ┌──────────────────┐ ┌─────────────────┐  │
│  │ Conversation    │ │ Multi-Model      │ │ Client CDN /     │ │ Web Crawler /    │  │
│  │ Panel Feed      │ │ Query Runner     │ │ Server Log Feed  │ │ Domain Authority │  │
│  │ (browser ext /  │ │ (API + headless  │ │ (bot/crawler     │ │ Resolver         │  │
│  │  data co-op)    │ │  browser fleet)  │ │  identification) │ │ (citation graph) │  │
│  └────────┬────────┘ └────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘  │
└───────────┼───────────────────┼────────────────────┼────────────────────┼───────────┘
            │                   │                     │                    │
┌───────────▼───────────────────▼─────────────────────▼────────────────────▼───────────┐
│                       MESSAGE BUS (Kafka / Kinesis / SQS+SNS)                          │
│        topics: raw_conversations | model_responses | edge_logs | crawl_results          │
└───────────┬───────────────────┬─────────────────────┬────────────────────┬───────────┘
            │                   │                     │                    │
┌───────────▼──────────┐ ┌──────▼───────────┐ ┌───────▼──────────┐ ┌───────▼───────────┐
│ Embedding +           │ │ NLP Extraction    │ │ Bot ID +          │ │ Citation Resolver  │
│ Clustering Workers     │ │ ("LLM-as-judge")  │ │ Verification       │ │ + Domain Authority │
│ (HNSW + HDBSCAN)       │ │ Workers           │ │ Workers (UA + IP) │ │ Scorer             │
└───────────┬────────────┘ └──────┬────────────┘ └───────┬───────────┘ └────────┬───────────┘
            │                     │                       │                     │
┌───────────▼─────────────────────▼───────────────────────▼─────────────────────▼───────────┐
│                                    STORAGE LAYER                                            │
│   Postgres (entities, taxonomy, config) │ ClickHouse (all time-series, append-only)         │
│   Qdrant / Pinecone (query + content embeddings) │ S3 (raw response/DOM/screenshot archive) │
└───────────┬───────────────────────────────────────────────────────────────┬───────────────┘
            │                                                                │
┌───────────▼───────────────────┐                              ┌────────────▼───────────────┐
│   ANALYTICS / SERVING API      │◄──── opportunity signals ────┤  AGENT ORCHESTRATION LAYER   │
│   (GraphQL/REST + BI cache)    │                              │  (LangGraph state machines)  │
└───────────┬─────────────────────┘                              └────────────┬───────────────┘
            │                                                                 │
┌───────────▼─────────────────────────────────────────────────────────────────▼───────────────┐
│                  CLIENT DASHBOARD (Next.js)   ·   CMS PUBLISH TARGETS (WP/Contentful/Sanity)  │
└────────────────────────────────────────────────────────────────────────────────────────────┘

Four subsystems sit on this shared spine. Each gets its own data model below, but they all write into the same Postgres (config/entities) + ClickHouse (events/time-series) + vector DB (semantic search/clustering) trio. That reuse is the actual architectural decision that matters — not the individual workers.

1. Prompt Volumes Data Pipeline

The brutally honest framing first: a number like "1.5B+ queries analyzed" cannot be a raw count of observed events. No vendor has a wiretap on ChatGPT's query log. What's actually happening is panel-based statistical extrapolation — the same methodology Nielsen uses for TV ratings or Similarweb/comScore use for web traffic: observe a consented sample, then scale it to the known population using a public anchor metric (OpenAI's disclosed weekly active users, for instance). Anyone selling this number as a literal count is either rounding very generously or blending in LLM-synthesized queries to pad long-tail coverage. Build it honestly and you get a better product, because you can show confidence intervals instead of fake precision.

1.1 Pipeline stages

[Consented Panel Feed]      [Seed Taxonomy: 500-2000 topic/vertical seeds]
        │                              │
        ▼                              ▼
 [PII Scrub + Consent Filter]   [LLM Query Synthesizer]
        │                              │  (generates realistic long-tail
        │                              │   variants per seed; tagged
        │                              │   is_synthetic=true)
        └──────────────┬───────────────┘
                        ▼
              [Dedup + Normalize]
                        │
                        ▼
              [Embedding Worker]
            (bge-large / text-embedding-3)
                        │
            ┌───────────┴────────────┐
            ▼                        ▼
   [Vector DB Upsert]      [Online ANN cluster assign]
   (Qdrant/Pinecone)        (HNSW, nearest centroid)
            │                        │
            ▼                        ▼
   [Nightly batch reclustering: HDBSCAN over full collection,
    centroid merge/split, auto-label via LLM summarization of
    N sample queries per cluster]
                        │
                        ▼
        [Topic Taxonomy table (Postgres)]
                        │
                        ▼
        [Volume Extrapolation Model]
   panel_count_in_cluster × (platform_population / panel_size)
   segmented by region + device + engine, with CI bands
                        │
                        ▼
        [prompt_volume_ts (ClickHouse)]

1.2 Vector DB collection schema (Qdrant)

```python
# Qdrant collection definition
from qdrant_client.models import VectorParams, Distance, PayloadSchemaType

COLLECTION_CONFIG = {
    "collection_name": "query_embeddings",
    "vectors_config": VectorParams(size=1536, distance=Distance.COSINE),
    "payload_schema": {
        "raw_text_hash":      PayloadSchemaType.KEYWORD,   # SHA256, no raw PII text stored long-term
        "engine":              PayloadSchemaType.KEYWORD,   # chatgpt | gemini | perplexity | claude
        "region":               PayloadSchemaType.KEYWORD,
        "detected_brand_ids":   PayloadSchemaType.KEYWORD,   # array of UUIDs, post-NER
        "cluster_id":           PayloadSchemaType.KEYWORD,   # FK -> postgres topic_clusters.id
        "is_synthetic":         PayloadSchemaType.BOOL,
        "captured_at":          PayloadSchemaType.DATETIME,
    },
}
```

Why HNSW + nightly HDBSCAN rather than pure streaming k-means: incoming query volume needs O(log n) nearest-centroid assignment to stay real-time, but cluster boundaries drift as new topics emerge (a new product launch creates a cluster that didn't exist yesterday). Streaming-only clustering either over-merges into stale buckets or never consolidates near-duplicates. The two-speed design (fast online assignment, slow batch reclustering) is the same pattern used in production recommender systems (e.g., how Spotify handles playlist/genre clustering drift) — it's not novel, it's just correct.

1.3 Postgres schema — topic taxonomy

```sql
CREATE TABLE topic_clusters (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id       UUID REFERENCES topic_clusters(id),   -- hierarchical: vertical > category > intent
    label           TEXT NOT NULL,                        -- LLM-generated human-readable name
    centroid_vector_id TEXT NOT NULL,                      -- pointer into Qdrant
    vertical        TEXT NOT NULL,
    sample_query_ids UUID[] NOT NULL,                      -- for re-labeling / audit
    created_at      TIMESTAMPTZ DEFAULT now(),
    last_reclustered_at TIMESTAMPTZ
);

CREATE TABLE brand_topic_mentions (
    brand_id        UUID NOT NULL REFERENCES brands(id),
    cluster_id      UUID NOT NULL REFERENCES topic_clusters(id),
    week_start       DATE NOT NULL,
    panel_observed_count INT NOT NULL,
    estimated_volume     BIGINT NOT NULL,        -- extrapolated
    confidence_low        BIGINT NOT NULL,
    confidence_high       BIGINT NOT NULL,
    is_synthetic_augmented BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (brand_id, cluster_id, week_start)
);
```

1.4 ClickHouse schema — time series

```sql
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
    is_synthetic_pct  Float32           -- transparency field: what % of this estimate is LLM-synthesized vs panel-observed
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (cluster_id, engine, region, date);
```

That is_synthetic_pct column is the field every vendor in this space should expose to customers and almost none does. It's the difference between a measurement product and a confident-sounding guess wearing a measurement product's clothes.

2. Answer Engine Insights (AEI) Engine

2.1 Execution flow

[Prompt Scheduler — Temporal/Airflow DAG, runs daily per brand]
        │
        ▼
[Generate prompt set: branded + unbranded + competitor-comparison
 prompts × N engines × M regions × K personas]
        │
        ▼
[Multi-Model Executor — fan-out async workers]
        │
   ┌────┴─────────────────────────────────────────┐
   ▼                                                ▼
[API Adapters]                          [Headless Browser Fleet]
 - Anthropic API (web search tool on)    - Playwright workers
 - OpenAI API (web search tool on)       - Residential/mobile proxy pool
 - Gemini API (grounding on)             - Session/cookie rotation
                                          - Captures the LOGGED-IN CONSUMER
                                          UI response, which differs from
                                          raw API output (UI has browsing/
                                          memory features not always
                                          identical to the API surface)
        │                                                │
        └────────────────────┬───────────────────────────┘
                              ▼
                [Raw Response Archive]
        (full text + DOM snapshot + screenshot → S3,
         pointer stored in Postgres `runs` table — audit trail)
                              │
                              ▼
                [NLP Extraction — "LLM-as-judge" pass]
        (cheap/fast model, e.g. Haiku/GPT-4o-mini class,
         constrained JSON output — see prompt template 2.3)
                              │
                              ▼
                [Normalization]
        - resolve cited URLs → eTLD+1 root domain (tldextract)
        - join against domain_authority table
        - dedupe near-identical brand mention spans
                              │
                              ▼
                [Aggregation → rollups]
        Share of Voice, Sentiment Index, Citation Authority
                              │
                              ▼
                [ClickHouse: share_of_voice_ts]

2.2 Postgres schema — runs and extraction

```sql
CREATE TABLE prompts (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id      UUID NOT NULL REFERENCES brands(id),
    text          TEXT NOT NULL,
    prompt_type   TEXT NOT NULL CHECK (prompt_type IN ('branded','unbranded','comparison')),
    cluster_id    UUID REFERENCES topic_clusters(id)   -- links AEI back to Prompt Volumes demand data
);

CREATE TABLE runs (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prompt_id     UUID NOT NULL REFERENCES prompts(id),
    engine        TEXT NOT NULL,           -- chatgpt | claude | gemini | perplexity | copilot
    capture_method TEXT NOT NULL,          -- 'api' | 'browser_ui'
    region        TEXT NOT NULL,
    persona       TEXT,
    raw_text_s3_key TEXT NOT NULL,
    dom_snapshot_s3_key TEXT,
    run_at        TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE extracted_mentions (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id        UUID NOT NULL REFERENCES runs(id),
    entity_name   TEXT NOT NULL,
    entity_type   TEXT NOT NULL CHECK (entity_type IN ('target_brand','competitor')),
    position_in_text INT,                  -- earlier mention = higher salience weight
    sentiment     FLOAT NOT NULL,          -- -1.0 to 1.0
    is_recommended BOOLEAN,
    extractor_model TEXT NOT NULL,         -- which judge model produced this — for audit/error tracking
    extractor_confidence FLOAT
);

CREATE TABLE citations (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id        UUID NOT NULL REFERENCES runs(id),
    url           TEXT NOT NULL,
    root_domain   TEXT NOT NULL,
    anchor_text   TEXT,
    position_in_text INT,
    domain_authority_score FLOAT
);
```

2.3 The extraction layer is the whole game — and it's LLM-judging-LLM

You cannot regex your way through "does this paragraph recommend Brand X favorably." This is a structured-extraction call, and it should use a cheap, fast model with a tightly constrained schema — not the same flagship model you used to generate the answer, both for cost and to avoid correlated bias.

```python
EXTRACTION_SYSTEM_PROMPT = """
You are a structured-data extractor. Given raw text from an AI answer engine response,
extract ONLY the following JSON. Do not add commentary. If a field is not present, use null
or an empty array. Confidence must reflect genuine uncertainty, not be defaulted to 1.0.

{
  "brand_mentions": [
    {"name": str, "position_char": int, "sentiment": float (-1 to 1),
     "is_recommended": bool, "confidence": float (0 to 1)}
  ],
  "competitor_mentions": [ ...same shape... ],
  "citations": [
    {"url": str, "anchor_text": str | null, "position_char": int}
  ],
  "answer_summary": str   # one sentence, factual, no editorializing
}
"""

async def extract_structured(run_id: str, raw_text: str, judge_model: str = "claude-haiku-4-5"):
    response = await llm_client.messages.create(
        model=judge_model,
        max_tokens=800,
        system=EXTRACTION_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": raw_text}],
        response_format={"type": "json_object"},
    )
    parsed = json.loads(response.content[0].text)
    await persist_extraction(run_id, parsed, extractor_model=judge_model)
    return parsed
```

The honest caveat that matters for anyone building or buying this: the judge model has its own error rate. Sentiment/entity extraction from unstructured text by a secondary LLM typically runs 5–15% disagreement against human-labeled ground truth in published NLP benchmarks for nuanced sentiment tasks — and that error compounds on top of the non-determinism of the first LLM's answer generation. A "Share of Voice: 34%" figure on a dashboard is really "34% ± a margin nobody is showing you." Build in a periodic human-labeled spot-check sample (even 50 runs/week, reviewed by an analyst) and track extractor agreement-rate as a first-class internal metric — that's what separates a defensible product from a vibes dashboard.

2.4 Async orchestration skeleton

```python
import asyncio
from dataclasses import dataclass

@dataclass
class PromptJob:
    prompt_id: str
    engine: str
    capture_method: str   # 'api' or 'browser_ui'

ENGINE_RATE_LIMITS = {  # requests/sec, token-bucket per engine to avoid bans/429s
    "chatgpt_api": 5, "chatgpt_browser": 0.5,
    "claude_api": 8, "gemini_api": 6, "perplexity_api": 3,
}

async def run_job(job: PromptJob, bucket: dict):
    async with bucket[job.engine]:
        if job.capture_method == "api":
            raw = await api_adapters[job.engine].query(job.prompt_id)
        else:
            raw = await browser_fleet.capture(job.engine, job.prompt_id)
        run_id = await persist_run(job, raw)
        await extract_structured(run_id, raw.text)

async def fan_out(jobs: list[PromptJob]):
    buckets = {k: asyncio.Semaphore(v) for k, v in ENGINE_RATE_LIMITS.items()}
    await asyncio.gather(*(run_job(j, buckets) for j in jobs))
```

2.5 ClickHouse rollup

```sql
CREATE TABLE share_of_voice_ts
(
    brand_id      UUID,
    competitor_id Nullable(UUID),
    engine        LowCardinality(String),
    cluster_id    UUID,
    date          Date,
    sov_pct       Float32,
    sentiment_avg Float32,
    citation_authority_avg Float32,
    sample_size   UInt32     -- ALWAYS expose this — a SoV computed on 6 runs is not the same
                              -- confidence as one computed on 600
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (brand_id, engine, cluster_id, date);
```

3. Agentic Workflow & Node Logic

This is a LangGraph StateGraph: a directed graph where nodes are functions that mutate a shared typed state, edges route based on that state, and at least one node deliberately interrupts execution for a human gate. The non-negotiable design constraint here, given the brand-risk stakes of auto-publishing content under a client's name, is that publish is never a fully autonomous edge — there's always a HITL checkpoint before cms_publish_node.

3.1 State schema

```python
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END

class ContentAgentState(TypedDict):
    brand_id: str
    opportunity: dict          # {cluster_id, gap_size, competitor_dominance, est_volume}
    brief: dict | None         # {target_keywords, outline, required_citations, word_count_target}
    draft: str | None
    draft_version: int
    claims_to_verify: list[dict]   # [{claim_text, span}, ...]
    verification_results: list[dict]  # [{claim_text, verified: bool, source_url, confidence}]
    unverified_claim_count: int
    approval_status: Literal["pending", "approved", "rejected", "needs_revision"]
    reviewer_feedback: str | None
    cms_target: Literal["wordpress", "contentful", "sanity"]
    published_url: str | None
    revision_count: int
```

3.2 Node definitions

```python
MAX_REVISIONS = 3
MIN_VERIFIED_CLAIM_RATIO = 0.9   # publish-blocking threshold

def detect_opportunity_node(state: ContentAgentState) -> ContentAgentState:
    """Query the AEI + Prompt Volumes warehouse for: high-demand cluster where
    target brand's share_of_voice is materially below top competitor's, and
    estimated_volume clears a minimum threshold (don't write content for noise)."""
    gap = warehouse.find_largest_gap(
        brand_id=state["brand_id"],
        min_volume=1000,           # weekly estimated query volume floor
        min_competitor_sov=0.15,
    )
    state["opportunity"] = gap
    return state

def generate_brief_node(state: ContentAgentState) -> ContentAgentState:
    """LLM call: turn the opportunity into a content brief. Pull the actual
    cited competitor content as input so the brief targets demonstrated
    citation-worthy structure, not guesswork."""
    competitor_sources = citation_store.top_cited_sources(state["opportunity"]["cluster_id"])
    state["brief"] = llm_generate_brief(state["opportunity"], competitor_sources)
    return state

def draft_generation_node(state: ContentAgentState) -> ContentAgentState:
    """Generate the article applying the published GEO findings: lead with
    direct answers, include cited statistics, use quotable structure, avoid
    keyword stuffing (negatively correlated with AI citation per Aggarwal et
    al., KDD 2024)."""
    feedback = state.get("reviewer_feedback")
    state["draft"] = llm_generate_draft(state["brief"], revision_feedback=feedback)
    state["claims_to_verify"] = extract_factual_claims(state["draft"])
    state["draft_version"] = state.get("draft_version", 0) + 1
    return state

def web_verification_node(state: ContentAgentState) -> ContentAgentState:
    """For every factual/statistical claim in the draft, run a web search +
    scrape and check whether a real source actually supports it. This is the
    hallucination-grounding gate — content that cites a stat the model
    invented is worse for AEO than no stat at all, because a single debunked
    citation can tank trust signals on the whole page."""
    results = []
    for claim in state["claims_to_verify"]:
        hits = web_search(claim["claim_text"])
        verified, source = verify_claim_against_sources(claim["claim_text"], hits)
        results.append({**claim, "verified": verified, "source_url": source})
    state["verification_results"] = results
    verified_count = sum(r["verified"] for r in results)
    state["unverified_claim_count"] = len(results) - verified_count
    return state

def hitl_gate_node(state: ContentAgentState) -> ContentAgentState:
    """Interrupt point. In LangGraph this is implemented via the `interrupt()`
    primitive (or a checkpointer + external resume call) — execution pauses
    here and a human reviewer in the dashboard sees the draft + verification
    report, then resumes the graph with an approval decision."""
    decision = await_human_review(state["draft"], state["verification_results"])
    state["approval_status"] = decision["status"]
    state["reviewer_feedback"] = decision.get("feedback")
    return state

def cms_publish_node(state: ContentAgentState) -> ContentAgentState:
    """Adapter pattern — one interface, three implementations."""
    adapter = CMS_ADAPTERS[state["cms_target"]]
    url = adapter.publish_draft(state["draft"], state["brief"])
    state["published_url"] = url
    return state

def post_publish_monitor_node(state: ContentAgentState) -> ContentAgentState:
    """Closes the loop: schedule a recurring AEI prompt run against this
    cluster/topic so the next dashboard refresh shows whether the new page
    actually moved share of voice. Without this, 'Agents' is content
    generation, not optimization — the loop is the product."""
    scheduler.add_recurring_check(state["opportunity"]["cluster_id"], state["brand_id"])
    return state
```

3.3 CMS adapter pattern

```python
class CMSAdapter(Protocol):
    def publish_draft(self, draft: str, brief: dict) -> str: ...

class WordPressAdapter:
    def publish_draft(self, draft, brief):
        # POST /wp-json/wp/v2/posts, status="draft", Application Password auth
        resp = requests.post(f"{self.base_url}/wp-json/wp/v2/posts",
                              auth=self.auth, json={"title": brief["title"],
                              "content": draft, "status": "draft"})
        return resp.json()["link"]

class ContentfulAdapter:
    def publish_draft(self, draft, brief):
        # Content Management API: create entry in draft environment, NOT
        # auto-publish to the production space — same "stage, don't ship" rule
        entry = self.cma_client.entries().create(content_type="article",
                 fields={"title": {"en-US": brief["title"]},
                         "body": {"en-US": draft}})
        return entry.id

class SanityAdapter:
    def publish_draft(self, draft, brief):
        # Mutation API, draft._id prefixed with "drafts." — Sanity's native
        # draft/publish separation maps directly onto the HITL gate
        return self.sanity_client.mutate([{"createOrReplace": {
            "_id": f"drafts.{slugify(brief['title'])}",
            "_type": "article", "title": brief["title"], "body": draft}}])

CMS_ADAPTERS = {"wordpress": WordPressAdapter(), "contentful": ContentfulAdapter(),
                 "sanity": SanityAdapter()}
```

Note every adapter publishes to a draft state, never live — the CMS's own draft/publish distinction is reused as a second safety net on top of the HITL gate, not a replacement for it.

3.4 Graph assembly with conditional routing

```python
graph = StateGraph(ContentAgentState)

graph.add_node("detect_op", detect_opportunity_node)
graph.add_node("brief", generate_brief_node)
graph.add_node("draft", draft_generation_node)
graph.add_node("verify", web_verification_node)
graph.add_node("human_gate", hitl_gate_node)
graph.add_node("publish", cms_publish_node)
graph.add_node("monitor", post_publish_monitor_node)
```
*(The text provided in the prompt was truncated here. Please provide the remainder of the text if needed.)*
