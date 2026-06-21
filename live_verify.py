import requests
import uuid
import time
import json
import sys

BASE_URL = "http://localhost:8080"
OUTPUT_FILE = "e:/Profound-cloning/docs/audit/sprint_a_live_verification.md"

def wait_for_server():
    for _ in range(15):
        try:
            res = requests.get(f"{BASE_URL}/docs")
            if res.status_code == 200:
                print("Server is up!")
                return True
        except requests.exceptions.ConnectionError:
            pass
        print("Waiting for server...")
        time.sleep(2)
    print("Server did not start in time.")
    return False

def format_req_res(name, req_method, req_url, req_body, req_headers, res_status, res_body):
    return f"""
### {name}
* **Request**: `{req_method} {req_url}`
* **Payload**:
```json
{json.dumps(req_body, indent=2) if req_body else "{}"}
```
* **Headers**: `Authorization: Bearer <token_hidden>`
* **Status Code**: **{res_status}**
* **Response**:
```json
{json.dumps(res_body, indent=2) if isinstance(res_body, dict) else res_body}
```
"""

def run_tests():
    if not wait_for_server():
        sys.exit(1)

    output = ["# Sprint A Live Verification Report\n\n**Date**: 2026-06-20\n\n"]
    
    email_a = f"usera_{uuid.uuid4().hex[:6]}@example.com"
    email_b = f"userb_{uuid.uuid4().hex[:6]}@example.com"

    # Register User A
    body_a = {"email": email_a, "password": "password123", "full_name": "User A", "organization_name": "Org A"}
    res = requests.post(f"{BASE_URL}/api/v1/workspaces/register", json=body_a)
    output.append(format_req_res("Register User A", "POST", "/api/v1/workspaces/register", body_a, None, res.status_code, res.json()))

    # Register User B
    body_b = {"email": email_b, "password": "password123", "full_name": "User B", "organization_name": "Org B"}
    res = requests.post(f"{BASE_URL}/api/v1/workspaces/register", json=body_b)
    output.append(format_req_res("Register User B", "POST", "/api/v1/workspaces/register", body_b, None, res.status_code, res.json()))

    # Login User A
    login_a_body = {"email": email_a, "password": "password123"}
    res = requests.post(f"{BASE_URL}/api/v1/workspaces/token", json=login_a_body)
    token_a = res.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    output.append(format_req_res("Login User A", "POST", "/api/v1/workspaces/token", login_a_body, None, res.status_code, res.json()))

    # Login User B
    login_b_body = {"email": email_b, "password": "password123"}
    res = requests.post(f"{BASE_URL}/api/v1/workspaces/token", json=login_b_body)
    token_b = res.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    output.append(format_req_res("Login User B", "POST", "/api/v1/workspaces/token", login_b_body, None, res.status_code, res.json()))

    # Create Workspace A
    ws_a_body = {"name": "WS A", "tier": "free"}
    res = requests.post(f"{BASE_URL}/api/v1/workspaces", headers=headers_a, json=ws_a_body)
    ws_a_id = res.json()["id"]
    output.append(format_req_res("Create Workspace A", "POST", "/api/v1/workspaces", ws_a_body, headers_a, res.status_code, res.json()))

    # Create Workspace B
    ws_b_body = {"name": "WS B", "tier": "free"}
    res = requests.post(f"{BASE_URL}/api/v1/workspaces", headers=headers_b, json=ws_b_body)
    ws_b_id = res.json()["id"]
    output.append(format_req_res("Create Workspace B", "POST", "/api/v1/workspaces", ws_b_body, headers_b, res.status_code, res.json()))

    # Create Project A
    proj_a_body = {"name": "Proj A", "workspace_id": ws_a_id}
    res = requests.post(f"{BASE_URL}/api/v1/workspaces/projects", headers=headers_a, json=proj_a_body)
    proj_a_id = res.json()["id"]
    output.append(format_req_res("Create Project A", "POST", "/api/v1/workspaces/projects", proj_a_body, headers_a, res.status_code, res.json()))

    # Create Project B
    proj_b_body = {"name": "Proj B", "workspace_id": ws_b_id}
    res = requests.post(f"{BASE_URL}/api/v1/workspaces/projects", headers=headers_b, json=proj_b_body)
    proj_b_id = res.json()["id"]
    output.append(format_req_res("Create Project B", "POST", "/api/v1/workspaces/projects", proj_b_body, headers_b, res.status_code, res.json()))

    output.append("## 1. User A accessing User A resources -> 200\n")
    res = requests.get(f"{BASE_URL}/api/v1/prompts?project_id={proj_a_id}", headers=headers_a)
    output.append(format_req_res("User A Accesses Project A Prompts", "GET", f"/api/v1/prompts?project_id={proj_a_id}", None, headers_a, res.status_code, res.json()))
    
    output.append("## 2. User A accessing User B resources -> 403\n")
    res = requests.get(f"{BASE_URL}/api/v1/prompts?project_id={proj_b_id}", headers=headers_a)
    output.append(format_req_res("User A Accesses Project B Prompts", "GET", f"/api/v1/prompts?project_id={proj_b_id}", None, headers_a, res.status_code, res.json()))
    res = requests.post(f"{BASE_URL}/api/v1/workspaces/projects", headers=headers_a, json={"name": "Hacked Proj", "workspace_id": ws_b_id})
    try:
        res_json = res.json()
    except:
        res_json = res.text
    output.append(format_req_res("User A creates project in Workspace B", "POST", f"/api/v1/workspaces/projects", {"name": "Hacked Proj", "workspace_id": ws_b_id}, headers_a, res.status_code, res_json))

    output.append("## 3. User B accessing User A resources -> 403\n")
    res = requests.get(f"{BASE_URL}/api/v1/prompts?project_id={proj_a_id}", headers=headers_b)
    output.append(format_req_res("User B Accesses Project A Prompts", "GET", f"/api/v1/prompts?project_id={proj_a_id}", None, headers_b, res.status_code, res.json()))
    res = requests.post(f"{BASE_URL}/api/v1/workspaces/projects", headers=headers_b, json={"name": "Hacked Proj", "workspace_id": ws_a_id})
    try:
        res_json = res.json()
    except:
        res_json = res.text
    output.append(format_req_res("User B creates project in Workspace A", "POST", f"/api/v1/workspaces/projects", {"name": "Hacked Proj", "workspace_id": ws_a_id}, headers_b, res.status_code, res_json))

    output.append("## 4. Invalid workspace -> 404\n")
    invalid_ws_id = str(uuid.uuid4())
    res = requests.post(f"{BASE_URL}/api/v1/workspaces/projects", headers=headers_a, json={"name": "Orphan Proj", "workspace_id": invalid_ws_id})
    try:
        res_json = res.json()
    except:
        res_json = res.text
    output.append(format_req_res("User A creates project with invalid workspace_id", "POST", f"/api/v1/workspaces/projects", {"name": "Orphan Proj", "workspace_id": invalid_ws_id}, headers_a, res.status_code, res_json))

    output.append("## 5. Invalid project -> 404 or 403\n")
    invalid_proj_id = str(uuid.uuid4())
    res = requests.get(f"{BASE_URL}/api/v1/prompts?project_id={invalid_proj_id}", headers=headers_a)
    try:
        res_json = res.json()
    except:
        res_json = res.text
    output.append(format_req_res("User A accesses invalid project", "GET", f"/api/v1/prompts?project_id={invalid_proj_id}", None, headers_a, res.status_code, res_json))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(output))
    
    print(f"Verification complete. Report saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    run_tests()
