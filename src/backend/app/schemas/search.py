"""
Search schemas for API request/response validation.

This module provides comprehensive data validation for search-related
operations in STONESOUP, including hybrid search, AI summaries, and
semantic search functionality.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, validator
from .common import BaseResponse, PaginatedResponse, ScoreExplanation, SearchMetadata
from .member import MemberResponse
from .story import StoryResponse


class SearchType(str, Enum):
    """Search type enumeration."""
    TEXT = "text"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"


class SearchScope(str, Enum):
    """Search scope enumeration."""
    ALL = "all"
    STORIES = "stories"
    MEMBERS = "members"


class SearchSort(str, Enum):
    """Search sort options."""
    RELEVANCE = "relevance"
    RECENT = "recent"
    POPULAR = "popular"
    ALPHABETICAL = "alphabetical"


class SearchFilters(BaseModel):
    """
    Search filters configuration.
    
    Educational Notes:
    - Provides comprehensive filtering options
    - Supports multiple filter types
    - Includes validation for filter values
    """
    # Content type filters
    story_types: Optional[List[str]] = Field(None, description="Filter by story types")
    story_statuses: Optional[List[str]] = Field(None, description="Filter by story statuses")
    
    # Member filters
    member_skills: Optional[List[str]] = Field(None, description="Filter by member skills")
    member_locations: Optional[List[str]] = Field(None, description="Filter by member locations")
    member_companies: Optional[List[str]] = Field(None, description="Filter by member companies")
    
    # Temporal filters
    date_from: Optional[datetime] = Field(None, description="Filter content from this date")
    date_to: Optional[datetime] = Field(None, description="Filter content to this date")
    
    # Boolean filters
    ai_generated_only: Optional[bool] = Field(None, description="Filter to AI-generated content only")
    verified_members_only: Optional[bool] = Field(None, description="Filter to verified members only")
    available_members_only: Optional[bool] = Field(None, description="Filter to available members only")
    
    # Numeric filters
    min_experience: Optional[float] = Field(None, ge=0, description="Minimum years of experience")
    max_experience: Optional[float] = Field(None, ge=0, description="Maximum years of experience")
    min_rate: Optional[float] = Field(None, ge=0, description="Minimum hourly rate")
    max_rate: Optional[float] = Field(None, ge=0, description="Maximum hourly rate")
    
    # Tag filters
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    skills: Optional[List[str]] = Field(None, description="Filter by skills")
    industries: Optional[List[str]] = Field(None, description="Filter by industries")
    
    @validator('story_types')
    def validate_story_types(cls, v):
        if v:
            valid_types = ['achievement', 'experience', 'skill_demonstration', 'testimonial', 'case_study', 'thought_leadership']
            for story_type in v:
                if story_type not in valid_types:
                    raise ValueError(f'Invalid story type: {story_type}')
        return v
    
    @validator('story_statuses')
    def validate_story_statuses(cls, v):
        if v:
            valid_statuses = ['draft', 'pending_review', 'published', 'archived', 'rejected']
            for status in v:
                if status not in valid_statuses:
                    raise ValueError(f'Invalid story status: {status}')
        return v


class SearchRequest(BaseModel):
    """
    Search request schema.
    
    Educational Notes:
    - Provides comprehensive search configuration
    - Supports multiple search modes
    - Includes advanced filtering and sorting
    """
    # Core search parameters
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    search_type: SearchType = Field(SearchType.HYBRID, description="Type of search to perform")
    scope: SearchScope = Field(SearchScope.ALL, description="Search scope")
    
    # Pagination
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Number of results per page")
    
    # Sorting
    sort: SearchSort = Field(SearchSort.RELEVANCE, description="Sort order")
    
    # Filters
    filters: Optional[SearchFilters] = Field(None, description="Search filters")
    
    # Semantic search parameters
    semantic_threshold: Optional[float] = Field(0.7, ge=0.0, le=1.0, description="Semantic similarity threshold")
    boost_recent: Optional[bool] = Field(True, description="Boost recent content in results")
    boost_popular: Optional[bool] = Field(True, description="Boost popular content in results")
    
    # AI features
    generate_summary: Optional[bool] = Field(False, description="Generate AI summary of results")
    include_suggestions: Optional[bool] = Field(True, description="Include search suggestions")
    
    # Advanced options
    explain_scores: Optional[bool] = Field(False, description="Include score explanations")
    include_highlights: Optional[bool] = Field(True, description="Include text highlights")
    
    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()


class SearchResult(BaseModel):
    """
    Base search result schema.
    
    Educational Notes:
    - Provides common fields for all search results
    - Includes scoring and highlighting information
    - Supports different result types
    """
    # Basic information
    id: str = Field(..., description="Result ID")
    type: str = Field(..., description="Result type (story, member)")
    title: str = Field(..., description="Result title")
    content: str = Field(..., description="Result content or description")
    
    # Scoring information
    score: float = Field(..., description="Search relevance score")
    score_explanation: Optional[ScoreExplanation] = Field(None, description="Score explanation")
    
    # Highlighting
    highlights: Optional[Dict[str, List[str]]] = Field(None, description="Search term highlights")
    
    # Metadata
    created_at: datetime = Field(..., description="When result was created")
    updated_at: datetime = Field(..., description="When result was updated")
    
    # Context
    cauldron_id: str = Field(..., description="Cauldron ID")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MemberSearchResult(SearchResult):
    """
    Member-specific search result.
    
    Educational Notes:
    - Extends base search result with member-specific fields
    - Includes member profile information
    - Provides member-specific scoring context
    """
    type: str = Field("member", description="Result type")
    member: MemberResponse = Field(..., description="Member details")
    
    # Member-specific scoring factors
    profile_completeness: float = Field(0.0, description="Profile completeness score")
    skill_match: float = Field(0.0, description="Skill match score")
    experience_relevance: float = Field(0.0, description="Experience relevance score")
    
    # Member context
    availability_status: str = Field("unknown", description="Member availability status")
    last_active: Optional[datetime] = Field(None, description="Last activity time")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class StorySearchResult(SearchResult):
    """
    Story-specific search result.
    
    Educational Notes:
    - Extends base search result with story-specific fields
    - Includes story content and metadata
    - Provides story-specific scoring context
    """
    type: str = Field("story", description="Result type")
    story: StoryResponse = Field(..., description="Story details")
    
    # Story-specific scoring factors
    content_quality: float = Field(0.0, description="Content quality score")
    engagement_score: float = Field(0.0, description="Engagement score")
    recency_score: float = Field(0.0, description="Recency score")
    
    # Story context
    member_names: List[str] = Field(default_factory=list, description="Associated member names")
    skill_matches: List[str] = Field(default_factory=list, description="Matching skills")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SearchResponse(BaseModel):
    """
    Search response schema.
    
    Educational Notes:
    - Provides comprehensive search results
    - Includes metadata and analytics
    - Supports different result types
    """
    # Results
    results: List[Union[MemberSearchResult, StorySearchResult]] = Field(default_factory=list, description="Search results")
    
    # Pagination
    total: int = Field(0, description="Total number of results")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(20, description="Number of results per page")
    has_next: bool = Field(False, description="Whether there are more pages")
    has_previous: bool = Field(False, description="Whether there are previous pages")
    
    # Search metadata
    search_metadata: SearchMetadata = Field(..., description="Search execution metadata")
    
    # Result breakdown
    result_counts: Dict[str, int] = Field(default_factory=dict, description="Count by result type")
    
    # Query suggestions
    suggestions: Optional[List[str]] = Field(None, description="Search suggestions")
    
    # AI summary
    ai_summary: Optional[str] = Field(None, description="AI-generated summary of results")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class HybridSearchResponse(BaseResponse):
    """
    Hybrid search response with stories and members.
    
    Educational Notes:
    - Combines story and member search results
    - Provides separate sections for each type
    - Includes cross-type relevance scoring
    """
    # Story results (primary)
    story_results: List[StorySearchResult] = Field(default_factory=list, description="Story search results")
    story_total: int = Field(0, description="Total story results")
    
    # Member results (secondary)
    member_results: List[MemberSearchResult] = Field(default_factory=list, description="Member search results")
    member_total: int = Field(0, description="Total member results")
    
    # Overall metadata
    search_metadata: SearchMetadata = Field(..., description="Search execution metadata")
    
    # Hybrid scoring explanation
    hybrid_explanation: str = Field(..., description="Explanation of hybrid search strategy")
    
    # Query suggestions
    suggestions: List[str] = Field(default_factory=list, description="Search suggestions")
    
    # AI summary
    ai_summary: Optional[str] = Field(None, description="AI-generated summary of results")


class SearchSuggestion(BaseModel):
    """
    Search suggestion schema.
    
    Educational Notes:
    - Provides search query suggestions
    - Includes suggestion metadata
    - Supports different suggestion types
    """
    query: str = Field(..., description="Suggested query")
    type: str = Field(..., description="Suggestion type")
    score: float = Field(..., description="Suggestion relevance score")
    category: Optional[str] = Field(None, description="Suggestion category")
    
    # Context
    result_count: int = Field(0, description="Expected number of results")
    popular: bool = Field(False, description="Whether suggestion is popular")
    
    @validator('type')
    def validate_type(cls, v):
        valid_types = ['completion', 'correction', 'related', 'trending', 'popular']
        if v not in valid_types:
            raise ValueError(f'Suggestion type must be one of: {valid_types}')
        return v


class SearchStats(BaseModel):
    """
    Search statistics and analytics.
    
    Educational Notes:
    - Provides search performance metrics
    - Includes usage analytics
    - Supports search optimization
    """
    # Query statistics
    total_queries: int = Field(..., description="Total number of queries")
    unique_queries: int = Field(..., description="Number of unique queries")
    avg_query_length: float = Field(..., description="Average query length")
    
    # Result statistics
    avg_results_per_query: float = Field(..., description="Average results per query")
    zero_result_queries: int = Field(..., description="Number of queries with no results")
    
    # Performance metrics
    avg_response_time: float = Field(..., description="Average response time in milliseconds")
    semantic_search_usage: float = Field(..., description="Percentage of semantic searches")
    
    # Popular queries
    top_queries: List[Dict[str, Any]] = Field(default_factory=list, description="Top search queries")
    trending_queries: List[Dict[str, Any]] = Field(default_factory=list, description="Trending queries")
    
    # Content analysis
    most_searched_skills: List[str] = Field(default_factory=list, description="Most searched skills")
    most_searched_types: List[str] = Field(default_factory=list, description="Most searched content types")
    
    # Temporal analysis
    search_volume_by_hour: Dict[str, int] = Field(default_factory=dict, description="Search volume by hour")
    search_volume_by_day: Dict[str, int] = Field(default_factory=dict, description="Search volume by day")
    
    # Metadata
    period_start: datetime = Field(..., description="Statistics period start")
    period_end: datetime = Field(..., description="Statistics period end")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="When statistics were generated")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AISummaryResponse(BaseModel):
    """
    AI-generated summary response.
    
    Educational Notes:
    - Provides AI-generated search result summaries
    - Includes summary metadata and confidence
    - Supports different summary types
    """
    # Summary content
    summary: str = Field(..., description="AI-generated summary")
    key_insights: List[str] = Field(default_factory=list, description="Key insights from results")
    
    # Summary metadata
    confidence_score: float = Field(..., description="AI confidence score")
    model_used: str = Field(..., description="AI model used")
    generation_time: float = Field(..., description="Generation time in seconds")
    
    # Context
    result_count: int = Field(..., description="Number of results summarized")
    query: str = Field(..., description="Original search query")
    
    # Summary type
    summary_type: str = Field("overview", description="Type of summary generated")
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="When summary was generated")
    
    @validator('summary_type')
    def validate_summary_type(cls, v):
        valid_types = ['overview', 'detailed', 'insights', 'recommendations']
        if v not in valid_types:
            raise ValueError(f'Summary type must be one of: {valid_types}')
        return v
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SearchIndex(BaseModel):
    """
    Search index status and metadata.
    
    Educational Notes:
    - Provides search index information
    - Includes indexing statistics
    - Supports index management
    """
    # Index information
    index_name: str = Field(..., description="Search index name")
    index_type: str = Field(..., description="Index type (text, vector, hybrid)")
    
    # Statistics
    total_documents: int = Field(..., description="Total indexed documents")
    total_size: int = Field(..., description="Total index size in bytes")
    
    # Status
    status: str = Field(..., description="Index status")
    last_updated: datetime = Field(..., description="When index was last updated")
    
    # Performance
    avg_search_time: float = Field(..., description="Average search time in milliseconds")
    indexing_rate: float = Field(..., description="Documents indexed per minute")
    
    # Configuration
    settings: Dict[str, Any] = Field(default_factory=dict, description="Index settings")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }