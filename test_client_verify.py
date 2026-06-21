import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test_geo_db.sqlite"

from fastapi.testclient import TestClient
from app.main import app
import uuid
import json
import asyncio
from app.core.database import engine, Base

async def reset_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

# We must run async reset first
asyncio.run(reset_db())

client = TestClient(app)
OUTPUT_FILE = "e:/Profound-cloning/docs/audit/sprint_a_live_verification.md"

def format_req_res(name, req_method, req_url, req_body, req_headers, res_status, res_body):
    return f"""
### {name}
* **Request**: `{req_method} {req_url}`
* **Payload**:
```json
{json.dumps(req_body, indent=2) if req_body else "{}"}
```
* **Status Code**: **{res_status}**
* **Response**:
```json
{json.dumps(res_body, indent=2) if isinstance(res_body, dict) else res_body}
```
"""

output = ["# Sprint A Live Verification Report\n\n**Date**: 2026-06-20\n\n"]

email_a = f"usera_{uuid.uuid4().hex[:6]}@example.com"
email_b = f"userb_{uuid.uuid4().hex[:6]}@example.com"

# User A
body_a = {"email": email_a, "password": "password123", "full_name": "User A", "organization_name": "Org A"}
res = client.post("/api/v1/workspaces/register", json=body_a)
output.append(format_req_res("Register User A", "POST", "/api/v1/workspaces/register", body_a, None, res.status_code, res.json()))

# User B
body_b = {"email": email_b, "password": "password123", "full_name": "User B", "organization_name": "Org B"}
res = client.post("/api/v1/workspaces/register", json=body_b)
output.append(format_req_res("Register User B", "POST", "/api/v1/workspaces/register", body_b, None, res.status_code, res.json()))

# Login A
res = client.post("/api/v1/workspaces/token", json={"email": email_a, "password": "password123"})
token_a = res.json()["access_token"]
headers_a = {"Authorization": f"Bearer {token_a}"}

# Login B
res = client.post("/api/v1/workspaces/token", json={"email": email_b, "password": "password123"})
token_b = res.json()["access_token"]
headers_b = {"Authorization": f"Bearer {token_b}"}

# WS A
ws_a_body = {"name": "WS A", "tier": "free"}
res = client.post("/api/v1/workspaces", headers=headers_a, json=ws_a_body)
ws_a_id = res.json()["id"]

# WS B
ws_b_body = {"name": "WS B", "tier": "free"}
res = client.post("/api/v1/workspaces", headers=headers_b, json=ws_b_body)
ws_b_id = res.json()["id"]

# Proj A
proj_a_body = {"name": "Proj A", "workspace_id": ws_a_id}
res = client.post("/api/v1/workspaces/projects", headers=headers_a, json=proj_a_body)
proj_a_id = res.json()["id"]

# Proj B
proj_b_body = {"name": "Proj B", "workspace_id": ws_b_id}
res = client.post("/api/v1/workspaces/projects", headers=headers_b, json=proj_b_body)
proj_b_id = res.json()["id"]

output.append("## 1. User A accessing User A resources -> 200\n")
res = client.get(f"/api/v1/prompts?project_id={proj_a_id}", headers=headers_a)
output.append(format_req_res("User A Accesses Project A Prompts", "GET", f"/api/v1/prompts?project_id={proj_a_id}", None, headers_a, res.status_code, res.json()))

output.append("## 2. User A accessing User B resources -> 403\n")
res = client.get(f"/api/v1/prompts?project_id={proj_b_id}", headers=headers_a)
output.append(format_req_res("User A Accesses Project B Prompts", "GET", f"/api/v1/prompts?project_id={proj_b_id}", None, headers_a, res.status_code, res.json()))

output.append("## 3. User B accessing User A resources -> 403\n")
res = client.get(f"/api/v1/prompts?project_id={proj_a_id}", headers=headers_b)
output.append(format_req_res("User B Accesses Project A Prompts", "GET", f"/api/v1/prompts?project_id={proj_a_id}", None, headers_b, res.status_code, res.json()))

output.append("## 4. Invalid workspace -> 404\n")
invalid_ws_id = str(uuid.uuid4())
res = client.post("/api/v1/workspaces/projects", headers=headers_a, json={"name": "Orphan Proj", "workspace_id": invalid_ws_id})
try:
    r_json = res.json()
except:
    r_json = res.text
output.append(format_req_res("Invalid workspace", "POST", "/api/v1/workspaces/projects", {"name": "Orphan Proj", "workspace_id": invalid_ws_id}, headers_a, res.status_code, r_json))

output.append("## 5. Invalid project -> 404/403\n")
invalid_proj_id = str(uuid.uuid4())
res = client.get(f"/api/v1/prompts?project_id={invalid_proj_id}", headers=headers_a)
try:
    r_json = res.json()
except:
    r_json = res.text
output.append(format_req_res("Invalid project", "GET", f"/api/v1/prompts?project_id={invalid_proj_id}", None, headers_a, res.status_code, r_json))

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(output))

print(f"Report written to {OUTPUT_FILE}")
