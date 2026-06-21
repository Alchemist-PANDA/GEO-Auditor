from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user, UserSession
from app.modules.agency.service import AgencyService
from app.modules.agency.schemas import AgencyOut, ClientOut, ClientCreate
from typing import List

router = APIRouter(prefix="/agency", tags=["Agency Operations"])

@router.get("/profile", response_model=AgencyOut)
async def get_agency_profile(
    db: AsyncSession = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    # Retrieve user org to fetch profile
    from app.modules.workspaces.models import User
    from sqlalchemy.future import select
    user_res = await db.execute(select(User).where(User.id == current_user.id))
    user = user_res.scalar_one()
    
    agency = await AgencyService.get_agency_by_org(db, user.organization_id)
    return agency

@router.get("/clients", response_model=List[ClientOut])
async def get_agency_clients(
    agency_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    from app.modules.agency.models import Agency
    from app.modules.workspaces.models import User
    from sqlalchemy.future import select
    from fastapi import HTTPException
    
    # 1. Get user to find organization
    user_res = await db.execute(select(User).where(User.id == current_user.id))
    user = user_res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    # 2. Get agency profile to check organization ownership
    agency_res = await db.execute(select(Agency).where(Agency.id == agency_id))
    agency = agency_res.scalar_one_or_none()
    if not agency:
        raise HTTPException(status_code=404, detail="Agency profile not found")
        
    if agency.organization_id != user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this agency profile")
        
    clients = await AgencyService.get_clients_by_agency(db, agency_id)
    return clients

@router.post("/clients", response_model=ClientOut, status_code=status.HTTP_201_CREATED)
async def add_agency_client(
    client_in: ClientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserSession = Depends(get_current_user)
):
    from app.modules.agency.models import Agency
    from app.modules.workspaces.models import User
    from sqlalchemy.future import select
    from fastapi import HTTPException
    
    # 1. Get user to find organization
    user_res = await db.execute(select(User).where(User.id == current_user.id))
    user = user_res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    # 2. Get agency profile to check organization ownership
    agency_res = await db.execute(select(Agency).where(Agency.id == client_in.agency_id))
    agency = agency_res.scalar_one_or_none()
    if not agency:
        raise HTTPException(status_code=404, detail="Agency profile not found")
        
    if agency.organization_id != user.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this agency profile")
        
    client = await AgencyService.create_client(db, client_in)
    return client
