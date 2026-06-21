# Production Truth — Customer Journey Verification

**Date**: 2026-06-21 08:40:24 UTC

This document details the end-to-end execution of a customer journey under mock sandbox settings, validating every API transaction, database row modification, and worker process execution.

### Step 1: User Registration
* **API Request**: `POST /api/v1/workspaces/register`
* **Payload**:
```json
{
  "email": "real_customer_d573@example.com",
  "password": "CustomerSecuredPassword123!",
  "full_name": "Real Customer",
  "organization_name": "Customer Enterprise"
}
```
* **Status Code**: **201**
* **API Response**:
```json
{
  "message": "User registered successfully"
}
```

* **Database Rows Created**:
  - users (id: abe5dc25-e6b5-4bd4-af3d-900107822dbc, email: real_customer_d573@example.com, organization_id: d7d95873-cc44-4007-bdbb-132f43a6971f, role: org_admin)
  - organizations (id: d7d95873-cc44-4007-bdbb-132f43a6971f, name: Customer Enterprise)
* **Result**: **PASS**

---
### Step 2: User Login & JWT Retrieval
* **API Request**: `POST /api/v1/workspaces/token`
* **Payload**:
```json
{
  "email": "real_customer_d573@example.com",
  "password": "CustomerSecuredPassword123!"
}
```
* **Status Code**: **200**
* **API Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJhdXRoZW50aWNhdGVkIiwic3ViIjoiYWJlNWRjMjUtZTZiNS00YmQ0LWFmM2QtOTAwMTA3ODIyZGJjIiwiZW1haWwiOiJyZWFsX2N1c3RvbWVyX2Q1NzNAZXhhbXBsZS5jb20iLCJyb2xlIjoib3JnX2FkbWluIiwiZXhwIjoxNzgyMTE3NjI1fQ.zzk6Qmo0RT4voAiJZPIN3zFmcC19nOv8wEw2QvZltO0",
  "token_type": "bearer"
}
```

* **Result**: **PASS**

---
### Setup Step A: Workspace Creation
* **API Request**: `POST /api/v1/workspaces`
* **Payload**:
```json
{
  "name": "GEO Validation WS",
  "tier": "premium"
}
```
* **Status Code**: **201**
* **API Response**:
```json
{
  "name": "GEO Validation WS",
  "tier": "premium",
  "id": "963e49b9-65a4-4c57-8eec-eac862a4ed21",
  "organization_id": "d7d95873-cc44-4007-bdbb-132f43a6971f",
  "prompt_limit": 100,
  "prompts_used": 0,
  "created_at": "2026-06-21T08:40:25.957301"
}
```

* **Database Rows Created**:
  - workspaces (id: 963e49b9-65a4-4c57-8eec-eac862a4ed21, name: GEO Validation WS, organization_id: d7d95873-cc44-4007-bdbb-132f43a6971f, tier: premium)
* **Result**: **PASS**

---
### Setup Step B: Project Container Creation
* **API Request**: `POST /api/v1/workspaces/projects`
* **Payload**:
```json
{
  "name": "Validation Project",
  "workspace_id": "963e49b9-65a4-4c57-8eec-eac862a4ed21"
}
```
* **Status Code**: **201**
* **API Response**:
```json
{
  "name": "Validation Project",
  "id": "2c4480d7-feec-45ed-96bf-4f01bd60f814",
  "workspace_id": "963e49b9-65a4-4c57-8eec-eac862a4ed21",
  "created_at": "2026-06-21T08:40:26.004785"
}
```

* **Database Rows Created**:
  - projects (id: 2c4480d7-feec-45ed-96bf-4f01bd60f814, name: Validation Project, workspace_id: 963e49b9-65a4-4c57-8eec-eac862a4ed21)
* **Result**: **PASS**

---
### Step 3: Brand Onboarding
* **API Request**: `POST /api/v1/workspaces/brands`
* **Payload**:
```json
{
  "name": "ValidationBrand",
  "domain": "valbrand.com",
  "project_id": "2c4480d7-feec-45ed-96bf-4f01bd60f814"
}
```
* **Status Code**: **201**
* **API Response**:
```json
{
  "name": "ValidationBrand",
  "domain": "valbrand.com",
  "id": "5404216d-17eb-42a0-9c4c-8824bc9cdd30",
  "project_id": "2c4480d7-feec-45ed-96bf-4f01bd60f814",
  "created_at": "2026-06-21T08:40:26.045491"
}
```

* **Database Rows Created**:
  - brands (id: 5404216d-17eb-42a0-9c4c-8824bc9cdd30, name: ValidationBrand, domain: valbrand.com, project_id: 2c4480d7-feec-45ed-96bf-4f01bd60f814)
* **Result**: **PASS**

---
### Step 4: Competitor Configuration
* **API Request**: `POST /api/v1/workspaces/competitors`
* **Payload**:
```json
{
  "name": "ValCompetitor",
  "domain": "valcomp.com",
  "brand_id": "5404216d-17eb-42a0-9c4c-8824bc9cdd30"
}
```
* **Status Code**: **201**
* **API Response**:
```json
{
  "name": "ValCompetitor",
  "domain": "valcomp.com",
  "id": "e053f1cb-bd5a-4f93-ba4d-ec37dc6b5440",
  "brand_id": "5404216d-17eb-42a0-9c4c-8824bc9cdd30",
  "created_at": "2026-06-21T08:40:26.081836"
}
```

* **Database Rows Created**:
  - competitors (id: e053f1cb-bd5a-4f93-ba4d-ec37dc6b5440, name: ValCompetitor, domain: valcomp.com, brand_id: 5404216d-17eb-42a0-9c4c-8824bc9cdd30)
* **Result**: **PASS**

---
### Step 5: Create Prompts List
* **API Request**: `POST /api/v1/prompts`
* **Payload**:
```json
{
  "project_id": "2c4480d7-feec-45ed-96bf-4f01bd60f814",
  "prompts": [
    {
      "text": "What is the best business card platform, is ValidationBrand or ValCompetitor better?",
      "locale": "Global",
      "tags": [
        "Corporate Cards"
      ]
    }
  ]
}
```
* **Status Code**: **201**
* **API Response**:
```json
{
  "added_count": 1,
  "prompts": [
    {
      "text": "What is the best business card platform, is ValidationBrand or ValCompetitor better?",
      "locale": "Global",
      "tags": [
        "Corporate Cards"
      ],
      "id": "8374e6bd-80bb-48ee-99a4-06e940c96451",
      "project_id": "2c4480d7-feec-45ed-96bf-4f01bd60f814",
      "created_at": "2026-06-21T08:40:26.184453"
    }
  ]
}
```

* **Database Rows Created**:
  - prompts (id: 8374e6bd-80bb-48ee-99a4-06e940c96451, text: What is the best business card platform, is ValidationBrand or ValCompetitor better?, locale: Global, project_id: 2c4480d7-feec-45ed-96bf-4f01bd60f814)
* **Result**: **PASS**

---
### Step 6: Trigger Prompts Execution
* **API Request**: `POST /api/v1/prompts/run`
* **Payload**:
```json
{
  "project_id": "2c4480d7-feec-45ed-96bf-4f01bd60f814",
  "models": [
    "gpt-4o-mini"
  ]
}
```
* **Status Code**: **202**
* **API Response**:
```json
{
  "job_ids": [
    "job_run_135baee6-90a6-4943-8bf0-1584ababc05c"
  ],
  "status": "queued",
  "message": "Prompts queued across 1 models. Total jobs launched: 1."
}
```

* **Database Rows Created**:
  - prompt_runs (id: 135baee6-90a6-4943-8bf0-1584ababc05c, prompt_id: 8374e6bd-80bb-48ee-99a4-06e940c96451, model_id: gpt-4o-mini, status: PENDING)
* **Result**: **PASS**

---
### Step 7-10: Worker Execution & AI Calculations
* **Worker Logs**:
```
Executing prompt run 135baee6-90a6-4943-8bf0-1584ababc05c on model gpt-4o-mini
Prompt run 135baee6-90a6-4943-8bf0-1584ababc05c completed successfully
```
* **Database Rows Created**:
  - prompt_runs (id: 135baee6-90a6-4943-8bf0-1584ababc05c, status: COMPLETED)
  - responses (id: 119c8962-4f7e-438d-96d5-4e88eac9b904, raw_text: For enterprise teams, **American Express** is widely cited a..., sentiment_score: 0.00)
  - citations (id: 20abdb91-53b4-42bc-a20c-37a81a582573, source_id: e127b086-1f95-46da-94e3-13391a59ffb9, position_index: 62)
  - citations (id: 8caab297-d3a1-452a-a94a-6dc5deebde52, source_id: bb361748-2c9a-4955-b4a9-08d3fba14d64, position_index: 79)
  - citations (id: dd079a7a-f4d0-4aac-8e52-a0d4e5a7188b, source_id: 89fdc3d9-ce8f-432d-96b2-6121a3f70399, position_index: 91)
  - visibility_scores (id: b2a9bf2c-9881-4f21-a5b4-7d15354c8a99, visibility_score: 0.00)
  - share_of_voice (id: 5e958c73-f9b8-4876-8760-0b3d71e9358d, share_percentage: 0.00)
* **Result**: **PASS**

---
### Step 11: Recommendations Engine Run
* **API Request**: `POST /api/v1/recommendations/generate?project_id=2c4480d7-feec-45ed-96bf-4f01bd60f814`
* **Payload**:
```json
{{}}
```
* **Status Code**: **201**
* **API Response**:
```json
{
  "generated_count": 4,
  "message": "Generated 4 recommendations using rule engine.",
  "recommendations": [
    {
      "id": "99eb57b2-86d5-4377-b6b1-0167799c97a5",
      "title": "Add Structured Data for AI Parsing",
      "description": "Implement FAQ, HowTo, and Product schema markup on key pages. Structured data helps AI models extract accurate information about your brand.",
      "priority": "HIGH",
      "status": "active",
      "estimated_visibility_gain": 0.8,
      "created_at": "2026-06-21T08:40:31.162967",
      "actions": [
        {
          "id": "f55b94d8-06bc-4856-bf40-4f582db472b0",
          "action_text": "Add FAQ schema to top 10 landing pages.",
          "is_completed": false,
          "completed_at": null
        },
        {
          "id": "c83318f8-1b12-4270-a22c-787dc5ef3388",
          "action_text": "Implement Product schema on all product/service pages.",
          "is_completed": false,
          "completed_at": null
        },
        {
          "id": "53e389e1-af37-4c2b-bc86-e54d33000ea5",
          "action_text": "Add HowTo schema to tutorial and guide content.",
          "is_completed": false,
          "completed_at": null
        }
      ]
    },
    {
      "id": "3a0eb442-75e9-4d78-9814-c48e8a6b18bc",
      "title": "Optimize robots.txt for AI Search Crawlers",
      "description": "Ensure AI scrapers (GPTBot, ClaudeBot, Google-Extended, PerplexityBot) can access your product pages and knowledge base. Blocked crawlers = zero visibility.",
      "priority": "CRITICAL",
      "status": "active",
      "estimated_visibility_gain": 1.5,
      "created_at": "2026-06-21T08:40:31.159373",
      "actions": [
        {
          "id": "88ebc40e-528c-4b70-a77b-52929f172d76",
          "action_text": "Verify robots.txt allows GPTBot, ClaudeBot, Google-Extended, PerplexityBot.",
          "is_completed": false,
          "completed_at": null
        },
        {
          "id": "41e442d8-cd4c-4cf9-afc9-b2ed6821094a",
          "action_text": "Test crawler access using each bot's user-agent string.",
          "is_completed": false,
          "completed_at": null
        }
      ]
    },
    {
      "id": "2e726f5a-07f8-4d45-ba28-e92eff484b8d",
      "title": "Get cited on 3 new domains",
      "description": "These domains cite your competitors but not ValidationBrand: nerdwallet.com, rho.co, hbr.org. Getting listed on these platforms can significantly boost your visibility in AI-generated responses.",
      "priority": "HIGH",
      "status": "active",
      "estimated_visibility_gain": 0.3,
      "created_at": "2026-06-21T08:40:31.142430",
      "actions": [
        {
          "id": "739a514e-50e0-488b-a9a3-33dc49aa00e0",
          "action_text": "Submit ValidationBrand for listing/review on nerdwallet.com.",
          "is_completed": false,
          "completed_at": null
        },
        {
          "id": "d3200f08-ceb4-43f5-af16-573e25af9f20",
          "action_text": "Submit ValidationBrand for listing/review on rho.co.",
          "is_completed": false,
          "completed_at": null
        },
        {
          "id": "24a36307-7d77-4ffd-a23c-fea61dafac79",
          "action_text": "Submit ValidationBrand for listing/review on hbr.org.",
          "is_completed": false,
          "completed_at": null
        }
      ]
    },
    {
      "id": "3b7cad15-7b1e-42cb-9dd6-d749a9e44383",
      "title": "Improve Brand Mention Rate (currently 0%)",
      "description": "ValidationBrand is mentioned in only 0% of AI responses. Target: >50%. Create authoritative content that AI models can reference when answering queries about your industry.",
      "priority": "CRITICAL",
      "status": "active",
      "estimated_visibility_gain": 2.5,
      "created_at": "2026-06-21T08:40:31.118438",
      "actions": [
        {
          "id": "6b7d5100-15c7-4262-91ea-9aacb1909f17",
          "action_text": "Publish authoritative FAQ content on your website covering top industry queries.",
          "is_completed": false,
          "completed_at": null
        },
        {
          "id": "971c4268-e3a8-4f53-a181-f1ee186c121f",
          "action_text": "Create detailed comparison guides positioning your brand against alternatives.",
          "is_completed": false,
          "completed_at": null
        },
        {
          "id": "0f5f0980-87ce-402c-b167-413df547691c",
          "action_text": "Build backlinks from high-authority domains (.edu, .gov, .org) to boost AI training signal.",
          "is_completed": false,
          "completed_at": null
        }
      ]
    }
  ]
}
```

* **Database Rows Created**:
  - recommendations (id: 3b7cad15-7b1e-42cb-9dd6-d749a9e44383, title: Improve Brand Mention Rate (currently 0%), priority: CRITICAL, status: active)
  - recommendations (id: 2e726f5a-07f8-4d45-ba28-e92eff484b8d, title: Get cited on 3 new domains, priority: HIGH, status: active)
  - recommendations (id: 3a0eb442-75e9-4d78-9814-c48e8a6b18bc, title: Optimize robots.txt for AI Search Crawlers, priority: CRITICAL, status: active)
  - recommendations (id: 99eb57b2-86d5-4377-b6b1-0167799c97a5, title: Add Structured Data for AI Parsing, priority: HIGH, status: active)
* **Result**: **PASS**

---
### Step 12: Fetch Dashboard Analytics
* **API Request**: `GET /api/v1/analytics/visibility?project_id=2c4480d7-feec-45ed-96bf-4f01bd60f814`
* **Payload**:
```json
{{}}
```
* **Status Code**: **200**
* **API Response**:
```json
{
  "visibility_score": 0.0,
  "weekly_change": 0.0,
  "history": [
    {
      "date": "2026-06-21",
      "score": 0.0
    }
  ],
  "rankings": [
    {
      "rank": 1,
      "brand": "ValidationBrand",
      "score": 0.0,
      "change": 0.0
    },
    {
      "rank": 2,
      "brand": "ValCompetitor",
      "score": 0.0,
      "change": 0.0
    }
  ],
  "share_of_voice": 0.0,
  "share_of_voice_breakdown": [
    {
      "name": "ValidationBrand",
      "share": 0.0
    },
    {
      "name": "ValCompetitor",
      "share": 0.0
    }
  ]
}
```

* **Result**: **PASS**

---
### Verification Verdict

**GREEN = VERIFIED**
All 12 steps of the customer journey successfully executed and passed end-to-end.
