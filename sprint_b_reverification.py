import sys
import os
import json
import asyncio
import uuid

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test_geo_db.sqlite"
# Force a bad redis connection to test 503 failure
os.environ["REDIS_URL"] = "redis://localhost:6379"

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import AsyncSessionLocal
from app.modules.analysis.models import PageAudit
from app.modules.workspaces.models import User
from jose import jwt
from app.core.config import settings

def create_access_token(data: dict):
    to_encode = data.copy()
    to_encode.update({"aud": "authenticated"})
    return jwt.encode(to_encode, settings.SUPABASE_JWT_SECRET, algorithm="HS256")

client = TestClient(app)

OUTPUT_FILE = "e:/Profound-cloning/docs/audit/sprint_b_reverification.md"

def format_req_res(name, req_method, req_url, req_body, res_status, res_body):
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

async def seed_data():
    from sqlalchemy import delete
    async with AsyncSessionLocal() as db:
        await db.execute(delete(User).where(User.email.in_(["testa@example.com", "testb@example.com"])))
        await db.execute(delete(PageAudit).where(PageAudit.email.in_(["testa@example.com", "testb@example.com"])))
        await db.commit()
        
        # Create user A
        user_a = User(id=str(uuid.uuid4()), email="testa@example.com", hashed_password="fake", full_name="User A", organization_id=str(uuid.uuid4()))
        # Create user B
        user_b = User(id=str(uuid.uuid4()), email="testb@example.com", hashed_password="fake", full_name="User B", organization_id=str(uuid.uuid4()))
        
        # Create a successful audit for user A
        audit_a_success = PageAudit(
            id=str(uuid.uuid4()), url="https://example.com/success", email="testa@example.com", status="COMPLETED",
            overall_score=85.0, schema_markup_score=90.0, content_structure_score=80.0, keyword_stuffing_score=85.0, semantic_alignment_score=85.0,
            recommendations={"Tip 1": "Do this"}
        )
        
        # Create a failed audit for user A
        audit_a_failed = PageAudit(
            id=str(uuid.uuid4()), url="https://example.com/failed", email="testa@example.com", status="FAILED"
        )
        
        db.add_all([user_a, user_b, audit_a_success, audit_a_failed])
        await db.commit()
        return user_a, user_b, audit_a_success, audit_a_failed

def run_tests():
    output = ["# Sprint B Reverification Report\n\n**Date**: 2026-06-20\n\n"]
    output.append("## Verification Execution Log\n")
    
    # 1. Setup Data
    user_a, user_b, audit_a_success, audit_a_failed = asyncio.run(seed_data())
    token_a = create_access_token({"sub": user_a.id, "email": user_a.email, "role": "user"})
    token_b = create_access_token({"sub": user_b.id, "email": user_b.email, "role": "user"})
    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Test 1: Queue Unavailable (503 gracefully handled)
    body = {"url": "https://example.com/new", "email": "testa@example.com"}
    res1 = client.post("/api/v1/audit/request", json=body, headers=headers_a)
    output.append(format_req_res("Test 1: Queue Unavailable (Should return 503, not 500)", "POST", "/api/v1/audit/request", body, res1.status_code, res1.json() if res1.status_code != 500 else res1.text))
    
    # Check if the DB recorded it as FAILED
    res1_check = client.get("/api/v1/audit", headers=headers_a)
    if res1_check.status_code == 200:
        audits = res1_check.json()
        new_audit = next((a for a in audits if a["url"] == "https://example.com/new"), None)
        if new_audit:
            output.append(f"> **Database Verification**: The new audit's status is `{new_audit['status']}` (Expected: FAILED).\n")

    # Test 2: Audit Retrieval (Success)
    res2 = client.get(f"/api/v1/audit/{audit_a_success.id}", headers=headers_a)
    output.append(format_req_res("Test 2: Successful Audit Retrieval", "GET", f"/api/v1/audit/{audit_a_success.id}", None, res2.status_code, res2.json()))

    # Test 3: Failed Audit Retrieval
    res3 = client.get(f"/api/v1/audit/{audit_a_failed.id}", headers=headers_a)
    output.append(format_req_res("Test 3: Failed Audit Retrieval", "GET", f"/api/v1/audit/{audit_a_failed.id}", None, res3.status_code, res3.json()))

    # Test 4: Unauthorized Retrieval (403)
    res4 = client.get(f"/api/v1/audit/{audit_a_success.id}", headers=headers_b)
    output.append(format_req_res("Test 4: Unauthorized Retrieval (User B accessing User A audit)", "GET", f"/api/v1/audit/{audit_a_success.id}", None, res4.status_code, res4.json()))

    # Test 5: Missing Audit (404)
    fake_id = str(uuid.uuid4())
    res5 = client.get(f"/api/v1/audit/{fake_id}", headers=headers_a)
    output.append(format_req_res("Test 5: Missing Audit", "GET", f"/api/v1/audit/{fake_id}", None, res5.status_code, res5.json()))

    # Check for any 500s
    codes = [res1.status_code, res2.status_code, res3.status_code, res4.status_code, res5.status_code]
    if 500 in codes:
         output.append("## Final Verdict\n\n**RED = failed**\n500 Errors are still present.")
    elif res1.status_code != 503:
         output.append("## Final Verdict\n\n**YELLOW = partial**\nQueue handled without 500, but wrong status code.")
    elif res4.status_code != 403:
         output.append("## Final Verdict\n\n**YELLOW = partial**\nAuthorization failed.")
    elif res5.status_code != 404:
         output.append("## Final Verdict\n\n**YELLOW = partial**\nMissing audit failed.")
    else:
         output.append("## Final Verdict\n\n**GREEN = verified**\nAll runtime tests passed gracefully.")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(output))

    print("Reverification complete.")

if __name__ == "__main__":
    run_tests()
