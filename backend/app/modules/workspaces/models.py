from sqlalchemy import Column, String, ForeignKey, Integer, Table, DateTime, Enum, Boolean, Numeric
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime

# Import Client to resolve relationship mapping
from app.modules.agency.models import Client

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    users = relationship("User", back_populates="organization")
    workspaces = relationship("Workspace", back_populates="organization", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)  # Auth provider user ID
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="SET NULL"))
    role = Column(String, default="member")  # sys_admin, org_admin, member, viewer
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    organization = relationship("Organization", back_populates="users")

class Workspace(Base):
    __tablename__ = "workspaces"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    tier = Column(String, default="pitch")  # pitch, basic, premium, agency_client
    prompt_limit = Column(Integer, default=25)
    prompts_used = Column(Integer, default=0)
    api_cost_used = Column(Numeric(10, 6), default=0.000000)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    organization = relationship("Organization", back_populates="workspaces")
    projects = relationship("Project", back_populates="workspace", cascade="all, delete-orphan")
    client_profile = relationship("Client", uselist=False, back_populates="workspace", cascade="all, delete-orphan")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    workspace = relationship("Workspace", back_populates="projects")
    brands = relationship("Brand", back_populates="project", cascade="all, delete-orphan")
    prompts = relationship("Prompt", back_populates="project", cascade="all, delete-orphan")
    share_of_voice_records = relationship("ShareOfVoice", back_populates="project", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="project", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="project", cascade="all, delete-orphan")

class Brand(Base):
    __tablename__ = "brands"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    domain = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="brands")
    competitors = relationship("Competitor", back_populates="brand", cascade="all, delete-orphan")
    visibility_scores = relationship("VisibilityScore", back_populates="brand", cascade="all, delete-orphan")
    visibility_history_records = relationship("VisibilityHistory", back_populates="brand", cascade="all, delete-orphan")
    share_of_voice_records = relationship("ShareOfVoice", back_populates="brand", cascade="all, delete-orphan")

class Competitor(Base):
    __tablename__ = "competitors"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    brand_id = Column(String, ForeignKey("brands.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    domain = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    brand = relationship("Brand", back_populates="competitors")
    share_of_voice_records = relationship("ShareOfVoice", back_populates="competitor", cascade="all, delete-orphan")
