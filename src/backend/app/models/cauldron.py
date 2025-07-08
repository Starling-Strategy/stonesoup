"""
Cauldron model for multi-tenant organizations/workspaces.

A Cauldron represents an isolated workspace or organization in STONESOUP.
Each cauldron has its own configuration, members, stories, and data,
providing complete data isolation for multi-tenancy.

The name "Cauldron" aligns with the Stone Soup metaphor - it's the container
where all the ingredients (members, stories, knowledge) come together to
create something greater than the sum of its parts.
"""
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, String, Text, JSON, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base_class import BaseModel


class Cauldron(BaseModel):
    """
    Cauldron model representing an organization/workspace in the talent marketplace.
    
    A Cauldron is the top-level container for all data in STONESOUP, providing:
    - Multi-tenancy through data isolation
    - Customizable AI guidance and prompts
    - Configuration for features and integrations
    - Branding and customization options
    
    Each cauldron operates independently with its own:
    - Members (talent pool)
    - Stories (contributions and achievements)
    - Search embeddings and AI configurations
    - Custom prompts and guidance
    """
    
    __tablename__ = "cauldrons"
    
    # Basic Information
    name = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Display name of the cauldron/organization"
    )
    
    slug = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="URL-friendly identifier for the cauldron"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Detailed description of the cauldron's purpose and community"
    )
    
    # Configuration
    configuration = Column(
        JSON,
        default=dict,
        nullable=False,
        comment="JSON configuration for features, integrations, and settings"
    )
    
    # AI Configuration
    global_guidance_prompt = Column(
        Text,
        nullable=True,
        comment="Global AI prompt that guides how stories are generated and evaluated"
    )
    
    embedding_model = Column(
        String(100),
        default="text-embedding-ada-002",
        nullable=False,
        comment="The embedding model to use for this cauldron's semantic search"
    )
    
    # Features and Permissions
    features = Column(
        JSON,
        default=dict,
        nullable=False,
        comment="Enabled features for this cauldron (e.g., story_generation, ai_matching)"
    )
    
    # Branding and Customization
    logo_url = Column(
        String,
        nullable=True,
        comment="URL to the cauldron's logo"
    )
    
    primary_color = Column(
        String(7),
        default="#6366F1",
        nullable=True,
        comment="Primary brand color in hex format"
    )
    
    custom_domain = Column(
        String,
        unique=True,
        nullable=True,
        index=True,
        comment="Custom domain for white-label deployments"
    )
    
    # Status and Limits
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether the cauldron is currently active"
    )
    
    is_public = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether the cauldron is publicly accessible"
    )
    
    member_limit = Column(
        JSON,
        default={"max": 100, "current": 0},
        nullable=False,
        comment="Member limits and current count"
    )
    
    story_limit = Column(
        JSON,
        default={"max": 1000, "current": 0},
        nullable=False,
        comment="Story limits and current count"
    )
    
    # Billing and Subscription
    subscription_tier = Column(
        String(50),
        default="free",
        nullable=False,
        comment="Current subscription tier (free, pro, enterprise)"
    )
    
    billing_email = Column(
        String,
        nullable=True,
        comment="Email for billing communications"
    )
    
    # Owner Information
    owner_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="ID of the member who owns this cauldron"
    )
    
    # Metadata
    extra_metadata = Column(
        JSON,
        default=dict,
        nullable=False,
        comment="Additional metadata and custom fields"
    )
    
    # Relationships (defined as strings to avoid circular imports)
    members = relationship(
        "Member",
        back_populates="cauldron",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    
    stories = relationship(
        "Story",
        back_populates="cauldron",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    
    # Indexes for performance
    __table_args__ = (
        Index("ix_cauldrons_is_active_is_public", "is_active", "is_public"),
        Index("ix_cauldrons_subscription_tier", "subscription_tier"),
        Index("ix_cauldrons_features", "features", postgresql_using="gin"),
        Index("ix_cauldrons_extra_metadata", "extra_metadata", postgresql_using="gin"),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert cauldron to dictionary representation."""
        return {
            **super().to_dict(),
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "configuration": self.configuration or {},
            "global_guidance_prompt": self.global_guidance_prompt,
            "embedding_model": self.embedding_model,
            "features": self.features or {},
            "logo_url": self.logo_url,
            "primary_color": self.primary_color,
            "custom_domain": self.custom_domain,
            "is_active": self.is_active,
            "is_public": self.is_public,
            "member_limit": self.member_limit or {},
            "story_limit": self.story_limit or {},
            "subscription_tier": self.subscription_tier,
            "billing_email": self.billing_email,
            "owner_id": str(self.owner_id) if self.owner_id else None,
            "extra_metadata": self.extra_metadata or {},
        }
    
    def __repr__(self) -> str:
        return f"<Cauldron {self.slug}>"
    
    @property
    def is_at_member_limit(self) -> bool:
        """Check if the cauldron has reached its member limit."""
        limits = self.member_limit or {}
        return limits.get("current", 0) >= limits.get("max", 0)
    
    @property
    def is_at_story_limit(self) -> bool:
        """Check if the cauldron has reached its story limit."""
        limits = self.story_limit or {}
        return limits.get("current", 0) >= limits.get("max", 0)
    
    def increment_member_count(self) -> None:
        """Increment the current member count."""
        if not self.member_limit:
            self.member_limit = {"max": 100, "current": 0}
        self.member_limit["current"] = self.member_limit.get("current", 0) + 1
    
    def decrement_member_count(self) -> None:
        """Decrement the current member count."""
        if self.member_limit and self.member_limit.get("current", 0) > 0:
            self.member_limit["current"] -= 1
    
    def increment_story_count(self) -> None:
        """Increment the current story count."""
        if not self.story_limit:
            self.story_limit = {"max": 1000, "current": 0}
        self.story_limit["current"] = self.story_limit.get("current", 0) + 1
    
    def decrement_story_count(self) -> None:
        """Decrement the current story count."""
        if self.story_limit and self.story_limit.get("current", 0) > 0:
            self.story_limit["current"] -= 1