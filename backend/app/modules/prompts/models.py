from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Table, ARRAY, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime

class AIModel(Base):
    __tablename__ = "ai_models"
    
    id = Column(String, primary_key=True)  # e.g., 'gpt-4o'
    name = Column(String, nullable=False)
    provider = Column(String, nullable=False)  # OpenAI, Anthropic, Google, Perplexity
    is_active = Column(Integer, default=1) # SQLAlchemy-friendly mapping
    
    prompt_runs = relationship("PromptRun", back_populates="model")

class Prompt(Base):
    __tablename__ = "prompts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    text = Column(String, nullable=False)
    locale = Column(String, default="Global")  # Global, USA, DE, JP, UK, CA, AU
    tags = Column(ARRAY(String).with_variant(JSON, "sqlite"), default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="prompts")
    prompt_runs = relationship("PromptRun", back_populates="prompt", cascade="all, delete-orphan")

class PromptRun(Base):
    __tablename__ = "prompt_runs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    prompt_id = Column(String, ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False)
    model_id = Column(String, ForeignKey("ai_models.id"), nullable=False)
    status = Column(String, default="PENDING")  # PENDING, RUNNING, COMPLETED, FAILED
    executed_at = Column(DateTime)
    error_message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    prompt = relationship("Prompt", back_populates="prompt_runs")
    model = relationship("AIModel", back_populates="prompt_runs")
    response = relationship("Response", uselist=False, back_populates="prompt_run", cascade="all, delete-orphan")
