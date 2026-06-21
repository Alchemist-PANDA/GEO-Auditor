# Product Architecture & Workflows

This document establishes the product architecture, persona workflows, and automation progression for the GEO/AEO Platform. 

---

## 1. Core Product Strategy

The platform is designed as a **dashboard-first analytics and workflow utility** rather than a passive report generator. Its primary value proposition is to bridge the gap between search-engine optimization (SEO) and artificial intelligence answer engine visibility (GEO/AEO).

```
   [Panel Ingest] + [Execution Engine] + [CDN Integrations]
                          │
                          ▼
                 [Analytics Engine]
                          │
                          ▼
            [Actions & Agent Orchestration]
```

### [CONFIRMED] Multi-Engine Tracking Focus
Rather than aggregating multiple search engines into a single opaque score, the platform prioritizes exposing **granular, per-engine metrics** (e.g., ChatGPT vs. Gemini vs. Perplexity vs. Claude). This matches the reality that user traffic dynamics vary significantly across these models, and marketing resources must be allocated accordingly.

### [RECOMMENDATION] Agency Workspace Support
Profound historically enforced a hard limit of a **single workspace per account**, creating a significant friction point for agencies managing multiple client brands. To address this market opportunity, the architecture should natively support **hierarchical workspaces** (Account → Workspace/Client → Brand Profile) with role-based access control (RBAC).

---

## 2. User Workflows

The platform serves three main user personas:
1. **AEO/SEO Strategist**: Analyzes visibility metrics, identifies keyword/intent gaps, and designs content strategies.
2. **Content Creator**: Leverages briefs and AI-generated drafts to quickly publish grounded, citation-optimized pages.
3. **Chief Marketing Officer (CMO)**: Monitors high-level share-of-voice (SoV), sentiment trends, and ROI attribution.

### The Trust-Building Loop (Closed-Loop Content Optimization)

To convince enterprise marketing teams to adopt automated content creation, the system follows a strict, step-by-step pipeline. This builds data credibility before unlocking autonomous execution:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  1. ANALYZE │ ──> │  2. BRIEF   │ ──> │  3. DRAFT   │ ──> │  4. VERIFY  │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                   │
                                                                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ 7. MONITOR  │ <── │ 6. PUBLISH  │ <── │ 5. HITL GATE│ <──  Verification │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

1. **Analyze**: The system correlates prompt volumes (demand) with brand visibility and competitor citation share to detect high-value content gaps.
2. **Brief**: An automated content brief is generated, identifying target structures, competitor citations, and semantic gaps.
3. **Draft**: A draft is generated, utilizing proven GEO formatting guidelines (direct answers, citation-dense paragraphs).
4. **Verify**: Factual claims are parsed and cross-checked against live web search results to ground hallucination risks.
5. **HITL Gate (Human-In-The-Loop)**: The strategist reviews the draft, verification logs, and optimization suggestions, then approves or requests revision.
6. **Publish**: The approved draft is published to the target CMS as a staged "draft" state (Wordpress, Contentful, Sanity).
7. **Monitor**: The system monitors crawler logs (Agent Analytics) to see when AI search bots index the page, then measures if citations for target prompts improve.

---

## 3. Tiered Capabilities

The platform scales capabilities across three packages:

### MVP (Minimum Viable Product)
* **Goal**: Validate scoring engine metrics and basic AEO audits.
* **Tracking & Scale**: Up to 50 prompts, single engine tracking (ChatGPT).
* **Data Sources**: Direct OpenAI API execution (no panel integration, no residential proxy scraping).
* **Workflows**: Manual CSV export, basic rule-based checklist audits (AEO Content Score estimated via simple heading/schema checks).
* **Deployment**: Single-node server, local files.

### Production
* **Goal**: Full automated analytics, discovery, and CMS drafting capabilities.
* **Tracking & Scale**: Up to 1,000 prompts, 5 core engines tracked (ChatGPT, Claude, Gemini, Perplexity, Copilot).
* **Data Sources**: Regular active prompt executions with mobile proxy rotation, licensed panel feed integrations for prompt discovery.
* **Workflows**: LangGraph-based brief and draft generation, web verification nodes, Slack/Teams notification integrations.
* **Analytics**: Real-time CDN log collection (Cloudflare Workers, CloudFront), IP-range bot verification.

### Enterprise
* **Goal**: Custom integrations, advanced machine learning, and SOC2/HIPAA compliance.
* **Tracking & Scale**: 10,000+ prompts, 10+ engines (including specialized and regional LLMs).
* **Data Sources**: Fully integrated multi-region panel extrapolation model with regional/demographic breakdowns.
* **Workflows**: Multi-tenant agency workspaces, custom CMS webhooks, automatic feedback loops updating the scoring models, OIDC/SAML SSO, RBAC.
* **Analytics**: Advanced log routing pipelines, global network benchmarking against millions of pages.

---

## 4. Architectural Summary Table

| Dimension | [CONFIRMED] Findings | [INFERRED] Systems Behavior | [ASSUMPTION] System Limits | [RECOMMENDATION] Optimization |
|---|---|---|---|---|
| **Engine Focus** | Dashboard splits metrics per-engine; blended scores are secondary. | Direct API outputs differ from logged-in consumer UI outputs. | UI-scraping consumer interfaces violates engine ToS. | Primary API grounding + small UI-scraped validation sample. |
| **Workflow Steps** | Sequencing: Analyze → Brief → Draft → Publish. | Publishing relies on an asynchronous human-in-the-loop gate. | CMS APIs require structured draft staging. | Enforce "Stage, Don't Ship" at the API layer for Wordpress/Sanity. |
| **Workspace Scope** | Single workspace limit per enterprise account. | The system lacks agency-tier dashboards or sub-org accounts. | Enterprise models must isolate tenant databases. | Natively build tenant-isolation schemas in Postgres/ClickHouse. |
| **ROI Attribution** | ROI attribution is missing; traffic is siloed from revenue. | Marketers rely on external Looker/Tableau dashboards to map ROI. | CRM integrations (Hubspot/Salesforce) are absent. | Create a direct CRM connector mapping citation referrers to pipeline. |
