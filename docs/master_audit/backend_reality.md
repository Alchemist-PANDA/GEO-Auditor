# Backend Reality Audit — Endpoint Verification

This document compiles all REST API endpoints defined in the FastAPI backend routers, auditing their authentication status, test coverage, and frontend integration.

---

## REST API Connectivity Matrix

| Route Path | HTTP Method | Protected | Tested | Used by Frontend | Code Reference |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/api/v1/workspaces/register` | `POST` | No (Public) | Yes | Yes (Registration UI) | [workspaces/router.py:24](file:///e:/Profound-cloning/backend/app/modules/workspaces/router.py#L24) |
| `/api/v1/workspaces/token` | `POST` | No (Public) | Yes | Yes (Login UI) | [workspaces/router.py:51](file:///e:/Profound-cloning/backend/app/modules/workspaces/router.py#L51) |
| `/api/v1/workspaces/sync` | `POST` | Yes | Yes | No (Dormant profile hook) | [workspaces/router.py:78](file:///e:/Profound-cloning/backend/app/modules/workspaces/router.py#L78) |
| `/api/v1/workspaces` | `POST` | Yes | Yes | Yes (Create WS method) | [workspaces/router.py:94](file:///e:/Profound-cloning/backend/app/modules/workspaces/router.py#L94) |
| `/api/v1/workspaces` | `GET` | Yes | Yes | Yes (List workspaces) | [workspaces/router.py:203](file:///e:/Profound-cloning/backend/app/modules/workspaces/router.py#L203) |
| `/api/v1/workspaces/projects` | `POST` | Yes | Yes | Yes (Create project) | [workspaces/router.py:112](file:///e:/Profound-cloning/backend/app/modules/workspaces/router.py#L112) |
| `/api/v1/workspaces/projects` | `GET` | Yes | Yes | Yes (List projects) | [workspaces/router.py:215](file:///e:/Profound-cloning/backend/app/modules/workspaces/router.py#L215) |
| `/api/v1/workspaces/brands` | `POST` | Yes | Yes | Yes (Create brand) | [workspaces/router.py:142](file:///e:/Profound-cloning/backend/app/modules/workspaces/router.py#L142) |
| `/api/v1/workspaces/projects/{project_id}/brands` | `GET` | Yes | Yes | Yes (List project brands) | [workspaces/router.py:234](file:///e:/Profound-cloning/backend/app/modules/workspaces/router.py#L234) |
| `/api/v1/workspaces/competitors` | `POST` | Yes | Yes | Yes (Create competitor) | [workspaces/router.py:172](file:///e:/Profound-cloning/backend/app/modules/workspaces/router.py#L172) |
| `/api/v1/workspaces/brands/{brand_id}/competitors` | `GET` | Yes | Yes | Yes (List brand comps) | [workspaces/router.py:245](file:///e:/Profound-cloning/backend/app/modules/workspaces/router.py#L245) |
| `/api/v1/prompts` | `GET` | Yes | Yes | Yes (List active prompts) | [prompts/router.py:15](file:///e:/Profound-cloning/backend/app/modules/prompts/router.py#L15) |
| `/api/v1/prompts` | `POST` | Yes | Yes | Yes (Batch upload prompts) | [prompts/router.py:26](file:///e:/Profound-cloning/backend/app/modules/prompts/router.py#L26) |
| `/api/v1/prompts/run` | `POST` | Yes (Rate Ltd) | Yes | Yes (Launch run console) | [prompts/router.py:36](file:///e:/Profound-cloning/backend/app/modules/prompts/router.py#L36) |
| `/api/v1/analytics/visibility` | `GET` | Yes | Yes | Yes (Dashboard KPI/SOV) | [analysis/router.py:33](file:///e:/Profound-cloning/backend/app/modules/analysis/router.py#L33) |
| `/api/v1/analytics/citations` | `GET` | Yes | Yes | Yes (Cited URLs panel) | [analysis/router.py:43](file:///e:/Profound-cloning/backend/app/modules/analysis/router.py#L43) |
| `/api/v1/analytics/explorer` | `GET` | Yes | Yes | Yes (Keyword cluster graph)| [analysis/router.py:53](file:///e:/Profound-cloning/backend/app/modules/analysis/router.py#L53) |
| `/api/v1/audit/request` | `POST` | Yes | Yes | Yes (Landing page check) | [analysis/router.py:65](file:///e:/Profound-cloning/backend/app/modules/analysis/router.py#L65) |
| `/api/v1/audit/{audit_id}` | `GET` | Yes | Yes | Yes (Retrieve audit report) | [analysis/router.py:119](file:///e:/Profound-cloning/backend/app/modules/analysis/router.py#L119) |
| `/api/v1/audit` | `GET` | Yes | Yes | Yes (List audit histories) | [analysis/router.py:135](file:///e:/Profound-cloning/backend/app/modules/analysis/router.py#L135) |
| `/api/v1/recommendations` | `GET` | Yes | Yes | Yes (Display dashboard recs)| [recommendations/router.py:16](file:///e:/Profound-cloning/backend/app/modules/recommendations/router.py#L16) |
| `/api/v1/recommendations/generate` | `POST` | Yes | Yes | Yes (Trigger rules generation) | [recommendations/router.py:28](file:///e:/Profound-cloning/backend/app/modules/recommendations/router.py#L28) |
| `/api/v1/recommendations/advanced` | `POST` | Yes (Rate Ltd) | Yes | Yes (Launch LLM analysis) | [recommendations/router.py:44](file:///e:/Profound-cloning/backend/app/modules/recommendations/router.py#L44) |
| `/api/v1/recommendations/{rec_id}/status` | `PATCH` | Yes | Yes | Yes (Resolve/ignore tasks) | [recommendations/router.py:60](file:///e:/Profound-cloning/backend/app/modules/recommendations/router.py#L60) |
| `/api/v1/agency/profile` | `GET` | Yes | **No** | No (Dormant profile route) | [agency/router.py:11](file:///e:/Profound-cloning/backend/app/modules/agency/router.py#L11) |
| `/api/v1/agency/clients` | `GET` | Yes | **No** | No (Static UI view) | [agency/router.py:25](file:///e:/Profound-cloning/backend/app/modules/agency/router.py#L25) |
| `/api/v1/agency/clients` | `POST` | Yes | **No** | No (Static UI view) | [agency/router.py:54](file:///e:/Profound-cloning/backend/app/modules/agency/router.py#L54) |
