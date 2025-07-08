"""
Pydantic schemas for API request/response validation.

This module provides comprehensive data validation and serialization
for all API endpoints in STONESOUP.
"""

from .search import (
    SearchRequest,
    SearchResponse,
    SearchResult,
    SearchSuggestion,
    SearchFilters,
    SearchSort,
    SearchStats,
    MemberSearchResult,
    StorySearchResult,
    HybridSearchResponse,
    AISummaryResponse,
)

from .member import (
    MemberCreate,
    MemberUpdate,
    MemberResponse,
    MemberList,
    MemberProfile,
    MemberAnalytics,
)

from .story import (
    StoryCreate,
    StoryUpdate,
    StoryResponse,
    StoryList,
    StoryContent,
    StoryAnalytics,
)

from .common import (
    BaseResponse,
    ErrorResponse,
    PaginatedResponse,
    HealthResponse,
    StatusResponse,
)

__all__ = [
    # Search schemas
    "SearchRequest",
    "SearchResponse", 
    "SearchResult",
    "SearchSuggestion",
    "SearchFilters",
    "SearchSort",
    "SearchStats",
    "MemberSearchResult",
    "StorySearchResult",
    "HybridSearchResponse",
    "AISummaryResponse",
    
    # Member schemas
    "MemberCreate",
    "MemberUpdate",
    "MemberResponse",
    "MemberList",
    "MemberProfile",
    "MemberAnalytics",
    
    # Story schemas
    "StoryCreate",
    "StoryUpdate",
    "StoryResponse",
    "StoryList",
    "StoryContent",
    "StoryAnalytics",
    
    # Common schemas
    "BaseResponse",
    "ErrorResponse",
    "PaginatedResponse",
    "HealthResponse",
    "StatusResponse",
]