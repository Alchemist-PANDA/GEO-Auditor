# API Architecture & Endpoint Specification

This document defines the platform APIs, including REST/GraphQL interfaces for configurations, analytical querying, logs forwarding, and enterprise authentication.

---

## 1. REST API Endpoint Definitions

All API endpoints are prefixed with `/api/v1` and require header authorization:
`Authorization: Bearer <workspace_token>`

### 1.1 Config & Scoping Services

#### `POST /workspaces` (Enterprise Org Provisioning)
* **Payload**:
  ```json
  {
    "company_name": "Acme Marketing",
    "initial_workspace": "Global Search"
  }
  ```
* **Response (201 Created)**:
  ```json
  {
    "workspace_id": "c76fb902-8611-4770-b747-8178a946c19f",
    "api_token": "pf_live_83b28f8..."
  }
  ```

#### `POST /brands` (Brand and Competitor setup)
* **Payload**:
  ```json
  {
    "name": "Nike",
    "domain": "nike.com",
    "competitor_domains": ["adidas.com", "puma.com"]
  }
  ```
* **Response (200 OK)**:
  ```json
  {
    "brand_id": "060d4b29-e85b-4395-8e7c-a496fb99281a",
    "competitors_created": 2
  }
  ```

#### `POST /prompts/seeds` (Initialize tracking list)
* **Payload**:
  ```json
  {
    "brand_id": "060d4b29-e85b-4395-8e7c-a496fb99281a",
    "vertical": "athletic_footwear",
    "seed_keywords": ["running shoes", "marathon training sneakers", "cushioned road shoes"]
  }
  ```
* **Response (202 Accepted)**:
  ```json
  {
    "job_id": "89028a30-e555-46aa-bf7d-2b7e19198642",
    "status": "processing_discovery"
  }
  ```

---

### 1.2 Ingest Services (CDN Webhook Forwarders)

#### `POST /ingest/logs` (Edge CDN Integration Target)
* **Headers**: `X-Profound-Verify: <shared_hmac_secret>`
* **Payload (Cloudflare/Fastly standard JSON fields)**:
  ```json
  {
    "client_site_id": "060d4b29-e85b-4395-8e7c-a496fb99281a",
    "events": [
      {
        "timestamp": "2026-06-20T10:15:30Z",
        "path": "/blog/best-cushioned-running-shoes",
        "user_agent": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/2.1; +http://openai.com/gptbot)",
        "source_ip": "20.15.22.4",
        "response_code": 200,
        "response_time_ms": 142
      }
    ]
  }
  ```
* **Response (200 OK)**:
  ```json
  {
    "status": "success",
    "ingested_count": 1
  }
  ```

---

## 2. GraphQL Serving API (Dashboard Analytics)

The frontend dashboard queries analytics and time-series metrics via GraphQL to allow flexible client-side drill-downs.

```graphql
type VisibilityStats {
  engine: String!
  visibilityScore: Float!
  averagePosition: Float
  sentimentPositivePct: Float!
  citationSharePct: Float!
}

type CompetitorMatrix {
  competitorId: ID!
  competitorName: String!
  visibilityScore: Float!
  shareOfVoice: Float!
}

type Query {
  # Main Analytics Panel
  brandOverview(
    brandId: ID!
    clusterId: ID
    startDate: String!
    endDate: String!
  ): [VisibilityStats!]!

  # Competitor Leaderboard
  competitorSOV(
    brandId: ID!
    clusterId: ID!
    period: String!
  ): [CompetitorMatrix!]!

  # Audit Optimization Signals
  pageAuditScore(
    url: String!
  ): PageAuditReport!
}

type PageAuditReport {
  overallScore: Int!
  signals: [AuditSignal!]!
}

type AuditSignal {
  category: String! # "semantic_alignment" | "schema" | "structure" | "fan_out" | "freshness"
  score: Int! # 0 - 100
  recommendation: String
  impactWeight: Float!
}
```

---

## 3. Enterprise IAM (OIDC/SAML integration)

Authentication at the Enterprise tier is gated by SAML 2.0 / OIDC integrations. 

1. **User Sign-In Redirect**: Users are redirected to `/api/v1/auth/sso/login?domain=acme.com`.
2. **SSO Provider Handshake**: The system validates assertion signatures against public keys configured in PostgreSQL.
3. **Workspace Token Issuance**: On successful authorization, the server issues a JWT token containing:
   - `sub`: User ID
   - `workspace_id`: Tenant identifier
   - `role`: Admin, Analyst, or Viewer (RBAC)

---

## 4. Architectural Summary Table

| Dimension | [CONFIRMED] Findings | [INFERRED] Systems Behavior | [ASSUMPTION] System Limits | [RECOMMENDATION] Optimization |
|---|---|---|---|---|
| **API Architecture** | Enterprise tier grants full API access; lower plans gate it. | GraphQL handles large group-bys and dynamic dashboard pivots. | API latency spikes during concurrent database exports. | Use Redis to cache GraphQL analytics queries with a 4-hour TTL. |
| **Ingestion Webhook** | Log telemetry does not require client JS scripts on pages. | Cloudflare logs are batch-posted directly to log ingest endpoints. | Rate limits on edge webhooks block high-traffic client sites. | Implement async queue dumping (AWS API Gateway → SQS) on the endpoint. |
| **RBAC Roles** | RBAC permissions cover Admin, Analyst, and Viewer tiers. | Viewers are blocked from editing prompt seeds or triggering runs. | SAML token asserts roles automatically during identity handshake. | Natively support map assertions (`memberOf` claims to system roles). |
| **CRM Integration** | No native CRM integration exists for closed-loop pipeline ROI. | Custom BI setups manually tie click ids to CRM logs. | Salesforce REST API limits restrict daily update pushes. | Build a batched nightly pipeline pushing citation attribution to contacts. |
