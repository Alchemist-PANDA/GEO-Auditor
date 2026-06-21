from fastapi import APIRouter, Depends, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.rate_limit import RateLimiter
from app.core.database import get_db
from app.core.security import get_current_user, UserSession
from app.modules.prompts.service import PromptService
from app.modules.prompts.schemas import (
    PromptBatchCreate, PromptOut, TriggerRunRequest, PromptWithRunsOut
)
from typing import List
from app.modules.analysis.router import verify_project_access

router = APIRouter(prefix="/prompts", tags=["Prompts"])

@router.get("", response_model=List[PromptWithRunsOut])
async def get_prompts(
    project_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    await verify_project_access(db, project_id, current_user)
    prompts = await PromptService.get_prompts_with_runs(db, project_id)
    return prompts


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_prompts(
    batch_in: PromptBatchCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    await verify_project_access(db, batch_in.project_id, current_user)
    prompts = await PromptService.create_prompts(db, batch_in.project_id, batch_in.prompts)
    return {"added_count": len(prompts), "prompts": [PromptOut.from_orm(p) for p in prompts]}

@router.post("/run", status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(RateLimiter(10, 60))])
async def trigger_prompt_run(
    run_req: TriggerRunRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    await verify_project_access(db, run_req.project_id, current_user)
    job_ids = await PromptService.trigger_run(
        db, 
        run_req.project_id, 
        run_req.models, 
        arq_pool=getattr(request.app.state, "arq_pool", None)
    )
    return {
        "job_ids": job_ids,
        "status": "queued",
        "message": f"Prompts queued across {len(run_req.models)} models. Total jobs launched: {len(job_ids)}."
    }

