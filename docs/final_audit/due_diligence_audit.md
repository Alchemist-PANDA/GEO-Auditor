# Investor & Acquirer Technical Due Diligence Report

A technical due diligence evaluation of the platform's architecture, intellectual property, technical debt, and business scaling risks.

---

## Due Diligence Summary

#### 1. Is the architecture sound?
* **Verdict**: <span style="color:yellow;font-weight:bold;">PARTIALLY</span>
* **Analysis**: The backend codebase is built on FastAPI and SQLAlchemy, which is a modern, modular, and standard architecture. However, the frontend is mostly an interactive prototype. 8 out of 11 views are mockups, and the database integration is incomplete. The SQLite fallback configuration lacks constraint enforcement, creating significant architecture risks.

#### 2. Is the intellectual property (IP) valuable?
* **Verdict**: <span style="color:red;font-weight:bold;">LOW VALUE</span>
* **Analysis**:
  - The crawler is a basic wrapper around `httpx` and a simple python `HTMLParser`. It doesn't contain advanced headless browser rendering (e.g., Playwright) to execute JavaScript-heavy target sites.
  - The sentiment analysis is a simple word-count regex matches engine.
  - The visibility score is an arbitrary scoring heuristic with no patentable or proprietary machine learning elements.
  - The prompt execution simply wraps LiteLLM call structures.
  - There is no deep proprietary IP. Most code could be replicated by mid-level engineers in a couple of weeks.

#### 3. What are the core technical risks?
* **Data Leakage (IDOR)**: Severe authorization bypasses on brands, competitors, and agency client routers mean any user can modify or view other organizations' data.
* **Broken Code coverage**: The backend test suite is broken due to missing JWT setups. There is no automated test coverage on the frontend.
* **Database Corruption**: Comments disabling SQLite foreign key checks allow orphan records to pile up.

#### 4. What are the customer retention risks?
* **Immediate Disillusionment**: If sold tomorrow, a customer will sign in and realize that most pages display hardcoded mock data. They cannot add their own brand/competitors via the UI, nor view dynamic citations or search trends. Churn rate would be near 100%.

#### 5. What are the scaling risks?
* **Concurrency Lockouts**: SQLite's single-file locking is entirely unsuitable for concurrent writes from background workers. Scaling beyond a few concurrent users will lock the database and crash requests.
* **Rate Limits & API Costs**: Running prompt executions cross-models (GPT, Claude, Gemini) will consume massive API credits. Without a proper rate-limiting billing ledger or customer credits usage tracker, the company would bleed cash on heavy users.
