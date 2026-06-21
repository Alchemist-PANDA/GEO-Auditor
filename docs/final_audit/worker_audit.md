# Background Worker Subsystem Audit

An audit of the asynchronous task runner queue, Redis connection resilience, job retry policies, and crash recovery mechanisms.

---

## Background Architecture

The platform offloads long-running tasks to background queues using `arq` (an async Redis-backed job queue). The worker code is located in [run_worker.py](file:///e:/Profound-cloning/backend/workers/run_worker.py).

### Core Tasks Defined
1. `run_prompt_execution`: Executes prompt calls against LLMs and parses citations.
2. `run_batch_visibility_update`: Computes aggregate brand metrics.
3. `run_recommendation_generation`: Compiles rule-based suggestions.
4. `run_heuristic_audit`: Fetches HTML pages and executes scoring formulas.
5. `scheduled_daily_scan`: Runs a cron job once a day to refresh tracking datasets.

---

## Worker Vulnerability Analysis

#### 1. Lack of Retry Configurations
* **The Root Issue**: The worker's `WorkerSettings` class does not override default `arq` retry parameters. Job tasks are enqueued without explicitly setting `max_tries` or defining custom backoff delays for API rate limits.
* **The Impact**: While `call_llm` implements local retries for rate limits (429s), any network dropout, provider server error (500s), database transaction conflict, or internal parse exception will cause the background task to fail instantly and terminate.

#### 2. permanent "Stuck" Status on Worker Failures
* **The Root Issue**: When a job starts, its state in the database is set to `RUNNING`. If the worker process crashes, the system undergoes an outage, or the job exceeds its timeout, the database is never updated to clean up.
* **The Impact**: The `PageAudit` or `PromptRun` status remains stuck in `RUNNING` or `PENDING` indefinitely. There is no background "sweep" task or cron job to identify stuck jobs (e.g., jobs running longer than the 120s timeout) and mark them as `FAILED`.

#### 3. No Dead Letter Queue (DLQ) or State Observability
* **The Root Issue**: There is no visibility dashboard or dashboard endpoint for task management. FAILED tasks simply log to stderr/stdout and are deleted from Redis.
* **The Impact**: Administrators and developers have no way to know which jobs failed, why they failed, or to trigger a retry. Failed runs are silently dropped, resulting in data gaps for visibility timelines.
