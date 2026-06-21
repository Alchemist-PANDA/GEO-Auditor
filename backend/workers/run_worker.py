"""
Arq Worker for GEO Platform background job processing.
Handles prompt execution, citation extraction, and visibility calculation.
"""
import asyncio
import logging
from arq import cron
from sqlalchemy.future import select
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.llm import call_llm
from app.modules.analysis.service import AnalysisService
from app.modules.prompts.models import PromptRun

logger = logging.getLogger(__name__)


async def run_prompt_execution(ctx, job_data: dict):
    """
    Execute a single prompt against an LLM provider and process the response.
    
    Pipeline:
    1. Call LLM via LiteLLM abstraction
    2. Parse response for citations, mentions, sentiment
    3. Extract topics via KeyBERT
    4. Update visibility metrics and SOV
    """
    prompt_run_id = job_data["prompt_run_id"]
    prompt_text = job_data["prompt_text"]
    model_id = job_data["model_id"]
    locale = job_data.get("locale", "Global")

    logger.info(f"Executing prompt run {prompt_run_id} on model {model_id}")

    try:
        # Mark as running
        async with AsyncSessionLocal() as db:
            run_res = await db.execute(
                select(PromptRun).where(PromptRun.id == prompt_run_id)
            )
            run = run_res.scalar_one()
            run.status = "RUNNING"
            await db.commit()

        # Call LLM
        res_data = await call_llm(
            model_id=model_id,
            prompt=prompt_text,
            locale=locale
        )

        # Process response: citations, mentions, visibility, topics
        async with AsyncSessionLocal() as db:
            await AnalysisService.process_raw_response(
                db=db,
                prompt_run_id=prompt_run_id,
                raw_text=res_data["text"],
                tokens=res_data["tokens"],
                latency=res_data["latency_ms"],
                cost=res_data.get("cost_usd", 0.0),
                provider_requested=res_data.get("provider_requested"),
                provider_used=res_data.get("provider_used")
            )
            await db.commit()

        logger.info(f"Prompt run {prompt_run_id} completed successfully")

    except Exception as exc:
        logger.error(f"Prompt run {prompt_run_id} failed: {exc}")
        async with AsyncSessionLocal() as db:
            run_res = await db.execute(
                select(PromptRun).where(PromptRun.id == prompt_run_id)
            )
            run = run_res.scalar_one()
            run.status = "FAILED"
            run.error_message = str(exc)[:500]
            await db.commit()
        raise exc


async def run_batch_visibility_update(ctx, job_data: dict):
    """
    Batch recalculate visibility metrics for a project across all models.
    Triggered after multiple prompt runs complete.
    """
    project_id = job_data["project_id"]
    logger.info(f"Batch visibility update for project {project_id}")

    async with AsyncSessionLocal() as db:
        from app.modules.workspaces.models import Brand
        from app.modules.prompts.models import AIModel

        brand_res = await db.execute(select(Brand).where(Brand.project_id == project_id))
        brands = brand_res.scalars().all()

        model_res = await db.execute(select(AIModel))
        models = model_res.scalars().all()

        for brand in brands:
            for model in models:
                await AnalysisService.update_visibility_metrics(db, brand, model.id)

        await db.commit()

    logger.info(f"Batch visibility update completed for project {project_id}")


async def run_recommendation_generation(ctx, job_data: dict):
    """Generate rule-based recommendations for a project."""
    project_id = job_data["project_id"]
    logger.info(f"Generating recommendations for project {project_id}")

    async with AsyncSessionLocal() as db:
        from app.modules.recommendations.service import RecommendationService
        await RecommendationService.generate_recommendations(db, project_id)
        await db.commit()

    logger.info(f"Recommendations generated for project {project_id}")


async def scheduled_daily_scan(ctx):
    """
    Daily cron job: re-run all active prompts and regenerate recommendations.
    """
    logger.info("Starting daily scheduled scan")
    await AnalysisService.trigger_scheduled_runs(ctx)
    logger.info("Daily scheduled scan completed")


async def run_heuristic_audit(ctx, job_data: dict):
    """
    Background job to run the page auditor and email the report.
    """
    audit_id = job_data["audit_id"]
    logger.info(f"Running background heuristic audit for ID {audit_id}")
    async with AsyncSessionLocal() as db:
        await AnalysisService.perform_heuristic_audit(db, audit_id)
        await db.commit()
    logger.info(f"Background heuristic audit completed for ID {audit_id}")


import time

async def worker_heartbeat_loop(ctx):
    """Periodically write worker heartbeat timestamp to Redis."""
    redis = ctx.get('redis')
    if redis is None:
        logger.error("Redis connection not found in worker context; heartbeat bypassed")
        return
    while True:
        try:
            # Set key with 15s expiration
            await redis.set("worker_heartbeat", int(time.time()), ex=15)
        except Exception as e:
            logger.error(f"Failed to write worker heartbeat to Redis: {e}")
        await asyncio.sleep(5)

async def on_startup(ctx):
    """Start the background heartbeat task on worker startup."""
    ctx['heartbeat_task'] = asyncio.create_task(worker_heartbeat_loop(ctx))
    logger.info("Worker startup hook executed: heartbeat task initialized")

async def on_shutdown(ctx):
    """Cancel the heartbeat task on worker shutdown."""
    if 'heartbeat_task' in ctx:
        ctx['heartbeat_task'].cancel()
        logger.info("Worker shutdown hook executed: heartbeat task cancelled")


class WorkerSettings:
    """Arq worker configuration."""
    functions = [
        run_prompt_execution,
        run_batch_visibility_update,
        run_recommendation_generation,
        run_heuristic_audit,
    ]
    redis_settings = settings.REDIS_URL
    max_jobs = 4
    job_timeout = 120
    cron_jobs = [
        cron(scheduled_daily_scan, hour=0, minute=0)
    ]
    on_startup = on_startup
    on_shutdown = on_shutdown


