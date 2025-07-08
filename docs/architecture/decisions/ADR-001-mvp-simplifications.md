# ADR-001: MVP Simplifications

**Date**: Current Session
**Status**: Accepted
**Context**: STONESOUP needs to demonstrate value quickly with minimal complexity

## Decision

We will radically simplify the MVP architecture to focus on core search functionality.

## Simplifications Made

### 1. Synchronous Processing Only
**Instead of**: Celery + Redis background jobs
**We'll use**: Direct async/await in API endpoints
**Because**: 
- Simpler to debug and deploy
- Acceptable performance for <100 members
- No additional infrastructure needed

### 2. Single AI Model (Gemini via OpenRouter)
**Instead of**: Multiple models with routing logic
**We'll use**: Gemini Pro 1.5 for everything
**Because**:
- One API to manage
- Consistent behavior
- Good balance of cost/quality

### 3. Hardcoded Single Tenant
**Instead of**: Full multi-tenant with RLS
**We'll use**: Hardcoded "10ksb" cauldron
**Because**:
- Dramatically simpler queries
- No auth complexity
- Can add multi-tenancy later

### 4. Basic Search Implementation
**Instead of**: Complex ranking with facets
**We'll use**: Simple text search + vector similarity
**Because**:
- Proves core value proposition
- Easy to understand and debug
- Can enhance based on user feedback

### 5. Minimal Schema (3 Tables)
**Instead of**: Complex relational model
**We'll use**:
```sql
- members (id, name, email, skills, bio, embedding)
- stories (id, member_id, content, confidence, embedding)  
- cauldrons (id, name) -- placeholder for future
```
**Because**:
- Covers core use cases
- Easy to migrate
- Fast to implement

## Consequences

### Positive
- Can deliver working demo in 3 weeks
- Easier to understand and maintain
- Lower operational complexity
- Faster feedback cycle

### Negative  
- Will need refactoring for scale
- Some features require architecture changes
- Not "production ready" for multiple orgs
- Technical debt we're consciously taking

### Neutral
- Learning opportunity about iterative development
- Clear example of YAGNI principle
- Good case study for future teams

## Alternatives Considered

1. **Full Architecture from Start**
   - Rejected: Too complex, delays value delivery

2. **No Framework (Pure SQL)**
   - Rejected: Too limiting for future growth

3. **Serverless Functions**
   - Rejected: Harder local development

## Learning Notes

This decision exemplifies several principles:
- **YAGNI**: You Aren't Gonna Need It (until proven)
- **Worse is Better**: Simple and working beats complex and theoretical
- **Iterative Development**: Start small, grow based on feedback

## Review Triggers

Revisit this decision when:
- User count exceeds 100
- Search latency exceeds 2 seconds  
- Second organization wants to join
- Team grows beyond 2 developers

## References
- [Original Plan](../plan.md)
- [Postponed Features](../postponed-features.md)
- [Do Things That Don't Scale - Paul Graham](http://paulgraham.com/ds.html)