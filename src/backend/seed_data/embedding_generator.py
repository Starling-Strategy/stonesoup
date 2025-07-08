"""
Embedding generation utilities for STONESOUP seed data.

This module provides functions to generate embeddings for both member profiles
and stories using OpenRouter's API. Embeddings are essential for the semantic
search capabilities of STONESOUP.

Educational Information:
========================

What are Embeddings?
-------------------
Embeddings are numerical vector representations of text that capture semantic
meaning. They allow us to find similar content based on meaning rather than
just keyword matching.

For example:
- "restaurant management" and "food service operations" would have similar embeddings
- "software development" and "programming" would be close in vector space
- "customer service" and "client relations" would cluster together

How STONESOUP Uses Embeddings:
-----------------------------
1. **Member Profile Embeddings**: Created from combined bio, skills, and expertise
2. **Story Embeddings**: Generated from title, content, and summary
3. **Semantic Search**: Find similar members or stories using cosine similarity
4. **Content Recommendations**: Suggest relevant stories based on member interests

Technical Details:
-----------------
- Uses OpenRouter's text-embedding-3-small model (1536 dimensions)
- Cosine similarity for finding related content
- Batch processing for efficiency
- Automatic retry logic for API reliability

Performance Considerations:
--------------------------
- Embeddings are expensive to compute (API calls)
- Generated once and stored in database
- Batch processing reduces API calls
- Caching prevents regeneration during development
"""

import os
import asyncio
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging
from pathlib import Path

# Import OpenRouter client
from app.ai.openrouter_client import OpenRouterClient, OpenRouterConfig

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """
    Generates embeddings for member profiles and stories using OpenRouter.
    
    This class handles:
    - Text preparation for optimal embedding generation
    - Batch processing for efficiency
    - Error handling and retry logic
    - Caching to avoid regeneration during development
    - Progress tracking for large datasets
    """
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the embedding generator.
        
        Args:
            cache_dir: Directory to cache embeddings (optional)
        """
        # Configure OpenRouter for embeddings
        config = OpenRouterConfig(
            embedding_model="openai/text-embedding-3-small",  # Cost-effective, good quality
            model_name="google/gemini-pro",  # Not used for embeddings
        )
        
        self.client = OpenRouterClient(config)
        
        # Setup caching
        self.cache_dir = Path(cache_dir) if cache_dir else Path("./embedding_cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        # Stats tracking
        self.stats = {
            "embeddings_generated": 0,
            "cache_hits": 0,
            "api_calls": 0,
            "total_cost": 0.0,
            "processing_time": 0.0
        }
    
    def _get_cache_key(self, text: str) -> str:
        """Generate a cache key for the given text."""
        import hashlib
        return hashlib.md5(text.encode()).hexdigest()
    
    def _load_from_cache(self, cache_key: str) -> Optional[List[float]]:
        """Load embedding from cache if available."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    self.stats["cache_hits"] += 1
                    return data["embedding"]
            except Exception as e:
                logger.warning(f"Failed to load cache file {cache_file}: {e}")
        return None
    
    def _save_to_cache(self, cache_key: str, embedding: List[float], text: str):
        """Save embedding to cache."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    "embedding": embedding,
                    "text_preview": text[:100] + "..." if len(text) > 100 else text,
                    "generated_at": datetime.utcnow().isoformat(),
                    "model": "openai/text-embedding-3-small"
                }, f)
        except Exception as e:
            logger.warning(f"Failed to save cache file {cache_file}: {e}")
    
    def prepare_member_text(self, member: Dict[str, Any]) -> str:
        """
        Prepare member profile text for embedding generation.
        
        Combines the most important profile information into a single text
        that captures the member's professional identity and expertise.
        
        Args:
            member: Member dictionary from sample_members.py
            
        Returns:
            Prepared text string optimized for embedding generation
        """
        # Core information
        name = member.get("name", "")
        title = member.get("title", "")
        company = member.get("company", "")
        bio = member.get("bio", "")
        location = member.get("location", "")
        
        # Professional details
        skills = member.get("skills", [])
        expertise_areas = member.get("expertise_areas", [])
        industries = member.get("industries", [])
        years_experience = member.get("years_of_experience", 0)
        
        # Build comprehensive text
        text_parts = []
        
        # Basic professional identity
        if name and title and company:
            text_parts.append(f"{name} is a {title} at {company}")
        
        # Location context
        if location:
            text_parts.append(f"based in {location}")
        
        # Experience level
        if years_experience:
            text_parts.append(f"with {years_experience} years of experience")
        
        # Bio (most important for semantic meaning)
        if bio:
            text_parts.append(bio)
        
        # Skills and expertise
        if skills:
            text_parts.append(f"Skills: {', '.join(skills)}")
        
        if expertise_areas:
            text_parts.append(f"Expertise: {', '.join(expertise_areas)}")
        
        if industries:
            text_parts.append(f"Industries: {', '.join(industries)}")
        
        # Join all parts
        full_text = ". ".join(text_parts)
        
        # Ensure reasonable length (embedding models have token limits)
        if len(full_text) > 4000:  # Conservative limit
            full_text = full_text[:4000] + "..."
        
        return full_text
    
    def prepare_story_text(self, story: Dict[str, Any]) -> str:
        """
        Prepare story text for embedding generation.
        
        Combines title, summary, and key content for optimal semantic representation.
        
        Args:
            story: Story dictionary from sample_stories.py
            
        Returns:
            Prepared text string optimized for embedding generation
        """
        title = story.get("title", "")
        content = story.get("content", "")
        summary = story.get("summary", "")
        tags = story.get("tags", [])
        skills = story.get("skills_demonstrated", [])
        company = story.get("company", "")
        story_type = story.get("story_type", "")
        
        text_parts = []
        
        # Title is most important
        if title:
            text_parts.append(f"Title: {title}")
        
        # Summary provides key context
        if summary:
            text_parts.append(f"Summary: {summary}")
        
        # Story type and company context
        if story_type:
            text_parts.append(f"Type: {story_type}")
        
        if company:
            text_parts.append(f"Company: {company}")
        
        # Skills demonstrated
        if skills:
            text_parts.append(f"Skills: {', '.join(skills)}")
        
        # Tags for categorization
        if tags:
            text_parts.append(f"Tags: {', '.join(tags)}")
        
        # Main content (truncated if too long)
        if content:
            # Remove markdown formatting for cleaner embedding
            clean_content = content.replace("**", "").replace("*", "").replace("#", "")
            # Truncate if too long
            if len(clean_content) > 2000:
                clean_content = clean_content[:2000] + "..."
            text_parts.append(clean_content)
        
        # Join all parts
        full_text = ". ".join(text_parts)
        
        # Ensure reasonable length
        if len(full_text) > 4000:
            full_text = full_text[:4000] + "..."
        
        return full_text
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector (1536 dimensions)
        """
        start_time = datetime.utcnow()
        
        # Check cache first
        cache_key = self._get_cache_key(text)
        cached_embedding = self._load_from_cache(cache_key)
        
        if cached_embedding:
            logger.debug(f"Cache hit for text: {text[:50]}...")
            return cached_embedding
        
        # Generate new embedding
        try:
            logger.debug(f"Generating embedding for text: {text[:50]}...")
            embedding = await self.client.generate_embedding(text)
            
            # Update stats
            self.stats["embeddings_generated"] += 1
            self.stats["api_calls"] += 1
            
            # Cache the result
            self._save_to_cache(cache_key, embedding, text)
            
            # Processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.stats["processing_time"] += processing_time
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    async def generate_embeddings_batch(self, texts: List[str], batch_size: int = 10) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process at once
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = []
            
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
            
            for text in batch:
                embedding = await self.generate_embedding(text)
                batch_embeddings.append(embedding)
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.1)
            
            embeddings.extend(batch_embeddings)
            
            # Progress update
            progress = (i + len(batch)) / len(texts) * 100
            logger.info(f"Progress: {progress:.1f}% ({i + len(batch)}/{len(texts)})")
        
        return embeddings
    
    async def generate_member_embeddings(self, members: List[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], List[float]]]:
        """
        Generate embeddings for all member profiles.
        
        Args:
            members: List of member dictionaries
            
        Returns:
            List of (member, embedding) tuples
        """
        logger.info(f"Generating embeddings for {len(members)} members...")
        
        # Prepare texts
        texts = [self.prepare_member_text(member) for member in members]
        
        # Generate embeddings
        embeddings = await self.generate_embeddings_batch(texts)
        
        # Combine members with their embeddings
        member_embeddings = list(zip(members, embeddings))
        
        logger.info(f"Generated {len(member_embeddings)} member embeddings")
        return member_embeddings
    
    async def generate_story_embeddings(self, stories: List[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], List[float]]]:
        """
        Generate embeddings for all stories.
        
        Args:
            stories: List of story dictionaries
            
        Returns:
            List of (story, embedding) tuples
        """
        logger.info(f"Generating embeddings for {len(stories)} stories...")
        
        # Prepare texts
        texts = [self.prepare_story_text(story) for story in stories]
        
        # Generate embeddings
        embeddings = await self.generate_embeddings_batch(texts)
        
        # Combine stories with their embeddings
        story_embeddings = list(zip(stories, embeddings))
        
        logger.info(f"Generated {len(story_embeddings)} story embeddings")
        return story_embeddings
    
    def get_stats(self) -> Dict[str, Any]:
        """Get generation statistics."""
        return {
            **self.stats,
            "cache_hit_rate": self.stats["cache_hits"] / max(1, self.stats["cache_hits"] + self.stats["api_calls"]),
            "avg_processing_time": self.stats["processing_time"] / max(1, self.stats["api_calls"]),
            "estimated_cost": self.stats["api_calls"] * 0.0001  # Rough estimate
        }
    
    def clear_cache(self):
        """Clear the embedding cache."""
        import shutil
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(exist_ok=True)
        logger.info("Embedding cache cleared")


# Utility functions for common operations
async def generate_all_embeddings(cache_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate embeddings for all sample members and stories.
    
    Args:
        cache_dir: Directory to cache embeddings
        
    Returns:
        Dictionary containing all embeddings and metadata
    """
    from .sample_members import generate_member_profiles
    from .sample_stories import get_all_sample_stories
    
    generator = EmbeddingGenerator(cache_dir)
    
    # Generate member profiles
    members = generate_member_profiles()
    
    # Generate stories (need a cauldron ID)
    cauldron_id = "seed-cauldron-001"
    stories = get_all_sample_stories(cauldron_id)
    
    # Generate embeddings
    logger.info("Starting embedding generation...")
    
    member_embeddings = await generator.generate_member_embeddings(members)
    story_embeddings = await generator.generate_story_embeddings(stories)
    
    # Compile results
    results = {
        "members": [
            {
                "profile": member,
                "embedding": embedding
            }
            for member, embedding in member_embeddings
        ],
        "stories": [
            {
                "story": story,
                "embedding": embedding
            }
            for story, embedding in story_embeddings
        ],
        "metadata": {
            "generated_at": datetime.utcnow().isoformat(),
            "member_count": len(member_embeddings),
            "story_count": len(story_embeddings),
            "embedding_model": "openai/text-embedding-3-small",
            "embedding_dimensions": 1536,
            "stats": generator.get_stats()
        }
    }
    
    logger.info(f"Generated embeddings for {len(member_embeddings)} members and {len(story_embeddings)} stories")
    logger.info(f"Generation stats: {generator.get_stats()}")
    
    return results


if __name__ == "__main__":
    # Test the embedding generation
    async def test_embedding_generation():
        # Test with a small sample
        from .sample_members import generate_member_profiles
        
        generator = EmbeddingGenerator()
        members = generate_member_profiles()[:2]  # Test with first 2 members
        
        # Generate embeddings
        member_embeddings = await generator.generate_member_embeddings(members)
        
        # Print results
        for member, embedding in member_embeddings:
            print(f"Member: {member['name']}")
            print(f"Embedding dimensions: {len(embedding)}")
            print(f"First 5 values: {embedding[:5]}")
            print()
        
        # Print stats
        print("Generation stats:", generator.get_stats())
    
    # Run the test
    asyncio.run(test_embedding_generation())