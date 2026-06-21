from fastapi import APIRouter, Depends, status, Query, HTTPException, Request
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user, UserSession
from app.core.rate_limit import RateLimiter
from app.modules.analysis.service import AnalysisService
from app.modules.analysis.schemas import VisibilityOverviewOut, CitationOut, VolumeOverviewOut, AuditRequest, AuditResponse, PageAuditOut
from app.modules.analysis.models import PageAudit
from arq import create_pool
from arq.connections import RedisSettings
from app.core.config import settings
from typing import List, Optional
from sqlalchemy.future import select
from app.modules.workspaces.models import Project, Workspace, User
from jose import jwt

router = APIRouter(prefix="/analytics", tags=["Analytics"])

async def verify_project_access(db: AsyncSession, project_id: str, current_user: UserSession):
    # Verify the current_user's organization owns the workspace that owns the project
    user_res = await db.execute(select(User).where(User.id == current_user.id))
    user = user_res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    res = await db.execute(
        select(Workspace.organization_id)
        .join(Project, Project.workspace_id == Workspace.id)
        .where(Project.id == project_id)
    )
    org_id = res.scalar_one_or_none()
    if not org_id or org_id != user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")

@router.get("/visibility", response_model=VisibilityOverviewOut)
async def get_visibility_analytics(
    project_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    await verify_project_access(db, project_id, current_user)
    overview = await AnalysisService.get_visibility_overview(db, project_id)
    return overview

@router.get("/citations", response_model=List[CitationOut])
async def get_citations(
    project_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    await verify_project_access(db, project_id, current_user)
    citations = await AnalysisService.get_citations(db, project_id)
    return citations

@router.get("/explorer", response_model=VolumeOverviewOut)
async def get_conversation_explorer_data(
    keyword: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    data = await AnalysisService.get_explorer_data(db, keyword)
    return data


audit_router = APIRouter(prefix="/audit", tags=["Audit"])

security_scheme_optional = HTTPBearer(auto_error=False)

async def get_optional_current_user(
    request: Request,
    credentials = Depends(security_scheme_optional)
) -> Optional[UserSession]:
    if not credentials:
        return None
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated"
        )
        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role", "member")
        if user_id and email:
            return UserSession(id=user_id, email=email, role=role)
    except Exception:
        pass
    return None

@audit_router.post("/request", response_model=AuditResponse, status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(RateLimiter(3, 60))])
async def request_page_audit(
    payload: AuditRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserSession] = Depends(get_optional_current_user)
):
    # Enforce that user can only request audit for their own email if authenticated
    if current_user:
        if payload.email.strip() != current_user.email:
            raise HTTPException(status_code=403, detail="Email mismatch with authenticated user")
            
    # 1. Validate URL basic structure
    url = payload.url.strip()
    if not url.startswith(("http://", "https://")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL must start with http:// or https://"
        )
    
    # 2. Save PENDING audit record to database
    import uuid
    audit = PageAudit(
        id=str(uuid.uuid4()),
        url=url,
        email=payload.email.strip(),
        status="PENDING"
    )
    db.add(audit)
    await db.flush()  # To populate audit.id
    
    # 3. Enqueue background parser task via ARQ
    try:
        redis_conn = getattr(request.app.state, "arq_pool", None)
        should_close = False
        if redis_conn is None:
            redis_conn = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))
            should_close = True
            
        job_data = {"audit_id": audit.id}
        await redis_conn.enqueue_job("run_heuristic_audit", job_data, _job_id=f"audit_{audit.id}")
        if should_close:
            await redis_conn.close()
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to enqueue audit job to Redis: {e}")
        
        audit.status = "FAILED"
        db.add(audit)
        await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"The audit queue is currently unavailable. Please try again later."
        )
        
    return AuditResponse(
        audit_id=audit.id,
        status="PENDING",
        message="Audit request received and queued for processing."
    )


@audit_router.get("/{audit_id}", response_model=PageAuditOut)
async def get_audit(
    audit_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    res = await db.execute(select(PageAudit).where(PageAudit.id == audit_id))
    audit = res.scalar_one_or_none()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
        
    if audit.email != current_user.email:
        raise HTTPException(status_code=403, detail="Not authorized to access this audit")
        
    return audit

@audit_router.get("", response_model=List[PageAuditOut])
async def list_audits(
    db: AsyncSession = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    res = await db.execute(
        select(PageAudit)
        .where(PageAudit.email == current_user.email)
        .order_by(PageAudit.created_at.desc())
    )
    audits = res.scalars().all()
    return audits

