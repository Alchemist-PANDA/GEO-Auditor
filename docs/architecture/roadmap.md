# Platform Implementation Roadmap & Sequencing

This document defines the phased implementation plan, scheduling targets, and execution dependencies for the platform.

---

## 1. The Automation Sequencing Constraint

A key learning from the reverse engineering of existing platforms is that **data credibility is the prerequisite for automation adoption**. Marketing teams will not authorize an AI agent to publish content under their brand name until they trust the underlying visibility data and scoring models. 

The roadmap is structured to build trust step-by-step before enabling autonomous publishing features:

```
                  ┌──────────────────────────────────────────┐
                  │          PHASE 1: ANALYTICS CORE         │
                  │  Build database, APIs, and basic audits  │
                  └──────────────────────────────────────────┘
                                       │
                                       ▼
                  ┌──────────────────────────────────────────┐
                  │        PHASE 2: CONTENT ASSISTANT        │
                  │ Generate briefs and verify drafts (HITL) │
                  └──────────────────────────────────────────┘
                                       │
                                       ▼
                  ┌──────────────────────────────────────────┐
                  │       PHASE 3: CLOSED-LOOP AGENT         │
                  │ Direct publishing and correlation alerts │
                  └──────────────────────────────────────────┘
```

---

## 2. Implementation Phases

### Phase 1: Analytics & Audit Core (MVP)
* **Goal**: Deliver a baseline visibility dashboard and basic page audits to validate the data model.
* **Duration**: 1–2 Quarters.
* **Core Tasks**:
  1. Set up the core database architecture (PostgreSQL and pgvector schema configurations).
  2. Implement direct API adapters to fetch model responses (focusing on ChatGPT and Perplexity).
  3. Build the first iteration of the AEO Content Score model, evaluating basic page elements (headings, schemas, and semantic similarity).
  4. Develop the public HTML email audit tool for lead generation.
  5. Provide manual CSV/JSON data exports for client reporting.

### Phase 2: Crawler Analytics & Content Assistant (Production)
* **Goal**: Scale ingestion capabilities, integrate real-time log tracking, and launch guided content workflows.
* **Duration**: 2–3 Quarters.
* **Core Tasks**:
  1. Build headless browser query runners using Playwright, executing prompts across proxy pools.
  2. Integrate CDN log forwarders (Cloudflare and CloudFront) and implement IP-range bot verification.
  3. Deploy Qdrant to manage prompt embeddings and implement HDBSCAN clustering for the Prompt Discovery pipeline.
  4. Launch the Actions Center dashboard, generating manual optimization recommendations and content briefs.
  5. Enable manual content drafting features guided by optimization metrics.

### Phase 3: Closed-Loop Automation & Enterprise IAM (Enterprise)
* **Goal**: Support agency workspaces, enable automated publishing pipelines, and resolve the CRM ROI attribution gap.
* **Duration**: 1–2 Quarters.
* **Core Tasks**:
  1. Natively support multi-tenant agency workspaces and sub-organization client profiles.
  2. Integrate OIDC/SAML single sign-on (SSO) systems and map role-based permissions (RBAC).
  3. Deploy CMS adapters (WordPress, Contentful, Sanity) to export agent-drafted content directly as drafts.
  4. Build the Google Analytics 4 (GA4) and CRM connectors (HubSpot, Salesforce) to track revenue attribution.
  5. Set up the automated feedback loop, automatically updating the AEO Content Score model using live citation outcomes.

---

## 3. Architectural Summary Table

| Dimension | [CONFIRMED] Findings | [INFERRED] Systems Behavior | [ASSUMPTION] System Limits | [RECOMMENDATION] Optimization |
|---|---|---|---|---|
| **Roadmap Phases** | Development follows a staged approach: Analyze → Brief → Draft. | Trust must be built in scoring datasets before users allow CMS automation. | CMS access settings limit direct API publishing keys. | Start by publishing content as drafts, keeping final approval manual. |
| **Data Ingestion** | Ingestion scales from simple API trackers to global panel networks. | Early phases run direct API calls; panel integrations are added later. | Access to panel datasets requires significant subscription investments. | Use synthetic prompts and API wrappers for early platform phases. |
| **SSO & RBAC** | Enterprise accounts require SAML/OIDC SSO configurations. | RBAC permissions are configured during tenant onboarding. | SSO configs require manual updates from customer IT teams. | Use standard OIDC provider libraries to simplify integration setup. |
| **Attribution** | Direct ROI attribution is missing from existing platforms. | Attribution is resolved by exporting logs to external BI dashboards. | Direct CRM modifications require dedicated API integration access. | Build attribution dashboards inside the client platform workspace. |
