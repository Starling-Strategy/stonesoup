# ADR-002: Multi-Tenancy Preparation in MVP

**Date**: Current Session  
**Status**: Accepted  
**Context**: Preparing for multi-tenancy while keeping MVP simple

## Decision

We will include `cauldron_id` in ALL tables from day one, even though we hardcode it to '10ksb-pilot' for the MVP.

## Why This Matters

### The Problem
If we don't include `cauldron_id` in our schema now:
1. **Massive Migration Later**: Adding it to millions of rows is painful
2. **Broken Relationships**: Foreign keys and joins become complex
3. **Security Risk**: Data leakage between tenants if not designed properly

### The Solution
```sql
-- Every table includes cauldron_id from the start
CREATE TABLE stories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cauldron_id VARCHAR(50) DEFAULT '10ksb-pilot' NOT NULL,  -- Critical!
    member_id UUID REFERENCES members(id),
    -- ... other fields
);

-- Composite indexes for performance
CREATE INDEX idx_stories_cauldron_member ON stories(cauldron_id, member_id);
```

## Implementation Strategy

### Phase 1: MVP (Current)
```python
# Hardcode in queries for simplicity
async def get_member_stories(member_id: UUID):
    return db.query(Story).filter(
        Story.cauldron_id == "10ksb-pilot",  # Hardcoded for now
        Story.member_id == member_id
    ).all()
```

### Phase 2: True Multi-Tenancy (Future)
```python
# Extract from JWT/context
async def get_member_stories(member_id: UUID, cauldron_id: str):
    return db.query(Story).filter(
        Story.cauldron_id == cauldron_id,  # Dynamic from user context
        Story.member_id == member_id
    ).all()
```

## Learning Note: Why This Pattern?

Think of `cauldron_id` like a house number that must be on every piece of mail. Even if you're only delivering to one house right now, you still put the house number on everything so the system is ready when you expand to the whole neighborhood.

## Consequences

### Positive
- Zero data migration when adding tenants
- Security by design - data isolation built in
- Queries naturally scoped by tenant
- Can add Row Level Security (RLS) later

### Negative
- Slightly more complex queries in MVP
- Need to remember to add to every table
- Composite indexes take more space

## Review Triggers

Revisit when:
- Adding second cauldron
- Performance issues with composite indexes
- Considering sharding by tenant