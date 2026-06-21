# Security Audit & Truth

This document evaluates the access control and data security posture of the platform backend codebase.

---

## 1. Authentication & JWT Validation
* **Mechanism**: Signed bearer token validation.
* **Code Reference**: [core/security.py:14-36](file:///e:/Profound-cloning/backend/app/core/security.py#L14-L36)
  ```python
  async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> UserSession:
      token = credentials.credentials
      try:
          payload = jwt.decode(
              token,
              settings.SUPABASE_JWT_SECRET,
              algorithms=["HS256"],
              audience="authenticated"
          )
          user_id = payload.get("sub")
          email = payload.get("email")
          role = payload.get("role", "member")
          if not user_id or not email:
              raise HTTPException(status_code=401, detail="Invalid token claims")
          return UserSession(id=user_id, email=email, role=role)
      except JWTError:
          raise HTTPException(status_code=401, detail="Could not validate credentials")
  ```
* **Security Finding (Insecure Secret Default)**:
  In [core/config.py:24-27](file:///e:/Profound-cloning/backend/app/core/config.py#L24-L27), `SUPABASE_JWT_SECRET` defaults to `"supabase_jwt_secret_placeholder_change_in_prod"`. In a production deployment, if this value is not supplied, it will run using this weak placeholder, leaving it vulnerable to signature forgery.
  * *Required Fix*: Raise a `ValueError` on startup if `ENVIRONMENT == "production"` and the secret is equal to the default placeholder.

---

## 2. IDOR, Tenant Isolation & Ownership Checks
Tenant isolation is strictly enforced across all major modules via organization membership checks.

### 2.1 Workspace & Resource Creations
- **Project Creation**:
  Checks that the workspace belongs to the user's organization.
  * *Code Reference*: [workspaces/router.py:136-137](file:///e:/Profound-cloning/backend/app/modules/workspaces/router.py#L136-L137)
  ```python
  if ws.organization_id != user.organization_id:
      raise HTTPException(status_code=403, detail="Not authorized to create project in this workspace")
  ```
- **Brand Creation**:
  Checks that the project workspace belongs to the user's organization.
  * *Code Reference*: [workspaces/router.py:166-167](file:///e:/Profound-cloning/backend/app/modules/workspaces/router.py#L166-L167)
  ```python
  if org_id != user.organization_id:
      raise HTTPException(status_code=403, detail="Not authorized to access this project")
  ```
- **Competitor Creation**:
  Checks that the brand belongs to a project workspace owned by the user's organization.
  * *Code Reference*: [workspaces/router.py:197-198](file:///e:/Profound-cloning/backend/app/modules/workspaces/router.py#L197-L198)
  ```python
  if org_id != user.organization_id:
      raise HTTPException(status_code=403, detail="Not authorized to access this brand")
  ```

### 2.2 Analytics & Recommendations Lists
- **verify_project_access Helper**:
  Used on routes listing visibility indicators, cited URLs, and tasks to ensure tenant project ownership.
  * *Code Reference*: [analysis/router.py:17-31](file:///e:/Profound-cloning/backend/app/modules/analysis/router.py#L17-L31)
  ```python
  async def verify_project_access(db: AsyncSession, project_id: str, current_user: UserSession):
      user_res = await db.execute(select(User).where(User.id == current_user.id))
      user = user_res.scalar_one_or_none()
      if not user:
          raise HTTPException(status_code=403, detail="Not authorized")
      res = await db.execute(
          select(Workspace.organization_id)
          .join(Project, Project.workspace_id == Workspace.id)
          .where(Project.id == project_id)
      )
      org_id = res.scalar_one_or_none()
      if not org_id or org_id != user.organization_id:
          raise HTTPException(status_code=403, detail="Not authorized to access this project")
  ```
- **Recommendations Status Updates**:
  Ensures a user can only patch items belonging to their project scope.
  * *Code Reference*: [recommendations/router.py:77](file:///e:/Profound-cloning/backend/app/modules/recommendations/router.py#L77)
  ```python
  await verify_project_access(db, rec.project_id, current_user)
  ```

### 2.3 Page Audit Submissions
- **Submission Access**: Enforces that the requested audit email exactly matches the logged-in token email.
  * *Code Reference*: [analysis/router.py:71-73](file:///e:/Profound-cloning/backend/app/modules/analysis/router.py#L71-L73)
  ```python
  if payload.email.strip() != current_user.email:
      raise HTTPException(status_code=403, detail="Email mismatch with authenticated user")
  ```
- **Report Retrieval**: Protects audit views from unauthorized users.
  * *Code Reference*: [analysis/router.py:130-131](file:///e:/Profound-cloning/backend/app/modules/analysis/router.py#L130-L131)
  ```python
  if audit.email != current_user.email:
      raise HTTPException(status_code=403, detail="Not authorized to access this audit")
  ```

---

## 3. Rate Limiting
The custom `RateLimiter` class is used to prevent abuse on resource-intensive endpoints:
- **Prompt Execution Runs**: Enforces a limit of 10 requests per 60 seconds.
  * *Code Reference*: [prompts/router.py:36](file:///e:/Profound-cloning/backend/app/modules/prompts/router.py#L36)
  ```python
  @router.post("/run", status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(RateLimiter(10, 60))])
  ```
- **Advanced Recommendations Generation**: Enforces a limit of 5 requests per 60 seconds.
  * *Code Reference*: [recommendations/router.py:44](file:///e:/Profound-cloning/backend/app/modules/recommendations/router.py#L44)
  ```python
  @router.post("/advanced", status_code=status.HTTP_201_CREATED, dependencies=[Depends(RateLimiter(5, 60))])
  ```
- **Audit Submissions (Missing Limitation)**:
  * *Finding*: The `/audit/request` endpoint lacks rate limiting, making it vulnerable to denial-of-service crawling tasks.

---

## 4. Foreign Key Constraints
Models are defined using standard SQLAlchemy `ForeignKey` relationships, ensuring referential integrity at the database engine layer:
- `Workspace.organization_id` -> references `organizations.id` on delete CASCADE: [workspaces/models.py:39](file:///e:/Profound-cloning/backend/app/modules/workspaces/models.py#L39)
- `Project.workspace_id` -> references `workspaces.id` on delete CASCADE: [workspaces/models.py:56](file:///e:/Profound-cloning/backend/app/modules/workspaces/models.py#L56)
- `Brand.project_id` -> references `projects.id` on delete CASCADE: [workspaces/models.py:72](file:///e:/Profound-cloning/backend/app/modules/workspaces/models.py#L72)
- `Competitor.brand_id` -> references `brands.id` on delete CASCADE: [workspaces/models.py:87](file:///e:/Profound-cloning/backend/app/modules/workspaces/models.py#L87)
- `PageAudit.workspace_id` -> references `workspaces.id` on delete SET NULL: [analysis/models.py:146](file:///e:/Profound-cloning/backend/app/modules/analysis/models.py#L146)
