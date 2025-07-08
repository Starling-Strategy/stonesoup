# ADR-003: Embedding Strategy - Members vs Stories

**Date**: Current Session  
**Status**: Accepted  
**Context**: Where to place embeddings for optimal search

## Decision

We will implement a dual embedding strategy:
1. **Story embeddings** (primary) - for finding specific expertise
2. **Member embeddings** (secondary) - for finding similar members

## Why Both?

### The Problem
Different search queries need different approaches:
- "Find someone with sustainable manufacturing experience" → Search story content
- "Find members similar to Elena Rodriguez" → Compare member profiles

### Story Embeddings (Primary Use Case)
```python
# stories table
embedding vector(1536) -- Embedding of the story content
```

**What it represents**: The semantic meaning of a specific story/achievement  
**Best for**: "Find members who have done X"  
**Example**: Story about implementing lean manufacturing → embedding captures concepts of efficiency, waste reduction, process improvement

### Member Embeddings (Secondary Use Case)  
```python
# members table  
embedding vector(1536) -- Aggregated profile embedding
```

**What it represents**: Overall professional identity and expertise areas  
**Best for**: "Find members similar to this person"  
**Generated from**: Bio + skills + aggregated story themes

## Implementation Strategy

### Story Search (Primary)
```python
async def search_by_expertise(query: str):
    """
    Find members who have specific experience.
    
    Learning Note: Story-First Search
    ================================
    We search story embeddings because they contain specific, 
    concrete examples of expertise. This is more precise than 
    searching general member profiles.
    
    Example: Query "AI in manufacturing"
    - Finds story: "Implemented computer vision for quality control"
    - Returns: Member who wrote that story
    """
    query_embedding = await generate_embedding(query)
    
    # Find most relevant stories
    story_results = await db.execute(
        select(Story, Member)
        .join(Member)
        .order_by(Story.embedding.cosine_distance(query_embedding))
        .limit(20)
    )
    
    # Group by member, showing their most relevant story
    return group_by_member(story_results)
```

### Member Search (Secondary)
```python
async def find_similar_members(member_id: UUID):
    """
    Find members with similar overall profiles.
    
    Used for: "People you might want to connect with"
    """
    target_member = await get_member(member_id)
    
    similar_members = await db.execute(
        select(Member)
        .where(Member.id != member_id)
        .order_by(Member.embedding.cosine_distance(target_member.embedding))
        .limit(10)
    )
    
    return similar_members
```

## Embedding Generation Strategy

### Story Embeddings
```python
async def generate_story_embedding(story: Story):
    """Generate embedding from story content."""
    # Use the full story content for rich semantic meaning
    text = f"Title: {story.title}\nContent: {story.content}"
    return await openrouter_client.generate_embedding(text)
```

### Member Embeddings
```python
async def generate_member_embedding(member: Member):
    """
    Generate aggregated profile embedding.
    
    Learning Note: Profile Aggregation
    =================================
    We combine multiple data sources to create a holistic
    representation of the member's professional identity.
    This is different from any single story.
    """
    # Combine bio, skills, and role information
    profile_text = f"""
    Professional: {member.name}
    Role: {member.role} at {member.company}
    Bio: {member.bio}
    Skills: {', '.join(member.skills)}
    """
    
    return await openrouter_client.generate_embedding(profile_text)
```

## Search Result Presentation

### For Expertise Search
```python
class SearchResult:
    member: Member
    relevant_story: Story  # The story that matched
    story_relevance: float  # How well story matched query
    member_summary: str    # AI-generated summary focused on the query
```

### For Similar Members
```python
class SimilarMemberResult:
    member: Member
    similarity_score: float
    shared_interests: List[str]  # Extracted common themes
```

## Database Schema Updates

```sql
-- Add cauldron_id to stories (addressing Flag 1)
CREATE TABLE stories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cauldron_id VARCHAR(50) DEFAULT '10ksb-pilot' NOT NULL,  -- FIXED!
    member_id UUID REFERENCES members(id),
    title VARCHAR(500),
    content TEXT NOT NULL,
    summary TEXT,
    confidence_score FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 1),
    source_url TEXT,
    embedding vector(1536) NOT NULL,  -- Story content embedding
    created_at TIMESTAMP DEFAULT NOW()
);

-- Members table (updated)
CREATE TABLE members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cauldron_id VARCHAR(50) DEFAULT '10ksb-pilot' NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    bio TEXT,
    skills TEXT[],
    company VARCHAR(255),
    role VARCHAR(255),
    embedding vector(1536),  -- Aggregated profile embedding
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Optimized indexes
CREATE INDEX idx_stories_cauldron_embedding ON stories(cauldron_id) 
    INCLUDE (embedding) USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_members_cauldron_embedding ON members(cauldron_id) 
    INCLUDE (embedding) USING ivfflat (embedding vector_cosine_ops);
```

## Migration Strategy

### MVP Implementation
1. Start with story embeddings only
2. Implement expertise search first (main use case)
3. Add member embeddings later for "similar members" feature

### Rationale
- Story search solves the primary PRD use case: "find members with X experience"
- Member similarity is nice-to-have for later phases
- Reduces complexity for MVP while keeping architecture flexible

## Learning Notes

### Why Story Embeddings Are More Powerful
- **Specific vs General**: Stories contain concrete examples, profiles are general
- **Context Rich**: Stories have situational context that embeddings capture well
- **Query Matching**: "AI in manufacturing" matches better against specific implementation stories than general "AI skills"

### When to Use Each
- **Story Search**: "Find someone who has experience with X"
- **Member Search**: "Find people similar to Y"
- **Hybrid**: Use both for comprehensive search ranking

## Future Enhancements

1. **Story Clustering**: Group similar stories to identify expertise themes
2. **Dynamic Member Embeddings**: Regenerate based on latest stories
3. **Weighted Aggregation**: Weight recent stories more heavily in member embeddings
4. **Multi-Vector Search**: Search both simultaneously and combine rankings