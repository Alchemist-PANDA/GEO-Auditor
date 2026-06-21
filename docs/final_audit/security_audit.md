# Security Audit Report

A security evaluation of the backend APIs, authentication, authorization, IDOR vectors, rate limiting, and database constraints.

---

## Vulnerability Classification

| Vulnerability | Component | Severity | Description |
| :--- | :--- | :---: | :--- |
| **IDOR on Brands / Competitors** | `workspaces/router.py` | <span style="color:red;font-weight:bold;">CRITICAL</span> | Brand and Competitor creation endpoints lack project/brand ownership checks. Anyone can add brands or competitors under other users' projects. |
| **IDOR on Agency Clients** | `agency/router.py` | <span style="color:red;font-weight:bold;">CRITICAL</span> | Agency client routes accept an arbitrary `agency_id` query parameter without verifying if the authenticated user belongs to that agency. |
| **Disabled Database Constraints** | `core/database.py` | <span style="color:orange;font-weight:bold;">HIGH</span> | SQLite foreign key checks are commented out. Deleting parents leaves orphaned rows, leading to database state corruption. |
| **Missing Rate Limiting on Audits**| `analysis/router.py` | <span style="color:orange;font-weight:bold;">HIGH</span> | `/audit/request` lacks rate limiting. Attackers can spam the endpoint, launching infinite background crawlers that exhaust server bandwidth. |
| **Hardcoded JWT Secret** | `core/config.py` | <span style="color:yellow;font-weight:bold;">MEDIUM</span> | `SUPABASE_JWT_SECRET` has a default hardcoded placeholder string. If not overridden in production, anyone can sign tokens. |
| **Information Leakage** | `analysis/router.py` | <span style="color:yellow;font-weight:bold;">MEDIUM</span> | Verifying access to non-existent project IDs returns `403 Forbidden` instead of `404 Not Found`, leaking project existence. |
| **Permissive CORS Policy** | `main.py` | <span style="color:blue;font-weight:bold;">LOW</span> | `allow_origins=["*"]` allows any external domain to make requests to the API. |

---

## Detailed Security Vulnerabilities

### 1. Critical IDOR on Brands and Competitors
* **The Vulnerability**:
  ```python
  @router.post("/brands", response_model=BrandOut, status_code=status.HTTP_201_CREATED)
  async def create_brand(brand_in: BrandCreate, db: AsyncSession = Depends(get_db), current_user: UserSession = Depends(get_current_user)):
      brand = await WorkspaceService.create_brand(db, brand_in)
      return brand
  ```
* **The Threat**: Since there is no ownership validation of `brand_in.project_id` against the `current_user`'s organization, any authenticated user can submit a brand under any `project_id`. The exact same vulnerability applies to the `/competitors` endpoint, allowing competitor spoofing.

### 2. Critical IDOR on Agency Client Listing and Creation
* **The Vulnerability**:
  ```python
  @router.get("/clients", response_model=List[ClientOut])
  async def get_agency_clients(agency_id: str = Query(...), db: AsyncSession = Depends(get_db), current_user: UserSession = Depends(get_current_user)):
      clients = await AgencyService.get_clients_by_agency(db, agency_id)
      return clients
  ```
* **The Threat**: The endpoint accepts an arbitrary `agency_id` and queries the database immediately without verifying if the `current_user` is an admin or member of the target `Agency` profile. An attacker can enumerate all clients on the agency tier.

### 3. Missing Rate Limiting on Audit requests
* **The Vulnerability**: Public users can trigger `/audit/request` which launches a real HTML crawler via `perform_heuristic_audit` in the worker.
* **The Threat**: Unlike prompt runs (which are limited to 10 requests per minute) and advanced recommendations (5 requests per minute), the audit request route has no rate limit. Attackers can flood the endpoint, launching thousands of parallel `httpx` worker requests that trigger a self-denial of service (DoS) or get the server's IP blacklisted by target domains.
