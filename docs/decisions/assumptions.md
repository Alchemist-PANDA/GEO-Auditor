# Architectural Assumptions & Risks

This document records the foundational assumptions, technical trade-offs, and operational risks associated with the platform's architecture.

---

## 1. Data Ingestion & Panel Sourcing

* **[ASSUMPTION] Panel Feed Accessibility**: The platform assumes a continuous, weekly-refreshed licensed data feed from consumer panel providers (such as Similarweb-licensed partners). 
* **[ASSUMPTION] Demographic Metrics Availability**: The panels are assumed to provide anonymized user data (regional, age, and income bands) across ten major regions (US, UK, CA, DE, FR, AU, ES, KR, IT, BR), allowing the platform to extrapolate search volume statistics accurately.
* **[ASSUMPTION] GDPR and CCPA Compliance**: The panel dataset is assumed to contain double-opt-in user records with all personally identifiable information (PII) scrubbed prior to transfer, maintaining compliance with GDPR and CCPA.

---

## 2. Headless Browsers vs. API Access

* **[ASSUMPTION] Terms of Service (ToS) Compliance Limits**: Driving logged-in user sessions using headless browser automation (Playwright/Puppeteer) on consumer chat interfaces (ChatGPT, Perplexity, Gemini) sits in tension with provider terms of service.
* **[INFERRED] Interface Differences**: Direct API responses often differ from consumer web interfaces (which include browsing features, search grounding integrations, memory, and custom system instructions).
* **[RECOMMENDATION] Hybrid Ingestion Model**: Use standard APIs (e.g., OpenAI's API with search enabled, Gemini Grounding API) for primary data collection. Restrict browser scraping to a small validation sample to monitor UI citation layouts without triggering provider bans.

---

## 3. NLP Extraction & Accuracy Thresholds

* **[ASSUMPTION] Judge Model Error Limits**: Using secondary LLMs as extraction judges introduces a baseline error rate. Benign entity extraction and sentiment analysis typically show a **5–15% disagreement rate** against human reviews.
* **[RECOMMENDATION] Human-in-the-Loop Validation**: Establish a weekly validation queue where human analysts audit 50 randomly sampled extraction runs. Use this data to track model alignment and adjust judge prompts.

---

## 4. Domain Authority Mapping

* **[ASSUMPTION] Domain Score Reliability**: To compute Citation Impact, the system assumes access to domain authority scores via third-party APIs (such as Moz, Ahrefs, or Semrush). The system assumes these scores reflect real-world crawl trust patterns.
* **[RECOMMENDATION] Local Cache Strategy**: To avoid API rate limit bottlenecks and control costs, cache domain authority scores locally for 15 days.

---

## 5. Architectural Summary Table

| Dimension | [CONFIRMED] Findings | [INFERRED] Systems Behavior | [ASSUMPTION] System Limits | [RECOMMENDATION] Optimization |
|---|---|---|---|---|
| **Panel Data** | Extrapolates search volumes from a licensed panel of active users. | Panel coverage rates are low, resulting in wide confidence intervals. | Panel data license terms restrict redistribution of raw logs. | Only display aggregated averages and confidence intervals to users. |
| **Ingestion Scrapers** | Captures answers directly from browser-based consumer experiences. | Headless browser fleets simulate human browsing patterns using proxy pools. | Captcha systems block browser automation at scale. | Use residential proxy pools and restrict scrapers to validation runs. |
| **NLP Judgement** | Uses secondary LLM passes to extract structured data arrays. | Judge models process raw responses using cheap, fast runtimes. | Judge classification outputs suffer from semantic drift over time. | Run weekly human checks to monitor classifier precision. |
| **Domain Authority** | Authority scoring differentiates trusted publishers from blogs. | Domain authority maps directly to the backlink graph. | Third-party domain authority lookup limits introduce query bottlenecks. | Cache lookup scores locally and query APIs asynchronously. |
