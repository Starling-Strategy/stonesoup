"""
Search service for STONESOUP with hybrid search functionality.

This service implements the story-first search strategy:
1. Semantic search on story embeddings (primary)
2. Member profile search (secondary) 
3. Hybrid scoring and ranking
4. AI-powered result summaries

Educational Notes:
=================

Hybrid Search Strategy:
- Stories are the primary content type (ingredients in the soup)
- Members are discovered through their stories
- Semantic similarity using pgvector for high-quality matches
- Text search fallback for broader coverage
- Recency and engagement boosts for relevance

pgvector Integration:
- Uses cosine similarity for semantic search
- HNSW index for fast vector similarity search
- Embedding generation via OpenRouter
- Efficient batch processing for large result sets
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import text, func, and_, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.sql import select

from app.models.story import Story, StoryStatus, StoryType
from app.models.member import Member
from app.models.cauldron import Cauldron
from app.schemas.search import (
    SearchRequest, SearchResponse, SearchResult, 
    MemberSearchResult, StorySearchResult, HybridSearchResponse,
    SearchType, SearchScope, SearchSort, SearchMetadata, ScoreExplanation
)
from app.schemas.member import MemberResponse
from app.schemas.story import StoryResponse
from app.ai.openrouter_client import openrouter_client
from app.core.config import settings

logger = logging.getLogger(__name__)


class SearchService:
    """
    Comprehensive search service implementing hybrid search.
    
    This service provides:
    - Semantic search using pgvector embeddings
    - Text-based search using PostgreSQL full-text search
    - Hybrid ranking combining multiple signals
    - Member discovery through story associations
    - AI-powered result summarization
    
    Architecture Philosophy:
    - Stories are the primary searchable content
    - Members are discovered through their stories
    - Semantic similarity provides high-quality matches
    - Multiple ranking signals ensure relevance
    """
    
    def __init__(self):
        self.logger = logger
        
    async def search(
        self,
        db: AsyncSession,
        search_request: SearchRequest,
        cauldron_id: str,
        current_user_id: Optional[str] = None
    ) -> Union[SearchResponse, HybridSearchResponse]:
        """
        Main search entry point with comprehensive search logic.
        
        Educational Notes:
        - Implements story-first search strategy
        - Uses semantic search for high-quality matches
        - Falls back to text search for broader coverage
        - Combines multiple ranking signals
        - Supports different search scopes and types
        
        Args:
            db: Database session
            search_request: Search configuration
            cauldron_id: Organization context
            current_user_id: Current user for personalization
            
        Returns:
            Search response with ranked results
        """
        start_time = time.time()
        
        try:
            # Generate query embedding for semantic search
            query_embedding = None
            if search_request.search_type in [SearchType.SEMANTIC, SearchType.HYBRID]:
                try:
                    query_embedding = await openrouter_client.generate_embedding(
                        search_request.query
                    )
                    self.logger.info(f"Generated query embedding for: {search_request.query}")
                except Exception as e:
                    self.logger.warning(f"Failed to generate embedding: {e}")
                    # Fall back to text search
                    if search_request.search_type == SearchType.SEMANTIC:
                        search_request.search_type = SearchType.TEXT
            
            # Execute search based on scope
            if search_request.scope == SearchScope.STORIES:
                story_results, story_total = await self._search_stories(
                    db, search_request, cauldron_id, query_embedding
                )
                member_results, member_total = [], 0
                
            elif search_request.scope == SearchScope.MEMBERS:
                member_results, member_total = await self._search_members(
                    db, search_request, cauldron_id, query_embedding
                )
                story_results, story_total = [], 0
                
            else:  # SearchScope.ALL
                # Story-first hybrid search
                story_results, story_total = await self._search_stories(
                    db, search_request, cauldron_id, query_embedding
                )
                
                # Discover members through stories and direct member search
                member_results, member_total = await self._search_members_hybrid(
                    db, search_request, cauldron_id, query_embedding, story_results
                )
            
            # Generate AI summary if requested
            ai_summary = None
            if search_request.generate_summary:
                ai_summary = await self._generate_search_summary(
                    search_request.query, story_results, member_results
                )
            
            # Generate search suggestions
            suggestions = []
            if search_request.include_suggestions:
                suggestions = await self._generate_suggestions(
                    db, search_request.query, cauldron_id
                )
            
            # Create search metadata
            execution_time = (time.time() - start_time) * 1000
            search_metadata = SearchMetadata(
                query=search_request.query,
                execution_time_ms=execution_time,
                total_results=story_total + member_total,
                semantic_search_used=query_embedding is not None,
                filters_applied=self._extract_applied_filters(search_request.filters),
                sort_applied=None  # TODO: Add sort metadata
            )
            
            # Return appropriate response type
            if search_request.scope == SearchScope.ALL:
                return HybridSearchResponse(
                    story_results=story_results,
                    story_total=story_total,
                    member_results=member_results,
                    member_total=member_total,
                    search_metadata=search_metadata,
                    hybrid_explanation=self._generate_hybrid_explanation(
                        story_total, member_total, query_embedding is not None
                    ),
                    suggestions=suggestions,
                    ai_summary=ai_summary
                )
            else:
                # Combine results for unified response
                all_results = story_results + member_results
                total = story_total + member_total
                
                return SearchResponse(
                    results=all_results,
                    total=total,
                    page=search_request.page,
                    page_size=search_request.page_size,
                    has_next=self._calculate_has_next(search_request, total),
                    has_previous=search_request.page > 1,
                    search_metadata=search_metadata,
                    result_counts={
                        "stories": story_total,
                        "members": member_total
                    },
                    suggestions=suggestions,
                    ai_summary=ai_summary
                )
                
        except Exception as e:
            self.logger.error(f"Search failed: {e}", exc_info=True)
            raise
    
    async def _search_stories(
        self,
        db: AsyncSession,
        search_request: SearchRequest,
        cauldron_id: str,
        query_embedding: Optional[List[float]] = None
    ) -> Tuple[List[StorySearchResult], int]:
        """
        Search stories using hybrid semantic and text search.
        
        Educational Notes:
        - Primary search function for story content
        - Uses pgvector for semantic similarity
        - Combines with text search for comprehensive coverage
        - Applies boost factors for engagement and recency
        - Respects multi-tenancy through cauldron filtering
        
        Search Strategy:
        1. Semantic search using story embeddings (if available)
        2. Text search using PostgreSQL full-text search
        3. Combine and rank results using multiple signals
        4. Apply filters and sorting
        5. Paginate results
        """
        try:
            # Calculate offset for pagination
            offset = (search_request.page - 1) * search_request.page_size
            
            # Build base query with multi-tenancy
            base_query = select(Story).where(
                and_(
                    Story.cauldron_id == cauldron_id,
                    Story.status == StoryStatus.PUBLISHED  # Only published stories
                )
            ).options(
                selectinload(Story.members)  # Load associated members
            )
            
            # Apply filters
            if search_request.filters:
                base_query = self._apply_story_filters(base_query, search_request.filters)
            
            # Execute semantic search if embedding available
            semantic_results = []
            if query_embedding and search_request.search_type in [SearchType.SEMANTIC, SearchType.HYBRID]:
                semantic_results = await self._semantic_search_stories(
                    db, base_query, query_embedding, search_request
                )
            
            # Execute text search
            text_results = []
            if search_request.search_type in [SearchType.TEXT, SearchType.HYBRID]:
                text_results = await self._text_search_stories(
                    db, base_query, search_request.query, search_request
                )
            
            # Combine and rank results
            combined_results = self._combine_story_results(
                semantic_results, text_results, search_request
            )
            
            # Apply sorting
            sorted_results = self._sort_story_results(combined_results, search_request.sort)
            
            # Get total count (before pagination)
            total_count = len(sorted_results)
            
            # Apply pagination
            paginated_results = sorted_results[offset:offset + search_request.page_size]
            
            # Convert to response objects
            story_search_results = []
            for story, score, explanation in paginated_results:
                # Create story response
                story_response = self._story_to_response(story)
                
                # Create search result
                result = StorySearchResult(
                    id=str(story.id),
                    type="story",
                    title=story.title,
                    content=story.summary or story.content[:200] + "...",
                    score=score,
                    score_explanation=explanation if search_request.explain_scores else None,
                    highlights=self._generate_highlights(story, search_request.query) if search_request.include_highlights else None,
                    created_at=story.created_at,
                    updated_at=story.updated_at,
                    cauldron_id=cauldron_id,
                    story=story_response,
                    content_quality=self._calculate_content_quality(story),
                    engagement_score=self._calculate_engagement_score(story),
                    recency_score=self._calculate_recency_score(story),
                    member_names=[member.name for member in story.members],
                    skill_matches=self._find_skill_matches(story, search_request.query)
                )
                
                story_search_results.append(result)
            
            self.logger.info(f"Story search completed: {len(story_search_results)} results")
            return story_search_results, total_count
            
        except Exception as e:
            self.logger.error(f"Story search failed: {e}", exc_info=True)
            return [], 0
    
    async def _semantic_search_stories(
        self,
        db: AsyncSession,
        base_query,
        query_embedding: List[float],
        search_request: SearchRequest
    ) -> List[Tuple[Story, float, ScoreExplanation]]:
        """
        Perform semantic search using pgvector similarity.
        
        Educational Notes:
        - Uses cosine similarity for semantic matching
        - Leverages HNSW index for fast vector search
        - Filters by similarity threshold
        - Provides transparency in scoring
        
        pgvector Query Structure:
        - embedding <=> %s::vector  (cosine distance operator)
        - ORDER BY embedding <=> %s::vector  (sort by similarity)
        - WHERE 1 - (embedding <=> %s::vector) >= threshold
        """
        try:
            # Convert embedding to string format for pgvector
            embedding_str = f"[{','.join(map(str, query_embedding))}]"
            
            # Build semantic search query
            semantic_query = base_query.where(
                Story.embedding.isnot(None)  # Only stories with embeddings
            ).where(
                # Similarity threshold filter (cosine similarity >= threshold)
                text(f"1 - (embedding <=> '{embedding_str}'::vector) >= :threshold")
            ).bind(
                threshold=search_request.semantic_threshold or 0.7
            ).order_by(
                # Order by similarity (closest first)
                text(f"embedding <=> '{embedding_str}'::vector")
            ).limit(50)  # Reasonable limit for semantic search
            
            result = await db.execute(semantic_query)
            stories = result.scalars().all()
            
            # Calculate similarity scores and explanations
            semantic_results = []
            for story in stories:
                if story.embedding:
                    # Calculate cosine similarity
                    similarity = await self._calculate_cosine_similarity(
                        query_embedding, story.embedding
                    )
                    
                    # Create score explanation
                    explanation = ScoreExplanation(
                        semantic_similarity=similarity,
                        recency_boost=self._calculate_recency_boost(story),
                        engagement_boost=self._calculate_engagement_boost(story),
                        final_score=similarity,  # Will be adjusted later
                        explanation=f"Semantic similarity: {similarity:.3f}, high relevance match"
                    )
                    
                    semantic_results.append((story, similarity, explanation))
            
            self.logger.info(f"Semantic search found {len(semantic_results)} results")
            return semantic_results
            
        except Exception as e:
            self.logger.error(f"Semantic search failed: {e}", exc_info=True)
            return []
    
    async def _text_search_stories(
        self,
        db: AsyncSession,
        base_query,
        query: str,
        search_request: SearchRequest
    ) -> List[Tuple[Story, float, ScoreExplanation]]:
        """
        Perform text-based search using PostgreSQL full-text search.
        
        Educational Notes:
        - Uses PostgreSQL's built-in full-text search
        - Searches across title, content, and tags
        - Provides relevance ranking via ts_rank
        - Supports phrase and wildcard queries
        """
        try:
            # Prepare search query for PostgreSQL
            search_query = self._prepare_search_query(query)
            
            # Build text search query
            text_query = base_query.where(
                or_(
                    # Search in title
                    text(f"to_tsvector('english', title) @@ plainto_tsquery('english', :query)"),
                    # Search in content
                    text(f"to_tsvector('english', content) @@ plainto_tsquery('english', :query)"),
                    # Search in tags (if they exist)
                    text(f"to_tsvector('english', array_to_string(tags, ' ')) @@ plainto_tsquery('english', :query)")
                )
            ).bind(query=search_query)
            
            # Add ranking
            text_query = text_query.add_columns(
                # Calculate text search rank
                text(f"ts_rank(to_tsvector('english', title || ' ' || content), plainto_tsquery('english', :query)) as text_rank")
            ).bind(query=search_query)
            
            result = await db.execute(text_query)
            rows = result.fetchall()
            
            # Process results
            text_results = []
            for row in rows:
                story = row[0]
                text_rank = float(row[1]) if row[1] else 0.0
                
                # Create score explanation
                explanation = ScoreExplanation(
                    text_similarity=text_rank,
                    recency_boost=self._calculate_recency_boost(story),
                    engagement_boost=self._calculate_engagement_boost(story),
                    final_score=text_rank,  # Will be adjusted later
                    explanation=f"Text relevance: {text_rank:.3f}, keyword match"
                )
                
                text_results.append((story, text_rank, explanation))
            
            self.logger.info(f"Text search found {len(text_results)} results")
            return text_results
            
        except Exception as e:
            self.logger.error(f"Text search failed: {e}", exc_info=True)
            return []
    
    async def _search_members_hybrid(
        self,
        db: AsyncSession,
        search_request: SearchRequest,
        cauldron_id: str,
        query_embedding: Optional[List[float]],
        story_results: List[StorySearchResult]
    ) -> Tuple[List[MemberSearchResult], int]:
        """
        Hybrid member search: discover through stories + direct search.
        
        Educational Notes:
        - Story-first approach: find members through their stories
        - Direct member search for broader coverage
        - Deduplicate and rank combined results
        - Emphasizes members with relevant stories
        """
        try:
            # Extract members from story results (story-first discovery)
            story_member_ids = set()
            member_story_map = {}
            
            for story_result in story_results:
                for member_id in story_result.story.member_ids:
                    story_member_ids.add(member_id)
                    if member_id not in member_story_map:
                        member_story_map[member_id] = []
                    member_story_map[member_id].append(story_result)
            
            # Direct member search
            direct_members, direct_total = await self._search_members(
                db, search_request, cauldron_id, query_embedding
            )
            
            # Combine and deduplicate
            all_members = {}
            
            # Add story-discovered members with boost
            for member_id in story_member_ids:
                member = await self._get_member_by_id(db, member_id, cauldron_id)
                if member:
                    relevance_boost = len(member_story_map[member_id]) * 0.1
                    score = 0.8 + relevance_boost  # High base score for story association
                    
                    explanation = ScoreExplanation(
                        semantic_similarity=None,
                        engagement_boost=relevance_boost,
                        final_score=score,
                        explanation=f"Discovered through {len(member_story_map[member_id])} relevant stories"
                    )
                    
                    all_members[member_id] = (member, score, explanation, member_story_map[member_id])
            
            # Add direct search results
            for member_result in direct_members:
                member_id = member_result.member.id
                if member_id not in all_members:
                    # Get full member object
                    member = await self._get_member_by_id(db, member_id, cauldron_id)
                    if member:
                        all_members[member_id] = (
                            member, 
                            member_result.score, 
                            member_result.score_explanation, 
                            []
                        )
            
            # Convert to member search results
            member_search_results = []
            for member_id, (member, score, explanation, related_stories) in all_members.items():
                member_response = self._member_to_response(member)
                
                result = MemberSearchResult(
                    id=str(member.id),
                    type="member",
                    title=member.name,
                    content=member.bio or f"{member.title} at {member.company}" if member.title and member.company else "Member profile",
                    score=score,
                    score_explanation=explanation if search_request.explain_scores else None,
                    highlights=self._generate_member_highlights(member, search_request.query) if search_request.include_highlights else None,
                    created_at=member.created_at,
                    updated_at=member.updated_at,
                    cauldron_id=cauldron_id,
                    member=member_response,
                    profile_completeness=self._calculate_profile_completeness(member),
                    skill_match=self._calculate_skill_match(member, search_request.query),
                    experience_relevance=self._calculate_experience_relevance(member, search_request.query),
                    availability_status="available" if member.is_available else "unavailable",
                    last_active=member.last_active_at
                )
                
                member_search_results.append(result)
            
            # Sort by score
            member_search_results.sort(key=lambda x: x.score, reverse=True)
            
            # Apply pagination
            offset = (search_request.page - 1) * search_request.page_size
            total_count = len(member_search_results)
            paginated_results = member_search_results[offset:offset + search_request.page_size]
            
            self.logger.info(f"Hybrid member search completed: {len(paginated_results)} results")
            return paginated_results, total_count
            
        except Exception as e:
            self.logger.error(f"Hybrid member search failed: {e}", exc_info=True)
            return [], 0
    
    async def _search_members(
        self,
        db: AsyncSession,
        search_request: SearchRequest,
        cauldron_id: str,
        query_embedding: Optional[List[float]] = None
    ) -> Tuple[List[MemberSearchResult], int]:
        """
        Direct member search using profile information.
        
        Educational Notes:
        - Searches member profiles directly
        - Uses both semantic and text search
        - Considers skills, bio, and professional information
        - Respects member status and availability
        """
        try:
            # Calculate offset for pagination
            offset = (search_request.page - 1) * search_request.page_size
            
            # Build base query
            base_query = select(Member).where(
                and_(
                    Member.cauldron_id == cauldron_id,
                    Member.is_active == True  # Only active members
                )
            )
            
            # Apply filters
            if search_request.filters:
                base_query = self._apply_member_filters(base_query, search_request.filters)
            
            # Execute semantic search if embedding available
            semantic_results = []
            if query_embedding and search_request.search_type in [SearchType.SEMANTIC, SearchType.HYBRID]:
                semantic_results = await self._semantic_search_members(
                    db, base_query, query_embedding, search_request
                )
            
            # Execute text search
            text_results = []
            if search_request.search_type in [SearchType.TEXT, SearchType.HYBRID]:
                text_results = await self._text_search_members(
                    db, base_query, search_request.query, search_request
                )
            
            # Combine and rank results
            combined_results = self._combine_member_results(
                semantic_results, text_results, search_request
            )
            
            # Apply sorting
            sorted_results = self._sort_member_results(combined_results, search_request.sort)
            
            # Get total count
            total_count = len(sorted_results)
            
            # Apply pagination
            paginated_results = sorted_results[offset:offset + search_request.page_size]
            
            # Convert to response objects
            member_search_results = []
            for member, score, explanation in paginated_results:
                member_response = self._member_to_response(member)
                
                result = MemberSearchResult(
                    id=str(member.id),
                    type="member",
                    title=member.name,
                    content=member.bio or f"{member.title} at {member.company}" if member.title and member.company else "Member profile",
                    score=score,
                    score_explanation=explanation if search_request.explain_scores else None,
                    highlights=self._generate_member_highlights(member, search_request.query) if search_request.include_highlights else None,
                    created_at=member.created_at,
                    updated_at=member.updated_at,
                    cauldron_id=cauldron_id,
                    member=member_response,
                    profile_completeness=self._calculate_profile_completeness(member),
                    skill_match=self._calculate_skill_match(member, search_request.query),
                    experience_relevance=self._calculate_experience_relevance(member, search_request.query),
                    availability_status="available" if member.is_available else "unavailable",
                    last_active=member.last_active_at
                )
                
                member_search_results.append(result)
            
            self.logger.info(f"Member search completed: {len(member_search_results)} results")
            return member_search_results, total_count
            
        except Exception as e:
            self.logger.error(f"Member search failed: {e}", exc_info=True)
            return [], 0
    
    # Helper methods for search functionality
    
    def _combine_story_results(
        self,
        semantic_results: List,
        text_results: List,
        search_request: SearchRequest
    ) -> List[Tuple[Story, float, ScoreExplanation]]:
        """Combine semantic and text search results with hybrid scoring."""
        if search_request.search_type == SearchType.SEMANTIC:
            return semantic_results
        elif search_request.search_type == SearchType.TEXT:
            return text_results
        
        # Hybrid combination
        results_map = {}
        
        # Add semantic results with high weight
        for story, score, explanation in semantic_results:
            story_id = str(story.id)
            weighted_score = score * 0.7  # 70% weight for semantic
            explanation.final_score = weighted_score
            results_map[story_id] = (story, weighted_score, explanation)
        
        # Add text results with lower weight, combining if already exists
        for story, score, explanation in text_results:
            story_id = str(story.id)
            weighted_score = score * 0.3  # 30% weight for text
            
            if story_id in results_map:
                # Combine scores
                existing_story, existing_score, existing_explanation = results_map[story_id]
                combined_score = existing_score + weighted_score
                existing_explanation.text_similarity = score
                existing_explanation.final_score = combined_score
                existing_explanation.explanation += f" + text match ({score:.3f})"
                results_map[story_id] = (existing_story, combined_score, existing_explanation)
            else:
                explanation.final_score = weighted_score
                results_map[story_id] = (story, weighted_score, explanation)
        
        return list(results_map.values())
    
    def _combine_member_results(
        self,
        semantic_results: List,
        text_results: List,
        search_request: SearchRequest
    ) -> List[Tuple[Member, float, ScoreExplanation]]:
        """Combine semantic and text member search results."""
        # Similar logic to story combination
        if search_request.search_type == SearchType.SEMANTIC:
            return semantic_results
        elif search_request.search_type == SearchType.TEXT:
            return text_results
        
        # Hybrid combination
        results_map = {}
        
        for member, score, explanation in semantic_results:
            member_id = str(member.id)
            weighted_score = score * 0.7
            explanation.final_score = weighted_score
            results_map[member_id] = (member, weighted_score, explanation)
        
        for member, score, explanation in text_results:
            member_id = str(member.id)
            weighted_score = score * 0.3
            
            if member_id in results_map:
                existing_member, existing_score, existing_explanation = results_map[member_id]
                combined_score = existing_score + weighted_score
                existing_explanation.text_similarity = score
                existing_explanation.final_score = combined_score
                existing_explanation.explanation += f" + text match ({score:.3f})"
                results_map[member_id] = (existing_member, combined_score, existing_explanation)
            else:
                explanation.final_score = weighted_score
                results_map[member_id] = (member, weighted_score, explanation)
        
        return list(results_map.values())
    
    def _sort_story_results(self, results: List, sort: SearchSort) -> List:
        """Sort story results based on sort criteria."""
        if sort == SearchSort.RELEVANCE:
            return sorted(results, key=lambda x: x[1], reverse=True)  # Sort by score
        elif sort == SearchSort.RECENT:
            return sorted(results, key=lambda x: x[0].created_at, reverse=True)
        elif sort == SearchSort.POPULAR:
            return sorted(results, key=lambda x: x[0].view_count + x[0].like_count, reverse=True)
        elif sort == SearchSort.ALPHABETICAL:
            return sorted(results, key=lambda x: x[0].title.lower())
        return results
    
    def _sort_member_results(self, results: List, sort: SearchSort) -> List:
        """Sort member results based on sort criteria."""
        if sort == SearchSort.RELEVANCE:
            return sorted(results, key=lambda x: x[1], reverse=True)
        elif sort == SearchSort.RECENT:
            return sorted(results, key=lambda x: x[0].created_at, reverse=True)
        elif sort == SearchSort.ALPHABETICAL:
            return sorted(results, key=lambda x: x[0].name.lower())
        return results
    
    # Additional helper methods would continue here...
    # (Content scoring, filtering, highlighting, etc.)
    
    async def _calculate_cosine_similarity(
        self, 
        embedding1: List[float], 
        embedding2: List[float]
    ) -> float:
        """Calculate cosine similarity between two embeddings."""
        import numpy as np
        
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def _story_to_response(self, story: Story) -> StoryResponse:
        """Convert Story model to StoryResponse schema."""
        return StoryResponse(
            id=str(story.id),
            title=story.title,
            content=story.content,
            summary=story.summary,
            story_type=story.story_type,
            status=story.status,
            tags=story.tags or [],
            skills_demonstrated=story.skills_demonstrated or [],
            occurred_at=story.occurred_at,
            published_at=story.published_at,
            external_url=story.external_url,
            company=story.company,
            ai_generated=story.ai_generated,
            confidence_score=story.confidence_score,
            view_count=story.view_count,
            like_count=story.like_count,
            has_embedding=story.embedding is not None,
            is_published=story.status == StoryStatus.PUBLISHED,
            is_editable=story.status in [StoryStatus.DRAFT, StoryStatus.REJECTED],
            created_at=story.created_at,
            updated_at=story.updated_at,
            cauldron_id=str(story.cauldron_id),
            member_ids=[str(member.id) for member in story.members],
            members=[{
                "id": str(member.id),
                "name": member.name,
                "email": member.email
            } for member in story.members],
            reviewed_by_id=str(story.reviewed_by_id) if story.reviewed_by_id else None,
            reviewed_at=story.reviewed_at
        )
    
    def _member_to_response(self, member: Member) -> MemberResponse:
        """Convert Member model to MemberResponse schema."""
        return MemberResponse(
            id=str(member.id),
            email=member.email,
            name=member.name,
            username=member.username,
            bio=member.bio,
            location=member.location,
            timezone=member.timezone,
            avatar_url=member.avatar_url,
            title=member.title,
            company=member.company,
            years_of_experience=member.years_of_experience,
            hourly_rate=member.hourly_rate,
            skills=member.skills or [],
            expertise_areas=member.expertise_areas or [],
            industries=member.industries or [],
            linkedin_url=member.linkedin_url,
            github_url=member.github_url,
            twitter_url=member.twitter_url,
            website_url=member.website_url,
            portfolio_urls=member.portfolio_urls or [],
            is_active=member.is_active,
            is_verified=member.is_verified,
            is_available=member.is_available,
            profile_completed=member.profile_completed,
            has_embedding=member.profile_embedding is not None,
            created_at=member.created_at,
            updated_at=member.updated_at,
            last_active_at=member.last_active_at,
            cauldron_id=str(member.cauldron_id),
            profile_url=f"/{member.username}" if member.username else None,
            story_count=len(member.member_stories) if member.member_stories else 0
        )
    
    # Placeholder methods for additional functionality
    def _calculate_content_quality(self, story: Story) -> float:
        """Calculate content quality score."""
        return 0.8  # Placeholder
    
    def _calculate_engagement_score(self, story: Story) -> float:
        """Calculate engagement score."""
        return (story.view_count + story.like_count * 2) / 100.0
    
    def _calculate_recency_score(self, story: Story) -> float:
        """Calculate recency score."""
        days_old = (datetime.utcnow() - story.created_at).days
        return max(0, 1 - (days_old / 365))  # Decay over a year
    
    def _calculate_profile_completeness(self, member: Member) -> float:
        """Calculate profile completeness score."""
        return 0.9 if member.profile_completed else 0.5  # Placeholder
    
    def _calculate_skill_match(self, member: Member, query: str) -> float:
        """Calculate skill match score."""
        return 0.7  # Placeholder
    
    def _calculate_experience_relevance(self, member: Member, query: str) -> float:
        """Calculate experience relevance."""
        return 0.6  # Placeholder


# Create global service instance
search_service = SearchService()