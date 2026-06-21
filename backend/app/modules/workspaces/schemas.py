from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserSession(BaseModel):
    id: str
    email: str
    role: str

class OrganizationBase(BaseModel):
    name: str

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationOut(OrganizationBase):
    id: str
    created_at: datetime
    class Config:
        from_attributes = True

class WorkspaceBase(BaseModel):
    name: str
    tier: Optional[str] = "pitch"

class WorkspaceCreate(WorkspaceBase):
    pass

class WorkspaceOut(WorkspaceBase):
    id: str
    organization_id: str
    prompt_limit: int
    prompts_used: int
    created_at: datetime
    class Config:
        from_attributes = True

class ProjectBase(BaseModel):
    name: str

class ProjectCreate(ProjectBase):
    workspace_id: str

class ProjectOut(ProjectBase):
    id: str
    workspace_id: str
    created_at: datetime
    class Config:
        from_attributes = True

class BrandBase(BaseModel):
    name: str
    domain: str

class BrandCreate(BrandBase):
    project_id: str

class BrandOut(BrandBase):
    id: str
    project_id: str
    created_at: datetime
    class Config:
        from_attributes = True

class CompetitorBase(BaseModel):
    name: str
    domain: str

class CompetitorCreate(CompetitorBase):
    brand_id: str

class CompetitorOut(CompetitorBase):
    id: str
    brand_id: str
    created_at: datetime
    class Config:
        from_attributes = True

class UserLoginRequest(BaseModel):
    email: str
    password: str

class UserRegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    organization_name: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

