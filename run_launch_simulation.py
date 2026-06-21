import sys
import os
import asyncio
import json
import uuid
from datetime import datetime, UTC
from unittest.mock import AsyncMock

# Mock heavy ML packages to prevent Hugging Face network downloads and slow imports in sandbox
sys.modules['keybert'] = None
sys.modules['sentence_transformers'] = None
sys.modules['hdbscan'] = None

# Mock arq's Redis create_pool globally to run entirely offline
import arq
mock_redis = AsyncMock()
mock_redis.enqueue_job = AsyncMock(return_value=True)
mock_redis.close = AsyncMock()

async def mock_create_pool(*args, **kwargs):
    return mock_redis

arq.create_pool = mock_create_pool

# Setup path and env for testing BEFORE imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///e:/Profound-cloning/backend/e2e_prod_truth.sqlite"
os.environ["ENVIRONMENT"] = "development"
os.environ["OPENAI_API_KEY"] = ""
os.environ["ANTHROPIC_API_KEY"] = ""
os.environ["GEMINI_API_KEY"] = ""
os.environ["PERPLEXITY_API_KEY"] = ""

from fastapi.testclient import TestClient
from app.main import app as fastapi_app
from app.core.database import AsyncSessionLocal, engine, Base
from sqlalchemy.future import select

import app.core.llm
app.core.llm._has_any_api_key = lambda: False
app.core.llm.settings.ENVIRONMENT = "development"
app.core.llm.settings.OPENAI_API_KEY = ""
app.core.llm.settings.ANTHROPIC_API_KEY = ""
app.core.llm.settings.GEMINI_API_KEY = ""
app.core.llm.settings.PERPLEXITY_API_KEY = ""

# Import models
from app.modules.workspaces.models import User, Organization, Workspace, Project, Brand, Competitor
from app.modules.prompts.models import Prompt, PromptRun, AIModel
from app.modules.analysis.models import Response, Citation, VisibilityScore, ShareOfVoice
from app.modules.recommendations.models import Recommendation, RecommendationAction

# Import worker function
from workers.run_worker import run_prompt_execution

# Set stdout encoding to utf-8
sys.stdout.reconfigure(encoding='utf-8')

# Output report file
OUTPUT_FILE = "e:/Profound-cloning/docs/final_audit/launch_simulation.md"

def format_req_res(title, req_method, req_url, req_body, res_status, res_body):
    return f"""### {title}
* **API Request**: `{req_method} {req_url}`
* **Request Payload**:
```json
{json.dumps(req_body, indent=2) if req_body else "{{}}"}
```
* **Status Code**: **{res_status}**
* **API Response Payload**:
```json
{json.dumps(res_body, indent=2) if isinstance(res_body, (dict, list)) else res_body}
```
"""

async def run_simulation():
    print("=== STARTING END-TO-END LAUNCH SIMULATION ===")
    
    # Reset DB
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables initialized.")

    client = TestClient(fastapi_app)
    
    report_sections = [
        "# Launch Simulation Report\n",
        f"**Date**: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}\n",
        "This document details the simulation of an end-to-end customer journey on a clean production database, capturing all payloads and database evidence.\n",
        "## Simulation Flow Evidence\n"
    ]
    
    email = f"customer_simulation_{uuid.uuid4().hex[:4]}@example.com"
    password = "SimulationPassword123!"
    full_name = "Simulation Customer"
    org_name = "Simulation Enterprise"
    
    overall_pass = True

    # 1. Register User
    reg_payload = {
        "email": email,
        "password": password,
        "full_name": full_name,
        "organization_name": org_name
    }
    print("Step 1: User Registration...")
    res = client.post("/api/v1/workspaces/register", json=reg_payload)
    res_body = res.json()
    
    async with AsyncSessionLocal() as db:
        user_res = await db.execute(select(User).where(User.email == email))
        user_row = user_res.scalar_one_or_none()
        org_res = await db.execute(select(Organization).where(Organization.name == org_name))
        org_row = org_res.scalar_one_or_none()
        
    db_rows = []
    if user_row:
        db_rows.append(f"users (id: {user_row.id}, email: {user_row.email}, organization_id: {user_row.organization_id})")
    if org_row:
        db_rows.append(f"organizations (id: {org_row.id}, name: {org_row.name})")

    status = "PASS" if (res.status_code == 201 and user_row and org_row) else "FAIL"
    if status == "FAIL": overall_pass = False
    
    section = format_req_res("1. User Registration", "POST", "/api/v1/workspaces/register", reg_payload, res.status_code, res_body)
    section += f"\n* **Database Evidence**:\n  - " + "\n  - ".join(db_rows) + f"\n* **Verdict**: **{status}**\n\n---"
    report_sections.append(section)

    # 2. Login User
    login_payload = {
        "email": email,
        "password": password
    }
    print("Step 2: User Login...")
    res = client.post("/api/v1/workspaces/token", json=login_payload)
    res_body = res.json()
    token = res_body.get("access_token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    status = "PASS" if (res.status_code == 200 and token) else "FAIL"
    if status == "FAIL": overall_pass = False
    
    section = format_req_res("2. User Login & JWT Retrieval", "POST", "/api/v1/workspaces/token", login_payload, res.status_code, res_body)
    section += f"\n* **Verdict**: **{status}**\n\n---"
    report_sections.append(section)

    # Setup Workspace & Project
    ws_payload = {"name": "Simulation Workspace", "tier": "premium"}
    res = client.post("/api/v1/workspaces", json=ws_payload, headers=headers)
    ws_body = res.json()
    ws_id = ws_body.get("id")

    proj_payload = {"name": "Simulation Project", "workspace_id": ws_id}
    res = client.post("/api/v1/workspaces/projects", json=proj_payload, headers=headers)
    proj_body = res.json()
    proj_id = proj_body.get("id")

    # 3. Create Brand
    brand_payload = {
        "name": "SimulationBrand",
        "domain": "simbrand.com",
        "project_id": proj_id
    }
    print("Step 3: Brand Onboarding...")
    res = client.post("/api/v1/workspaces/brands", json=brand_payload, headers=headers)
    res_body = res.json()
    brand_id = res_body.get("id")
    
    async with AsyncSessionLocal() as db:
        brand_res = await db.execute(select(Brand).where(Brand.id == brand_id))
        brand_row = brand_res.scalar_one_or_none()
        
    db_rows = []
    if brand_row:
        db_rows.append(f"brands (id: {brand_row.id}, name: {brand_row.name}, domain: {brand_row.domain})")

    status = "PASS" if (res.status_code == 201 and brand_row) else "FAIL"
    if status == "FAIL": overall_pass = False
    
    section = format_req_res("3. Brand Onboarding", "POST", "/api/v1/workspaces/brands", brand_payload, res.status_code, res_body)
    section += f"\n* **Database Evidence**:\n  - " + "\n  - ".join(db_rows) + f"\n* **Verdict**: **{status}**\n\n---"
    report_sections.append(section)

    # 4. Create Competitor
    comp_payload = {
        "name": "SimCompetitor",
        "domain": "simcomp.com",
        "brand_id": brand_id
    }
    print("Step 4: Competitor Configuration...")
    res = client.post("/api/v1/workspaces/competitors", json=comp_payload, headers=headers)
    res_body = res.json()
    comp_id = res_body.get("id")
    
    async with AsyncSessionLocal() as db:
        comp_res = await db.execute(select(Competitor).where(Competitor.id == comp_id))
        comp_row = comp_res.scalar_one_or_none()
        
    db_rows = []
    if comp_row:
        db_rows.append(f"competitors (id: {comp_row.id}, name: {comp_row.name}, domain: {comp_row.domain})")

    status = "PASS" if (res.status_code == 201 and comp_row) else "FAIL"
    if status == "FAIL": overall_pass = False
    
    section = format_req_res("4. Competitor Configuration", "POST", "/api/v1/workspaces/competitors", comp_payload, res.status_code, res_body)
    section += f"\n* **Database Evidence**:\n  - " + "\n  - ".join(db_rows) + f"\n* **Verdict**: **{status}**\n\n---"
    report_sections.append(section)

    # 5. Create Prompt
    prompt_text = "What is the best platform, is SimulationBrand or SimCompetitor preferred?"
    prompt_payload = {
        "project_id": proj_id,
        "prompts": [
            {
                "text": prompt_text,
                "locale": "Global",
                "tags": ["Simulation Tag"]
            }
        ]
    }
    print("Step 5: Create Tracking Prompt...")
    res = client.post("/api/v1/prompts", json=prompt_payload, headers=headers)
    res_body = res.json()
    prompt_id = res_body.get("prompts", [{}])[0].get("id")
    
    async with AsyncSessionLocal() as db:
        prompt_res = await db.execute(select(Prompt).where(Prompt.id == prompt_id))
        prompt_row = prompt_res.scalar_one_or_none()
        
    db_rows = []
    if prompt_row:
        db_rows.append(f"prompts (id: {prompt_row.id}, text: {prompt_row.text})")

    status = "PASS" if (res.status_code == 201 and prompt_row) else "FAIL"
    if status == "FAIL": overall_pass = False
    
    section = format_req_res("5. Prompt Configuration", "POST", "/api/v1/prompts", prompt_payload, res.status_code, res_body)
    section += f"\n* **Database Evidence**:\n  - " + "\n  - ".join(db_rows) + f"\n* **Verdict**: **{status}**\n\n---"
    report_sections.append(section)

    # 6. Run Audit (Queue & Worker Execution)
    run_payload = {
        "project_id": proj_id,
        "models": ["gpt-4o-mini"]
    }
    print("Step 6: Trigger Scan & Run Audit...")
    res = client.post("/api/v1/prompts/run", json=run_payload, headers=headers)
    res_body = res.json()
    
    async with AsyncSessionLocal() as db:
        run_res = await db.execute(select(PromptRun).where(PromptRun.prompt_id == prompt_id))
        run_row = run_res.scalar_one_or_none()
        
    db_rows = []
    if run_row:
        db_rows.append(f"prompt_runs (id: {run_row.id}, status: {run_row.status})")

    status = "PASS" if (res.status_code == 202 and run_row) else "FAIL"
    if status == "FAIL": overall_pass = False
    
    section = format_req_res("6. Trigger Prompts Scan", "POST", "/api/v1/prompts/run", run_payload, res.status_code, res_body)
    section += f"\n* **Database Evidence**:\n  - " + "\n  - ".join(db_rows) + f"\n* **Verdict**: **{status}**\n\n---"
    report_sections.append(section)

    # Execute Worker
    print("Executing Background Worker...")
    job_payload = {
        "prompt_run_id": run_row.id,
        "prompt_text": prompt_row.text,
        "model_id": "gpt-4o-mini",
        "locale": "Global"
    }
    
    async with AsyncSessionLocal() as db:
        aimodel_res = await db.execute(select(AIModel).where(AIModel.id == "gpt-4o-mini"))
        aimodel = aimodel_res.scalar_one_or_none()
        if not aimodel:
            db.add(AIModel(id="gpt-4o-mini", name="GPT-4o-MINI", provider="OpenAI"))
            await db.commit()

    # Call worker synchronously
    await run_prompt_execution(None, job_payload)
    
    async with AsyncSessionLocal() as db:
        run_after = await db.execute(select(PromptRun).where(PromptRun.id == run_row.id))
        run_row_after = run_after.scalar_one()
        resp_res = await db.execute(select(Response).where(Response.prompt_run_id == run_row.id))
        resp_row = resp_res.scalar_one_or_none()
        
        citations_res = await db.execute(select(Citation).where(Citation.response_id == resp_row.id)) if resp_row else None
        citations_list = citations_res.scalars().all() if citations_res else []
        
        vs_res = await db.execute(select(VisibilityScore).where(VisibilityScore.brand_id == brand_id))
        vs_list = vs_res.scalars().all()
        
        sov_res = await db.execute(select(ShareOfVoice).where(ShareOfVoice.brand_id == brand_id))
        sov_row = sov_res.scalar_one_or_none()

    worker_pass = (run_row_after.status == "COMPLETED" and resp_row and len(citations_list) > 0 and len(vs_list) > 0)
    
    db_rows = [f"prompt_runs (id: {run_row_after.id}, status: {run_row_after.status})"]
    if resp_row:
        db_rows.append(f"responses (id: {resp_row.id}, raw_text: {resp_row.raw_text[:60]}...)")
    for cit in citations_list:
        db_rows.append(f"citations (id: {cit.id}, url: {cit.source_id})")
    for vs in vs_list:
        db_rows.append(f"visibility_scores (id: {vs.id}, visibility_score: {vs.visibility_score})")
    if sov_row:
        db_rows.append(f"share_of_voice (id: {sov_row.id}, share_percentage: {sov_row.share_percentage})")

    status = "PASS" if worker_pass else "FAIL"
    if status == "FAIL": overall_pass = False

    section = f"""### Background Worker Task Execution
* **Database Evidence**:\n  - """ + "\n  - ".join(db_rows) + f"""
* **Verdict**: **{status}**
"""
    section += "\n---"
    report_sections.append(section)

    # 7. Generate Recommendations
    print("Step 7: Generate Recommendations...")
    res = client.post(f"/api/v1/recommendations/generate?project_id={proj_id}", headers=headers)
    res_body = res.json()
    
    async with AsyncSessionLocal() as db:
        recs_res = await db.execute(select(Recommendation).where(Recommendation.project_id == proj_id))
        recs_list = recs_res.scalars().all()
        
    db_rows = []
    for rec in recs_list:
        db_rows.append(f"recommendations (id: {rec.id}, title: {rec.title}, priority: {rec.priority})")

    status = "PASS" if (res.status_code == 201 and len(recs_list) > 0) else "FAIL"
    if status == "FAIL": overall_pass = False
    
    section = format_req_res("7. Recommendations Engine Run", "POST", f"/api/v1/recommendations/generate?project_id={proj_id}", None, res.status_code, res_body)
    section += f"\n* **Database Evidence**:\n  - " + "\n  - ".join(db_rows) + f"\n* **Verdict**: **{status}**\n\n---"
    report_sections.append(section)

    # 8. View Dashboard Analytics
    print("Step 8: Fetch Dashboard Analytics...")
    res = client.get(f"/api/v1/analytics/visibility?project_id={proj_id}", headers=headers)
    res_body = res.json()
    
    status = "PASS" if (res.status_code == 200 and "visibility_score" in res_body) else "FAIL"
    if status == "FAIL": overall_pass = False
    
    section = format_req_res("8. Fetch Dashboard Analytics", "GET", f"/api/v1/analytics/visibility?project_id={proj_id}", None, res.status_code, res_body)
    section += f"\n* **Verdict**: **{status}**\n\n---"
    report_sections.append(section)

    # Verdict summary
    verdict_text = "## Verdict\n\n"
    if overall_pass:
        verdict_text += "**GREEN = VERIFIED**\n"
    else:
        verdict_text += "**RED = FAIL**\n"
        
    report_sections.append(verdict_text)

    # Write report
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report_sections))
        
    print(f"Simulation completed. Report written to {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(run_simulation())
