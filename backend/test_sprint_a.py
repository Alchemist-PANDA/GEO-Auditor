import asyncio
import os
import uuid
from sqlalchemy.future import select
from httpx import AsyncClient
from app.main import app
from app.core.database import AsyncSessionLocal
from app.modules.workspaces.models import User, Organization, Workspace, Project
from app.modules.workspaces.router import pwd_context

async def run_verification():
    print("=== STARTING SPRINT A VERIFICATION ===")
    
    # 1. Registration Flow for User A and User B
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create User A
        reg_a = await client.post("/api/v1/workspaces/register", json={
            "email": "user_a@example.com",
            "password": "passwordA123",
            "full_name": "User A",
            "organization_name": "Org A"
        })
        print(f"User A Registration Response: {reg_a.status_code} - {reg_a.json()}")
        
        # Create User B
        reg_b = await client.post("/api/v1/workspaces/register", json={
            "email": "user_b@example.com",
            "password": "passwordB123",
            "full_name": "User B",
            "organization_name": "Org B"
        })
        print(f"User B Registration Response: {reg_b.status_code} - {reg_b.json()}")

    # Verify rows in DB
    async with AsyncSessionLocal() as db:
        users = (await db.execute(select(User))).scalars().all()
        orgs = (await db.execute(select(Organization))).scalars().all()
        print(f"DB Check - Users in DB: {[u.email for u in users]}")
        print(f"DB Check - Orgs in DB: {[o.name for o in orgs]}")
        
        # Get User A and User B database records
        user_a_db = (await db.execute(select(User).where(User.email == "user_a@example.com"))).scalar_one()
        user_b_db = (await db.execute(select(User).where(User.email == "user_b@example.com"))).scalar_one()

    # 2. Login Flow & Token Generation
    async with AsyncClient(app=app, base_url="http://test") as client:
        # User A Login
        login_a = await client.post("/api/v1/workspaces/token", json={
            "email": "user_a@example.com",
            "password": "passwordA123"
        })
        print(f"User A Login Response: {login_a.status_code}")
        token_a = login_a.json()["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}

        # User B Login
        login_b = await client.post("/api/v1/workspaces/token", json={
            "email": "user_b@example.com",
            "password": "passwordB123"
        })
        print(f"User B Login Response: {login_b.status_code}")
        token_b = login_b.json()["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # 3. Create Workspaces and Projects
        ws_a_res = await client.post("/api/v1/workspaces", headers=headers_a, json={
            "name": "Workspace A",
            "tier": "pitch"
        })
        print(f"Workspace A Creation: {ws_a_res.status_code} - {ws_a_res.json()}")
        ws_a_id = ws_a_res.json()["id"]

        ws_b_res = await client.post("/api/v1/workspaces", headers=headers_b, json={
            "name": "Workspace B",
            "tier": "pitch"
        })
        print(f"Workspace B Creation: {ws_b_res.status_code} - {ws_b_res.json()}")
        ws_b_id = ws_b_res.json()["id"]

        # Create Projects
        proj_a_res = await client.post("/api/v1/workspaces/projects", headers=headers_a, json={
            "name": "Project A",
            "workspace_id": ws_a_id
        })
        print(f"Project A Creation: {proj_a_res.status_code} - {proj_a_res.json()}")
        proj_a_id = proj_a_res.json()["id"]

        proj_b_res = await client.post("/api/v1/workspaces/projects", headers=headers_b, json={
            "name": "Project B",
            "workspace_id": ws_b_id
        })
        print(f"Project B Creation: {proj_b_res.status_code} - {proj_b_res.json()}")
        proj_b_id = proj_b_res.json()["id"]

    # 4. Authorization Flow Check (IDOR)
    async with AsyncClient(app=app, base_url="http://test") as client:
        # User A attempts to access Project B visibility details
        acc_b_by_a = await client.get(f"/api/v1/analytics/visibility?project_id={proj_b_id}", headers=headers_a)
        print(f"User A accessing Project B (Expect 403): {acc_b_by_a.status_code} - {acc_b_by_a.text}")

        # User B attempts to access Project A visibility details
        acc_a_by_b = await client.get(f"/api/v1/analytics/visibility?project_id={proj_a_id}", headers=headers_b)
        print(f"User B accessing Project A (Expect 403): {acc_a_by_b.status_code} - {acc_a_by_b.text}")

        # User A accessing Project A visibility details
        acc_a_by_a = await client.get(f"/api/v1/analytics/visibility?project_id={proj_a_id}", headers=headers_a)
        print(f"User A accessing Project A (Expect 200/404 based on data existence, NOT 403/500): {acc_a_by_a.status_code} - {acc_a_by_a.text}")

    # 5. Error Handling Checks
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Invalid Login (Expect 401)
        bad_login = await client.post("/api/v1/workspaces/token", json={
            "email": "user_a@example.com",
            "password": "wrongpassword"
        })
        print(f"Bad Login (Expect 401): {bad_login.status_code} - {bad_login.json()}")

        # Missing project ID on IDOR check (Expect 403 or 404)
        missing_proj = await client.get(f"/api/v1/analytics/visibility?project_id={str(uuid.uuid4())}", headers=headers_a)
        print(f"Missing Project Access (Expect 403/404): {missing_proj.status_code} - {missing_proj.text}")

    # 6. Database dump for report
    async with AsyncSessionLocal() as db:
        users = (await db.execute(select(User))).scalars().all()
        orgs = (await db.execute(select(Organization))).scalars().all()
        workspaces = (await db.execute(select(Workspace))).scalars().all()
        projects = (await db.execute(select(Project))).scalars().all()
        
        print("\n=== DATABASE STATE ===")
        print(f"Total Users: {len(users)}")
        for u in users:
            print(f"  - User: id={u.id}, email={u.email}, org_id={u.organization_id}")
        print(f"Total Organizations: {len(orgs)}")
        for o in orgs:
            print(f"  - Org: id={o.id}, name={o.name}")
        print(f"Total Workspaces: {len(workspaces)}")
        for w in workspaces:
            print(f"  - Workspace: id={w.id}, name={w.name}, org_id={w.organization_id}")
        print(f"Total Projects: {len(projects)}")
        for p in projects:
            print(f"  - Project: id={p.id}, name={p.name}, workspace_id={p.workspace_id}")

if __name__ == "__main__":
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///geo_db.sqlite"
    asyncio.run(run_verification())
