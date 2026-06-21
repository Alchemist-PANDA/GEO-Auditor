# Repository Audit Report

This report documents the real, verified technical state of the entire Generative Engine Optimization (GEO) platform codebase across its core subsystems.

---

## Subsystem Health Matrix

| Subsystem | Health Status | Core Verified Evidence |
| :--- | :---: | :--- |
| **Frontend** | <span style="color:red;font-weight:bold;">RED</span> | **8 out of 11 routes** in the dashboard are client-side static mocks with hardcoded SVGs/tables. No automated frontend tests exist. **Register route is completely missing.** |
| **Backend** | <span style="color:yellow;font-weight:bold;">YELLOW</span> | FastAPI app is structured cleanly, but **pytest suite is currently broken (fails with 401s)** due to route-auth additions that are not mocked in the tests. Multiple API endpoints lack IDOR validation. |
| **Workers** | <span style="color:yellow;font-weight:bold;">YELLOW</span> | `arq` worker handles background prompt executions and audits, but lacks retry policies, backoffs, or a dead letter queue. Dev mode falls back to hardcoded responses if API keys are missing. |
| **Database** | <span style="color:red;font-weight:bold;">RED</span> | SQLite database does not enforce constraints because **`PRAGMA foreign_keys=ON` connection hook is commented out** in the SQLAlchemy setup. Missing search indexes across major tracking fields. |
| **Infrastructure** | <span style="color:red;font-weight:bold;">RED</span> | Only a single backend `Dockerfile` is provided. No Docker Compose environment, no production database/Redis scaling setup, and no environment deployment scripting. |
| **Documentation** | <span style="color:yellow;font-weight:bold;">YELLOW</span> | Standard setup READMEs exist, but project completion metrics are heavily overstated and obscure the fact that the application is mostly an interactive mock. |

---

## Detailed Findings

### 1. Frontend Subsystem
* **Mock Dominance**: The pages for **Prompts**, **Citations**, **Topic Explorer**, **Industry Ranking**, **Search / Prompt Discovery**, **Inbox / Alerts**, **Model Analytics**, and **Agency Portal** are 100% mocked. They contain static UI tables, SVG charts, and hardcoded values that do not connect to the backend APIs.
* **Missing Signup**: There is no registration page (`/register`) implemented in the code, preventing self-service user signup.
* **UI Themes & Layouts**: Highly inconsistent design. Several pages use a dark slate theme, while others (like citations and search) use a light gray theme, pointing to copy-pasted templates. The workspace navigation is hardcoded to a mock "Rho" brand in the sidebar.

### 2. Backend Subsystem
* **Broken Test Suite**: Running `pytest` fails with `401 Unauthorized` errors on route tests (`test_audit_api.py` and `test_auth.py`). This is because auth dependencies (`get_current_user`) were added to the API endpoints without updating the tests to include valid JWT mock headers or seeding the required mock users in the SQLite database.
* **IDOR Exploits**: Brand, competitor, and agency endpoints lack ownership checks. Any authenticated user can insert data into any project or organization by spoofing identifiers.

### 3. Workers Subsystem
* **Task Loss Vulnerability**: If Redis goes down, `arq` fails to enqueue background audits. While the API handles this via a 503 response, there is no job persistence or dead-letter recovery for tasks that fail mid-execution.
* **Mock LLM Dependency**: Dev environment uses random selections from three hardcoded text strings. This prevents verifying the GEO engine's actual parsing of user-created brands or custom URLs without live API credits.

### 4. Database Subsystem
* **Commented Constraints**: The event listener that triggers `PRAGMA foreign_keys=ON` on connection is commented out in [database.py](file:///e:/Profound-cloning/backend/app/core/database.py#L14-L19). Database constraints are ignored in SQLite, allowing cascade deletions to break and orphan rows to pile up.

### 5. Infrastructure & Devops
* **No Compose Scripting**: No Docker Compose files are present to easily orchestrate the backend FastAPI server, `arq` worker, Redis instance, and PostgreSQL database. Deployment requires tedious manual configuration.
