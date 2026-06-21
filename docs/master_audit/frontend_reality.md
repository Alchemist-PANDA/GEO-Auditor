# Frontend Reality Audit

This document inventories the implementation status of all dashboard page interfaces in the Next.js frontend application.

---

## Page Connectivity Table

| Route Path | File Path | Status | Data Connectivity | Details |
| :--- | :--- | :--- | :--- | :--- |
| `/` (Landing Page) | [page.tsx](file:///e:/Profound-cloning/frontend/src/app/page.tsx) | **Partially Connected** | **Form Wired / UI Mock Logs** | Submits URL/email to the `/audit/request` API endpoint, but fails for anonymous users due to authentication gating. The scrolling crawler logs in the portal console are client-side visual animations. |
| `/login` | [login/page.tsx](file:///e:/Profound-cloning/frontend/src/app/login/page.tsx) | **Connected** | **Fully Bound** | Hits the `/workspaces/token` backend endpoint to verify credentials and store Bearer JWTs. |
| `/register` | [register/page.tsx](file:///e:/Profound-cloning/frontend/src/app/register/page.tsx) | **Connected** | **Fully Bound** | Submits registration details to the `/workspaces/register` backend endpoint. |
| `/dashboard` | [(dashboard)/dashboard/page.tsx](file:///e:/Profound-cloning/frontend/src/app/%28dashboard%29/dashboard/page.tsx) | **Connected** | **Fully Bound** | Fetches workspaces, projects, visibility index scores, and share of voice breakdowns dynamically from `/analytics/visibility`. |
| `/prompts` | [(dashboard)/prompts/page.tsx](file:///e:/Profound-cloning/frontend/src/app/%28dashboard%29/prompts/page.tsx) | **Connected** | **Fully Bound** | Displays active prompts, accepts batch inserts via `/prompts`, and triggers model runs via `/prompts/run`. |
| `/audits` | [(dashboard)/audits/page.tsx](file:///e:/Profound-cloning/frontend/src/app/%28dashboard%29/audits/page.tsx) | **Connected** | **Fully Bound** | Fetches PageAudit records from the backend and renders score dials, statuses, and recommendations. |
| `/explorer` | [(dashboard)/explorer/page.tsx](file:///e:/Profound-cloning/frontend/src/app/%28dashboard%29/explorer/page.tsx) | **Connected** | **Fully Bound** | Sends search keywords to `/analytics/explorer` and renders dynamic volume counts, geotargeting percentages, and node cluster graphs. |
| `/citations` | [(dashboard)/citations/page.tsx](file:///e:/Profound-cloning/frontend/src/app/%28dashboard%29/citations/page.tsx) | **Connected** | **Fully Bound** | Displays citing URL tables and estimated domain visibility gains fetched from `/analytics/citations`. |
| `/recommendations`| [(dashboard)/recommendations/page.tsx](file:///e:/Profound-cloning/frontend/src/app/%28dashboard%29/recommendations/page.tsx)| **Connected** | **Fully Bound** | Fetches tasks from `/recommendations`, triggers updates on tasks, and queues LLM strategies via `/recommendations/advanced`. |
| `/agency` | [(dashboard)/agency/page.tsx](file:///e:/Profound-cloning/frontend/src/app/%28dashboard%29/agency/page.tsx) | **Mock Data** | **Static Mockup** | Displays a mockup "Coming Soon" splash. The corresponding backend routers inside [agency/router.py](file:///e:/Profound-cloning/backend/app/modules/agency/router.py) are completely unlinked. |
| `/inbox` | [(dashboard)/inbox/page.tsx](file:///e:/Profound-cloning/frontend/src/app/%28dashboard%29/inbox/page.tsx) | **Mock Data** | **Static Mockup** | Renders static hardcoded notifications listing dummy security/crawl alerts. |
| `/industry` | [(dashboard)/industry/page.tsx](file:///e:/Profound-cloning/frontend/src/app/%28dashboard%29/industry/page.tsx) | **Mock Data** | **Static Mockup** | Displays a static mockup table listing hardcoded competitor rankings. |
| `/model` | [(dashboard)/model/page.tsx](file:///e:/Profound-cloning/frontend/src/app/%28dashboard%29/model/page.tsx) | **Mock Data** | **Static Mockup** | Displays hardcoded Radar SVG charts comparing LLMs using dummy statistical ratios. |
| `/search` | [(dashboard)/search/page.tsx](file:///e:/Profound-cloning/frontend/src/app/%28dashboard%29/search/page.tsx) | **Mock Data** | **Static Mockup** | Renders visual mockup lists for search engine metrics. |
