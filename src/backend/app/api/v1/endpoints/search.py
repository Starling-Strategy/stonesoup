"""
Comprehensive search endpoints for STONESOUP with hybrid search functionality.

This module implements:
- Story-first hybrid search strategy
- Semantic search using pgvector embeddings
- AI-powered result summaries
- Multi-tenancy with automatic cauldron scoping
- Advanced filtering and sorting options

Educational Notes:
=================

Search Architecture:
- Stories are the primary searchable content (ingredients in the soup)
- Members are discovered through their stories and direct search
- Semantic similarity using OpenAI embeddings via OpenRouter
- pgvector for efficient similarity search
- Hybrid ranking combining multiple signals

Multi-Tenancy:
- Cauldron ID extracted from JWT token (no URL parameters needed)
- All searches automatically scoped to user's organization
- No explicit access checks required (handled by auth middleware)

Performance Optimizations:
- Semantic search with HNSW indexes
- Efficient pagination
- Result caching (future enhancement)
- Batch embedding generation
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.core.security import get_current_user, get_cauldron_id_from_request, CurrentUser
from app.schemas.search import (
    SearchRequest, SearchResponse, HybridSearchResponse,
    SearchType, SearchScope, SearchSort, SearchFilters,
    AISummaryResponse, SearchSuggestion
)
from app.services.search_service import search_service
from app.services.ai_summary_service import ai_summary_service, SummaryType

router = APIRouter()
logger = logging.getLogger(__name__)


class QuickSearchRequest(BaseModel):
    """Quick search request for simple queries."""
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    scope: SearchScope = Field(SearchScope.ALL, description="Search scope")
    limit: int = Field(20, ge=1, le=100, description="Maximum results")


@router.post(
    "/",
    response_model=Union[SearchResponse, HybridSearchResponse],
    summary="Advanced Search",
    description="Perform advanced search with full configuration options"
)
async def advanced_search(
    search_request: SearchRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
) -> Union[SearchResponse, HybridSearchResponse]:
    """
    Advanced search endpoint with comprehensive configuration.
    
    This endpoint implements the story-first hybrid search strategy:
    1. Semantic search on story embeddings for high-quality matches
    2. Member discovery through story associations and direct search
    3. Hybrid scoring combining semantic similarity, text relevance, and engagement
    4. AI-powered result summaries when requested
    
    Educational Notes:
    - Uses pgvector for efficient semantic search
    - Automatically generates embeddings for search queries
    - Supports multiple search types: text, semantic, and hybrid
    - Provides detailed score explanations for transparency
    - Respects multi-tenancy through cauldron context
    
    Features:
    - Semantic similarity search using OpenAI embeddings
    - Text-based full-text search with PostgreSQL
    - Hybrid ranking with engagement and recency boosts
    - Advanced filtering by skills, location, company, etc.
    - AI-generated summaries of search results
    - Search suggestions and query recommendations
    """
    try:
        # Get cauldron context from authenticated user
        cauldron_id = get_cauldron_id_from_request(request)
        if not cauldron_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cauldron context not found"
            )
        
        logger.info(f"Advanced search initiated: query='{search_request.query}', scope={search_request.scope}, user={current_user.user_id}")
        
        # Execute search using the search service
        search_result = await search_service.search(
            db=db,
            search_request=search_request,
            cauldron_id=cauldron_id,
            current_user_id=current_user.user_id
        )
        
        logger.info(f"Search completed: {search_result.search_metadata.total_results} results in {search_result.search_metadata.execution_time_ms:.2f}ms")
        
        return search_result
        
    except Exception as e:
        logger.error(f"Advanced search failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.post(
    "/quick",
    response_model=HybridSearchResponse,
    summary="Quick Search",
    description="Simple search interface for basic queries"
)
async def quick_search(
    search_request: QuickSearchRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
) -> HybridSearchResponse:
    """
    Quick search endpoint for simple queries.
    
    Educational Notes:
    - Simplified interface for basic search needs
    - Uses sensible defaults for search configuration
    - Always returns hybrid response for consistent UX
    - Optimized for speed and simplicity
    
    This endpoint is ideal for:
    - Search bars in the UI
    - Quick talent discovery
    - Mobile applications
    - Embedded search widgets
    """
    try:
        cauldron_id = get_cauldron_id_from_request(request)
        if not cauldron_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cauldron context not found"
            )
        
        # Create full search request with defaults
        full_request = SearchRequest(
            query=search_request.query,
            search_type=SearchType.HYBRID,  # Default to hybrid for best results
            scope=search_request.scope,
            page=1,
            page_size=search_request.limit,
            sort=SearchSort.RELEVANCE,
            semantic_threshold=0.7,
            boost_recent=True,
            boost_popular=True,
            generate_summary=True,  # Always generate summary for quick search
            include_suggestions=True,
            include_highlights=True
        )
        
        logger.info(f"Quick search: query='{search_request.query}', scope={search_request.scope}")
        
        result = await search_service.search(
            db=db,
            search_request=full_request,
            cauldron_id=cauldron_id,
            current_user_id=current_user.user_id
        )
        
        # Ensure we return a HybridSearchResponse
        if isinstance(result, HybridSearchResponse):
            return result
        else:
            # Convert SearchResponse to HybridSearchResponse
            story_results = [r for r in result.results if r.type == "story"]
            member_results = [r for r in result.results if r.type == "member"]
            
            return HybridSearchResponse(
                story_results=story_results,
                story_total=result.result_counts.get("stories", 0),
                member_results=member_results,
                member_total=result.result_counts.get("members", 0),
                search_metadata=result.search_metadata,
                hybrid_explanation=f"Quick search found {result.total} results using hybrid strategy",
                suggestions=result.suggestions or [],
                ai_summary=result.ai_summary
            )
        
    except Exception as e:
        logger.error(f"Quick search failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quick search failed: {str(e)}"
        )


@router.get(
    "/suggestions",
    response_model=List[SearchSuggestion],
    summary="Search Suggestions",
    description="Get intelligent search suggestions based on partial query"
)
async def get_search_suggestions(
    q: str = Query(..., min_length=1, max_length=100, description="Partial search query"),
    limit: int = Query(10, ge=1, le=20, description="Maximum number of suggestions"),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
) -> List[SearchSuggestion]:
    """
    Get intelligent search suggestions based on partial query.
    
    Educational Notes:
    - Provides real-time search suggestions
    - Uses autocomplete and query expansion
    - Analyzes popular searches and content
    - Supports different suggestion types
    
    Suggestion Types:
    - completion: Auto-complete based on popular queries
    - correction: Spelling corrections
    - related: Related search terms
    - trending: Currently popular searches
    - popular: Historically popular searches
    """
    try:
        cauldron_id = get_cauldron_id_from_request(request)
        if not cauldron_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cauldron context not found"
            )
        
        # For now, return basic suggestions
        # TODO: Implement full suggestion logic in search service
        suggestions = [
            SearchSuggestion(
                query=f"{q} developer",
                type="completion",
                score=0.9,
                category="skills",
                result_count=25,
                popular=True
            ),
            SearchSuggestion(
                query=f"{q} engineer",
                type="completion", 
                score=0.8,
                category="roles",
                result_count=18,
                popular=True
            ),
            SearchSuggestion(
                query=f"{q} python",
                type="related",
                score=0.7,
                category="technologies",
                result_count=12,
                popular=False
            )
        ]
        
        return suggestions[:limit]
        
    except Exception as e:
        logger.error(f"Search suggestions failed: {e}")
        return []


@router.post(
    "/summary",
    response_model=AISummaryResponse,
    summary="Generate Search Summary",
    description="Generate AI-powered summary of search results"
)
async def generate_search_summary(
    search_request: SearchRequest,
    summary_type: SummaryType = Query(SummaryType.OVERVIEW, description="Type of summary to generate"),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
) -> AISummaryResponse:
    """
    Generate AI-powered summary of search results.
    
    Educational Notes:
    - Provides intelligent analysis of search results
    - Helps users quickly understand talent landscape
    - Supports different summary types for different use cases
    - Uses advanced AI to extract insights and patterns
    
    Summary Types:
    - overview: Concise overview of available talent
    - detailed: Comprehensive analysis with specific examples
    - insights: Key insights and patterns in the talent pool
    - recommendations: Actionable recommendations for talent acquisition
    """
    try:
        cauldron_id = get_cauldron_id_from_request(request)
        if not cauldron_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cauldron context not found"
            )
        
        # Execute search first to get results
        search_result = await search_service.search(
            db=db,
            search_request=search_request,
            cauldron_id=cauldron_id,
            current_user_id=current_user.user_id
        )
        
        # Extract story and member results
        if isinstance(search_result, HybridSearchResponse):
            story_results = search_result.story_results
            member_results = search_result.member_results
        else:
            story_results = [r for r in search_result.results if r.type == "story"]
            member_results = [r for r in search_result.results if r.type == "member"]
        
        # Generate summary
        summary = await ai_summary_service.generate_search_summary(
            query=search_request.query,
            story_results=story_results,
            member_results=member_results,
            summary_type=summary_type
        )
        
        return summary
        
    except Exception as e:
        logger.error(f"Search summary generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Summary generation failed: {str(e)}"
        )


@router.get(
    "/analytics",
    response_model=Dict[str, Any],
    summary="Search Analytics",
    description="Get search analytics and insights for the cauldron"
)
async def get_search_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get search analytics and insights for the cauldron.
    
    Educational Notes:
    - Provides insights into search patterns and usage
    - Helps understand what talent is being sought
    - Identifies trends in skill demand
    - Supports strategic talent planning
    
    Analytics Include:
    - Popular search queries
    - Trending skills and roles
    - Search success rates
    - User engagement patterns
    - Content performance metrics
    """
    try:
        cauldron_id = get_cauldron_id_from_request(request)
        if not cauldron_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cauldron context not found"
            )
        
        # TODO: Implement search analytics collection and analysis
        # For now, return placeholder data
        analytics = {
            "period_days": days,
            "total_searches": 1247,
            "unique_queries": 892,
            "avg_results_per_search": 8.3,
            "success_rate": 0.87,
            "top_queries": [
                {"query": "python developer", "count": 45, "success_rate": 0.92},
                {"query": "react engineer", "count": 38, "success_rate": 0.89},
                {"query": "data scientist", "count": 32, "success_rate": 0.85}
            ],
            "trending_skills": [
                {"skill": "Python", "growth": 0.23},
                {"skill": "React", "growth": 0.18},
                {"skill": "Machine Learning", "growth": 0.31}
            ],
            "search_volume_by_day": {
                "2024-01-01": 42,
                "2024-01-02": 38,
                "2024-01-03": 51
            },
            "cauldron_id": cauldron_id,
            "generated_at": "2024-01-01T12:00:00Z"
        }
        
        return analytics
        
    except Exception as e:
        logger.error(f"Search analytics failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analytics failed: {str(e)}"
        )


# Legacy endpoints for backward compatibility
@router.get(
    "/members",
    response_model=SearchResponse,
    summary="Search Members (Legacy)",
    description="Legacy endpoint for member search - use /quick or / instead"
)
async def search_members_legacy(
    q: str = Query(..., min_length=1, description="Search query"),
    skip: int = Query(0, ge=0, description="Number of results to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
) -> SearchResponse:
    """Legacy member search endpoint."""
    cauldron_id = get_cauldron_id_from_request(request)
    
    search_request = SearchRequest(
        query=q,
        search_type=SearchType.HYBRID,
        scope=SearchScope.MEMBERS,
        page=(skip // limit) + 1,
        page_size=limit
    )
    
    return await search_service.search(
        db=db,
        search_request=search_request,
        cauldron_id=cauldron_id,
        current_user_id=current_user.user_id
    )


@router.get(
    "/stories",
    response_model=SearchResponse,
    summary="Search Stories (Legacy)",
    description="Legacy endpoint for story search - use /quick or / instead"
)
async def search_stories_legacy(
    q: str = Query(..., min_length=1, description="Search query"),
    skip: int = Query(0, ge=0, description="Number of results to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
) -> SearchResponse:
    """Legacy story search endpoint."""
    cauldron_id = get_cauldron_id_from_request(request)
    
    search_request = SearchRequest(
        query=q,
        search_type=SearchType.HYBRID,
        scope=SearchScope.STORIES,
        page=(skip // limit) + 1,
        page_size=limit
    )
    
    return await search_service.search(
        db=db,
        search_request=search_request,
        cauldron_id=cauldron_id,
        current_user_id=current_user.user_id
    )