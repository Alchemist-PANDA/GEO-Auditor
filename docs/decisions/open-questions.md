# Open Questions & System Uncertainties

This document records unresolved questions, design alternatives, and technical risks requiring further validation.

---

## 1. Legal Boundaries of Consumer Panel Data

* **[ASSUMPTION] Compliance Feeds**: The platform assumes panel data providers handle double-opt-in consent and comply with GDPR/CCPA.
* **[RECOMMENDATION] Audit Safeguards**: Implement an automated compliance worker to check incoming panel queries for common PII patterns (names, emails, credit cards). Any matching record is deleted immediately.

---

## 2. Managing Non-Deterministic LLM Responses

Unlike traditional search, generative AI answers are non-deterministic, returning different responses for the same query.

* **[CONFIRMED] Multi-Run Capture**: To manage variance, the platform executes prompt runs multiple times across different configurations.
* **[RECOMMENDATION] Concurrency Study**: Conduct a statistical study to determine the optimal run frequency per prompt (e.g., 3 runs/day vs. 10 runs/day) to achieve stable average scores without exceeding API budget constraints.

---

## 3. Real-Time Alert Tuning

* **[INFERRED] Statistical Thresholds**: Using flat threshold alerts (e.g., "alert if visibility drops by 10%") triggers false positives due to sampling noise. The system uses an Exponentially Weighted Moving Average (EWMA) control chart:
  
  $$\sigma_{\text{EWMA}} = \sqrt{\frac{\alpha}{2-\alpha} \times \sigma^2}$$

  An alert is triggered only when a score falls outside the historical variance envelope ($Z > 2.5$).
* **[RECOMMENDATION] False-Positive Review**:
  1. What is the minimum historical sample size (e.g., 14 days) required before enabling alerts?
  2. How should the system display alerts to users without causing alert fatigue?

---

## 4. Architectural Summary Table

| Dimension | [CONFIRMED] Findings | [INFERRED] Systems Behavior | [ASSUMPTION] System Limits | [RECOMMENDATION] Optimization |
|---|---|---|---|---|
| **Legal Compliance** | Panel data complies with GDPR, CCPA, and HIPAA assessments. | Panel providers scrub PII before data is transferred. | Ingesting unscrubbed PII exposes the platform to regulatory penalties. | Deploy a local regex-based scrubbing worker on the ingestion pipeline. |
| **Response Variance** | Multi-model executions run repeatedly to capture variations. | Running more runs per prompt narrows metric confidence intervals. | Running frequent prompt queries increases API costs. | Use a sliding window to determine the minimum run frequency needed per prompt. |
| **Alert Tuning** | Alerts track changes in brand mentions and competitors. | System uses EWMA control charts to filter metric noise. | Alerts generated off small sample sets trigger false alarms. | Enforce a 14-day data minimum before enabling alert notifications. |
| **Scraper Limits** | UI-scraped data runs are limited by account plan tiers. | Browser automation fleets hit captchas during high-frequency crawls. | Provider security updates require regular scraper maintenance. | Primary collection via grounding APIs; fallback to scrapers. |
