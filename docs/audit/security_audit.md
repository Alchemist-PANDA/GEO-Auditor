# Security Audit

## Review Categories

### 1. JWT Implementation & Password Handling
- **Status**: Critical Risk
- **Details**: Passwords are not hashed. The authentication route uses a hardcoded plaintext check (`if payload.password != "password123"`). JWTs are signed with a static default secret (`supabase_jwt_secret_placeholder_change_in_prod`) if environment variables are not set properly.

### 2. Authorization Controls (IDOR Vulnerability)
- **Status**: Critical Risk
- **Details**: While endpoints require a valid JWT token via `Depends(get_current_user)`, there are **zero** authorization checks to verify if the requesting user actually owns or has access to the requested resources. For example, `GET /api/v1/analytics/visibility?project_id=XYZ` does not verify if the `current_user` belongs to the workspace that owns `project_id=XYZ`. This is a classic Insecure Direct Object Reference (IDOR) vulnerability.

### 3. Rate Limiting
- **Status**: High Risk
- **Details**: No rate limiting middleware is configured. The LLM APIs (OpenAI, Gemini, Claude) are directly exposed to authenticated users without limits, creating a severe financial denial-of-service (DDoS) risk.

### 4. CORS
- **Status**: High Risk
- **Details**: `allow_origins=["*"]`, `allow_credentials=True` is an insecure CORS configuration that allows any domain to make cross-origin requests.

### 5. Secrets Handling
- **Status**: Medium Risk
- **Details**: API keys and Database URLs are loaded via environment variables (good), but the fallback defaults in `config.py` are unsafe for production.

### 6. SQL Injection Risks
- **Status**: Low Risk
- **Details**: The application consistently uses the SQLAlchemy ORM (`select(Model).where(...)`), which safely parameterizes queries, effectively mitigating direct SQL injection risks.

## Verdict
The platform fails basic security standards. 
It requires immediate remediation of IDOR vulnerabilities, implementation of a secure password hashing mechanism (or full offloading to Supabase Auth), and proper CORS/Rate-Limiting configurations before ANY public exposure.
