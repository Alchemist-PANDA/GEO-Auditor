# Backend Subsystem Audit

A comprehensive security and logic audit of the backend API endpoints, controllers, routers, and services.

---

## API Endpoint Audit Summary

| Endpoint | Purpose | Request/Response Validation | Error Handling | Ownership Validation |
| :--- | :--- | :--- | :--- | :--- |
| `POST /workspaces/token` | User Login / JWT Issuance | **Strong** | **Strong** (401 on incorrect credentials) | N/A (Authentication endpoint) |
| `POST /workspaces/register` | User Registration | **Strong** | **Strong** (400 on duplicate email) | N/A (Public endpoint) |
| `POST /workspaces/sync` | Profile Sync | **Strong** | **Medium** | **Medium** (Scopes organization to current user) |
| `POST /workspaces` | Workspace Creation | **Strong** | **Medium** | **Strong** (Assigns organization id from active user) |
| `POST /workspaces/projects` | Project Creation | **Strong** | **Strong** (404 on missing workspace) | **Strong** (Verifies user organization matches workspace) |
| `POST /workspaces/brands` | Brand Creation | **Strong** | **Weak** | <span style="color:red;font-weight:bold;">NONE</span> (Does not verify project ownership) |
| `POST /workspaces/competitors`| Competitor Creation | **Strong** | **Weak** | <span style="color:red;font-weight:bold;">NONE</span> (Does not verify brand ownership) |
| `GET /prompts` | Get Prompts | **Strong** | **Medium** | **Strong** (Verifies user organization owns project) |
| `POST /prompts` | Add Prompts Batch | **Strong** | **Medium** | **Strong** (Verifies user organization owns project) |
| `POST /prompts/run` | Trigger Prompt runs | **Strong** | **Medium** | **Strong** (Verifies user organization owns project) |
| `GET /analytics/visibility`| Visibility Scores | **Strong** | **Medium** | **Strong** (Verifies user organization owns project) |
| `GET /analytics/citations` | Citations Tracker | **Strong** | **Medium** | **Strong** (Verifies user organization owns project) |
| `GET /analytics/explorer` | Topic Clustering | **Strong** | **Medium** | <span style="color:yellow;font-weight:bold;">NONE</span> (Open read endpoint for all topics) |
| `POST /audit/request` | Public Crawl Request | **Strong** (Enforces email matches token) | **Strong** (503 on Redis downtime) | **Strong** |
| `GET /audit/{audit_id}` | Retrieve Page Audit | **Strong** | **Strong** (404 on missing audit) | **Strong** (Verifies email matches token) |
| `GET /audit` | List Page Audits | **Strong** | **Medium** | **Strong** (Filters audits by active user email) |
| `GET /agency/profile` | Agency Statistics | **Strong** | **Medium** | **Strong** (Verifies agency profile matches user org) |
| `GET /agency/clients` | List Clients | **Strong** | **Medium** | <span style="color:red;font-weight:bold;">NONE</span> (Accepts `agency_id` without user authorization check) |
| `POST /agency/clients` | Create Client | **Strong** | **Medium** | <span style="color:red;font-weight:bold;">NONE</span> (Allows creating client profiles arbitrarily) |

---

## Detailed Findings

### 1. Critical IDOR Vulnerabilities
* **Brand Creation Bypass**: `POST /api/v1/workspaces/brands` accepts a `BrandCreate` payload with a `project_id`. However, the router does not call `verify_project_access` or perform any check to ensure that the user's organization owns that project. Any authenticated user can create tracking brands inside other users' projects.
* **Competitor Creation Bypass**: `POST /api/v1/workspaces/competitors` accepts a `CompetitorCreate` payload with a `brand_id`. No validation checks are run against the brand. Anyone can inject competitors into other tenants' brand profiles.
* **Agency Client Management Bypass**: `GET /api/v1/agency/clients` accepts an `agency_id` as a query parameter and returns all clients under that agency. It does not check if the user belongs to the target agency. Similarly, `POST /api/v1/agency/clients` allows injecting client rows under any `agency_id`.

### 2. Broken Test Suite
* **Authentication Refusal**: The router tests (`test_auth.py` and `test_audit_api.py`) are completely broken in dev because:
  - Route authentication was introduced, but tests issue HTTP requests without bearer tokens, resulting in immediate `401 Unauthorized` responses.
  - The tests try to authenticate using mock email addresses (`test@profound-aeo.com` and `user@profound-aeo.com`) that do not exist in the seeded SQLite database.
* **PostgreSQL Connection Failures**: Running the generic `pytest` command defaults the database connection to the PostgreSQL port `5432` configured in `config.py`. Since PostgreSQL is not running in local test environments, the engine throws `ConnectionRefusedError` and blocks the entire suite.

### 3. Logic & Error Handling Flaws
* **Crawl Failure Handling**: Inside [service.py](file:///e:/Profound-cloning/backend/app/modules/analysis/service.py#L678-L680), if a target URL fails to crawl (due to timeout, connection error, DNS lookup, etc.), the engine catches the exception and overrides the crawler HTML content with a fallback title: `"<html><title>Error Fetching Site</title>...</html>"`. The audit then successfully parses this fallback HTML, computes a low score (~35/100), marks the audit status as `COMPLETED`, and sends a report. It should mark the audit status as `FAILED` or raise a validation exception.
