# Workers & Async Processing Blueprint

This document details the architecture of the background worker fleet, covering the asynchronous execution engine, extraction judges, clustering routines, and agent workflow state machines.

---

## 1. Multi-Model Query Runner (Execution Fleet)

The execution fleet queries search engines across multiple parameters (region, engine, model variant). 

### 1.1 Concurrency & Rate Limiting Strategy
To prevent provider bans and 429 rate limit exceptions, request execution is regulated using a distributed token-bucket scheduler:
* **API Ingestion**: Employs asyncio semaphores tuned to match API vendor token counts.
* **Browser-UI Scrapers**: Gated via strict browser limits (0.5 jobs/second per proxy IP) to simulate realistic human browsing patterns.

```python
import asyncio
from dataclasses import dataclass

@dataclass
class PromptJob:
    job_id: str
    prompt_text: str
    engine: str # chatgpt | claude | gemini | perplexity
    capture_method: str # 'api' | 'browser_ui'

ENGINE_LIMITS = {
    "chatgpt_api": 10, "chatgpt_browser": 1,
    "claude_api": 12, "gemini_api": 15, "perplexity_api": 5
}

async def run_prompt_job(job: PromptJob, semaphores: dict):
    # Route job to specific token-bucket gate
    sem_key = f"{job.engine}_{job.capture_method}"
    async with semaphores.get(sem_key, asyncio.Semaphore(1)):
        if job.capture_method == "api":
            raw_response = await call_model_api(job)
        else:
            raw_response = await call_browser_ui(job)
        
        # Save raw content to S3 and notify Message Bus
        run_id = await save_raw_payload(job, raw_response)
        await publish_to_message_bus(run_id, "model_responses")
```

---

## 2. NLP Extraction Worker ("LLM-as-Judge")

Once the query runner completes, the system parses the raw unstructured response using a fast, cost-effective judge model (e.g., `gpt-4o-mini`, `claude-3-5-haiku`) to extract structured mentions and links.

### 2.1 Extraction System Prompt
```
You are a structured data extraction engine. Analyze the raw text from an AI search result and extract ONLY the following JSON structure. If an item is not found, set its value to null. Output only valid JSON. Do not include markdown wraps or conversational commentary.

{
  "brand_mentions": [
    {
      "name": "string",
      "position_char": 105,
      "sentiment": 0.8, # scale from -1.0 (very negative) to 1.0 (very positive)
      "is_recommended": true, # whether the brand is recommended/compared favorably
      "confidence": 0.95
    }
  ],
  "citations": [
    {
      "url": "string",
      "anchor_text": "string",
      "position_char": 450
    }
  ],
  "overall_summary": "string"
}
```

---

## 3. Embedding & Clustering Worker

This worker reads raw conversations from the licensed panel feed and manages the query discovery taxonomy.

### 3.1 Nightly Re-Clustering Job (HDBSCAN)
Clustering runs on a two-speed schema to maintain responsiveness:
1. **Online Query Routing**: Incoming queries are converted to embeddings (using `text-embedding-3-large`) and assigned to the nearest cluster centroid in Qdrant (using HNSW distance).
2. **Nightly Reclustering**: An offline batch job pools all queries, runs HDBSCAN to define new clusters, splits over-merged categories, merges near-duplicates, and triggers an LLM summarization step to name and label the new cluster centroids.

---

## 4. Content Agent Orchestration (LangGraph Flow)

The content execution loop is orchestrated via a state graph with a durable checkpointer, forcing a human-in-the-loop (HITL) interrupt before publication.

```python
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END

class ContentState(TypedDict):
    brand_id: str
    opportunity: dict
    brief: dict | None
    draft: str | None
    draft_version: int
    claims_to_verify: list[dict]
    verification_results: list[dict]
    unverified_claim_count: int
    approval_status: Literal["pending", "approved", "needs_revision", "rejected"]
    reviewer_feedback: str | None
    cms_target: Literal["wordpress", "contentful", "sanity"]
    published_url: str | None

# Node Actions
def verify_claims(state: ContentState) -> ContentState:
    # Extracts factual statements in the draft and performs search engine verification checks
    claims = extract_claims_from_text(state["draft"])
    verification = []
    for claim in claims:
        search_hits = web_search_tool(claim["claim_text"])
        is_verified, source_url = check_source_grounding(claim["claim_text"], search_hits)
        verification.append({
            "claim_text": claim["claim_text"],
            "verified": is_verified,
            "source_url": source_url
        })
    state["verification_results"] = verification
    state["unverified_claim_count"] = sum(1 for v in verification if not v["verified"])
    return state

# State Routing Logic
def route_after_verification(state: ContentState):
    if state["unverified_claim_count"] > 0 and state["draft_version"] < 3:
        return "draft_generation" # Loop back for automatic model revision
    return "human_review_gate"

# LangGraph Build
builder = StateGraph(ContentState)
builder.add_node("detect_gap", detect_gap_node)
builder.add_node("create_brief", create_brief_node)
builder.add_node("draft_generation", draft_generation_node)
builder.add_node("verify_claims", verify_claims)
builder.add_node("human_review_gate", human_review_gate_node) # Pauses execution and serializes state
builder.add_node("cms_publish", cms_publish_node)

builder.set_entry_point("detect_gap")
builder.add_edge("detect_gap", "create_brief")
builder.add_edge("create_brief", "draft_generation")
builder.add_edge("draft_generation", "verify_claims")
builder.add_conditional_edges("verify_claims", route_after_verification)
# Flow from review gate is webhook-resumed
```

---

## 5. Architectural Summary Table

| Dimension | [CONFIRMED] Findings | [INFERRED] Systems Behavior | [ASSUMPTION] System Limits | [RECOMMENDATION] Optimization |
|---|---|---|---|---|
| **Query Runner** | Ingest executes runs against 10 engines. | Headless Playwright workers mimic mobile browser viewports to scrape responses. | Crawling UI accounts frequently hit captcha security blocks. | Primary collection via grounding APIs; fallback to scrapers. |
| **NLP Judges** | Judge models isolate brands, ranks, and citations from responses. | LLMs output schema-strict JSON arrays to simplify ingestion. | Judge errors (5-15%) skew final metrics. | Implement Weekly Human-in-the-Loop audits (50 sample runs). |
| **Topic Discovery** | HDBSCAN clustering processes parent prompts + query fan-outs. | Fast centroid mapping routes new queries before clustering runs. | Huge vector collections bottleneck clustering runtimes. | Map incoming records using Cosine ANN; run HDBSCAN nightly. |
| **LangGraph Execution** | The workflow utilizes briefs before full draft publishes. | State is persisted during user review pauses. | Synchronous process locks fail under high task loads. | Use PostgreSQL-backed checkpointers for asynchronous resume. |
