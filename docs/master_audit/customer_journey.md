# Customer Journey Audit

This document simulates a customer's progression through the platform, tracking the health of each interaction.

---

## Journey Progress Tracker

| Stage | Step | Status | Core Blocker |
| :--- | :--- | :--- | :--- |
| **1** | **Register** | **Working** | None. Registration endpoint successfully hashes passwords and seeds organization schemas in the database. |
| **2** | **Login** | **Working** | None. Generates and stores signed JWTs in `localStorage` as `auth_token`. |
| **3** | **Create Brand** | **Working** | None. Endpoint checks tenancy restrictions and inserts brand records associated with the user's organization. |
| **4** | **Add Competitor** | **Working** | None. Endpoint inserts competitor domain names associated with the target brand structure. |
| **5** | **Run Audit** | **Broken / Partial** | **1. Guest Portal Block**: Landing page audit submissions are blocked because the `/audit/request` endpoint requires Bearer JWT authentication and enforces that the payload email matches the authenticated user.<br>**2. Redis Queue Dependency**: If Redis is not running locally, enqueuing prompt runs or heuristic audits fails. |
| **6** | **View Results** | **Partial** | **Disconnected Sub-Pages**: While the main Dashboard, Citations list, and Heuristic Audits history pull from backend data, sub-menus like `/model` and `/industry` show entirely static hardcoded layouts. |

---

## Detailed Step Evaluations

### Step 1: User Registration
* **Frontend**: `/register`
* **API Route**: `POST /api/v1/workspaces/register`
* **Status**: **Working**
* **Verification**: Password input is hashed correctly, and a default Organization + Workspace + Project is automatically seeded in the DB during registration.

### Step 2: Login
* **Frontend**: `/login`
* **API Route**: `POST /api/v1/workspaces/token`
* **Status**: **Working**
* **Verification**: Verifies bcrypt password, creates JWT session, saves token to client storage, and redirects to dashboard.

### Step 3: Create Brand
* **Frontend**: `/dashboard` (Setup modals)
* **API Route**: `POST /api/v1/workspaces/brands`
* **Status**: **Working**
* **Verification**: Tenancy constraints verify the parent project belongs to the user's organization before inserting.

### Step 4: Add Competitor
* **Frontend**: `/dashboard` (Add competitor forms)
* **API Route**: `POST /api/v1/workspaces/competitors`
* **Status**: **Working**
* **Verification**: Domain and name are inserted under the appropriate brand identifier with proper ownership validation.

### Step 5: Run Audit
* **Frontend**: `/` (Landing page free audit) & `/prompts` (Launch console)
* **API Routes**: `POST /api/v1/audit/request` & `POST /api/v1/prompts/run`
* **Status**: **Broken** (for Landing page guests), **Working** (for logged-in console runs in Sandbox mode)
* **Blocker**: Anonymous users on the landing page cannot submit URL audits because the endpoint requires JWT authentication.

### Step 6: View Results
* **Frontend**: `/dashboard`, `/citations`, `/audits`, `/recommendations`
* **API Routes**: `GET /api/v1/analytics/visibility`, `GET /api/v1/analytics/citations`, `GET /api/v1/audit`, `GET /api/v1/recommendations`
* **Status**: **Partial**
* **Gaps**: Core dashboards retrieve database values properly. However, sub-navigation dashboards (Model Analytics, Inbox, Industry rankings) render only mock hardcoded client layouts.
