"""
AI Summary Generation Service for STONESOUP search results.

This service provides intelligent summarization of search results using
AI to help users quickly understand and navigate large result sets.

Educational Notes:
=================

AI Summary Strategy:
- Analyze search results to extract key themes and insights
- Generate concise, actionable summaries
- Highlight skill gaps and member expertise
- Provide recommendations for talent discovery
- Support different summary types (overview, detailed, insights)

Use Cases:
- Search result summaries for quick understanding
- Talent landscape analysis
- Skill gap identification
- Member recommendation generation
- Content discovery assistance
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

from app.ai.openrouter_client import openrouter_client, OpenRouterResponse
from app.schemas.search import AISummaryResponse, StorySearchResult, MemberSearchResult
from app.core.config import settings

logger = logging.getLogger(__name__)


class SummaryType(str, Enum):
    """Types of AI summaries that can be generated."""
    OVERVIEW = "overview"
    DETAILED = "detailed"
    INSIGHTS = "insights"
    RECOMMENDATIONS = "recommendations"


class AISummaryService:
    """
    Service for generating AI-powered summaries of search results.
    
    This service analyzes search results and generates intelligent
    summaries that help users understand:
    - What talent is available
    - Key skills and expertise areas
    - Notable achievements and experiences
    - Recommendations for talent discovery
    """
    
    def __init__(self):
        self.logger = logger
        
    async def generate_search_summary(
        self,
        query: str,
        story_results: List[StorySearchResult],
        member_results: List[MemberSearchResult],
        summary_type: SummaryType = SummaryType.OVERVIEW,
        max_length: int = 500
    ) -> AISummaryResponse:
        """
        Generate an AI summary of search results.
        
        Educational Notes:
        - Analyzes both story and member results
        - Extracts key themes and insights
        - Provides actionable recommendations
        - Maintains focus on talent discovery
        
        Args:
            query: Original search query
            story_results: List of story search results
            member_results: List of member search results
            summary_type: Type of summary to generate
            max_length: Maximum summary length
            
        Returns:
            AI-generated summary with metadata
        """
        start_time = datetime.utcnow()
        
        try:
            # Prepare search result context
            context = self._prepare_search_context(
                query, story_results, member_results
            )
            
            # Generate summary prompt based on type
            prompt = self._create_summary_prompt(
                context, summary_type, max_length
            )
            
            # Generate summary using AI
            generation_start = datetime.utcnow()
            ai_response = await openrouter_client.generate_text(
                prompt=prompt,
                temperature=0.3,  # Lower temperature for factual summaries
                max_tokens=max_length + 100  # Some buffer for AI response
            )
            generation_time = (datetime.utcnow() - generation_start).total_seconds()
            
            # Extract key insights
            insights = self._extract_key_insights(
                context, story_results, member_results
            )
            
            # Create response
            return AISummaryResponse(
                summary=ai_response.text.strip(),
                key_insights=insights,
                confidence_score=ai_response.confidence_score,
                model_used=ai_response.model,
                generation_time=generation_time,
                result_count=len(story_results) + len(member_results),
                query=query,
                summary_type=summary_type.value,
                generated_at=start_time
            )
            
        except Exception as e:
            self.logger.error(f"AI summary generation failed: {e}", exc_info=True)
            # Return a fallback summary
            return self._create_fallback_summary(
                query, story_results, member_results, summary_type
            )
    
    def _prepare_search_context(
        self,
        query: str,
        story_results: List[StorySearchResult],
        member_results: List[MemberSearchResult]
    ) -> Dict[str, Any]:
        """
        Prepare structured context from search results for AI analysis.
        
        Educational Notes:
        - Extracts key information from search results
        - Structures data for AI processing
        - Identifies patterns and themes
        - Maintains focus on talent insights
        """
        # Analyze stories
        story_themes = []
        story_skills = set()
        story_companies = set()
        
        for result in story_results[:10]:  # Limit to top 10 for context
            story = result.story
            story_themes.append({
                "title": story.title,
                "type": story.story_type.value,
                "skills": story.skills_demonstrated,
                "company": story.company,
                "summary": story.summary or story.content[:200] + "..."
            })
            story_skills.update(story.skills_demonstrated or [])
            if story.company:
                story_companies.add(story.company)
        
        # Analyze members
        member_profiles = []
        member_skills = set()
        member_locations = set()
        member_companies = set()
        
        for result in member_results[:10]:  # Limit to top 10 for context
            member = result.member
            member_profiles.append({
                "name": member.name,
                "title": member.title,
                "company": member.company,
                "location": member.location,
                "skills": member.skills,
                "experience": member.years_of_experience,
                "bio": member.bio
            })
            member_skills.update(member.skills or [])
            if member.location:
                member_locations.add(member.location)
            if member.company:
                member_companies.add(member.company)
        
        return {
            "query": query,
            "total_results": len(story_results) + len(member_results),
            "story_count": len(story_results),
            "member_count": len(member_results),
            "story_themes": story_themes,
            "member_profiles": member_profiles,
            "all_skills": list(story_skills.union(member_skills)),
            "companies": list(story_companies.union(member_companies)),
            "locations": list(member_locations),
            "top_skills": self._get_top_skills(story_skills, member_skills),
            "skill_gaps": self._identify_skill_gaps(query, story_skills, member_skills)
        }
    
    def _create_summary_prompt(
        self,
        context: Dict[str, Any],
        summary_type: SummaryType,
        max_length: int
    ) -> str:
        """
        Create AI prompt for summary generation based on type.
        
        Educational Notes:
        - Different prompts for different summary types
        - Structured prompts for consistent results
        - Focus on talent discovery and insights
        - Include specific instructions for AI behavior
        """
        base_context = f"""
Search Query: "{context['query']}"
Total Results: {context['total_results']} ({context['story_count']} stories, {context['member_count']} members)
Top Skills Found: {', '.join(context['top_skills'][:5])}
Companies: {', '.join(context['companies'][:5])}
"""
        
        if summary_type == SummaryType.OVERVIEW:
            return f"""
{base_context}

Generate a concise overview (max {max_length} words) of these search results for talent discovery. 
Focus on:
- What talent and expertise is available
- Key skills and experience areas represented
- Notable companies and backgrounds
- Overall landscape of results

Make it actionable for someone looking to understand the talent pool.

Detailed Results Context:
Stories: {context['story_themes'][:3]}
Members: {context['member_profiles'][:3]}
"""
        
        elif summary_type == SummaryType.DETAILED:
            return f"""
{base_context}

Generate a detailed analysis (max {max_length} words) of these search results. 
Include:
- Breakdown of talent by skill areas
- Experience levels and backgrounds
- Notable achievements and projects
- Geographic and company distribution
- Specific examples from top results

Detailed Results Context:
All Stories: {context['story_themes']}
All Members: {context['member_profiles']}
"""
        
        elif summary_type == SummaryType.INSIGHTS:
            return f"""
{base_context}

Generate key insights (max {max_length} words) from these search results.
Focus on:
- Talent market patterns and trends
- Skill availability and gaps
- Unique expertise areas
- Cross-functional capabilities
- Hidden gems or standout profiles

Provide 3-5 specific insights that would help with talent strategy.

Context for Analysis:
Skills Distribution: {context['all_skills']}
Potential Gaps: {context['skill_gaps']}
"""
        
        elif summary_type == SummaryType.RECOMMENDATIONS:
            return f"""
{base_context}

Generate specific recommendations (max {max_length} words) based on these search results.
Provide:
- Top talent recommendations with reasons
- Alternative search strategies to explore
- Skills to prioritize or deprioritize
- Geographic or company expansion opportunities
- Next steps for talent acquisition

Be specific and actionable.

Context for Recommendations:
Available Talent: {context['member_profiles'][:5]}
Demonstrated Skills: {context['story_themes'][:5]}
"""
        
        return base_context  # Fallback
    
    def _extract_key_insights(
        self,
        context: Dict[str, Any],
        story_results: List[StorySearchResult],
        member_results: List[MemberSearchResult]
    ) -> List[str]:
        """
        Extract structured key insights from search results.
        
        Educational Notes:
        - Provides specific, actionable insights
        - Focuses on talent discovery value
        - Identifies patterns and opportunities
        - Complements AI-generated summary
        """
        insights = []
        
        # Skill availability insights
        if context['top_skills']:
            insights.append(
                f"Strong representation in {', '.join(context['top_skills'][:3])} skills"
            )
        
        # Experience level insights
        experienced_members = [
            m for m in context['member_profiles'] 
            if m.get('experience', 0) and m['experience'] > 5
        ]
        if experienced_members:
            insights.append(
                f"{len(experienced_members)} senior professionals with 5+ years experience"
            )
        
        # Geographic diversity
        if len(context['locations']) > 3:
            insights.append(
                f"Geographically diverse talent across {len(context['locations'])} locations"
            )
        
        # Company background diversity
        if len(context['companies']) > 3:
            insights.append(
                f"Diverse company backgrounds from {len(context['companies'])} organizations"
            )
        
        # Story quality insight
        if story_results:
            avg_engagement = sum(r.engagement_score for r in story_results) / len(story_results)
            if avg_engagement > 0.5:
                insights.append("High-quality portfolio content with strong engagement")
        
        return insights[:5]  # Limit to top 5 insights
    
    def _get_top_skills(
        self, 
        story_skills: set, 
        member_skills: set
    ) -> List[str]:
        """Get top skills by frequency across results."""
        # Simple frequency counting - could be enhanced with weighting
        all_skills = list(story_skills.union(member_skills))
        # For now, return first 10 - could implement proper frequency counting
        return all_skills[:10]
    
    def _identify_skill_gaps(
        self, 
        query: str, 
        story_skills: set, 
        member_skills: set
    ) -> List[str]:
        """Identify potential skill gaps based on query vs available skills."""
        # Simple gap identification - extract words from query not in skills
        query_words = set(query.lower().split())
        available_skills_lower = {skill.lower() for skill in story_skills.union(member_skills)}
        
        gaps = []
        for word in query_words:
            if len(word) > 3 and word not in available_skills_lower:
                gaps.append(word)
        
        return gaps[:5]  # Limit to 5 potential gaps
    
    def _create_fallback_summary(
        self,
        query: str,
        story_results: List[StorySearchResult],
        member_results: List[MemberSearchResult],
        summary_type: SummaryType
    ) -> AISummaryResponse:
        """
        Create a fallback summary when AI generation fails.
        
        Educational Notes:
        - Provides basic summary without AI
        - Ensures users always get some summary
        - Uses template-based approach
        - Maintains consistent response format
        """
        # Create basic summary
        total_results = len(story_results) + len(member_results)
        
        if total_results == 0:
            summary = f'No results found for "{query}". Try broader search terms or different keywords.'
        elif total_results == 1:
            summary = f'Found 1 result for "{query}". This appears to be a specific match.'
        else:
            summary = f'Found {total_results} results for "{query}" ({len(story_results)} stories, {len(member_results)} members). Results include diverse talent and expertise.'
        
        # Extract basic insights
        insights = []
        if story_results:
            insights.append(f"{len(story_results)} relevant stories found")
        if member_results:
            insights.append(f"{len(member_results)} qualified members identified")
        
        return AISummaryResponse(
            summary=summary,
            key_insights=insights,
            confidence_score=0.5,  # Low confidence for fallback
            model_used="fallback",
            generation_time=0.0,
            result_count=total_results,
            query=query,
            summary_type=summary_type.value,
            generated_at=datetime.utcnow()
        )
    
    async def generate_member_recommendations(
        self,
        query: str,
        member_results: List[MemberSearchResult],
        max_recommendations: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generate specific member recommendations with explanations.
        
        Educational Notes:
        - Provides detailed member recommendations
        - Includes reasoning for each recommendation
        - Supports talent decision making
        - Integrates with search results
        """
        try:
            if not member_results:
                return []
            
            # Prepare member context
            member_context = []
            for result in member_results[:max_recommendations]:
                member = result.member
                member_context.append({
                    "name": member.name,
                    "title": member.title,
                    "company": member.company,
                    "skills": member.skills[:5],  # Top 5 skills
                    "experience": member.years_of_experience,
                    "match_score": result.score,
                    "availability": "Available" if member.is_available else "Not Available"
                })
            
            # Generate recommendation prompt
            prompt = f"""
Based on the search query "{query}", analyze these member profiles and provide specific recommendations:

Member Profiles:
{member_context}

For each member, provide:
1. Why they're a good match for "{query}"
2. Their strongest qualifications
3. Any unique value they bring
4. Recommendation confidence (High/Medium/Low)

Keep each recommendation to 2-3 sentences.
"""
            
            # Generate recommendations
            ai_response = await openrouter_client.generate_text(
                prompt=prompt,
                temperature=0.4,
                max_tokens=800
            )
            
            # Parse AI response into structured recommendations
            # For now, return a simple structure
            recommendations = []
            for i, result in enumerate(member_results[:max_recommendations]):
                recommendations.append({
                    "member_id": result.member.id,
                    "member_name": result.member.name,
                    "recommendation": f"Strong match for {query} based on {result.member.title} background",
                    "confidence": "High" if result.score > 0.8 else "Medium" if result.score > 0.6 else "Low",
                    "match_reasons": result.member.skills[:3],
                    "score": result.score
                })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Member recommendation generation failed: {e}")
            return []
    
    async def generate_skill_analysis(
        self,
        query: str,
        story_results: List[StorySearchResult],
        member_results: List[MemberSearchResult]
    ) -> Dict[str, Any]:
        """
        Generate detailed skill analysis from search results.
        
        Educational Notes:
        - Analyzes skill distribution and availability
        - Identifies skill gaps and strengths
        - Provides market insights
        - Supports talent strategy decisions
        """
        try:
            # Collect all skills
            all_skills = set()
            skill_frequency = {}
            
            # Count skills from stories
            for result in story_results:
                for skill in result.story.skills_demonstrated:
                    all_skills.add(skill)
                    skill_frequency[skill] = skill_frequency.get(skill, 0) + 1
            
            # Count skills from members
            for result in member_results:
                for skill in result.member.skills:
                    all_skills.add(skill)
                    skill_frequency[skill] = skill_frequency.get(skill, 0) + 1
            
            # Sort skills by frequency
            top_skills = sorted(
                skill_frequency.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
            
            # Generate analysis
            prompt = f"""
Analyze the skill landscape for search query "{query}":

Top Skills Found (by frequency):
{top_skills}

Total Unique Skills: {len(all_skills)}
Total Results Analyzed: {len(story_results) + len(member_results)}

Provide analysis on:
1. Skill market strength and availability
2. Emerging or trending skills
3. Potential skill gaps
4. Recommendations for talent acquisition

Keep analysis concise and actionable.
"""
            
            ai_response = await openrouter_client.generate_text(
                prompt=prompt,
                temperature=0.3,
                max_tokens=500
            )
            
            return {
                "analysis": ai_response.text,
                "top_skills": [{"skill": skill, "count": count} for skill, count in top_skills],
                "total_unique_skills": len(all_skills),
                "skill_diversity_score": len(all_skills) / max(1, len(story_results) + len(member_results)),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Skill analysis generation failed: {e}")
            return {
                "analysis": "Skill analysis unavailable",
                "top_skills": [],
                "total_unique_skills": 0,
                "skill_diversity_score": 0.0,
                "generated_at": datetime.utcnow().isoformat()
            }


# Create global service instance
ai_summary_service = AISummaryService()