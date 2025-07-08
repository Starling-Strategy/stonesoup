# STONESOUP Postponed Features

This document tracks features that were planned but postponed to focus on MVP delivery. Each feature includes rationale for postponement and conditions for future implementation.

## 🔄 Postponed from MVP

### 1. Complex AI Pipeline (LangGraph Agents)
**Original Vision**: Multi-stage agent pipeline for content processing
- Document ingestion agent
- Entity extraction agent  
- Story generation agent
- Quality validation agent

**Why Postponed**: Over-engineered for initial value demonstration
**When to Implement**: After validating that users find AI-generated summaries valuable
**Learning Note**: Start simple with direct AI calls, add orchestration when complexity demands it

### 2. Background Job Processing (Celery + Redis)
**Original Vision**: Async processing for AI operations
**Why Postponed**: Synchronous processing is acceptable for demo scale (<100 members)
**When to Implement**: When processing time exceeds 3 seconds or volume exceeds 10 requests/minute
**Learning Note**: Premature optimization is the root of all evil

### 3. Advanced Search Features
**Original Vision**: 
- Faceted search with filters
- Search suggestions/autocomplete
- Saved searches
- Search analytics

**Why Postponed**: Basic keyword + vector search sufficient for MVP
**When to Implement**: After users request specific search improvements
**Learning Note**: User feedback should drive search enhancements

### 4. Multi-Tenant Architecture (Full Implementation)
**Original Vision**: Complete isolation with PostgreSQL RLS policies
**Current State**: Single cauldron (10KSB) hardcoded
**Why Postponed**: Complexity without immediate value
**When to Implement**: When second organization wants to use platform
**Learning Note**: YAGNI (You Aren't Gonna Need It) - until you do

### 5. Admin Dashboard
**Original Vision**: 
- User management
- Content moderation
- Analytics dashboard
- System configuration

**Why Postponed**: Can manage through direct database access initially
**When to Implement**: When non-technical users need to manage system
**Learning Note**: Developer tools are fine until you have non-developer users

### 6. Email Notifications
**Original Vision**: 
- Welcome emails
- Story notifications
- Weekly digests

**Why Postponed**: Not core to search/discovery experience
**When to Implement**: When users request proactive updates
**Learning Note**: Pull (search) before push (notifications)

### 7. File Upload & Processing
**Original Vision**: Upload documents to generate member profiles
**Why Postponed**: Manual data entry sufficient for 50-100 members
**When to Implement**: When manual process takes >1 hour/week
**Learning Note**: Do things that don't scale - Paul Graham

### 8. Advanced AI Features
**Original Vision**:
- Multiple AI model selection
- Custom prompt templates
- Fine-tuning on community data
- Hallucination detection

**Why Postponed**: Basic summarization sufficient for MVP
**When to Implement**: When AI quality becomes a user complaint
**Learning Note**: Ship with "good enough" AI, iterate based on feedback

### 9. Caching Layer
**Original Vision**: Redis caching for embeddings and API responses
**Why Postponed**: Performance acceptable without caching at demo scale
**When to Implement**: When same queries repeated >10x/day
**Learning Note**: Measure before optimizing

### 10. Comprehensive Testing
**Original Vision**: 80%+ test coverage, E2E tests, performance tests
**Why Postponed**: Manual testing sufficient for MVP
**When to Implement**: After core features stabilize
**Learning Note**: Tests are important but working software is more important

## 📊 Feature Prioritization Framework

When considering postponed features, evaluate:

1. **User Value**: Does this directly improve user experience?
2. **Technical Debt**: Will postponing this make future work harder?
3. **Complexity**: Can we achieve 80% of value with 20% of effort?
4. **Risk**: What's the worst case if we don't have this?

## 🎯 Post-MVP Roadmap

### Phase 2 (Weeks 4-6): Enhanced Search
1. Faceted filtering
2. Search suggestions
3. Better ranking algorithm

### Phase 3 (Weeks 7-10): AI Pipeline
1. LangGraph integration
2. Background processing
3. Quality validation

### Phase 4 (Weeks 11-14): Scale & Polish
1. Multi-tenancy
2. Admin dashboard
3. Performance optimization

### Phase 5 (Weeks 15+): Advanced Features
1. Email notifications
2. File uploads
3. Analytics

## 💡 Lessons for Future Features

1. **Start with manual processes** - Automate only when painful
2. **Build for one user** - Generalize when you have ten
3. **Optimize when slow** - Not when you imagine it might be slow
4. **Add complexity when required** - Not when it seems elegant

---

Remember: Every postponed feature is a bet that we can deliver value without it. Keep this list updated as we learn what users actually need.