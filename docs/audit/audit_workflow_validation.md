# Audit Workflow Validation

## Flow
Landing Page -> Submit URL -> Create PageAudit -> Queue ARQ Job -> Worker Executes -> Audit Stored -> Email Generated -> Dashboard Accessible

## Runtime Analysis
Based on source code analysis and runtime environment testing:

1. **Landing Page -> Submit URL**: Works via API `POST /api/v1/analytics/audit/request`. The URL structure is validated (must start with `http://` or `https://`).
2. **Create PageAudit**: A `PageAudit` record is successfully created in the database with status `PENDING`.
3. **Queue ARQ Job**: The backend tries to queue `run_heuristic_audit` to Redis. **Failure Point**: If Redis is not accessible, this fails with a 500 error. The application does not handle missing Redis gracefully with a fallback queue.
4. **Worker Executes**: The `arq` worker picks up the job. It uses `AnalysisService.perform_heuristic_audit` which fetches HTML via `httpx`, parses it, and computes scores.
5. **Audit Stored**: The database is updated with `overall_score`, `schema_markup_score`, etc., and status is set to `COMPLETED`.
6. **Email Generated**: `AnalysisService.send_audit_email` simulates an email payload for Resend API. In development, it writes an HTML file to local logs.
7. **Dashboard Accessible**: No UI/Dashboard endpoint is currently fetching or rendering the completed `PageAudit` results. The `page_audits` table remains at 0 rows indicating this feature has never been used in the active environment.

## Conclusion
- **Status**: RED (Broken in practice)
- **Details**: The workflow strictly depends on Redis for the ARQ job queue and fails if it is not present. Furthermore, the frontend connection to retrieve and display these audits on a dashboard does not exist (the table is completely empty).
