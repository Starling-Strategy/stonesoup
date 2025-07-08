"""
Story schemas for API request/response validation.

This module provides comprehensive data validation for story-related
operations in STONESOUP.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, validator
from .common import BaseResponse, PaginatedResponse


class StoryStatus(str, Enum):
    """Story status enumeration."""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    REJECTED = "rejected"


class StoryType(str, Enum):
    """Story type enumeration."""
    ACHIEVEMENT = "achievement"
    EXPERIENCE = "experience"
    SKILL_DEMONSTRATION = "skill_demonstration"
    TESTIMONIAL = "testimonial"
    CASE_STUDY = "case_study"
    THOUGHT_LEADERSHIP = "thought_leadership"


class StoryCreate(BaseModel):
    """
    Schema for creating a new story.
    
    Educational Notes:
    - Title and content are required for all stories
    - Type helps categorize stories for better search
    - Tags and skills enable semantic search
    - Member associations support collaborative stories
    """
    title: str = Field(..., min_length=1, max_length=255, description="Story title")
    content: str = Field(..., min_length=10, description="Story content in markdown format")
    summary: Optional[str] = Field(None, max_length=500, description="Brief summary for previews")
    
    # Story classification
    story_type: StoryType = Field(StoryType.EXPERIENCE, description="Type of story")
    
    # Metadata
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags for categorization")
    skills_demonstrated: Optional[List[str]] = Field(default_factory=list, description="Skills showcased")
    
    # Timeline
    occurred_at: Optional[datetime] = Field(None, description="When the story event occurred")
    
    # External references
    external_url: Optional[str] = Field(None, description="Link to external content")
    company: Optional[str] = Field(None, max_length=100, description="Associated company")
    
    # Member associations
    member_ids: Optional[List[str]] = Field(default_factory=list, description="Associated member IDs")
    
    # AI generation context
    ai_generated: bool = Field(False, description="Whether story was AI-generated")
    generation_prompt: Optional[str] = Field(None, description="Prompt used for generation")
    
    # Additional metadata
    extra_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('tags', 'skills_demonstrated')
    def validate_lists(cls, v):
        if v and len(v) > 20:
            raise ValueError('List cannot contain more than 20 items')
        return v
    
    @validator('member_ids')
    def validate_member_ids(cls, v):
        if v and len(v) > 10:
            raise ValueError('Cannot associate more than 10 members with a story')
        return v
    
    @validator('content')
    def validate_content_length(cls, v):
        if len(v) > 10000:
            raise ValueError('Story content cannot exceed 10,000 characters')
        return v


class StoryUpdate(BaseModel):
    """
    Schema for updating an existing story.
    
    Educational Notes:
    - All fields are optional for partial updates
    - Status changes may require additional validation
    - Member associations can be updated
    """
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Story title")
    content: Optional[str] = Field(None, min_length=10, description="Story content in markdown format")
    summary: Optional[str] = Field(None, max_length=500, description="Brief summary for previews")
    
    # Story classification
    story_type: Optional[StoryType] = Field(None, description="Type of story")
    status: Optional[StoryStatus] = Field(None, description="Story status")
    
    # Metadata
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")
    skills_demonstrated: Optional[List[str]] = Field(None, description="Skills showcased")
    
    # Timeline
    occurred_at: Optional[datetime] = Field(None, description="When the story event occurred")
    
    # External references
    external_url: Optional[str] = Field(None, description="Link to external content")
    company: Optional[str] = Field(None, max_length=100, description="Associated company")
    
    # Member associations
    member_ids: Optional[List[str]] = Field(None, description="Associated member IDs")
    
    # Additional metadata
    extra_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @validator('tags', 'skills_demonstrated')
    def validate_lists(cls, v):
        if v and len(v) > 20:
            raise ValueError('List cannot contain more than 20 items')
        return v
    
    @validator('member_ids')
    def validate_member_ids(cls, v):
        if v and len(v) > 10:
            raise ValueError('Cannot associate more than 10 members with a story')
        return v
    
    @validator('content')
    def validate_content_length(cls, v):
        if v and len(v) > 10000:
            raise ValueError('Story content cannot exceed 10,000 characters')
        return v


class StoryResponse(BaseModel):
    """
    Schema for story API responses.
    
    Educational Notes:
    - Includes all story information safe for public viewing
    - Provides computed fields for convenience
    - Includes embedding status for search functionality
    """
    id: str = Field(..., description="Story UUID")
    title: str = Field(..., description="Story title")
    content: str = Field(..., description="Story content in markdown format")
    summary: Optional[str] = Field(None, description="Brief summary for previews")
    
    # Story classification
    story_type: StoryType = Field(..., description="Type of story")
    status: StoryStatus = Field(..., description="Story status")
    
    # Metadata
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    skills_demonstrated: List[str] = Field(default_factory=list, description="Skills showcased")
    
    # Timeline
    occurred_at: Optional[datetime] = Field(None, description="When the story event occurred")
    published_at: Optional[datetime] = Field(None, description="When the story was published")
    
    # External references
    external_url: Optional[str] = Field(None, description="Link to external content")
    company: Optional[str] = Field(None, description="Associated company")
    
    # AI generation info
    ai_generated: bool = Field(False, description="Whether story was AI-generated")
    confidence_score: Optional[float] = Field(None, description="AI confidence score")
    
    # Metrics
    view_count: int = Field(0, description="Number of views")
    like_count: int = Field(0, description="Number of likes")
    
    # Status indicators
    has_embedding: bool = Field(False, description="Whether story has embedding")
    is_published: bool = Field(False, description="Whether story is published")
    is_editable: bool = Field(False, description="Whether story can be edited")
    
    # Timestamps
    created_at: datetime = Field(..., description="When story was created")
    updated_at: datetime = Field(..., description="When story was last updated")
    
    # Cauldron context
    cauldron_id: str = Field(..., description="Cauldron (organization) ID")
    
    # Associated members
    member_ids: List[str] = Field(default_factory=list, description="Associated member IDs")
    members: List[Dict[str, Any]] = Field(default_factory=list, description="Associated member details")
    
    # Review information (if applicable)
    reviewed_by_id: Optional[str] = Field(None, description="ID of reviewer")
    reviewed_at: Optional[datetime] = Field(None, description="When reviewed")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class StoryContent(BaseModel):
    """
    Schema for story content operations.
    
    Educational Notes:
    - Focused on content-specific operations
    - Includes version control information
    - Supports content analysis
    """
    content: str = Field(..., description="Story content in markdown format")
    content_type: str = Field("markdown", description="Content format type")
    word_count: int = Field(0, description="Word count")
    reading_time: int = Field(0, description="Estimated reading time in minutes")
    
    # Content analysis
    complexity_score: Optional[float] = Field(None, description="Content complexity score")
    sentiment_score: Optional[float] = Field(None, description="Content sentiment score")
    
    # Version control
    version: int = Field(1, description="Content version number")
    previous_version: Optional[str] = Field(None, description="Previous version ID")
    
    # Metadata
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="When content was updated")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class StoryList(PaginatedResponse[StoryResponse]):
    """
    Paginated list of stories.
    
    Educational Notes:
    - Extends generic paginated response
    - Includes summary statistics
    - Provides filtering context
    """
    # Additional list metadata
    filters_applied: Optional[Dict[str, Any]] = Field(None, description="Filters applied to the list")
    sort_applied: Optional[str] = Field(None, description="Sort order applied")
    
    # Summary statistics
    total_published: int = Field(0, description="Total published stories")
    total_draft: int = Field(0, description="Total draft stories")
    total_ai_generated: int = Field(0, description="Total AI-generated stories")


class StoryAnalytics(BaseModel):
    """
    Story analytics and statistics.
    
    Educational Notes:
    - Provides comprehensive story metrics
    - Includes engagement and performance data
    - Used for analytics dashboards
    """
    # Story overview
    total_stories: int = Field(..., description="Total number of stories")
    published_stories: int = Field(..., description="Number of published stories")
    draft_stories: int = Field(..., description="Number of draft stories")
    ai_generated_stories: int = Field(..., description="Number of AI-generated stories")
    
    # Engagement metrics
    total_views: int = Field(..., description="Total story views")
    total_likes: int = Field(..., description="Total story likes")
    avg_engagement_rate: float = Field(..., description="Average engagement rate")
    
    # Content metrics
    avg_word_count: float = Field(..., description="Average word count per story")
    avg_reading_time: float = Field(..., description="Average reading time in minutes")
    
    # Performance metrics
    top_stories: List[Dict[str, Any]] = Field(default_factory=list, description="Top performing stories")
    trending_tags: List[Dict[str, Any]] = Field(default_factory=list, description="Trending tags")
    popular_skills: List[Dict[str, Any]] = Field(default_factory=list, description="Popular skills")
    
    # Type distribution
    type_distribution: Dict[str, int] = Field(default_factory=dict, description="Story type distribution")
    status_distribution: Dict[str, int] = Field(default_factory=dict, description="Story status distribution")
    
    # Temporal analysis
    stories_by_month: Dict[str, int] = Field(default_factory=dict, description="Stories created by month")
    growth_rate: float = Field(..., description="Monthly growth rate percentage")
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="When analytics were generated")
    cauldron_id: str = Field(..., description="Cauldron ID for the analytics")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class StoryBulkOperation(BaseModel):
    """
    Schema for bulk story operations.
    
    Educational Notes:
    - Allows bulk updates to multiple stories
    - Includes validation for operation limits
    - Provides operation tracking
    """
    story_ids: List[str] = Field(..., min_items=1, max_items=100, description="List of story IDs")
    operation: str = Field(..., description="Operation to perform")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Operation metadata")
    
    @validator('operation')
    def validate_operation(cls, v):
        valid_operations = ['publish', 'archive', 'delete', 'regenerate_embedding', 'update_tags']
        if v not in valid_operations:
            raise ValueError(f'Operation must be one of: {valid_operations}')
        return v


class StoryBulkResult(BaseModel):
    """
    Result of bulk story operations.
    
    Educational Notes:
    - Provides detailed operation results
    - Includes success and failure counts
    - Lists specific errors for debugging
    """
    total_requested: int = Field(..., description="Total operations requested")
    successful: int = Field(..., description="Number of successful operations")
    failed: int = Field(..., description="Number of failed operations")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="List of errors")
    processed_ids: List[str] = Field(default_factory=list, description="Successfully processed story IDs")
    
    # Operation metadata
    operation: str = Field(..., description="Operation that was performed")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="When operation started")
    completed_at: Optional[datetime] = Field(None, description="When operation completed")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class StoryGeneration(BaseModel):
    """
    Schema for AI story generation requests.
    
    Educational Notes:
    - Provides structured input for story generation
    - Includes context and constraints
    - Supports different generation modes
    """
    # Generation context
    prompt: str = Field(..., min_length=10, description="Generation prompt")
    member_id: str = Field(..., description="Member ID for context")
    story_type: StoryType = Field(StoryType.EXPERIENCE, description="Type of story to generate")
    
    # Generation parameters
    max_length: int = Field(1000, ge=100, le=5000, description="Maximum story length")
    temperature: float = Field(0.7, ge=0.1, le=2.0, description="Generation creativity")
    include_skills: Optional[List[str]] = Field(None, description="Skills to highlight")
    
    # Context information
    company: Optional[str] = Field(None, description="Company context")
    role: Optional[str] = Field(None, description="Role context")
    time_period: Optional[str] = Field(None, description="Time period context")
    
    # Output preferences
    tone: str = Field("professional", description="Desired tone")
    format: str = Field("narrative", description="Story format")
    
    @validator('tone')
    def validate_tone(cls, v):
        valid_tones = ['professional', 'casual', 'technical', 'inspirational', 'humble']
        if v not in valid_tones:
            raise ValueError(f'Tone must be one of: {valid_tones}')
        return v
    
    @validator('format')
    def validate_format(cls, v):
        valid_formats = ['narrative', 'bullet_points', 'structured', 'case_study']
        if v not in valid_formats:
            raise ValueError(f'Format must be one of: {valid_formats}')
        return v


class StoryGenerationResult(BaseModel):
    """
    Result of AI story generation.
    
    Educational Notes:
    - Provides generated content with metadata
    - Includes generation confidence and metrics
    - Supports review and editing workflow
    """
    # Generated content
    title: str = Field(..., description="Generated story title")
    content: str = Field(..., description="Generated story content")
    summary: str = Field(..., description="Generated story summary")
    
    # Generation metadata
    confidence_score: float = Field(..., description="AI confidence score")
    model_used: str = Field(..., description="AI model used for generation")
    generation_time: float = Field(..., description="Generation time in seconds")
    
    # Extracted information
    suggested_tags: List[str] = Field(default_factory=list, description="Suggested tags")
    identified_skills: List[str] = Field(default_factory=list, description="Identified skills")
    
    # Quality metrics
    readability_score: Optional[float] = Field(None, description="Content readability score")
    relevance_score: Optional[float] = Field(None, description="Content relevance score")
    
    # Generation context
    prompt_used: str = Field(..., description="Actual prompt used")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Generation parameters")
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="When story was generated")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }