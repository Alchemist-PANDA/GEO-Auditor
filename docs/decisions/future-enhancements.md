# Future Enhancements & Architectural Expansion

This document maps out future enhancements, technical additions, and product expansions designed to scale the platform.

---

## 1. EU Data Residency & Regional Hosting

* **[CONFIRMED] Current Footprint**: The platform runs on US-hosted infrastructure, with global data processing managed via standard Data Processing Agreements (DPAs).
* **[RECOMMENDATION] Isolated Regional Pods**: To support European enterprise clients with strict compliance rules, design the ingestion and storage layers to run in isolated regional pods (e.g., in `eu-west-1`). User data, logs, and query archives remain within the EU pod, while anonymized metrics are synced to the global analytics database.

---

## 2. Enterprise SCIM Identity Sync

* **[CONFIRMED] Current SSO**: SSO support handles SAML 2.0 and OIDC configurations. SCIM user provisioning is not currently supported.
* **[RECOMMENDATION] Directory Provisioning**: Build a SCIM 2.0 API gateway integrated with client directory systems (such as Okta, Microsoft Entra ID). This allows enterprise IT teams to automatically assign and revoke workspace roles (Admin, Analyst, Viewer) during employee onboarding and offboarding.

---

## 3. Auto-Improving Feedback Loop

* **[INFERRED] Current Optimization**: The AEO Content Score model is updated monthly using the global citation database. The recommendations engine uses a rule-based decision tree to suggest optimization actions.
* **[RECOMMENDATION] Autonomous Feedback Loop**: Build a closed-loop optimization system. When a recommendation is marked complete, the system tracks the target URL's crawl frequency and citation changes. These outcomes are fed back into the recommendation engine to dynamically update priority weights:

$$\text{Weight}_{\text{new}} = \text{Weight}_{\text{old}} \times (1 + \eta \times \Delta \text{CitationRate})$$

- $\eta$: Learning rate parameters.
- $\Delta\text{CitationRate}$: Change in citation rate observed over a 14-day post-optimization window.

---

## 4. Multi-Tenant Agency Workspaces

* **[CONFIRMED] Workspace Limits**: Enterprise accounts are currently limited to a single workspace.
* **[RECOMMENDATION] Hierarchical Workspace Model**:
  - Implement a parent organizational layer (`Agency Workspace`) managing multiple isolated children environments (`Client Brands`).
  - Add client-level billing dashboards, customizable reporting, and role-based permissions (RBAC) allowing agency team members to access specific workspaces without sharing credentials across different clients.

---

## 5. Architectural Summary Table

| Dimension | [CONFIRMED] Findings | [INFERRED] Systems Behavior | [ASSUMPTION] System Limits | [RECOMMENDATION] Optimization |
|---|---|---|---|---|
| **Data Residency** | EU user data is processed on US servers via DPAs. | Log forwarding and databases run within a single cloud region. | Strict GDPR compliance rules restrict transferring personal logs to the US. | Build regional ingestion pods to keep logs within local borders. |
| **User Directory** | Identity integration supports SAML and OIDC SSO. | Client teams provision user roles manually via the dashboard UI. | Manual user provisioning introduces security risks for enterprise teams. | Build a SCIM 2.0 gateway to automate user lifecycle management. |
| **Feedback Loop** | System tracks crawler visits and citations for target pages. | Recommendation engines use rule tables to prioritize tasks. | Static rules do not adapt to shifts in engine citation patterns. | Feed citation outcomes back into the engine to update priority weights. |
| **Workspace Scope** | Platform features restrict accounts to a single workspace. | Users share accounts or run multiple sub-org workspaces separately. | Segmented accounts limit performance benchmarking across client portfolios. | Build a hierarchical database model to isolate tenant workspaces. |
