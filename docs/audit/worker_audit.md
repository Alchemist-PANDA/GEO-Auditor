# Worker Audit

## Configuration
- **File**: `workers/run_worker.py`
- **Framework**: `arq`
- **Connection**: Redis (via `REDIS_URL`)

## Validated Behaviors

### 1. Worker Registration
- **Functions Registered**: `run_prompt_execution`, `run_batch_visibility_update`, `run_recommendation_generation`, `run_heuristic_audit`.
- **Cron Jobs**: `scheduled_daily_scan` runs daily at midnight.
- **Max Jobs**: 4 concurrently.
- **Timeout**: 120 seconds per job.

### 2. Queue Execution
Workers successfully accept payloads (e.g., `prompt_run_id`, `model_id`) and execute functions asynchronously. `run_prompt_execution` correctly interacts with the LLM layer and updates `AnalysisService`.

### 3. Retry & Failure Handling
- **Observed Behavior**: If an exception occurs within `run_prompt_execution` (e.g., LLM timeout, API key missing), it catches the exception and manually updates the `PromptRun` record in the database with `status="FAILED"` and sets `error_message`.
- **Limitation**: The worker re-raises the exception (`raise exc`) at the end of the `except` block. In `arq`, raising an exception automatically triggers a retry based on default retry policies (typically 5 retries with backoff). This means a permanently failing task (like invalid credentials) will retry unnecessarily 5 times before failing permanently.

### 4. Intentional Failure Trigger
- Triggering an intentional failure (e.g., missing API key or Database timeout) revealed that the database state does accurately reflect the failure (`FAILED` status), but the logs get flooded with `arq` retries due to the re-raised exception.

## Verdict
- **Status**: YELLOW (Partially Works)
- **Issues**: Unnecessary retries on deterministic failures. Strict dependency on Redis (if Redis goes down, background processing completely halts, and there's no Dead Letter Queue strategy configured).
