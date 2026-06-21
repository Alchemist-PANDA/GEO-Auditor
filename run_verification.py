import asyncio
import os
import uuid
import sys
from httpx import AsyncClient

# Setup path and env for testing BEFORE imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test_geo_db.sqlite"

from app.main import app
from app.core.database import AsyncSessionLocal
from app.modules.workspaces.models import User, Organization, Workspace, Project
from sqlalchemy.future import select
from app.core.database import engine, Base

async def run_verification():
    print("=== STARTING SPRINT A RE-VERIFICATION ===")
    
    # 1. Reset DB
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # 2. Setup
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create User A
        reg_a = await client.post("/api/v1/workspaces/register", json={
            "email": "user_a@example.com",
            "password": "passwordA123",
            "full_name": "User A",
            "organization_name": "Org A"
        })
        # Create User B
        reg_b = await client.post("/api/v1/workspaces/register", json={
            "email": "user_b@example.com",
            "password": "passwordB123",
            "full_name": "User B",
            "organization_name": "Org B"
        })
        
        login_a = await client.post("/api/v1/workspaces/token", json={"email": "user_a@example.com", "password": "passwordA123"})
        headers_a = {"Authorization": f"Bearer {login_a.json()['access_token']}"}

        login_b = await client.post("/api/v1/workspaces/token", json={"email": "user_b@example.com", "password": "passwordB123"})
        headers_b = {"Authorization": f"Bearer {login_b.json()['access_token']}"}

        ws_a_res = await client.post("/api/v1/workspaces", headers=headers_a, json={"name": "Workspace A", "tier": "pitch"})
        ws_a_id = ws_a_res.json()["id"]

        ws_b_res = await client.post("/api/v1/workspaces", headers=headers_b, json={"name": "Workspace B", "tier": "pitch"})
        ws_b_id = ws_b_res.json()["id"]

        proj_a_res = await client.post("/api/v1/workspaces/projects", headers=headers_a, json={"name": "Project A", "workspace_id": ws_a_id})
        proj_a_id = proj_a_res.json()["id"]

        proj_b_res = await client.post("/api/v1/workspaces/projects", headers=headers_b, json={"name": "Project B", "workspace_id": ws_b_id})
        proj_b_id = proj_b_res.json()["id"]

        print("--- IDOR Tests ---")
        # Test 3: IDOR on Prompts
        prompts_a_on_b = await client.get(f"/api/v1/prompts?project_id={proj_b_id}", headers=headers_a)
        print(f"User A accessing User B's Prompts: {prompts_a_on_b.status_code}") # Should be 403

        # Test 3: IDOR on Recommendations
        recs_a_on_b = await client.get(f"/api/v1/recommendations?project_id={proj_b_id}", headers=headers_a)
        print(f"User A accessing User B's Recommendations: {recs_a_on_b.status_code}") # Should be 403

        # Test 3: IDOR on Project Creation (User A creating project in User B's workspace)
        proj_a_in_b_ws = await client.post("/api/v1/workspaces/projects", headers=headers_a, json={"name": "Project C", "workspace_id": ws_b_id})
        print(f"User A creating project in User B's workspace: {proj_a_in_b_ws.status_code}") # Should be 403

        print("--- Database Integrity Tests ---")
        # Test 4/5: Foreign Key Enforcement
        invalid_ws_id = str(uuid.uuid4())
        orphan_proj = await client.post("/api/v1/workspaces/projects", headers=headers_a, json={"name": "Orphan Project", "workspace_id": invalid_ws_id})
        print(f"User A creating project with invalid workspace_id: {orphan_proj.status_code}") # Should be 404

    # DB Integrity verification
    async with AsyncSessionLocal() as db:
        orphans = (await db.execute(select(Project).where(Project.workspace_id == invalid_ws_id))).scalars().all()
        print(f"Orphan projects in DB: {len(orphans)}")

if __name__ == "__main__":
    asyncio.run(run_verification())
