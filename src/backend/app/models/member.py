"""
Member model with pgvector support.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy import Column, String, Text, Float, Boolean, DateTime, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
import uuid

from app.db.base import Base


class Member(Base):
    """Member model representing users in the talent marketplace."""
    
    __tablename__ = "members"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Clerk user ID (external reference)
    clerk_user_id = Column(String, unique=True, nullable=False, index=True)
    
    # Basic information
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=True, index=True)
    
    # Profile information
    bio = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    timezone = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    
    # Professional information
    title = Column(String, nullable=True)
    company = Column(String, nullable=True)
    years_of_experience = Column(Float, nullable=True)
    hourly_rate = Column(Float, nullable=True)
    
    # Skills and expertise (stored as JSON array)
    skills = Column(JSON, default=list)
    expertise_areas = Column(JSON, default=list)
    industries = Column(JSON, default=list)
    
    # Embedding for similarity search (1536 dimensions for OpenAI embeddings)
    profile_embedding = Column(Vector(1536), nullable=True)
    
    # Profile completeness and status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_available = Column(Boolean, default=True)
    profile_completed = Column(Boolean, default=False)
    
    # Social and portfolio links
    linkedin_url = Column(String, nullable=True)
    github_url = Column(String, nullable=True)
    twitter_url = Column(String, nullable=True)
    website_url = Column(String, nullable=True)
    portfolio_urls = Column(JSON, default=list)
    
    # Metadata
    metadata = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_active_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    
    # Indexes for performance
    __table_args__ = (
        Index("ix_members_is_active_is_available", "is_active", "is_available"),
        Index("ix_members_skills", "skills", postgresql_using="gin"),
        Index("ix_members_expertise_areas", "expertise_areas", postgresql_using="gin"),
        Index("ix_members_industries", "industries", postgresql_using="gin"),
        # Create an index for vector similarity search
        Index(
            "ix_members_profile_embedding",
            "profile_embedding",
            postgresql_using="ivfflat",
            postgresql_with={"lists": 100},
            postgresql_ops={"profile_embedding": "vector_l2_ops"}
        ),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "clerk_user_id": self.clerk_user_id,
            "email": self.email,
            "name": self.name,
            "username": self.username,
            "bio": self.bio,
            "location": self.location,
            "timezone": self.timezone,
            "avatar_url": self.avatar_url,
            "title": self.title,
            "company": self.company,
            "years_of_experience": self.years_of_experience,
            "hourly_rate": self.hourly_rate,
            "skills": self.skills or [],
            "expertise_areas": self.expertise_areas or [],
            "industries": self.industries or [],
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "is_available": self.is_available,
            "profile_completed": self.profile_completed,
            "linkedin_url": self.linkedin_url,
            "github_url": self.github_url,
            "twitter_url": self.twitter_url,
            "website_url": self.website_url,
            "portfolio_urls": self.portfolio_urls or [],
            "metadata": self.metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_active_at": self.last_active_at.isoformat() if self.last_active_at else None,
        }
    
    def __repr__(self) -> str:
        return f"<Member {self.email}>"