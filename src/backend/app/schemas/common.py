"""
Common schemas shared across the API.

This module provides base schemas and utilities used throughout
the STONESOUP API for consistent data validation and responses.
"""

from typing import Any, Dict, List, Optional, Generic, TypeVar, Union
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, validator
from pydantic.generics import GenericModel

# Type variable for generic responses
T = TypeVar('T')


class SortOrder(str, Enum):
    """Sort order options for API responses."""
    ASC = "asc"
    DESC = "desc"


class StatusEnum(str, Enum):
    """Common status values across the application."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    ARCHIVED = "archived"
    DELETED = "deleted"


class BaseResponse(BaseModel):
    """
    Base response schema with common fields.
    
    Educational Notes:
    - All responses include timestamp for debugging
    - Status field indicates success/failure
    - Message provides human-readable context
    """
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="success", description="Response status")
    message: Optional[str] = Field(None, description="Human-readable message")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorResponse(BaseResponse):
    """
    Error response schema with detailed error information.
    
    Educational Notes:
    - Provides structured error information
    - Includes error code for programmatic handling
    - Details field contains specific error context
    - Maintains consistent error format across API
    """
    status: str = Field(default="error", description="Error status")
    error_code: Optional[str] = Field(None, description="Machine-readable error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    
class PaginatedResponse(GenericModel, Generic[T]):
    """
    Generic paginated response schema.
    
    Educational Notes:
    - Generic type allows reuse with any data type
    - Includes pagination metadata for frontend
    - Total count helps with pagination UI
    - Has_next/has_previous provide navigation hints
    """
    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_previous: bool = Field(..., description="Whether there are previous pages")
    
    @validator('page', pre=True)
    def validate_page(cls, v):
        if v < 1:
            raise ValueError('Page must be >= 1')
        return v
    
    @validator('page_size', pre=True)
    def validate_page_size(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Page size must be between 1 and 100')
        return v


class HealthResponse(BaseResponse):
    """
    Health check response schema.
    
    Educational Notes:
    - Provides system health information
    - Includes version and uptime details
    - Can be extended with additional metrics
    """
    version: str = Field(..., description="Application version")
    uptime: str = Field(..., description="System uptime")
    database_status: str = Field(..., description="Database connection status")
    redis_status: Optional[str] = Field(None, description="Redis connection status")
    
    
class StatusResponse(BaseResponse):
    """
    Generic status response for operations.
    
    Educational Notes:
    - Used for operations that don't return data
    - Provides operation result and context
    - Can include operation metadata
    """
    operation: str = Field(..., description="Operation that was performed")
    resource_id: Optional[str] = Field(None, description="ID of affected resource")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class SortOption(BaseModel):
    """
    Sort option for API queries.
    
    Educational Notes:
    - Provides flexible sorting configuration
    - Field validation ensures valid sort fields
    - Order validation ensures valid sort directions
    """
    field: str = Field(..., description="Field to sort by")
    order: SortOrder = Field(SortOrder.ASC, description="Sort order")
    
    @validator('field')
    def validate_field(cls, v):
        # Allow alphanumeric, underscore, and dot for nested fields
        if not v.replace('_', '').replace('.', '').isalnum():
            raise ValueError('Sort field must contain only alphanumeric characters, underscores, and dots')
        return v


class FilterOption(BaseModel):
    """
    Filter option for API queries.
    
    Educational Notes:
    - Provides flexible filtering configuration
    - Supports multiple filter operators
    - Values can be strings, numbers, or lists
    """
    field: str = Field(..., description="Field to filter by")
    operator: str = Field(..., description="Filter operator (eq, ne, gt, lt, in, contains)")
    value: Union[str, int, float, List[Union[str, int, float]]] = Field(..., description="Filter value")
    
    @validator('operator')
    def validate_operator(cls, v):
        valid_operators = ['eq', 'ne', 'gt', 'lt', 'gte', 'lte', 'in', 'contains', 'startswith', 'endswith']
        if v not in valid_operators:
            raise ValueError(f'Operator must be one of: {valid_operators}')
        return v


class SearchMetadata(BaseModel):
    """
    Search metadata for search responses.
    
    Educational Notes:
    - Provides search execution context
    - Includes performance metrics
    - Helps with search result understanding
    """
    query: str = Field(..., description="Original search query")
    execution_time_ms: float = Field(..., description="Search execution time in milliseconds")
    total_results: int = Field(..., description="Total number of results found")
    semantic_search_used: bool = Field(False, description="Whether semantic search was used")
    filters_applied: Optional[List[FilterOption]] = Field(None, description="Filters that were applied")
    sort_applied: Optional[SortOption] = Field(None, description="Sort that was applied")


class ScoreExplanation(BaseModel):
    """
    Explanation of search result scoring.
    
    Educational Notes:
    - Provides transparency into search ranking
    - Helps users understand result relevance
    - Useful for debugging search quality
    """
    text_similarity: Optional[float] = Field(None, description="Text similarity score (0-1)")
    semantic_similarity: Optional[float] = Field(None, description="Semantic similarity score (0-1)")
    recency_boost: Optional[float] = Field(None, description="Recency boost factor")
    engagement_boost: Optional[float] = Field(None, description="Engagement boost factor")
    final_score: float = Field(..., description="Final combined score")
    explanation: str = Field(..., description="Human-readable explanation")


class CauldronContext(BaseModel):
    """
    Cauldron context information for multi-tenancy.
    
    Educational Notes:
    - Provides organization context
    - Ensures data isolation
    - Includes cauldron metadata
    """
    cauldron_id: str = Field(..., description="Cauldron (organization) ID")
    cauldron_name: str = Field(..., description="Cauldron display name")
    cauldron_slug: str = Field(..., description="Cauldron URL slug")
    user_role: str = Field(..., description="User's role in the cauldron")


class APIKeyInfo(BaseModel):
    """
    API key information for authentication.
    
    Educational Notes:
    - Provides API key metadata
    - Includes usage and permissions info
    - Helps with API key management
    """
    key_id: str = Field(..., description="API key identifier")
    name: str = Field(..., description="API key display name")
    permissions: List[str] = Field(..., description="List of permissions")
    expires_at: Optional[datetime] = Field(None, description="Key expiration date")
    last_used: Optional[datetime] = Field(None, description="Last usage timestamp")
    usage_count: int = Field(0, description="Number of times used")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ValidationError(BaseModel):
    """
    Validation error details.
    
    Educational Notes:
    - Provides structured validation feedback
    - Includes field-specific error messages
    - Helps with form validation on frontend
    """
    field: str = Field(..., description="Field that failed validation")
    message: str = Field(..., description="Validation error message")
    code: str = Field(..., description="Machine-readable error code")
    value: Optional[Any] = Field(None, description="Value that caused the error")