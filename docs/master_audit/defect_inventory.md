# Actionable Defect Inventory

This document details all verified defects identified in the codebase, categorized by priority.

---

## P0 — Launch Blockers

### Defect ID: DEF-001 — Public Audit Gated by Authentication
* **Severity**: P0 (Launch Blocker)
* **Evidence**:
  In [analysis/router.py](file:///e:/Profound-cloning/backend/app/modules/analysis/router.py#L65-L73):
  ```python
  @audit_router.post("/request", response_model=AuditResponse, status_code=status.HTTP_202_ACCEPTED)
  async def request_page_audit(
      payload: AuditRequest,
      db: AsyncSession = Depends(get_db),
      current_user: UserSession = Depends(get_current_user)
  ):
      if payload.email.strip() != current_user.email:
          raise HTTPException(status_code=403, detail="Email mismatch with authenticated user")
  ```
* **Root Cause**:
  The backend endpoint `/audit/request` is secured by a Bearer JWT token dependency (`Depends(get_current_user)`) and enforces that the requested email matches the logged-in user. However, the public landing page ([page.tsx](file:///e:/Profound-cloning/frontend/src/app/page.tsx)) features an anonymous lead-generation form requesting a URL and email without any login state, causing a `401 Unauthorized` block on submissions.
* **Affected Files**:
  - [analysis/router.py](file:///e:/Profound-cloning/backend/app/modules/analysis/router.py)
  - [page.tsx](file:///e:/Profound-cloning/frontend/src/app/page.tsx)
* **Fix Strategy**:
  Introduce a public, unauthenticated endpoint `/audit/public-request` that does not require `get_current_user` but has strong IP-based rate limiting (e.g., 2 audits per IP per hour) to prevent script abuse. Change the landing page form to target this new public endpoint.

---

## P1 — Critical Sprints

### Defect ID: DEF-002 — Disconnected Mock Pages / Dead Routes
* **Severity**: P1 (Critical)
* **Evidence**:
  The folder router structure contains folders for `/agency`, `/inbox`, `/industry`, `/model`, and `/search`.
  - [agency/page.tsx](file:///e:/Profound-cloning/frontend/src/app/%28dashboard%29/agency/page.tsx#L22-L46): Displays a "Coming Soon" splash. The corresponding backend router endpoints in [agency/router.py](file:///e:/Profound-cloning/backend/app/modules/agency/router.py) are completely unused.
  - [model/page.tsx](file:///e:/Profound-cloning/frontend/src/app/%28dashboard%29/model/page.tsx#L76-L81): Uses inline mock tables and custom SVG graphics to display dummy analytics comparing ChatGPT, Claude, and Gemini.
* **Root Cause**:
  Development created these routes as visual placeholders during layout phases, but never hooked them to backend database models or API routes.
* **Affected Files**:
  - `frontend/src/app/(dashboard)/agency/page.tsx`
  - `frontend/src/app/(dashboard)/inbox/page.tsx`
  - `frontend/src/app/(dashboard)/industry/page.tsx`
  - `frontend/src/app/(dashboard)/model/page.tsx`
  - `frontend/src/app/(dashboard)/search/page.tsx`
* **Fix Strategy**:
  Since these pages are not present in the primary Sidebar navigation panel ([Sidebar.tsx](file:///e:/Profound-cloning/frontend/src/components/layout/Sidebar.tsx)), remove or hide the routes from the production Next.js build configuration, or fully implement database bindings for Model and Industry trends to prevent dead routes from leaking into production.

---

## P2 — Important Sprints

### Defect ID: DEF-003 — Permissive Wildcard CORS Configuration
* **Severity**: P2 (Important)
* **Evidence**:
  In [main.py](file:///e:/Profound-cloning/backend/app/main.py#L19-L25):
  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```
* **Root Cause**:
  Wildcard origins are allowed, enabling any malicious origin to query the APIs, violating standard security headers when cookies or tokens are involved.
* **Affected Files**:
  - [main.py](file:///e:/Profound-cloning/backend/app/main.py)
* **Fix Strategy**:
  Bind `allow_origins` to a configured settings array (e.g., `settings.CORS_ORIGINS`) populated from environment variables, defaulting to `["http://localhost:3000"]` for dev, and strict production domain names in deployment.

### Defect ID: DEF-004 — Hardcoded Local Email File Dump Fallback
* **Severity**: P2 (Important)
* **Evidence**:
  In [analysis/service.py](file:///e:/Profound-cloning/backend/app/modules/analysis/service.py#L975-L980):
  ```python
  log_dir = r"e:\Profound-cloning\docs\implementation\logs\emails"
  os.makedirs(log_dir, exist_ok=True)
  file_path = os.path.join(log_dir, f"audit_{audit.id}.html")
  with open(file_path, "w", encoding="utf-8") as f:
      f.write(email_html)
  ```
* **Root Cause**:
  If `RESEND_API_KEY` is missing (as in standard local dev runs), the email worker dumps reports to a hardcoded local file path in the Windows system workspace. If deployed to a server/container (e.g. Linux), this absolute path write will crash due to permission or syntax errors.
* **Affected Files**:
  - [analysis/service.py](file:///e:/Profound-cloning/backend/app/modules/analysis/service.py)
* **Fix Strategy**:
  Specify a relative logging path or temp folder within the workspace root directory (e.g., `os.path.join(os.getcwd(), "tmp", "emails")`), and implement a standard SMTP fallback configuration for production email dispatch when Resend is not used.

### Defect ID: DEF-005 — Weak Default JWT Secret
* **Severity**: P2 (Important)
* **Evidence**:
  In [core/config.py](file:///e:/Profound-cloning/backend/app/core/config.py#L24-L27):
  ```python
  SUPABASE_JWT_SECRET: str = Field(
      default="supabase_jwt_secret_placeholder_change_in_prod",
      validation_alias="SUPABASE_JWT_SECRET"
  )
  ```
* **Root Cause**:
  The system falls back to a weak default secret token if the environment variable is omitted in production, enabling easy JWT forgery.
* **Affected Files**:
  - [core/config.py](file:///e:/Profound-cloning/backend/app/core/config.py)
* **Fix Strategy**:
  Add validation logic on application startup that raises a `ValueError` if `ENVIRONMENT == "production"` and `SUPABASE_JWT_SECRET` matches the default placeholder.
