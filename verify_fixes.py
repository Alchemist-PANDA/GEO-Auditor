import requests
import uuid

BASE_URL = "http://localhost:8080"

def run_tests():
    print("=== STARTING RE-VERIFICATION ===")
    
    email_a = f"usera_{uuid.uuid4().hex[:6]}@example.com"
    email_b = f"userb_{uuid.uuid4().hex[:6]}@example.com"

    # Register User A
    res = requests.post(f"{BASE_URL}/api/v1/workspaces/register", json={
        "email": email_a, "password": "password123", "full_name": "User A", "organization_name": "Org A"
    })
    print("User A Register:", res.status_code)

    # Register User B
    res = requests.post(f"{BASE_URL}/api/v1/workspaces/register", json={
        "email": email_b, "password": "password123", "full_name": "User B", "organization_name": "Org B"
    })
    print("User B Register:", res.status_code)

    # Login User A
    res = requests.post(f"{BASE_URL}/api/v1/workspaces/token", json={"email": email_a, "password": "password123"})
    token_a = res.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Login User B
    res = requests.post(f"{BASE_URL}/api/v1/workspaces/token", json={"email": email_b, "password": "password123"})
    token_b = res.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Create Workspace A
    res = requests.post(f"{BASE_URL}/api/v1/workspaces", headers=headers_a, json={"name": "WS A", "tier": "free"})
    ws_a_id = res.json()["id"]

    # Create Workspace B
    res = requests.post(f"{BASE_URL}/api/v1/workspaces", headers=headers_b, json={"name": "WS B", "tier": "free"})
    ws_b_id = res.json()["id"]

    # Create Project A
    res = requests.post(f"{BASE_URL}/api/v1/workspaces/projects", headers=headers_a, json={"name": "Proj A", "workspace_id": ws_a_id})
    proj_a_id = res.json()["id"]

    # Create Project B
    res = requests.post(f"{BASE_URL}/api/v1/workspaces/projects", headers=headers_b, json={"name": "Proj B", "workspace_id": ws_b_id})
    proj_b_id = res.json()["id"]

    # Test IDOR on Prompts
    res = requests.get(f"{BASE_URL}/api/v1/prompts?project_id={proj_b_id}", headers=headers_a)
    print("IDOR Prompts (expect 403):", res.status_code)

    # Test IDOR on Recommendations
    res = requests.get(f"{BASE_URL}/api/v1/recommendations?project_id={proj_b_id}", headers=headers_a)
    print("IDOR Recommendations (expect 403):", res.status_code)

    # Test IDOR Project Creation
    res = requests.post(f"{BASE_URL}/api/v1/workspaces/projects", headers=headers_a, json={"name": "Hacked Proj", "workspace_id": ws_b_id})
    print("IDOR Project Creation (expect 403):", res.status_code)

    # Test Foreign Key / Invalid Workspace
    invalid_ws_id = str(uuid.uuid4())
    res = requests.post(f"{BASE_URL}/api/v1/workspaces/projects", headers=headers_a, json={"name": "Orphan Proj", "workspace_id": invalid_ws_id})
    print("Foreign Key Enforcement (expect 404):", res.status_code)

if __name__ == "__main__":
    run_tests()
