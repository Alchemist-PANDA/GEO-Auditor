# Testing Status & Truth

This document audits the test coverage of the backend modules, detailing what is covered and what remains untested.

---

## 1. Test Coverage Overview

The backend has **59 passing tests** covering core logic, including algorithms and auth.

### 1.1 Covered by Automated Tests
- **GEO Algorithms**: Evaluates visibility computations, Share of Voice distributions, model weight mappings, and citation impact factors in [test_geo_algorithms.py](file:///e:/Profound-cloning/backend/tests/test_geo_algorithms.py).
- **Authentication**: Verifies password hashing, token generation, and secure register flows in [test_auth.py](file:///e:/Profound-cloning/backend/tests/test_auth.py).
- **Heuristic Auditing Scorer**: Validates the HTML parser, schema checks, header structure ratings, and keyword stuffing detection in [test_heuristic_auditor.py](file:///e:/Profound-cloning/backend/tests/test_heuristic_auditor.py).
- **Audit Request API**: Verifies enqueuing behavior, database logging, URL validation, and authorization matching in [test_audit_api.py](file:///e:/Profound-cloning/backend/tests/test_audit_api.py).
- **GEO Recommendations**: Validates the recommendation generator rule runs in [test_recommendations.py](file:///e:/Profound-cloning/backend/tests/test_recommendations.py).

### 1.2 Untested Subsystems & Gaps
- **Agency Operations**: The endpoints for fetching agency profiles, fetching clients, and adding clients defined in [agency/router.py](file:///e:/Profound-cloning/backend/app/modules/agency/router.py) have **no test coverage** in the suite.
- **Dynamic API Key Swapping & LLM Failovers**: Mocks are used for all LiteLLM calls. The dynamic key availability checks and fallback routes (e.g. failing over from Gemini to OpenAI) are untested.
- **Frontend Verification**: The Next.js client app does not have any automated UI tests (Jest or Playwright). Verification relies on manual inspection or running external node scripts like `screenshot.js`.
