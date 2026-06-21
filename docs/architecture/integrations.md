# Integrations & API Adapters Specification

This document defines the integration interfaces, target API schemas, authentication protocols, and data mappings required to connect CMS systems, web analytics, and CRM platforms.

---

## 1. CMS Publishing Adapters (The Staging Rule)

To protect brand reputation, CMS adapters publish generated content in a staged draft state rather than publishing live directly.

```
                  ┌──────────────────────┐
                  │    Agent Approved    │
                  └──────────────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │   Staging Adapters   │
                  └──────────────────────┘
                 /           │            \
                /            │             \
               ▼             ▼              ▼
         [WordPress]   [Contentful]      [Sanity]
         Draft State    Draft Space    Draft Mutation
```

### 1.1 WordPress Adapter
* **Authentication**: Application Passwords configured via WordPress REST API credentials.
* **API Target**: `POST /wp-json/wp/v2/posts`
* **JSON Payload**:
  ```json
  {
    "title": "Optimized Cushioned Running Shoes Guide",
    "content": "<!-- Direct Answer Paragraph --> ...",
    "status": "draft",
    "categories": [12],
    "meta": {
      "aeo_optimized_prompt": "best cushioned running shoes"
    }
  }
  ```

### 1.2 Contentful Adapter
* **Authentication**: Content Management Token (CMA) bearer authentication.
* **API Target**: `POST /spaces/{space_id}/environments/{environment_id}/entries`
* **JSON Payload**:
  ```json
  {
    "fields": {
      "title": { "en-US": "Optimized Cushioned Running Shoes Guide" },
      "body": { "en-US": "..." },
      "status": { "en-US": "Draft" }
    }
  }
  ```

### 1.3 Sanity Adapter
* **Authentication**: Sanity Write Access Token.
* **API Target**: Mutation API `POST /v1/data/mutate/{dataset}`
* **JSON Payload**:
  ```json
  {
    "mutations": [
      {
        "createOrReplace": {
          "_id": "drafts.best-cushioned-running-shoes",
          "_type": "article",
          "title": "Optimized Cushioned Running Shoes Guide",
          "body": "..."
        }
      }
    ]
  }
  ```

---

## 2. Google Analytics 4 (GA4) Traffic Sync

To track organic visibility, the platform pulls AI referral sessions from GA4.

* **API Target**: Google Analytics Data API v1beta.
* **Dimension Filter**: Matches referrer queries on known engine domains (e.g., `google.com` with AI overview parameters, `perplexity.ai`, `chatgpt.com`).
* **Metric Extraction**: Daily count of active sessions and conversion goals generated from those sessions.

---

## 3. CRM Integrations (Attribution Moat)

A common issue in GEO dashboards is the lack of direct ROI mapping (AI visibility vs. final revenue). The platform addresses this by bridging organic traffic referrals to CRM pipeline deals.

```
  [AI Referral Session] ──> [Append Session ID to Form Intake]
                                          │
                                          ▼
                             [Sync to Salesforce/HubSpot]
                                          │
                                          ▼
                             [Correlate Deal Value in DB]
```

### 3.1 Closed-Loop Salesforce Mapping
1. **Referral Tracking**: Custom scripts parse incoming traffic referrers, detecting AI search engines.
2. **Session Persistence**: Appends the session ID and referrer tag (`utm_medium=ai_search`) to lead capture forms.
3. **CRM Sync**: When a lead registers, it is sent to Salesforce with custom lead field parameters:
   - `LeadSource`: "Organic AI Search"
   - `AI_Referrer_Engine__c`: "Perplexity"
4. **Attribution Rollup**: A background job queries the Salesforce API nightly to match closed-won deals with historical AI referral sessions, populating the platform's ROI attribution dashboard:

$$\text{AEO Revenue Impact} = \sum \text{Value of Closed Deals where LeadSource} = \text{"Organic AI Search"}$$

---

## 4. Architectural Summary Table

| Dimension | [CONFIRMED] Findings | [INFERRED] Systems Behavior | [ASSUMPTION] System Limits | [RECOMMENDATION] Optimization |
|---|---|---|---|---|
| **CMS Adapter** | Adapters stage drafts to WordPress, Contentful, and Sanity. | Adapters format drafts to match CMS target schemas. | Auto-publishing content live risks publishing hallucinations. | Enforce "draft" status settings at the API payload layer. |
| **GA4 Connector** | Integrations map referral sessions from organic search engines. | Traffic referrers are parsed from standard client HTTP headers. | Dynamic engine routing limits standard referrer header values. | Capture custom query parameters to isolate AI traffic from standard search. |
| **CRM Pipeline** | No native HubSpot or Salesforce CRM integration exists. | Marketing teams run manual CSV exports to associate pipeline leads. | Salesforce API rate limits restrict frequent database syncs. | Run daily batched delta queries instead of streaming CRM updates. |
| **Authentication** | Platform security supports SAML/OIDC SSO profiles. | Identity mapping is managed during client tenant provisioning. | Multi-tenant clients need isolated workspace configurations. | Provision workspace tokens dynamically for each tenant. |
