"""
Member model with pgvector support and multi-tenancy.

Members represent users in the STONESOUP talent marketplace. Each member
belongs to a specific cauldron (organization) and has a profile that can
be searched using semantic similarity via pgvector embeddings.

The model supports:
- Multi-tenancy through cauldron_id
- Semantic search via profile embeddings
- Rich profile information including skills and expertise
- Integration with Clerk for authentication
- Social and portfolio links
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy import Column, String, Text, Float, Boolean, DateTime, JSON, Index, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import uuid

from app.db.base_class import BaseModel, CauldronMixin


class Member(BaseModel, CauldronMixin):
    """Member model representing users in the talent marketplace."""
    
    __tablename__ = "members"
    
    # Clerk user ID (external reference)
    # Note: We use a composite unique constraint with cauldron_id to allow
    # the same Clerk user to be a member of multiple cauldrons
    clerk_user_id = Column(
        String,
        nullable=False,
        index=True,
        comment="Clerk authentication user ID"
    )
    
    # Basic information
    email = Column(
        String,
        nullable=False,
        index=True,
        comment="Member's email address"
    )
    name = Column(
        String,
        nullable=False,
        comment="Member's display name"
    )
    username = Column(
        String,
        nullable=True,
        index=True,
        comment="Optional username for profile URLs"
    )
    
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
    extra_metadata = Column(JSON, default=dict)
    
    # Additional timestamps
    last_active_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=True,
        comment="Last time the member was active on the platform"
    )
    
    # Relationships
    member_stories = relationship(
        "Story",
        secondary="story_members",
        back_populates="members",
        lazy="selectin"
    )
    
    reviewed_stories = relationship(
        "Story",
        foreign_keys="Story.reviewed_by_id",
        back_populates="reviewer"
    )
    
    # Indexes and constraints for performance and data integrity
    __table_args__ = (
        # Unique constraints for multi-tenancy
        UniqueConstraint("cauldron_id", "email", name="uq_members_cauldron_email"),
        UniqueConstraint("cauldron_id", "username", name="uq_members_cauldron_username"),
        UniqueConstraint("cauldron_id", "clerk_user_id", name="uq_members_cauldron_clerk_user"),
        
        # Performance indexes
        Index("ix_members_cauldron_is_active", "cauldron_id", "is_active"),
        Index("ix_members_is_active_is_available", "is_active", "is_available"),
        Index("ix_members_skills", "skills", postgresql_using="gin"),
        Index("ix_members_expertise_areas", "expertise_areas", postgresql_using="gin"),
        Index("ix_members_industries", "industries", postgresql_using="gin"),
        
        # Create HNSW index for vector similarity search
        # HNSW (Hierarchical Navigable Small World) provides better performance
        # for high-dimensional vector searches compared to IVFFlat
        Index(
            "ix_members_profile_embedding_hnsw",
            "profile_embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"profile_embedding": "vector_cosine_ops"}
        ),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            **super().to_dict(),  # Include base fields (id, created_at, updated_at)
            "cauldron_id": str(self.cauldron_id) if self.cauldron_id else None,
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
            "extra_metadata": self.extra_metadata or {},
            "last_active_at": self.last_active_at.isoformat() if self.last_active_at else None,
        }
    
    def __repr__(self) -> str:
        return f"<Member {self.email}>"