from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.modules.prompts.models import Prompt, PromptRun, AIModel
from app.modules.prompts.schemas import PromptBase
from app.core.exceptions import PromptLimitExceededException
from app.modules.workspaces.models import Project, Workspace
from redis.asyncio import Redis
from app.core.config import settings
import uuid
from datetime import datetime

class PromptService:
    @staticmethod
    async def create_prompts(db: AsyncSession, project_id: str, prompts_in: list[PromptBase]) -> list[Prompt]:
        # Check workspace limit
        project_res = await db.execute(select(Project).where(Project.id == project_id))
        project = project_res.scalar_one_or_none()
        if not project:
            raise Exception("Project not found")
            
        workspace_res = await db.execute(select(Workspace).where(Workspace.id == project.workspace_id))
        workspace = workspace_res.scalar_one()
        
        existing_prompts_res = await db.execute(select(Prompt).where(Prompt.project_id == project_id))
        existing_count = len(existing_prompts_res.scalars().all())
        
        if existing_count + len(prompts_in) > workspace.prompt_limit:
            raise PromptLimitExceededException()
            
        prompts = []
        for p_in in prompts_in:
            prompt = Prompt(
                project_id=project_id,
                text=p_in.text,
                locale=p_in.locale,
                tags=p_in.tags
            )
            db.add(prompt)
            prompts.append(prompt)
            
        workspace.prompts_used = existing_count + len(prompts_in)
        await db.flush()
        return prompts

    @staticmethod
    async def trigger_run(db: AsyncSession, project_id: str, models: list[str], arq_pool=None) -> list[str]:
        # Fetch active prompts
        prompt_res = await db.execute(select(Prompt).where(Prompt.project_id == project_id))
        prompts = prompt_res.scalars().all()
        
        job_ids = []
        redis_conn = arq_pool
        should_close = False
        if redis_conn is None:
            from arq import create_pool
            from arq.connections import RedisSettings
            redis_conn = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))
            should_close = True
        
        for prompt in prompts:
            for model_id in models:
                # Setup model record if not exists
                model_res = await db.execute(select(AIModel).where(AIModel.id == model_id))
                model = model_res.scalar_one_or_none()
                if not model:
                    model = AIModel(id=model_id, name=model_id.upper(), provider="LLMProvider")
                    db.add(model)
                    await db.flush()
                
                # Create prompt run tracking
                run = PromptRun(
                    prompt_id=prompt.id,
                    model_id=model_id,
                    status="PENDING"
                )
                db.add(run)
                await db.flush()
                
                # Push job details to Arq queue
                # Queue payload is: prompt_run_id, prompt_text, model_id, locale
                job_payload = {
                    "prompt_run_id": run.id,
                    "prompt_text": prompt.text,
                    "model_id": model_id,
                    "locale": prompt.locale
                }
                
                # arq uses standard redis hashes to enqueue
                # we call arq's helper via enqueue_job function key
                job_id = f"job_run_{run.id}"
                await redis_conn.enqueue_job("run_prompt_execution", job_payload, _job_id=job_id)
                job_ids.append(job_id)
                
        if should_close:
            await redis_conn.close()
        return job_ids
        
    @staticmethod
    async def get_prompts_with_runs(db: AsyncSession, project_id: str):
        res = await db.execute(
            select(Prompt)
            .where(Prompt.project_id == project_id)
            .options(selectinload(Prompt.prompt_runs))
        )
        return res.scalars().all()
