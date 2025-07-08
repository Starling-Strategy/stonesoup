"""
Member schemas for API request/response validation.

This module provides comprehensive data validation for member-related
operations in STONESOUP.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, validator, EmailStr
from .common import BaseResponse, PaginatedResponse, CauldronContext


class MemberStatus(str, Enum):
    """Member status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    ARCHIVED = "archived"


class MemberCreate(BaseModel):
    """
    Schema for creating a new member.
    
    Educational Notes:
    - Email validation ensures proper format
    - Optional fields allow flexible member creation
    - Skills and expertise are stored as arrays
    - Multi-tenancy handled automatically via cauldron context
    """
    email: EmailStr = Field(..., description="Member's email address")
    clerk_user_id: Optional[str] = Field(None, description="Clerk user ID if linked")
    name: str = Field(..., min_length=1, max_length=255, description="Member's display name")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Username for profile URLs")
    
    # Profile information
    bio: Optional[str] = Field(None, max_length=1000, description="Member's bio/description")
    location: Optional[str] = Field(None, max_length=100, description="Member's location")
    timezone: Optional[str] = Field(None, max_length=50, description="Member's timezone")
    avatar_url: Optional[str] = Field(None, description="URL to member's avatar image")
    
    # Professional information
    title: Optional[str] = Field(None, max_length=100, description="Job title")
    company: Optional[str] = Field(None, max_length=100, description="Current company")
    years_of_experience: Optional[float] = Field(None, ge=0, le=50, description="Years of experience")
    hourly_rate: Optional[float] = Field(None, ge=0, description="Hourly rate in USD")
    
    # Skills and expertise
    skills: Optional[List[str]] = Field(default_factory=list, description="List of skills")
    expertise_areas: Optional[List[str]] = Field(default_factory=list, description="Areas of expertise")
    industries: Optional[List[str]] = Field(default_factory=list, description="Industry experience")
    
    # Social and portfolio links
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    github_url: Optional[str] = Field(None, description="GitHub profile URL")
    twitter_url: Optional[str] = Field(None, description="Twitter profile URL")
    website_url: Optional[str] = Field(None, description="Personal website URL")
    portfolio_urls: Optional[List[str]] = Field(default_factory=list, description="Portfolio URLs")
    
    # Status
    is_active: bool = Field(True, description="Whether member is active")
    is_available: bool = Field(True, description="Whether member is available for work")
    
    # Metadata
    extra_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('username')
    def validate_username(cls, v):
        if v and not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must contain only alphanumeric characters, underscores, and hyphens')
        return v
    
    @validator('skills', 'expertise_areas', 'industries')
    def validate_lists(cls, v):
        if v and len(v) > 20:
            raise ValueError('List cannot contain more than 20 items')
        return v
    
    @validator('portfolio_urls')
    def validate_portfolio_urls(cls, v):
        if v and len(v) > 10:
            raise ValueError('Cannot have more than 10 portfolio URLs')
        return v


class MemberUpdate(BaseModel):
    """
    Schema for updating an existing member.
    
    Educational Notes:
    - All fields are optional for partial updates
    - Email updates require special handling
    - Skills and expertise can be completely replaced
    """
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Member's display name")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Username for profile URLs")
    
    # Profile information
    bio: Optional[str] = Field(None, max_length=1000, description="Member's bio/description")
    location: Optional[str] = Field(None, max_length=100, description="Member's location")
    timezone: Optional[str] = Field(None, max_length=50, description="Member's timezone")
    avatar_url: Optional[str] = Field(None, description="URL to member's avatar image")
    
    # Professional information
    title: Optional[str] = Field(None, max_length=100, description="Job title")
    company: Optional[str] = Field(None, max_length=100, description="Current company")
    years_of_experience: Optional[float] = Field(None, ge=0, le=50, description="Years of experience")
    hourly_rate: Optional[float] = Field(None, ge=0, description="Hourly rate in USD")
    
    # Skills and expertise
    skills: Optional[List[str]] = Field(None, description="List of skills")
    expertise_areas: Optional[List[str]] = Field(None, description="Areas of expertise")
    industries: Optional[List[str]] = Field(None, description="Industry experience")
    
    # Social and portfolio links
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    github_url: Optional[str] = Field(None, description="GitHub profile URL")
    twitter_url: Optional[str] = Field(None, description="Twitter profile URL")
    website_url: Optional[str] = Field(None, description="Personal website URL")
    portfolio_urls: Optional[List[str]] = Field(None, description="Portfolio URLs")
    
    # Status
    is_active: Optional[bool] = Field(None, description="Whether member is active")
    is_available: Optional[bool] = Field(None, description="Whether member is available for work")
    
    # Metadata
    extra_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @validator('username')
    def validate_username(cls, v):
        if v and not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must contain only alphanumeric characters, underscores, and hyphens')
        return v
    
    @validator('skills', 'expertise_areas', 'industries')
    def validate_lists(cls, v):
        if v and len(v) > 20:
            raise ValueError('List cannot contain more than 20 items')
        return v
    
    @validator('portfolio_urls')
    def validate_portfolio_urls(cls, v):
        if v and len(v) > 10:
            raise ValueError('Cannot have more than 10 portfolio URLs')
        return v


class MemberResponse(BaseModel):
    """
    Schema for member API responses.
    
    Educational Notes:
    - Includes all member information safe for public viewing
    - Excludes sensitive fields like clerk_user_id
    - Provides computed fields for convenience
    - Includes embedding status for search functionality
    """
    id: str = Field(..., description="Member UUID")
    email: EmailStr = Field(..., description="Member's email address")
    name: str = Field(..., description="Member's display name")
    username: Optional[str] = Field(None, description="Username for profile URLs")
    
    # Profile information
    bio: Optional[str] = Field(None, description="Member's bio/description")
    location: Optional[str] = Field(None, description="Member's location")
    timezone: Optional[str] = Field(None, description="Member's timezone")
    avatar_url: Optional[str] = Field(None, description="URL to member's avatar image")
    
    # Professional information
    title: Optional[str] = Field(None, description="Job title")
    company: Optional[str] = Field(None, description="Current company")
    years_of_experience: Optional[float] = Field(None, description="Years of experience")
    hourly_rate: Optional[float] = Field(None, description="Hourly rate in USD")
    
    # Skills and expertise
    skills: List[str] = Field(default_factory=list, description="List of skills")
    expertise_areas: List[str] = Field(default_factory=list, description="Areas of expertise")
    industries: List[str] = Field(default_factory=list, description="Industry experience")
    
    # Social and portfolio links
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    github_url: Optional[str] = Field(None, description="GitHub profile URL")
    twitter_url: Optional[str] = Field(None, description="Twitter profile URL")
    website_url: Optional[str] = Field(None, description="Personal website URL")
    portfolio_urls: List[str] = Field(default_factory=list, description="Portfolio URLs")
    
    # Status and metadata
    is_active: bool = Field(..., description="Whether member is active")
    is_verified: bool = Field(..., description="Whether member is verified")
    is_available: bool = Field(..., description="Whether member is available for work")
    profile_completed: bool = Field(..., description="Whether profile is completed")
    has_embedding: bool = Field(False, description="Whether member has profile embedding")
    
    # Timestamps
    created_at: datetime = Field(..., description="When member was created")
    updated_at: datetime = Field(..., description="When member was last updated")
    last_active_at: Optional[datetime] = Field(None, description="When member was last active")
    
    # Cauldron context
    cauldron_id: str = Field(..., description="Cauldron (organization) ID")
    
    # Computed fields
    profile_url: Optional[str] = Field(None, description="Profile URL if username exists")
    story_count: int = Field(0, description="Number of stories by this member")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MemberProfile(MemberResponse):
    """
    Extended member profile with additional details.
    
    Educational Notes:
    - Extends basic member response with more details
    - Includes recent stories and analytics
    - Used for detailed profile views
    """
    # Additional profile details
    extra_metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Recent activity
    recent_stories: List[Dict[str, Any]] = Field(default_factory=list, description="Recent stories")
    
    # Profile statistics
    total_views: int = Field(0, description="Total profile views")
    total_likes: int = Field(0, description="Total likes across all stories")
    
    # Engagement metrics
    engagement_score: float = Field(0.0, description="Member engagement score")
    response_rate: Optional[float] = Field(None, description="Response rate percentage")
    
    # Skills analysis
    top_skills: List[str] = Field(default_factory=list, description="Top 5 skills based on stories")
    skill_endorsements: Dict[str, int] = Field(default_factory=dict, description="Skill endorsement counts")


class MemberList(PaginatedResponse[MemberResponse]):
    """
    Paginated list of members.
    
    Educational Notes:
    - Extends generic paginated response
    - Includes summary statistics
    - Provides filtering context
    """
    # Additional list metadata
    filters_applied: Optional[Dict[str, Any]] = Field(None, description="Filters applied to the list")
    sort_applied: Optional[str] = Field(None, description="Sort order applied")
    
    # Summary statistics
    total_active: int = Field(0, description="Total active members")
    total_available: int = Field(0, description="Total available members")
    total_verified: int = Field(0, description="Total verified members")


class MemberAnalytics(BaseModel):
    """
    Member analytics and statistics.
    
    Educational Notes:
    - Provides comprehensive member metrics
    - Includes engagement and activity data
    - Used for analytics dashboards
    """
    # Member overview
    total_members: int = Field(..., description="Total number of members")
    active_members: int = Field(..., description="Number of active members")
    verified_members: int = Field(..., description="Number of verified members")
    available_members: int = Field(..., description="Number of available members")
    
    # Growth metrics
    new_members_this_month: int = Field(..., description="New members this month")
    new_members_last_month: int = Field(..., description="New members last month")
    growth_rate: float = Field(..., description="Monthly growth rate percentage")
    
    # Engagement metrics
    avg_story_count: float = Field(..., description="Average stories per member")
    avg_profile_completion: float = Field(..., description="Average profile completion percentage")
    avg_response_rate: float = Field(..., description="Average response rate")
    
    # Skills analysis
    top_skills: List[Dict[str, Any]] = Field(default_factory=list, description="Top skills across all members")
    skill_diversity: float = Field(..., description="Skill diversity score")
    
    # Geographic distribution
    top_locations: List[Dict[str, Any]] = Field(default_factory=list, description="Top member locations")
    timezone_distribution: Dict[str, int] = Field(default_factory=dict, description="Timezone distribution")
    
    # Professional insights
    experience_distribution: Dict[str, int] = Field(default_factory=dict, description="Experience level distribution")
    industry_distribution: Dict[str, int] = Field(default_factory=dict, description="Industry distribution")
    rate_distribution: Dict[str, int] = Field(default_factory=dict, description="Hourly rate distribution")
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="When analytics were generated")
    cauldron_id: str = Field(..., description="Cauldron ID for the analytics")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MemberBulkOperation(BaseModel):
    """
    Schema for bulk member operations.
    
    Educational Notes:
    - Allows bulk updates to multiple members
    - Includes validation for operation limits
    - Provides operation tracking
    """
    member_ids: List[str] = Field(..., min_items=1, max_items=100, description="List of member IDs")
    operation: str = Field(..., description="Operation to perform (activate, deactivate, delete)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Operation metadata")
    
    @validator('operation')
    def validate_operation(cls, v):
        valid_operations = ['activate', 'deactivate', 'delete', 'archive', 'verify']
        if v not in valid_operations:
            raise ValueError(f'Operation must be one of: {valid_operations}')
        return v


class MemberBulkResult(BaseModel):
    """
    Result of bulk member operations.
    
    Educational Notes:
    - Provides detailed operation results
    - Includes success and failure counts
    - Lists specific errors for debugging
    """
    total_requested: int = Field(..., description="Total operations requested")
    successful: int = Field(..., description="Number of successful operations")
    failed: int = Field(..., description="Number of failed operations")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="List of errors")
    processed_ids: List[str] = Field(default_factory=list, description="Successfully processed member IDs")
    
    # Operation metadata
    operation: str = Field(..., description="Operation that was performed")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="When operation started")
    completed_at: Optional[datetime] = Field(None, description="When operation completed")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }