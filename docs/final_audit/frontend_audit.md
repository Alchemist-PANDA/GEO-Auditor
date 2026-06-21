# Frontend Subsystem Audit

An exhaustive review of the user-facing pages, interactive components, state stores, and backend integrations.

---

## Page-by-Page Audit Matrix

| Page Route | URL | API Connected? | Mock Data Usage | Production Ready? |
| :--- | :--- | :---: | :--- | :---: |
| **Landing** | `/` | **Yes** | Displays actual API response status, but crawler console logs are simulated client-side. | **No** |
| **Login** | `/login` | **Yes** | Syncs profile dynamically. | **Yes** |
| **Register** | `/register` | **No** | **MISSING PAGE.** Route does not exist in code. | **No** |
| **Dashboard** | `/dashboard` | **Partial** | Pulls visibility scores, but falls back to static hardcoded metrics if DB is empty. | **No** |
| **Prompts** | `/prompts` | **No** | **100% Mocked.** Hardcoded Tesla EV data. | **No** |
| **Citations** | `/citations` | **No** | **100% Mocked.** Hardcoded citations table. | **No** |
| **Explorer** | `/explorer` | **No** | **100% Mocked.** Hardcoded real estate SVG graph. | **No** |
| **Improve** | `/recommendations` | **Yes** | Fully connected. Fetches, triggers local/LLM generation. | **Yes** |
| **Audits** | `/audits` | **Yes** | Fetches and displays real audits, but only accessible via manual URL navigation. | **No** |
| **Agency** | `/agency` | **No** | **Coming soon banner.** Non-functional. | **No** |
| **Industry** | `/industry` | **No** | **100% Mocked.** Hardcoded SVG area chart. | **No** |
| **Inbox** | `/inbox` | **No** | **100% Mocked.** Hardcoded alerts. Light theme. | **No** |
| **Search** | `/search` | **No** | **100% Mocked.** Hardcoded variations table. Light theme. | **No** |
| **Model** | `/model` | **No** | **100% Mocked.** Hardcoded SVG radar chart. | **No** |

---

## Core Findings & Issues

### 1. Missing Pages
* **No Signup Flow**: The lack of a registration/sign-up screen forces users to rely on a developer back-door (`login/page.tsx` automatically creates organization and user profile records when any credentials with `password123` are typed).

### 2. High Percentage of Mock Data
* **8 out of 11 routes** in the dashboard layout are purely static pages. A user attempting to use the platform for any brand other than "Rho" or "Tesla" will notice that:
  - "Prompts" lists unrelated electric vehicle search queries.
  - "Topic Explorer" displays a hardcoded node network for "real estate agency".
  - "Citations" lists fake financial technology links.
  - "Industry" displays static curves comparing Chase, Amex, and Rho.
* These components do not utilize the dynamic Zustand store functions (`geoStore.ts`) even though the backend implements the endpoints.

### 3. UX & Aesthetic Inconsistencies
* **Contrasting Backgrounds**: The dashboard, login, and recommendations pages feature a dark mode styling. However, **Inbox**, **Citations**, and **Search / Prompt Discovery** use a bright light mode theme (`bg-[#f8fafc]` and dark slate text), which ruins visual flow.
* **Hardcoded Sidebar Data**: The sidebar (`Sidebar.tsx`) has static listings for Brands (Chase, Amex, Brex), Topics (Fintech software, Expense management), and Domains (ramp.com, gartner.com), rather than loading the user's active project configuration dynamically.
* **Sidebar Navigation**: There is an `Audits` link in the sidebar, but it is not linked from the main landing page, making the dynamic crawls history difficult for first-time public users to find.

### 4. Performance & Code Quality Risks
* **Recharts Console Warnings**: Missing keys and outdated properties in the Recharts implementations cause warning spam in developer consoles.
* **Typo in Code**: In `search/page.tsx`, the static query list has a typo: `v.query || v.corporate` which is safe-guarded locally but highlights sloppy mock copying.
