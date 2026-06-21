from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PromptBase(BaseModel):
    text: str
    locale: Optional[str] = "Global"
    tags: Optional[List[str]] = []

class PromptCreate(PromptBase):
    pass

class PromptBatchCreate(BaseModel):
    project_id: str
    prompts: List[PromptBase]

class PromptOut(PromptBase):
    id: str
    project_id: str
    created_at: datetime
    class Config:
        from_attributes = True

class PromptRunOut(BaseModel):
    id: str
    model_id: str
    status: str
    executed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    class Config:
        from_attributes = True

class PromptWithRunsOut(PromptOut):
    prompt_runs: List[PromptRunOut] = []

class TriggerRunRequest(BaseModel):
    project_id: str
    models: List[str]
