# Launch Simulation Report

**Date**: 2026-06-21 09:12:15 UTC

This document details the simulation of an end-to-end customer journey on a clean production database, capturing all payloads and database evidence.

## Simulation Flow Evidence

### 1. User Registration
* **API Request**: `POST /api/v1/workspaces/register`
* **Request Payload**:
```json
{
  "email": "customer_simulation_87d7@example.com",
  "password": "SimulationPassword123!",
  "full_name": "Simulation Customer",
  "organization_name": "Simulation Enterprise"
}
```
* **Status Code**: **201**
* **API Response Payload**:
```json
{
  "message": "User registered successfully"
}
```

* **Database Evidence**:
  - users (id: fc34dc95-2792-4421-b9fb-85a609b9ce51, email: customer_simulation_87d7@example.com, organization_id: 63b0b134-cca5-49b8-a769-46a3889f9924)
  - organizations (id: 63b0b134-cca5-49b8-a769-46a3889f9924, name: Simulation Enterprise)
* **Verdict**: **PASS**

---
### 2. User Login & JWT Retrieval
* **API Request**: `POST /api/v1/workspaces/token`
* **Request Payload**:
```json
{
  "email": "customer_simulation_87d7@example.com",
  "password": "SimulationPassword123!"
}
```
* **Status Code**: **200**
* **API Response Payload**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJhdXRoZW50aWNhdGVkIiwic3ViIjoiZmMzNGRjOTUtMjc5Mi00NDIxLWI5ZmItODVhNjA5YjljZTUxIiwiZW1haWwiOiJjdXN0b21lcl9zaW11bGF0aW9uXzg3ZDdAZXhhbXBsZS5jb20iLCJyb2xlIjoib3JnX2FkbWluIiwiZXhwIjoxNzgyMTE5NTM4fQ.bMk4fcCMPJRRSM1ZQCRjafnX53ep9CdMri33j7GZOUk",
  "token_type": "bearer"
}
```

* **Verdict**: **PASS**

---
### 3. Brand Onboarding
* **API Request**: `POST /api/v1/workspaces/brands`
* **Request Payload**:
```json
{
  "name": "SimulationBrand",
  "domain": "simbrand.com",
  "project_id": "0417ba7d-97be-41f5-8376-8d842620c9a4"
}
```
* **Status Code**: **201**
* **API Response Payload**:
```json
{
  "name": "SimulationBrand",
  "domain": "simbrand.com",
  "id": "7f91b930-784c-470a-98d1-fc1064259f96",
  "project_id": "0417ba7d-97be-41f5-8376-8d842620c9a4",
  "created_at": "2026-06-21T09:12:18.176476"
}
```

* **Database Evidence**:
  - brands (id: 7f91b930-784c-470a-98d1-fc1064259f96, name: SimulationBrand, domain: simbrand.com)
* **Verdict**: **PASS**

---
### 4. Competitor Configuration
* **API Request**: `POST /api/v1/workspaces/competitors`
* **Request Payload**:
```json
{
  "name": "SimCompetitor",
  "domain": "simcomp.com",
  "brand_id": "7f91b930-784c-470a-98d1-fc1064259f96"
}
```
* **Status Code**: **201**
* **API Response Payload**:
```json
{
  "name": "SimCompetitor",
  "domain": "simcomp.com",
  "id": "dd0eedd9-449a-4dc8-8ba7-0a25c4db8f13",
  "brand_id": "7f91b930-784c-470a-98d1-fc1064259f96",
  "created_at": "2026-06-21T09:12:18.234373"
}
```

* **Database Evidence**:
  - competitors (id: dd0eedd9-449a-4dc8-8ba7-0a25c4db8f13, name: SimCompetitor, domain: simcomp.com)
* **Verdict**: **PASS**

---
### 5. Prompt Configuration
* **API Request**: `POST /api/v1/prompts`
* **Request Payload**:
```json
{
  "project_id": "0417ba7d-97be-41f5-8376-8d842620c9a4",
  "prompts": [
    {
      "text": "What is the best platform, is SimulationBrand or SimCompetitor preferred?",
      "locale": "Global",
      "tags": [
        "Simulation Tag"
      ]
    }
  ]
}
```
* **Status Code**: **201**
* **API Response Payload**:
```json
{
  "added_count": 1,
  "prompts": [
    {
      "text": "What is the best platform, is SimulationBrand or SimCompetitor preferred?",
      "locale": "Global",
      "tags": [
        "Simulation Tag"
      ],
      "id": "f611b55f-122d-481b-bc40-65efa5abe1b5",
      "project_id": "0417ba7d-97be-41f5-8376-8d842620c9a4",
      "created_at": "2026-06-21T09:12:18.322604"
    }
  ]
}
```

* **Database Evidence**:
  - prompts (id: f611b55f-122d-481b-bc40-65efa5abe1b5, text: What is the best platform, is SimulationBrand or SimCompetitor preferred?)
* **Verdict**: **PASS**

---
### 6. Trigger Prompts Scan
* **API Request**: `POST /api/v1/prompts/run`
* **Request Payload**:
```json
{
  "project_id": "0417ba7d-97be-41f5-8376-8d842620c9a4",
  "models": [
    "gpt-4o-mini"
  ]
}
```
* **Status Code**: **202**
* **API Response Payload**:
```json
{
  "job_ids": [
    "job_run_8770acd6-2670-4542-8ee0-016c4ddaef59"
  ],
  "status": "queued",
  "message": "Prompts queued across 1 models. Total jobs launched: 1."
}
```

* **Database Evidence**:
  - prompt_runs (id: 8770acd6-2670-4542-8ee0-016c4ddaef59, status: PENDING)
* **Verdict**: **PASS**

---
### Background Worker Task Execution
* **Database Evidence**:
  - prompt_runs (id: 8770acd6-2670-4542-8ee0-016c4ddaef59, status: COMPLETED)
  - responses (id: 5a14b76a-3f67-4add-ab75-36db78733330, raw_text: For enterprise teams, **American Express** is widely cited a...)
  - citations (id: e53b6aa1-b34b-467b-8272-294a23ee336c, url: 772d5469-d020-4a15-8ea7-0ca02f1e51a5)
  - citations (id: 5852327a-c6d4-43c2-b8bf-bc9c90f408bc, url: c8d1b0f0-f541-4288-b1f5-e350b15c95ca)
  - citations (id: 6f3cf615-cc1e-46e7-be0d-bca4073f142c, url: a34bf201-b900-4d1c-b0ef-1575ad4a7aaf)
  - visibility_scores (id: a15f185a-748d-4e04-a5c0-7e4aa452b3f8, visibility_score: 0.00)
  - share_of_voice (id: 7482ab0d-233c-462c-8fbd-0470fcf1a03c, share_percentage: 0.00)
* **Verdict**: **PASS**

---
### 7. Recommendations Engine Run
* **API Request**: `POST /api/v1/recommendations/generate?project_id=0417ba7d-97be-41f5-8376-8d842620c9a4`
* **Request Payload**:
```json
{{}}
```
* **Status Code**: **201**
* **API Response Payload**:
```json
{
  "generated_count": 4,
  "message": "Generated 4 recommendations using rule engine.",
  "recommendations": [
    {
      "id": "003a605b-2ad3-4ad8-980e-3965189167a2",
      "title": "Add Structured Data for AI Parsing",
      "description": "Implement FAQ, HowTo, and Product schema markup on key pages. Structured data helps AI models extract accurate information about your brand.",
      "priority": "HIGH",
      "status": "active",
      "estimated_visibility_gain": 0.8,
      "created_at": "2026-06-21T09:12:23.407522",
      "actions": [
        {
          "id": "5f1e845f-106b-4891-a50e-b1a4edd2422e",
          "action_text": "Add FAQ schema to top 10 landing pages.",
          "is_completed": false,
          "completed_at": null
        },
        {
          "id": "c738aa11-eb71-4855-bcd3-c3cf263e28e4",
          "action_text": "Implement Product schema on all product/service pages.",
          "is_completed": false,
          "completed_at": null
        },
        {
          "id": "cae417eb-2c6a-4fe0-ba0d-fd52ea2a1df0",
          "action_text": "Add HowTo schema to tutorial and guide content.",
          "is_completed": false,
          "completed_at": null
        }
      ]
    },
    {
      "id": "6d23f7b3-83e3-4db1-a84f-13bb53081b39",
      "title": "Optimize robots.txt for AI Search Crawlers",
      "description": "Ensure AI scrapers (GPTBot, ClaudeBot, Google-Extended, PerplexityBot) can access your product pages and knowledge base. Blocked crawlers = zero visibility.",
      "priority": "CRITICAL",
      "status": "active",
      "estimated_visibility_gain": 1.5,
      "created_at": "2026-06-21T09:12:23.404164",
      "actions": [
        {
          "id": "c257992f-83e9-4900-ba79-b649630ac616",
          "action_text": "Verify robots.txt allows GPTBot, ClaudeBot, Google-Extended, PerplexityBot.",
          "is_completed": false,
          "completed_at": null
        },
        {
          "id": "77dd6d59-6d5a-4485-baa8-f793759a2de6",
          "action_text": "Test crawler access using each bot's user-agent string.",
          "is_completed": false,
          "completed_at": null
        }
      ]
    },
    {
      "id": "568a4b30-168b-4eb6-9ff7-c8a050a6ef82",
      "title": "Get cited on 3 new domains",
      "description": "These domains cite your competitors but not SimulationBrand: nerdwallet.com, hbr.org, rho.co. Getting listed on these platforms can significantly boost your visibility in AI-generated responses.",
      "priority": "HIGH",
      "status": "active",
      "estimated_visibility_gain": 0.3,
      "created_at": "2026-06-21T09:12:23.386961",
      "actions": [
        {
          "id": "7c0bffee-e153-4f87-be98-b7a2c72ddb6f",
          "action_text": "Submit SimulationBrand for listing/review on nerdwallet.com.",
          "is_completed": false,
          "completed_at": null
        },
        {
          "id": "5c2d4ea8-7915-4701-9698-7f9faf1a4c1f",
          "action_text": "Submit SimulationBrand for listing/review on hbr.org.",
          "is_completed": false,
          "completed_at": null
        },
        {
          "id": "0e360dc6-b0ba-40eb-a1b0-801eda36e4b5",
          "action_text": "Submit SimulationBrand for listing/review on rho.co.",
          "is_completed": false,
          "completed_at": null
        }
      ]
    },
    {
      "id": "bb709655-0d24-4a15-81ce-41b10ae03ff8",
      "title": "Improve Brand Mention Rate (currently 0%)",
      "description": "SimulationBrand is mentioned in only 0% of AI responses. Target: >50%. Create authoritative content that AI models can reference when answering queries about your industry.",
      "priority": "CRITICAL",
      "status": "active",
      "estimated_visibility_gain": 2.5,
      "created_at": "2026-06-21T09:12:23.367949",
      "actions": [
        {
          "id": "96f740f5-26fb-46da-a335-e94792122463",
          "action_text": "Publish authoritative FAQ content on your website covering top industry queries.",
          "is_completed": false,
          "completed_at": null
        },
        {
          "id": "00a0df19-cc24-401a-9e05-212a84b95d86",
          "action_text": "Create detailed comparison guides positioning your brand against alternatives.",
          "is_completed": false,
          "completed_at": null
        },
        {
          "id": "63152f9e-e68d-4f9c-8900-19dcef460c78",
          "action_text": "Build backlinks from high-authority domains (.edu, .gov, .org) to boost AI training signal.",
          "is_completed": false,
          "completed_at": null
        }
      ]
    }
  ]
}
```

* **Database Evidence**:
  - recommendations (id: bb709655-0d24-4a15-81ce-41b10ae03ff8, title: Improve Brand Mention Rate (currently 0%), priority: CRITICAL)
  - recommendations (id: 568a4b30-168b-4eb6-9ff7-c8a050a6ef82, title: Get cited on 3 new domains, priority: HIGH)
  - recommendations (id: 6d23f7b3-83e3-4db1-a84f-13bb53081b39, title: Optimize robots.txt for AI Search Crawlers, priority: CRITICAL)
  - recommendations (id: 003a605b-2ad3-4ad8-980e-3965189167a2, title: Add Structured Data for AI Parsing, priority: HIGH)
* **Verdict**: **PASS**

---
### 8. Fetch Dashboard Analytics
* **API Request**: `GET /api/v1/analytics/visibility?project_id=0417ba7d-97be-41f5-8376-8d842620c9a4`
* **Request Payload**:
```json
{{}}
```
* **Status Code**: **200**
* **API Response Payload**:
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
      "brand": "SimulationBrand",
      "score": 0.0,
      "change": 0.0
    },
    {
      "rank": 2,
      "brand": "SimCompetitor",
      "score": 0.0,
      "change": 0.0
    }
  ],
  "share_of_voice": 0.0,
  "share_of_voice_breakdown": [
    {
      "name": "SimulationBrand",
      "share": 0.0
    },
    {
      "name": "SimCompetitor",
      "share": 0.0
    }
  ]
}
```

* **Verdict**: **PASS**

---
## Verdict

**GREEN = VERIFIED**
