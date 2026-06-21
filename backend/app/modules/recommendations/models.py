from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean, Numeric
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    priority = Column(String, default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String, default="active")  # active, validating, resolved, ignored
    estimated_visibility_gain = Column(Numeric(5, 2), default=0.00)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="recommendations")
    actions = relationship("RecommendationAction", back_populates="recommendation", cascade="all, delete-orphan")

class RecommendationAction(Base):
    __tablename__ = "recommendation_actions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    recommendation_id = Column(String, ForeignKey("recommendations.id", ondelete="CASCADE"), nullable=False)
    action_text = Column(String, nullable=False)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    
    recommendation = relationship("Recommendation", back_populates="actions")
