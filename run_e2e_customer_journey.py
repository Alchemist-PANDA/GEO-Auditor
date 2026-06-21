import sys
import os
import asyncio
import json
import uuid
from datetime import datetime
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
OUTPUT_FILE = "e:/Profound-cloning/docs/final_audit/production_truth.md"

def format_req_res(title, req_method, req_url, req_body, res_status, res_body):
    return f"""### {title}
* **API Request**: `{req_method} {req_url}`
* **Payload**:
```json
{json.dumps(req_body, indent=2) if req_body else "{{}}"}
```
* **Status Code**: **{res_status}**
* **API Response**:
```json
{json.dumps(res_body, indent=2) if isinstance(res_body, (dict, list)) else res_body}
```
"""

async def run_journey():
    print("=== STARTING END-TO-END CUSTOMER JOURNEY TEST ===")
    
    # 1. Reset DB
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables re-created successfully.")

    client = TestClient(fastapi_app)
    
    report_sections = [
        "# Production Truth — Customer Journey Verification\n",
        f"**Date**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n",
        "This document details the end-to-end execution of a customer journey under mock sandbox settings, validating every API transaction, database row modification, and worker process execution.\n"
    ]
    
    # User Details
    email = f"real_customer_{uuid.uuid4().hex[:4]}@example.com"
    password = "CustomerSecuredPassword123!"
    full_name = "Real Customer"
    org_name = "Customer Enterprise"
    
    # Track status
    overall_pass = True

    # ────────────────────────────────────────────────────────
    # 1. Register User
    # ────────────────────────────────────────────────────────
    reg_payload = {
        "email": email,
        "password": password,
        "full_name": full_name,
        "organization_name": org_name
    }
    print("Executing Step 1: User Registration...")
    res = client.post("/api/v1/workspaces/register", json=reg_payload)
    res_body = res.json()
    
    # Check DB rows
    async with AsyncSessionLocal() as db:
        user_res = await db.execute(select(User).where(User.email == email))
        user_row = user_res.scalar_one_or_none()
        org_res = await db.execute(select(Organization).where(Organization.name == org_name))
        org_row = org_res.scalar_one_or_none()
        
    db_rows = []
    if user_row:
        db_rows.append(f"users (id: {user_row.id}, email: {user_row.email}, organization_id: {user_row.organization_id}, role: {user_row.role})")
    if org_row:
        db_rows.append(f"organizations (id: {org_row.id}, name: {org_row.name})")

    status = "PASS" if (res.status_code == 201 and user_row and org_row) else "FAIL"
    if status == "FAIL": overall_pass = False
    
    section = format_req_res("Step 1: User Registration", "POST", "/api/v1/workspaces/register", reg_payload, res.status_code, res_body)
    section += f"\n* **Database Rows Created**:\n  - " + "\n  - ".join(db_rows) + f"\n* **Result**: **{status}**\n\n---"
    report_sections.append(section)

    # ────────────────────────────────────────────────────────
    # 2. Login User
    # ────────────────────────────────────────────────────────
    login_payload = {
        "email": email,
        "password": password
    }
    print("Executing Step 2: User Login...")
    res = client.post("/api/v1/workspaces/token", json=login_payload)
    res_body = res.json()
    token = res_body.get("access_token")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    status = "PASS" if (res.status_code == 200 and token) else "FAIL"
    if status == "FAIL": overall_pass = False
    
    section = format_req_res("Step 2: User Login & JWT Retrieval", "POST", "/api/v1/workspaces/token", login_payload, res.status_code, res_body)
    section += f"\n* **Result**: **{status}**\n\n---"
    report_sections.append(section)

    # ────────────────────────────────────────────────────────
    # Setup step: Create Workspace
    # ────────────────────────────────────────────────────────
    ws_payload = {
        "name": "GEO Validation WS",
        "tier": "premium"
    }
    print("Setting up: Creating Workspace...")
    res = client.post("/api/v1/workspaces", json=ws_payload, headers=headers)
    ws_body = res.json()
    ws_id = ws_body.get("id")
    
    async with AsyncSessionLocal() as db:
        ws_res = await db.execute(select(Workspace).where(Workspace.id == ws_id))
        ws_row = ws_res.scalar_one_or_none()
        
    db_rows = []
    if ws_row:
        db_rows.append(f"workspaces (id: {ws_row.id}, name: {ws_row.name}, organization_id: {ws_row.organization_id}, tier: {ws_row.tier})")
        
    status = "PASS" if (res.status_code == 201 and ws_row) else "FAIL"
    if status == "FAIL": overall_pass = False
    
    section = format_req_res("Setup Step A: Workspace Creation", "POST", "/api/v1/workspaces", ws_payload, res.status_code, ws_body)
    section += f"\n* **Database Rows Created**:\n  - " + "\n  - ".join(db_rows) + f"\n* **Result**: **{status}**\n\n---"
    report_sections.append(section)

    # ────────────────────────────────────────────────────────
    # Setup step: Create Project
    # ────────────────────────────────────────────────────────
    proj_payload = {
        "name": "Validation Project",
        "workspace_id": ws_id
    }
    print("Setting up: Creating Project...")
    res = client.post("/api/v1/workspaces/projects", json=proj_payload, headers=headers)
    proj_body = res.json()
    proj_id = proj_body.get("id")
    
    async with AsyncSessionLocal() as db:
        proj_res = await db.execute(select(Project).where(Project.id == proj_id))
        proj_row = proj_res.scalar_one_or_none()
        
    db_rows = []
    if proj_row:
        db_rows.append(f"projects (id: {proj_row.id}, name: {proj_row.name}, workspace_id: {proj_row.workspace_id})")
        
    status = "PASS" if (res.status_code == 201 and proj_row) else "FAIL"
    if status == "FAIL": overall_pass = False
    
    section = format_req_res("Setup Step B: Project Container Creation", "POST", "/api/v1/workspaces/projects", proj_payload, res.status_code, proj_body)
    section += f"\n* **Database Rows Created**:\n  - " + "\n  - ".join(db_rows) + f"\n* **Result**: **{status}**\n\n---"
    report_sections.append(section)

    # ────────────────────────────────────────────────────────
    # 3. Create Brand
    # ────────────────────────────────────────────────────────
    brand_payload = {
        "name": "ValidationBrand",
        "domain": "valbrand.com",
        "project_id": proj_id
    }
    print("Executing Step 3: Brand Creation...")
    res = client.post("/api/v1/workspaces/brands", json=brand_payload, headers=headers)
    res_body = res.json()
    brand_id = res_body.get("id")
    
    async with AsyncSessionLocal() as db:
        brand_res = await db.execute(select(Brand).where(Brand.id == brand_id))
        brand_row = brand_res.scalar_one_or_none()
        
    db_rows = []
    if brand_row:
        db_rows.append(f"brands (id: {brand_row.id}, name: {brand_row.name}, domain: {brand_row.domain}, project_id: {brand_row.project_id})")

    status = "PASS" if (res.status_code == 201 and brand_row) else "FAIL"
    if status == "FAIL": overall_pass = False
    
    section = format_req_res("Step 3: Brand Onboarding", "POST", "/api/v1/workspaces/brands", brand_payload, res.status_code, res_body)
    section += f"\n* **Database Rows Created**:\n  - " + "\n  - ".join(db_rows) + f"\n* **Result**: **{status}**\n\n---"
    report_sections.append(section)

    # ────────────────────────────────────────────────────────
    # 4. Add Competitor
    # ────────────────────────────────────────────────────────
    comp_payload = {
        "name": "ValCompetitor",
        "domain": "valcomp.com",
        "brand_id": brand_id
    }
    print("Executing Step 4: Add Competitor...")
    res = client.post("/api/v1/workspaces/competitors", json=comp_payload, headers=headers)
    res_body = res.json()
    comp_id = res_body.get("id")
    
    async with AsyncSessionLocal() as db:
        comp_res = await db.execute(select(Competitor).where(Competitor.id == comp_id))
        comp_row = comp_res.scalar_one_or_none()
        
    db_rows = []
    if comp_row:
        db_rows.append(f"competitors (id: {comp_row.id}, name: {comp_row.name}, domain: {comp_row.domain}, brand_id: {comp_row.brand_id})")

    status = "PASS" if (res.status_code == 201 and comp_row) else "FAIL"
    if status == "FAIL": overall_pass = False
    
    section = format_req_res("Step 4: Competitor Configuration", "POST", "/api/v1/workspaces/competitors", comp_payload, res.status_code, res_body)
    section += f"\n* **Database Rows Created**:\n  - " + "\n  - ".join(db_rows) + f"\n* **Result**: **{status}**\n\n---"
    report_sections.append(section)

    # ────────────────────────────────────────────────────────
    # 5. Create Prompt
    # ────────────────────────────────────────────────────────
    prompt_text = "What is the best business card platform, is ValidationBrand or ValCompetitor better?"
    prompt_payload = {
        "project_id": proj_id,
        "prompts": [
            {
                "text": prompt_text,
                "locale": "Global",
                "tags": ["Corporate Cards"]
            }
        ]
    }
    print("Executing Step 5: Create Prompt...")
    res = client.post("/api/v1/prompts", json=prompt_payload, headers=headers)
    res_body = res.json()
    prompt_id = res_body.get("prompts", [{}])[0].get("id")
    
    async with AsyncSessionLocal() as db:
        prompt_res = await db.execute(select(Prompt).where(Prompt.id == prompt_id))
        prompt_row = prompt_res.scalar_one_or_none()
        
    db_rows = []
    if prompt_row:
        db_rows.append(f"prompts (id: {prompt_row.id}, text: {prompt_row.text}, locale: {prompt_row.locale}, project_id: {prompt_row.project_id})")

    status = "PASS" if (res.status_code == 201 and prompt_row) else "FAIL"
    if status == "FAIL": overall_pass = False
    
    section = format_req_res("Step 5: Create Prompts List", "POST", "/api/v1/prompts", prompt_payload, res.status_code, res_body)
    section += f"\n* **Database Rows Created**:\n  - " + "\n  - ".join(db_rows) + f"\n* **Result**: **{status}**\n\n---"
    report_sections.append(section)

    # ────────────────────────────────────────────────────────
    # 6. Run Prompt (Queue)
    # ────────────────────────────────────────────────────────
    run_payload = {
        "project_id": proj_id,
        "models": ["gpt-4o-mini"]
    }
    print("Executing Step 6: Queue Prompt Runs...")
    res = client.post("/api/v1/prompts/run", json=run_payload, headers=headers)
    res_body = res.json()
    
    async with AsyncSessionLocal() as db:
        run_res = await db.execute(select(PromptRun).where(PromptRun.prompt_id == prompt_id))
        run_row = run_res.scalar_one_or_none()
        
    db_rows = []
    if run_row:
        db_rows.append(f"prompt_runs (id: {run_row.id}, prompt_id: {run_row.prompt_id}, model_id: {run_row.model_id}, status: {run_row.status})")

    status = "PASS" if (res.status_code == 202 and run_row and run_row.status == "PENDING") else "FAIL"
    if status == "FAIL": overall_pass = False
    
    section = format_req_res("Step 6: Trigger Prompts Execution", "POST", "/api/v1/prompts/run", run_payload, res.status_code, res_body)
    section += f"\n* **Database Rows Created**:\n  - " + "\n  - ".join(db_rows) + f"\n* **Result**: **{status}**\n\n---"
    report_sections.append(section)

    # ────────────────────────────────────────────────────────
    # 7. Worker Executes / 8. LLM Response / 9. Citations / 10. Visibility
    # ────────────────────────────────────────────────────────
    print("Executing Step 7-10: Worker Execution & Calculations...")
    job_payload = {
        "prompt_run_id": run_row.id,
        "prompt_text": prompt_row.text,
        "model_id": "gpt-4o-mini",
        "locale": "Global"
    }
    
    worker_logs = []
    
    # Standard logger capture for run_prompt_execution
    import logging
    logger = logging.getLogger("workers.run_worker")
    logger.setLevel(logging.INFO)
    log_stream = []
    class DummyHandler(logging.Handler):
        def emit(self, record):
            log_stream.append(record.getMessage())
    handler = DummyHandler()
    logger.addHandler(handler)
    
    # Setup AI Model record so the worker can reference it
    async with AsyncSessionLocal() as db:
        aimodel_res = await db.execute(select(AIModel).where(AIModel.id == "gpt-4o-mini"))
        aimodel = aimodel_res.scalar_one_or_none()
        if not aimodel:
            db.add(AIModel(id="gpt-4o-mini", name="GPT-4o-MINI", provider="OpenAI"))
            await db.commit()

    # Call worker synchronously
    await run_prompt_execution(None, job_payload)
    
    logger.removeHandler(handler)
    worker_logs_str = "\n".join(log_stream)
    
    # Query database to check if worker succeeded and inserted response + calculations
    async with AsyncSessionLocal() as db:
        run_res_after = await db.execute(select(PromptRun).where(PromptRun.id == run_row.id))
        run_row_after = run_res_after.scalar_one()
        
        resp_res = await db.execute(select(Response).where(Response.prompt_run_id == run_row.id))
        resp_row = resp_res.scalar_one_or_none()
        
        if resp_row:
            citations_res = await db.execute(select(Citation).where(Citation.response_id == resp_row.id))
            citations_list = citations_res.scalars().all()
            
            vs_res = await db.execute(select(VisibilityScore).where(VisibilityScore.brand_id == brand_id))
            vs_list = vs_res.scalars().all()
            
            sov_res = await db.execute(select(ShareOfVoice).where(ShareOfVoice.brand_id == brand_id))
            sov_row = sov_res.scalar_one_or_none()
        else:
            citations_list = []
            vs_list = []
            sov_row = None
            
    db_rows = [
        f"prompt_runs (id: {run_row_after.id}, status: {run_row_after.status})"
    ]
    if resp_row:
        db_rows.append(f"responses (id: {resp_row.id}, raw_text: {resp_row.raw_text[:60]}..., sentiment_score: {resp_row.sentiment_score})")
    for cit in citations_list:
        db_rows.append(f"citations (id: {cit.id}, source_id: {cit.source_id}, position_index: {cit.position_index})")
    for vs in vs_list:
        db_rows.append(f"visibility_scores (id: {vs.id}, visibility_score: {vs.visibility_score})")
    if sov_row:
        db_rows.append(f"share_of_voice (id: {sov_row.id}, share_percentage: {sov_row.share_percentage})")

    status = "PASS" if (run_row_after.status == "COMPLETED" and resp_row and len(citations_list) > 0 and len(vs_list) > 0) else "FAIL"
    if status == "FAIL": overall_pass = False

    section = f"""### Step 7-10: Worker Execution & AI Calculations
* **Worker Logs**:
```
{worker_logs_str}
```
* **Database Rows Created**:
  - """ + "\n  - ".join(db_rows) + f"""
* **Result**: **{status}**
"""
    section += "\n---"
    report_sections.append(section)

    # ────────────────────────────────────────────────────────
    # 11. Recommendations Generated
    # ────────────────────────────────────────────────────────
    print("Executing Step 11: Generate Recommendations...")
    res = client.post(f"/api/v1/recommendations/generate?project_id={proj_id}", headers=headers)
    res_body = res.json()
    
    async with AsyncSessionLocal() as db:
        recs_res = await db.execute(select(Recommendation).where(Recommendation.project_id == proj_id))
        recs_list = recs_res.scalars().all()
        
    db_rows = []
    for rec in recs_list:
        db_rows.append(f"recommendations (id: {rec.id}, title: {rec.title}, priority: {rec.priority}, status: {rec.status})")

    status = "PASS" if (res.status_code == 201 and len(recs_list) > 0) else "FAIL"
    if status == "FAIL": overall_pass = False
    
    section = format_req_res("Step 11: Recommendations Engine Run", "POST", f"/api/v1/recommendations/generate?project_id={proj_id}", None, res.status_code, res_body)
    section += f"\n* **Database Rows Created**:\n  - " + "\n  - ".join(db_rows) + f"\n* **Result**: **{status}**\n\n---"
    report_sections.append(section)

    # ────────────────────────────────────────────────────────
    # 12. Dashboard Displays Results
    # ────────────────────────────────────────────────────────
    print("Executing Step 12: Load Dashboard Results...")
    res = client.get(f"/api/v1/analytics/visibility?project_id={proj_id}", headers=headers)
    res_body = res.json()
    
    status = "PASS" if (res.status_code == 200 and "visibility_score" in res_body) else "FAIL"
    if status == "FAIL": overall_pass = False
    
    section = format_req_res("Step 12: Fetch Dashboard Analytics", "GET", f"/api/v1/analytics/visibility?project_id={proj_id}", None, res.status_code, res_body)
    section += f"\n* **Result**: **{status}**\n\n---"
    report_sections.append(section)

    # ────────────────────────────────────────────────────────
    # Write Final Output
    # ────────────────────────────────────────────────────────
    final_verdict = "### Verification Verdict\n"
    if overall_pass:
        final_verdict += "\n**GREEN = VERIFIED**\nAll 12 steps of the customer journey successfully executed and passed end-to-end.\n"
    else:
        final_verdict += "\n**RED = FAIL**\nOne or more core steps failed execution.\n"
    
    report_sections.append(final_verdict)
    
    # Write to target path
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report_sections))
        
    print(f"Journey verification complete. Report created under: {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(run_journey())
