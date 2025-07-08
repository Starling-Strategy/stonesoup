"""
Models package for STONESOUP.

This module imports all SQLAlchemy models to ensure they are registered
with the declarative base before any database operations occur.

The models follow a consistent pattern:
- All inherit from BaseModel for common fields (id, timestamps)
- Multi-tenant models also inherit from CauldronMixin
- All use pgvector for semantic search capabilities
- All include comprehensive indexes for performance
"""
from app.models.cauldron import Cauldron
from app.models.member import Member
from app.models.story import Story, StoryStatus, StoryType, story_members

__all__ = [
    "Cauldron",
    "Member", 
    "Story",
    "StoryStatus",
    "StoryType",
    "story_members",
]