# Launch Candidate Checklist

This file tracks the completion progress of the Launch Candidate tonight.

## Checklist

- [ ] Phase 1: Critical Security Fixes
  - [ ] Brand creation IDOR mitigation
  - [ ] Competitor creation IDOR mitigation
  - [ ] Agency Client endpoints IDOR mitigation
  - [ ] SQLite foreign key constraint hooks enabled
- [ ] Phase 2: Test Suite Pass
  - [ ] Pytest suite execution green (59/59 tests passing)
- [ ] Phase 3: Frontend Reality Pass
  - [ ] Connected: Dashboard, Prompts, Citations, Explorer, Audits, Recommendations
  - [ ] Hidden: Model, Industry, Search, Inbox
- [ ] Phase 4: Customer Onboarding
  - [ ] `/register` page built and verified
  - [ ] Brand & Competitor creation UI wizard/modal implemented
  - [ ] End-to-end audit execution and report dispatch works
- [ ] Phase 5: End-to-End Verification
  - [ ] Verified register -> create brand -> add competitors -> run audit -> view results
