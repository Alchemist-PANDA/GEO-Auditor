from sqlalchemy import Column, String, ForeignKey, Integer, Numeric, DateTime, Date, Boolean, Table, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime, date

class Domain(Base):
    __tablename__ = "domains"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    domain = Column(String, unique=True, nullable=False)
    domain_authority = Column(Integer, default=0)
    is_competitor = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    citation_sources = relationship("CitationSource", back_populates="domain")

class CitationSource(Base):
    __tablename__ = "citation_sources"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    url = Column(String, unique=True, nullable=False)
    domain_id = Column(String, ForeignKey("domains.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    domain = relationship("Domain", back_populates="citation_sources")
    citations = relationship("Citation", back_populates="source", cascade="all, delete-orphan")

class Response(Base):
    __tablename__ = "responses"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    prompt_run_id = Column(String, ForeignKey("prompt_runs.id", ondelete="CASCADE"), unique=True, nullable=False)
    raw_text = Column(String, nullable=False)
    tokens_used = Column(Integer, default=0)
    latency_ms = Column(Integer, default=0)
    sentiment_score = Column(Numeric(3, 2), default=0.00)
    cost_usd = Column(Numeric(10, 6), default=0.000000)
    provider_requested = Column(String, nullable=True)
    provider_used = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    prompt_run = relationship("PromptRun", back_populates="response")
    citations = relationship("Citation", back_populates="response", cascade="all, delete-orphan")

# pgvector removed in favor of JSONB array storage

class Citation(Base):
    __tablename__ = "citations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    response_id = Column(String, ForeignKey("responses.id", ondelete="CASCADE"), nullable=False)
    source_id = Column(String, ForeignKey("citation_sources.id", ondelete="CASCADE"), nullable=False)
    is_anchor_citation = Column(Boolean, default=False)
    citation_text = Column(String)
    position_index = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    response = relationship("Response", back_populates="citations")
    source = relationship("CitationSource", back_populates="citations")

class TopicCluster(Base):
    __tablename__ = "topic_clusters"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    topics = relationship("Topic", back_populates="cluster", cascade="all, delete-orphan")

class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    cluster_id = Column(String, ForeignKey("topic_clusters.id", ondelete="SET NULL"), nullable=True)
    name = Column(String, nullable=False)
    embedding = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    cluster = relationship("TopicCluster", back_populates="topics")

class Industry(Base):
    __tablename__ = "industries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    rankings = relationship("IndustryRanking", back_populates="industry", cascade="all, delete-orphan")

class IndustryRanking(Base):
    __tablename__ = "industry_rankings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    industry_id = Column(String, ForeignKey("industries.id", ondelete="CASCADE"), nullable=False)
    brand_name = Column(String, nullable=False)
    visibility_score = Column(Numeric(5, 2), nullable=False)
    weekly_change = Column(Numeric(5, 2), default=0.00)
    ranking = Column(Integer, nullable=False)
    recorded_date = Column(Date, default=date.today)
    
    industry = relationship("Industry", back_populates="rankings")

class VisibilityScore(Base):
    __tablename__ = "visibility_scores"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    brand_id = Column(String, ForeignKey("brands.id", ondelete="CASCADE"), nullable=False)
    visibility_score = Column(Numeric(5, 2), nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    brand = relationship("Brand", back_populates="visibility_scores")

class VisibilityHistory(Base):
    __tablename__ = "visibility_history"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    brand_id = Column(String, ForeignKey("brands.id", ondelete="CASCADE"), nullable=False)
    model_id = Column(String, ForeignKey("ai_models.id"), nullable=False)
    visibility_score = Column(Numeric(5, 2), nullable=False)
    sentiment_score = Column(Numeric(3, 2), default=0.00)
    recorded_date = Column(Date, default=date.today)
    
    brand = relationship("Brand", back_populates="visibility_history_records")

class ShareOfVoice(Base):
    __tablename__ = "share_of_voice"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    brand_id = Column(String, ForeignKey("brands.id", ondelete="CASCADE"))
    competitor_id = Column(String, ForeignKey("competitors.id", ondelete="CASCADE"))
    share_percentage = Column(Numeric(5, 2), nullable=False)
    recorded_date = Column(Date, default=date.today)
    
    project = relationship("Project", back_populates="share_of_voice_records")
    brand = relationship("Brand", back_populates="share_of_voice_records")
    competitor = relationship("Competitor", back_populates="share_of_voice_records")

class PageAudit(Base):
    __tablename__ = "page_audits"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String, ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True)
    url = Column(String, nullable=False)
    email = Column(String, nullable=False)
    overall_score = Column(Integer, default=0)
    semantic_alignment_score = Column(Integer, default=0)
    schema_markup_score = Column(Integer, default=0)
    content_structure_score = Column(Integer, default=0)
    keyword_stuffing_score = Column(Integer, default=0)
    recommendations = Column(JSON, default=dict)
    status = Column(String, default="PENDING")
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

