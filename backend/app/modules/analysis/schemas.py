from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, date

class VisibilityOverviewOut(BaseModel):
    visibility_score: float
    weekly_change: float
    history: List[Dict[str, Any]]
    rankings: List[Dict[str, Any]]
    share_of_voice: float
    share_of_voice_breakdown: List[Dict[str, Any]] = []

class CitationOut(BaseModel):
    url: str
    mentions_count: int
    visibility_gain: float
    last_observed: datetime
    status: str

class VolumeOverviewOut(BaseModel):
    total_volume: str
    frequency_rank: str
    platforms: Dict[str, str]
    geos: Dict[str, str]
    variations: List[Dict[str, int]]
    graph_nodes: List[Dict[str, str]]

class AuditRequest(BaseModel):
    url: str
    email: str

class AuditResponse(BaseModel):
    audit_id: str
    status: str
    message: str

class PageAuditOut(BaseModel):
    id: str
    url: str
    email: str
    status: str
    overall_score: Optional[float] = None
    schema_markup_score: Optional[float] = None
    content_structure_score: Optional[float] = None
    keyword_stuffing_score: Optional[float] = None
    semantic_alignment_score: Optional[float] = None
    recommendations: Optional[Dict[str, str]] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

