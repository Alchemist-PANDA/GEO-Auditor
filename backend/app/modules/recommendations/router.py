from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.rate_limit import RateLimiter
from app.core.database import get_db
from app.core.security import get_current_user, UserSession
from app.modules.recommendations.service import RecommendationService
from app.modules.recommendations.schemas import (
    RecommendationOut, RecommendationStatusUpdate
)
from typing import List
from app.modules.analysis.router import verify_project_access

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("", response_model=List[RecommendationOut])
async def get_project_recommendations(
    project_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    """Get all recommendations for a project. Auto-generates if none exist."""
    await verify_project_access(db, project_id, current_user)
    recs = await RecommendationService.get_recommendations_by_project(db, project_id)
    return recs


@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_recommendations(
    project_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    """Trigger rule-based recommendation generation (free, runs locally)."""
    await verify_project_access(db, project_id, current_user)
    await RecommendationService.generate_recommendations(db, project_id)
    
    from sqlalchemy.orm import selectinload
    from sqlalchemy.future import select
    from app.modules.recommendations.models import Recommendation
    res = await db.execute(
        select(Recommendation)
        .where(Recommendation.project_id == project_id)
        .options(selectinload(Recommendation.actions))
        .order_by(Recommendation.created_at.desc())
    )
    recs = res.scalars().all()
    return {
        "generated_count": len(recs),
        "message": f"Generated {len(recs)} recommendations using rule engine.",
        "recommendations": [RecommendationOut.model_validate(r) for r in recs]
    }


@router.post("/advanced", status_code=status.HTTP_201_CREATED, dependencies=[Depends(RateLimiter(5, 60))])
async def generate_advanced_recommendations(
    project_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    """Trigger LLM-powered strategic recommendation generation (uses API credits)."""
    await verify_project_access(db, project_id, current_user)
    await RecommendationService.generate_advanced_recommendations(db, project_id)
    
    from sqlalchemy.orm import selectinload
    from sqlalchemy.future import select
    from app.modules.recommendations.models import Recommendation
    res = await db.execute(
        select(Recommendation)
        .where(Recommendation.project_id == project_id)
        .options(selectinload(Recommendation.actions))
        .order_by(Recommendation.created_at.desc())
    )
    recs = res.scalars().all()
    return {
        "generated_count": len(recs),
        "message": f"Generated {len(recs)} advanced recommendations using LLM analysis.",
        "recommendations": [RecommendationOut.model_validate(r) for r in recs]
    }


@router.patch("/{rec_id}/status")
async def update_recommendation_status(
    rec_id: str = Path(...),
    body: RecommendationStatusUpdate = ...,
    db: AsyncSession = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    """Update recommendation status (active, validating, resolved, ignored)."""
    from sqlalchemy.future import select
    from app.modules.recommendations.models import Recommendation
    
    res = await db.execute(select(Recommendation).where(Recommendation.id == rec_id))
    rec = res.scalar_one_or_none()
    from fastapi import HTTPException
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
        
    await verify_project_access(db, rec.project_id, current_user)
    
    rec = await RecommendationService.update_recommendation_status(db, rec_id, body.status)
    return {"id": rec.id, "status": rec.status, "message": "Status updated."}
