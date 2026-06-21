from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class AgencyBase(BaseModel):
    white_label_domain: Optional[str] = None
    logo_url: Optional[str] = None
    custom_colors: Optional[Dict] = {}

class AgencyCreate(AgencyBase):
    organization_id: str

class AgencyOut(AgencyBase):
    id: str
    organization_id: str
    created_at: datetime
    class Config:
        from_attributes = True

class ClientBase(BaseModel):
    billing_status: str

class ClientCreate(ClientBase):
    agency_id: str
    workspace_id: str

class ClientOut(ClientBase):
    id: str
    agency_id: str
    workspace_id: str
    created_at: datetime
    class Config:
        from_attributes = True
