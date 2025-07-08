# STONESOUP Architecture Documentation

## Overview

This directory contains architectural documentation for the STONESOUP project, following a learning-first approach where every decision is explained and documented.

## Document Structure

### `/decisions` - Architecture Decision Records (ADRs)
Documenting key architectural decisions, trade-offs, and rationale:
- [ADR-001: MVP Simplifications](decisions/ADR-001-mvp-simplifications.md) - Why we simplified for MVP

### `/diagrams` - Visual Architecture
Visual representations of system design (coming soon):
- System overview
- Data flow diagrams  
- Component interactions

### `/concepts` - Technical Concepts Explained
Educational documents explaining key concepts:
- [Vector Search Explained](concepts/vector-search.md) (coming soon)
- [AI Embeddings 101](concepts/embeddings-101.md) (coming soon)
- [Multi-Tenancy Patterns](concepts/multi-tenancy.md) (coming soon)

## Key Architectural Principles

### 1. Start Simple, Evolve Deliberately
- MVP uses simplest possible architecture
- Complexity added only when proven necessary
- Each evolution documented with ADR

### 2. Learning-First Design
- Every component includes educational comments
- Complex concepts have dedicated explanations
- Code should teach, not just function

### 3. Pragmatic Choices
- "Good enough" beats "perfect but not shipped"
- Technical debt acknowledged and documented
- Clear triggers for revisiting decisions

## Current Architecture (MVP)

### High-Level Overview
```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Next.js   │────▶│   FastAPI    │────▶│ PostgreSQL  │
│  Frontend   │     │   Backend    │     │ + pgvector  │
└─────────────┘     └──────────────┘     └─────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │  OpenRouter  │
                    │   (AI API)   │
                    └──────────────┘
```

### Core Components

1. **Frontend (Next.js 14)**
   - Simple search interface
   - Member profile display
   - Clerk authentication

2. **Backend (FastAPI)**
   - RESTful API
   - Synchronous processing
   - Direct database queries

3. **Database (PostgreSQL + pgvector)**
   - 3 core tables
   - Vector similarity search
   - Basic text search

4. **AI (OpenRouter)**
   - Gemini Pro for summaries
   - OpenAI embeddings
   - Simple prompt templates

## Learning Resources

### Understanding the Tech Stack
- **FastAPI**: Modern Python web framework with automatic API docs
- **pgvector**: PostgreSQL extension enabling similarity search
- **OpenRouter**: Unified API for multiple AI models
- **Clerk**: Managed authentication service

### Key Concepts to Master
1. **Vector Embeddings**: How text becomes searchable numbers
2. **Similarity Search**: Finding related content mathematically
3. **API Design**: RESTful principles and patterns
4. **React Patterns**: Hooks, state management, component design

## Evolution Path

### Phase 1: MVP (Current)
- Basic search functionality
- Simple AI summaries
- Manual data management

### Phase 2: Enhanced Search
- Faceted filtering
- Better ranking
- Search analytics

### Phase 3: AI Pipeline
- LangGraph orchestration
- Background processing
- Quality validation

### Phase 4: Scale
- Multi-tenancy
- Caching layer
- Performance optimization

## Contributing to Architecture

When making architectural changes:
1. Document the decision with an ADR
2. Update relevant diagrams
3. Add educational comments in code
4. Consider writing a concept guide

## Questions This Architecture Answers

1. **Why not microservices?** - Unnecessary complexity for MVP scale
2. **Why PostgreSQL?** - Robust, supports vectors, familiar to most developers
3. **Why synchronous processing?** - Simpler to debug, acceptable for demo scale
4. **Why OpenRouter?** - Access to multiple models without multiple APIs

## Next Steps

As you work with this architecture:
1. Read the ADRs to understand decisions
2. Check concept guides for deep dives
3. Look for `Learning Note:` comments in code
4. Ask "why" before adding complexity

---

Remember: This architecture is intentionally simple. Complexity is earned through user feedback and actual requirements, not anticipated needs.