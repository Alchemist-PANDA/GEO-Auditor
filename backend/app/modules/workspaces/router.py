from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user, UserSession
from app.modules.workspaces.service import WorkspaceService
from app.modules.workspaces.schemas import (
    WorkspaceCreate, WorkspaceOut, ProjectCreate, ProjectOut, 
    BrandCreate, BrandOut, CompetitorCreate, CompetitorOut,
    UserLoginRequest, UserRegisterRequest, TokenResponse
)
from typing import List
from jose import jwt
from app.core.config import settings
from datetime import datetime, timedelta
import uuid
from passlib.context import CryptContext
from app.modules.workspaces.models import User, Organization, Workspace, Project, Brand, Competitor
from sqlalchemy.future import select

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    # Check if user exists
    user_res = await db.execute(select(User).where(User.email == payload.email))
    if user_res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
        
    org = Organization(id=str(uuid.uuid4()), name=payload.organization_name)
    db.add(org)
    
    hashed_pwd = pwd_context.hash(payload.password)
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=payload.email,
        hashed_password=hashed_pwd,
        full_name=payload.full_name,
        organization_id=org.id,
        role="org_admin"
    )
    db.add(user)
    await db.commit()
    return {"message": "User registered successfully"}

@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(
    payload: UserLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    user_res = await db.execute(select(User).where(User.email == payload.email))
    user = user_res.scalar_one_or_none()
    
    if not user or not pwd_context.verify(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    claims = {
        "aud": "authenticated",
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    
    access_token = jwt.encode(claims, settings.SUPABASE_JWT_SECRET, algorithm="HS256")
    return TokenResponse(access_token=access_token)


@router.post("/sync", status_code=status.HTTP_200_OK)
async def sync_user_profile(
    full_name: str, 
    organization_name: str, 
    db: AsyncSession = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    user = await WorkspaceService.sync_user(
        db=db,
        user_id=current_user.id,
        email=current_user.email,
        full_name=full_name,
        org_name=organization_name
    )
    return {"status": "success", "user": {"id": user.id, "email": user.email, "organization_id": user.organization_id}}

@router.post("", response_model=WorkspaceOut, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    ws_in: WorkspaceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    # Retrieve user profile to find organization id
    # Here we assume user profile exists from sync
    from app.modules.workspaces.models import User
    from sqlalchemy.future import select
    user_res = await db.execute(select(User).where(User.id == current_user.id))
    user = user_res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    ws = await WorkspaceService.create_workspace(db, user.organization_id, ws_in)
    return ws

@router.post("/projects", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    from app.modules.workspaces.models import Workspace, User
    from sqlalchemy.future import select
    
    # 1. Get user to find their organization
    user_res = await db.execute(select(User).where(User.id == current_user.id))
    user = user_res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    # 2. Get workspace to check ownership
    ws_res = await db.execute(select(Workspace).where(Workspace.id == project_in.workspace_id))
    ws = ws_res.scalar_one_or_none()
    
    if not ws:
        # Without foreign key constraints, this could have been silent error
        # Now we handle it properly
        raise HTTPException(status_code=404, detail="Workspace not found")
        
    if ws.organization_id != user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized to create project in this workspace")
        
    project = await WorkspaceService.create_project(db, project_in)
    return project

@router.post("/brands", response_model=BrandOut, status_code=status.HTTP_201_CREATED)
async def create_brand(
    brand_in: BrandCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    from app.modules.workspaces.models import Project, Workspace, User
    
    # 1. Get user to find organization
    user_res = await db.execute(select(User).where(User.id == current_user.id))
    user = user_res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # 2. Get project to check organization ownership
    res = await db.execute(
        select(Workspace.organization_id)
        .join(Project, Project.workspace_id == Workspace.id)
        .where(Project.id == brand_in.project_id)
    )
    org_id = res.scalar_one_or_none()
    if not org_id:
        raise HTTPException(status_code=404, detail="Project not found")
        
    if org_id != user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
        
    brand = await WorkspaceService.create_brand(db, brand_in)
    return brand

@router.post("/competitors", response_model=CompetitorOut, status_code=status.HTTP_201_CREATED)
async def create_competitor(
    comp_in: CompetitorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    from app.modules.workspaces.models import Project, Workspace, User, Brand
    
    # 1. Get user to find organization
    user_res = await db.execute(select(User).where(User.id == current_user.id))
    user = user_res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # 2. Get brand to check organization ownership via project/workspace
    res = await db.execute(
        select(Workspace.organization_id)
        .join(Project, Project.workspace_id == Workspace.id)
        .join(Brand, Brand.project_id == Project.id)
        .where(Brand.id == comp_in.brand_id)
    )
    org_id = res.scalar_one_or_none()
    if not org_id:
        raise HTTPException(status_code=404, detail="Brand not found")
        
    if org_id != user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this brand")
        
    comp = await WorkspaceService.create_competitor(db, comp_in)
    return comp

@router.get("", response_model=List[WorkspaceOut])
async def list_workspaces(
    db: AsyncSession = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    user_res = await db.execute(select(User).where(User.id == current_user.id))
    user = user_res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    res = await db.execute(select(Workspace).where(Workspace.organization_id == user.organization_id))
    return res.scalars().all()

@router.get("/projects", response_model=List[ProjectOut])
async def list_projects(
    workspace_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    user_res = await db.execute(select(User).where(User.id == current_user.id))
    user = user_res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    ws_res = await db.execute(select(Workspace).where(Workspace.id == workspace_id))
    ws = ws_res.scalar_one_or_none()
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    if ws.organization_id != user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    res = await db.execute(select(Project).where(Project.workspace_id == workspace_id))
    return res.scalars().all()

@router.get("/projects/{project_id}/brands", response_model=List[BrandOut])
async def list_brands(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    from app.modules.analysis.router import verify_project_access
    await verify_project_access(db, project_id, current_user)
    res = await db.execute(select(Brand).where(Brand.project_id == project_id))
    return res.scalars().all()

@router.get("/brands/{brand_id}/competitors", response_model=List[CompetitorOut])
async def list_competitors(
    brand_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    user_res = await db.execute(select(User).where(User.id == current_user.id))
    user = user_res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    res = await db.execute(
        select(Workspace.organization_id)
        .join(Project, Project.workspace_id == Workspace.id)
        .join(Brand, Brand.project_id == Project.id)
        .where(Brand.id == brand_id)
    )
    org_id = res.scalar_one_or_none()
    if not org_id:
        raise HTTPException(status_code=404, detail="Brand not found")
    if org_id != user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    comp_res = await db.execute(select(Competitor).where(Competitor.brand_id == brand_id))
    return comp_res.scalars().all()

