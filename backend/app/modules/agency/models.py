from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime

class Agency(Base):
    __tablename__ = "agencies"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), unique=True, nullable=False)
    white_label_domain = Column(String)
    logo_url = Column(String)
    custom_colors = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    clients = relationship("Client", back_populates="agency", cascade="all, delete-orphan")

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agency_id = Column(String, ForeignKey("agencies.id", ondelete="CASCADE"), nullable=False)
    workspace_id = Column(String, ForeignKey("workspaces.id", ondelete="CASCADE"), unique=True, nullable=False)
    billing_status = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    agency = relationship("Agency", back_populates="clients")
    workspace = relationship("Workspace", back_populates="client_profile")

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    created_by = Column(String, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="reports")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"))
    action = Column(String, nullable=False)
    metadata_json = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
