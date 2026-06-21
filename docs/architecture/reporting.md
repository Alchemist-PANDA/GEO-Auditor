# Reporting, Exports, & BI Integration Architecture

This document defines the architecture of the reporting engine, covering public conversion reports, enterprise data exports, BI integrations, and Slack/Teams digest notifications.

---

## 1. Export & Integration Interfaces

Enterprise integrations prioritize raw data access over polished document formats (like PDF or PowerPoint). Customers are expected to run custom reports using their own BI tools.

```
       [ClickHouse / Postgres]
                  │
        ┌─────────┼─────────┐
        ▼         ▼         ▼
     [ CSV ]   [ JSON ]  [ APIs ] ──> [ GA4 / Looker / BigQuery / Tableau ]
```

### 1.1 Export Formats
* **CSV Exports**: Supported across all metrics tables (Citations, Mentions, Share of Voice, and Prompt Volumes) via the dashboard UI.
* **JSON Exports**: Configured for bulk extraction queries.
* **REST APIs**: Gated to the Enterprise tier; exposes all metrics data endpoints.

### 1.2 BI & Platform Connectors
The platform supports direct integrations with the following systems:
* **Google Analytics 4 (GA4)**: Imports AI referral traffic metrics.
* **Google BigQuery / Snowflake**: Direct data warehouse sync for enterprise analysis.
* **Looker Studio / Tableau / Adobe Analytics**: Pre-packaged templates mapping Share of Voice and Citation metrics.

---

## 2. Public HTML Audit Emails (Lead-Gen)

The public lead-generation audit tool delivers HTML-formatted emails directly to prospects. PDF attachments are avoided to ensure fast load times and keep call-to-actions in the user's primary client channel.

### 2.1 Emailed Audit Layout
1. **Headline Score Banner**: Employs ternary ratings (**Good / Fair / Poor**) based on the AEO Content Score.
2. **Platform Breakdown Grid**: Mentions and rank values across ChatGPT, Perplexity, and Google AI Overviews.
3. **Sentiment Extraction Quotes**: Displays actual positive and negative answer engine snippets to illustrate the brand's qualitative rating.
4. **Cited Domain List**: Displays top cited sources for the prospect's category.
5. **CTA (Call to Action)**: Direct link to schedule an account team consultation or log in to try the platform.

---

## 3. The Prompt Research Report

The Prompt Research Report is a comprehensive analysis generated on-demand by account teams. It contains three distinct analytical views:

```
┌───────────────────────────────────────────────────────────────────────────┐
│                           PROMPT RESEARCH REPORT                          │
├───────────────────────────────────────────────────────────────────────────┤
│  1. INPUTS VIEW      : Seed keywords, vertical mappings, and brand targets│
│  2. INTENT VIEW      : Split of informational vs commercial vs transaction │
│  3. TOPICS LIST      : HDBSCAN clusters ranked by coverage & SoV scores   │
└───────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Inputs View
Lists the query boundaries configured for the run:
* Input seed keywords and brand domains.
* Excluded query terms and translation profiles.
* Historic date ranges analyzed (defaults to 6 months).

### 3.2 Intent View
Analyzes user intent splits within the target category, allowing strategists to tailor content approaches:
* **Informational** (e.g., "how to cushion running shoes"): Indicates a need for educational blog posts.
* **Commercial** (e.g., "best marathon trainers"): Indicates a need for review-friendly landing pages.
* **Transactional** (e.g., "buy Nike Zoom Fly"): Indicates a need for product listing page optimization.

### 3.3 Topics List
Displays discovered clusters ranked by **Coverage Score**:

$$\text{CoverageScore} = \frac{\text{Conversation Count for Cluster}}{\text{Total conversations in Category}} \times 100$$

Each cluster includes its centroid canonical query, intent designation, coverage rating, and a button to add the cluster to tracking pipelines.

---

## 4. Operational Digests (Slack & Teams Notifications)

Weekly automated push notifications keep client stakeholders updated on key metrics:

```json
{
  "workspace_id": "c76fb902-8611-4770-b747-8178a946c19f",
  "channel": "slack",
  "payload": {
    "text": "Weekly GEO/AEO Performance Update for *Nike*",
    "blocks": [
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": "*Nike* Share of Voice is *34%* (No Change vs last week).\n• ChatGPT Visibility: *42%* (+2%)\n• Perplexity Visibility: *18%* (-1%)\n• Google AI Overviews: *22%* (No Change)"
        }
      },
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": "*Top Recommended Action*: Outreach to *runningshoegeek.com* (cited in 14 target queries where you are absent)."
        }
      }
    ]
  }
}
```

---

## 5. Architectural Summary Table

| Dimension | [CONFIRMED] Findings | [INFERRED] Systems Behavior | [ASSUMPTION] System Limits | [RECOMMENDATION] Optimization |
|---|---|---|---|---|
| **Export Formats** | Platform supports CSV and JSON formats; gates APIs to Enterprise. | Data exports are generated asynchronously to prevent timeout issues on large databases. | Multi-gigabyte exports crash origin servers during SQL queries. | Stream database queries directly to the client rather than buffering. |
| **Audit Delivery** | Emailed audits are sent directly in HTML format without PDF attachments. | Email formats improve CTA click-through rates. | CSS support limits rendering in clients like Outlook. | Inline all CSS styles and use email-safe HTML table layouts. |
| **Research Report** | The Prompt Research Report contains Inputs, Intent, and Topic views. | Discovery runs are generated manually by account teams. | Processing millions of panel queries dynamically creates query lag. | Cache panel queries and generate reports via background jobs. |
| **BI Integration** | Connectors integrate with BigQuery, GA4, and Looker. | BI connectors query DB endpoints directly. | Direct queries from external BI systems saturate the serving database. | Provide BI systems with access to read-replica database instances. |
