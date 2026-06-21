# Database Audit

## Row Counts
- **organizations**: 1 rows
- **users**: 0 rows
- **workspaces**: 1 rows
- **projects**: 10 rows
- **brands**: 10 rows
- **competitors**: 10 rows
- **prompts**: 15 rows
- **prompt_runs**: 15 rows
- **responses**: 15 rows
- **citations**: 52 rows
- **visibility_scores**: 15 rows
- **page_audits**: 0 rows
- **recommendations**: 49 rows

## Foreign Key Integrity
- Checked `PRAGMA foreign_key_check`.
- **Result:** No foreign key violations found. 

## Missing Relationships / Schema Mismatches
- `users` table is currently empty, but foreign key references `organization_id -> organizations(id)`.
- `page_audits` table is empty.
- Note: It was previously noted that there is a "Client relationship mapping issue", though basic PRAGMA checks pass. The issue may be at the SQLAlchemy ORM layer (e.g. InvalidRequestError) rather than database level schema.
