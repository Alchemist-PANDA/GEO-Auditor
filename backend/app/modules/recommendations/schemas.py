from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class RecommendationActionOut(BaseModel):
    id: str
    action_text: str
    is_completed: bool
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RecommendationOut(BaseModel):
    id: str
    title: str
    description: str
    priority: str
    status: str
    estimated_visibility_gain: float
    created_at: datetime
    actions: List[RecommendationActionOut] = []

    class Config:
        from_attributes = True


class RecommendationStatusUpdate(BaseModel):
    status: str  # active, validating, resolved, ignored


class GenerateRecommendationsRequest(BaseModel):
    project_id: str
    use_llm: bool = False
