# STONESOUP - Intelligent Community Management Platform

## Project Overview
STONESOUP is an AI-powered community management platform that creates dynamic, narrative-driven profiles of community members. Like a stone soup that becomes richer through diverse contributions, it makes expertise and experiences instantly discoverable.

**First Implementation**: Goldman Sachs 10,000 Small Businesses (10KSB) "Cauldron"

## Learning-First Development Philosophy
🎓 **This is a learning project** - Always explain decisions, provide detailed comments, and use plain language documentation.

- Propose approaches before implementing
- Explain complex concepts and architectural decisions
- Include comprehensive comments in all code
- Document major decisions and reasoning
- Prioritize readability and educational value

## Tech Stack & Versions
- **Frontend**: Next.js 14+ with TypeScript, shadcn/ui, Tailwind CSS
- **Backend API**: FastAPI with Python 3.11+
- **Python Package Manager**: UV (Rust-based) - use for all Python dependencies
- **AI Orchestration**: LangGraph (deploy on LangGraph paid platform)
- **Database**: PostgreSQL with pgvector extension (hosted on Railway)
- **Vector Search**: pgvector for similarity search
- **Authentication**: Clerk
- **Error Monitoring**: Sentry
- **Hosting**: Railway (backend + PostgreSQL), Vercel (frontend)
- **Deployment**: Docker containers

## Project Structure (Monorepo)
```
stonesoup/
├── src/
│   ├── frontend/          # Next.js app (Vercel deployment)
│   ├── backend/           # FastAPI app (Railway deployment)
│   └── agents/            # LangGraph orchestration code
├── docker/                # Dockerfile configurations
├── docs/                  # Project documentation
├── claude.md             # This file
└── README.md
```

## Core Commands
```bash
# Python (use UV for all Python operations)
uv venv                    # Create virtual environment
uv pip install -r requirements.txt  # Install dependencies
uv pip freeze > requirements.txt    # Update requirements

# Frontend
npm run dev               # Start Next.js development server
npm run build            # Build for production
npm run typecheck        # TypeScript checking
npm run lint             # ESLint + Prettier

# Backend
uvicorn main:app --reload  # Start FastAPI development server
python -m pytest         # Run tests

# Database
psql $DATABASE_URL        # Connect to PostgreSQL
alembic upgrade head      # Run database migrations
alembic revision --autogenerate -m "description"  # Create new migration

# Docker
docker-compose up --build  # Build and run all services
```

## Code Style & Standards

### TypeScript/JavaScript
- **Strict TypeScript**: Always use strict mode, no `any` types
- **Imports**: Use destructured imports when possible: `import { foo } from 'bar'`
- **Components**: Functional components with hooks, not class components
- **File naming**: kebab-case for files, PascalCase for components
- **Comments**: Explain complex logic, business rules, and AI decisions

### Python
- **Type hints**: Required for all function signatures
- **Imports**: Explicit imports, group by standard/third-party/local
- **Error handling**: Use try/except with specific exception types
- **Documentation**: Docstrings for all functions, classes, and modules
- **Comments**: Explain AI model decisions, confidence thresholds, business logic

### Multi-Tenancy Architecture
🏗️ **CRITICAL**: Every database operation MUST be scoped by `cauldron_id`
- All PostgreSQL tables include `cauldron_id` column
- All queries filter by `cauldron_id` using Row Level Security (RLS)
- Database policies enforce tenant isolation at PostgreSQL level
- API endpoints validate tenant access via Clerk organizations
- Use parameterized queries to prevent SQL injection

## AI Integration Guidelines

### LangGraph Agent Development
- Document agent workflows clearly
- Explain decision trees and routing logic
- Include confidence score handling
- Comment on why specific agents are chosen for tasks

### AI Model Integration (OpenRouter)
- **Primary Provider**: OpenRouter for unified AI access
- **Models Available**: Gemini, GPT-4, Claude, and others
- **Always include error handling for API calls**
- **Log API usage and costs** (OpenRouter tracks per-request)
- **Implement retry logic with exponential backoff**
- **Document prompt engineering decisions**
- **Use model-specific features** when beneficial

### OpenRouter Configuration
```python
# Default configuration uses Gemini via OpenRouter
from app.ai import openrouter_client

# Text generation
response = await openrouter_client.generate_text(
    prompt="Your prompt here",
    system_instruction="You are a helpful assistant",
    temperature=0.7
)

# Embeddings (using OpenAI's model via OpenRouter)
embedding = await openrouter_client.generate_embedding(
    text="Text to embed"
)

# Use different models when needed
response = await openrouter_client.generate_text(
    prompt="Complex reasoning task",
    model="anthropic/claude-3-opus"  # Use Claude for complex tasks
)

# Cost tracking
stats = openrouter_client.get_usage_stats()
print(f"Total cost: {stats['total_cost']}")
```

### Available Models via OpenRouter
- **google/gemini-pro-1.5**: Default for general tasks
- **openai/gpt-4-turbo**: For complex reasoning
- **anthropic/claude-3-opus**: For nuanced understanding
- **openai/text-embedding-3-small**: For embeddings (1536 dimensions)

### Data Quality & Confidence
- Include confidence scores for all AI-generated content
- Implement human review queues for low-confidence items
- Document validation logic and thresholds

## The Commandments of Development (Prioritized)

### 🎯 Top Priority Commandments
1. **Separation of Concerns**: One thing should do one thing well
2. **Security First**: Keep all secrets secure, respect user privacy
3. **No Magic Strings**: Use constants and configuration
4. **Structured Logging**: Include context and correlation IDs
5. **Design for AI Failure**: Always have fallback mechanisms

### 🛡️ Safety & Quality
6. **Don't Trust AI**: Validate all AI outputs
7. **Test Everything**: Write tests that explain expected behavior
8. **Monitor Models**: Track performance, drift, and costs
9. **Plan Your Work**: Document decisions and alternatives considered

### 📈 Performance & Maintenance
10. **No Premature Optimization**: Profile before optimizing
11. **One Source of Truth**: Avoid data duplication
12. **Mind Costs**: Track AI API usage and database operations
13. **Commit Small and Often**: Meaningful, atomic commits

## Documentation Standards
- **Decision Records**: Document major architectural decisions
- **Plain Language**: Accessible to non-technical stakeholders
- **Visual Appeals**: Use diagrams, code examples, and clear formatting
- **Learning Focus**: Explain not just what, but why and how

## Error Handling Patterns
```python
# AI API calls with Sentry integration
import sentry_sdk
from sentry_sdk import capture_exception
from app.ai import openrouter_client

try:
    response = await openrouter_client.generate_text(
        prompt=prompt,
        system_instruction="You are a helpful assistant"
    )
    if response.confidence_score < CONFIDENCE_THRESHOLD:
        # Queue for human review
        await queue_for_review(response)
except Exception as e:
    # Capture in Sentry with context
    sentry_sdk.set_context("ai_request", {
        "cauldron_id": cauldron_id,
        "prompt_type": prompt_type,
        "model": response.model if 'response' in locals() else "unknown",
        "provider": "openrouter"
    })
    capture_exception(e)
    
    logger.error(f"OpenRouter API error: {e}", extra={"cauldron_id": cauldron_id})
    # Fallback to cached/default response
```


## Security Considerations
- **Multi-tenant isolation**: PostgreSQL Row Level Security (RLS) by cauldron_id
- **Authentication**: Clerk organizations for tenant management
- **Input validation**: Parameterized queries, Pydantic validation
- **Rate limiting**: Implement for AI API calls using Redis on Railway
- **Audit logging**: Track access with structured logging to Sentry
- **PII handling**: Minimal collection, secure processing
- **SQL Injection Prevention**: Always use parameterized queries
- **Vector Injection**: Validate embedding dimensions and values

## Development Workflow
1. **Plan**: Create issue/task with clear acceptance criteria
2. **Design**: Document approach in plain language
3. **Implement**: Code with extensive comments and type safety
4. **Test**: Unit tests that serve as documentation
5. **Review**: Ensure code teaches and explains
6. **Deploy**: Use Docker for consistent environments
7. **Monitor**: Track performance and AI model behavior

## AI-Specific Guidance
- **Explain reasoning**: Document why specific AI approaches were chosen
- **Include alternatives**: Note other approaches considered
- **Performance metrics**: Track accuracy, latency, and costs
- **Fallback strategies**: Always have non-AI alternatives
- **Human-in-the-loop**: Design for human oversight and intervention

## Learning-First Implementation Guidelines

### Every Component Must Teach
When implementing any feature, follow these practices:

1. **Add "Learning Note" Comment Blocks**
```python
# Learning Note: Vector Search Explained
# =====================================
# Vector search finds similar content by comparing numerical representations
# of text. Think of it like finding similar colors in a color space - 
# texts with similar meanings are "close" in vector space.
#
# We use 1536 dimensions because that's what OpenAI's embedding model outputs.
# Each dimension captures some aspect of meaning.
#
# See: docs/architecture/concepts/vector-search.md for deep dive
```

2. **Document Trade-offs in Code**
```python
# We chose cosine similarity over Euclidean distance because:
# 1. It's scale-invariant (magnitude doesn't matter)
# 2. Better for high-dimensional spaces
# 3. Standard for text embeddings
# Trade-off: Slightly slower computation
```

3. **Explain Complex Logic Step-by-Step**
```python
async def hybrid_search(query: str, limit: int = 10):
    """
    Hybrid search combines text and vector search for best results.
    
    Learning Path:
    1. Text search finds exact keyword matches (good for names, specific terms)
    2. Vector search finds semantic similarity (good for concepts, skills)
    3. We combine scores with weights to balance both approaches
    
    This gives us the best of both worlds: precision and understanding.
    """
    # Step 1: Get text search results (exact matches score higher)
    text_results = await text_search(query)
    
    # Step 2: Generate embedding for semantic search
    # This converts the query into a 1536-dimensional vector
    query_embedding = await generate_embedding(query)
    
    # Step 3: Find semantically similar content
    vector_results = await vector_search(query_embedding)
    
    # Step 4: Combine and rank results
    # Text matches get 0.3 weight, semantic matches get 0.7 weight
    # This bias toward semantic search handles synonyms and related concepts
    combined = combine_results(text_results, vector_results, weights=(0.3, 0.7))
    
    return combined[:limit]
```

4. **Use Descriptive Names That Teach**
```python
# Bad: emb, sim, calc_dist
# Good: member_embedding, cosine_similarity, calculate_vector_distance

# Bad: process_data()
# Good: extract_skills_from_bio()

# Bad: DIMS = 1536
# Good: OPENAI_EMBEDDING_DIMENSIONS = 1536  # OpenAI text-embedding-3-small output size
```

5. **Link to Deeper Resources**
```python
# For deep dive on pgvector indexing strategies, see:
# - docs/architecture/concepts/vector-indexes.md
# - https://github.com/pgvector/pgvector#indexing
# 
# TLDR: We use IVFFlat for balanced speed/accuracy on our data size
```

### Architecture Documentation Requirements

For every significant implementation:

1. **Create an ADR (Architecture Decision Record)**
   - Location: `docs/architecture/decisions/ADR-XXX-title.md`
   - Template: Decision, Rationale, Consequences, Alternatives
   - Include learning notes about why alternatives were rejected

2. **Add Concept Guides for Complex Topics**
   - Location: `docs/architecture/concepts/topic-name.md`
   - Explain the concept in plain language first
   - Then dive into technical implementation
   - Include diagrams where helpful

3. **Write Step-by-Step Tutorials**
   - Location: `docs/tutorials/task-name.md`
   - Show the complete flow through the system
   - Explain what happens at each step
   - Include common gotchas and troubleshooting

### Code Review Checklist for Learning

Before committing code, ensure:
- [ ] Complex functions have learning note comments
- [ ] Trade-offs are documented where decisions were made
- [ ] Variable names are descriptive and educational
- [ ] Links to documentation are included for deep topics
- [ ] A junior developer could understand the implementation
- [ ] The "why" is as clear as the "what"

### Example: Implementing a New Feature

When adding a new feature like member search:

1. **Start with Documentation**
   - Write `docs/architecture/decisions/ADR-002-search-implementation.md`
   - Explain why hybrid search, what alternatives exist

2. **Implement with Teaching Comments**
   - Each function explains its purpose and approach
   - Complex algorithms have step-by-step breakdowns
   - Edge cases are documented with examples

3. **Create a Concept Guide**
   - Write `docs/architecture/concepts/hybrid-search.md`
   - Explain text vs. vector search
   - Show when each is better with examples

4. **Add a Tutorial**
   - Write `docs/tutorials/searching-for-members.md`
   - Walk through a search request end-to-end
   - Show how data flows through the system

## Learning Resources Integration
- Include links to relevant documentation in comments
- Explain complex concepts with examples
- Use meaningful variable names that describe purpose
- Write tests that demonstrate intended behavior
- Create documentation that teaches, not just describes

## Railway Auto-Configuration

### Automatic Database Connection
Railway integration provides zero-configuration database setup:
```python
# The app automatically retrieves connection strings on startup
# No manual configuration needed when deployed to Railway

# app/core/railway_client.py handles:
# - PostgreSQL URL retrieval via Railway API
# - Redis URL retrieval
# - Service health monitoring
# - Automatic environment variable setting

# Manual override still possible:
DATABASE_URL=postgresql://...  # Set this to override auto-config
REDIS_URL=redis://...          # Set this to override auto-config
```

### Railway Environment Variables
```bash
# Required in .env
RAILWAY_TOKEN=your-railway-api-token
RAILWAY_PROJECT_ID=your-project-id
RAILWAY_ENVIRONMENT=production  # optional, defaults to production

# Auto-configured (retrieved from Railway)
DATABASE_URL      # PostgreSQL with pgvector
REDIS_URL        # Redis for caching/queues
```

## PostgreSQL with pgvector Setup

### Database Schema Pattern
```python
# Example table with vector storage
from sqlalchemy import Column, Integer, String, Text, Float, Index
from pgvector.sqlalchemy import Vector
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Story(Base):
    __tablename__ = "stories"
    
    id = Column(Integer, primary_key=True)
    cauldron_id = Column(String, nullable=False, index=True)  # Multi-tenancy
    title = Column(String)
    content = Column(Text)
    embedding = Column(Vector(1536))  # Gemini embedding dimension
    confidence_score = Column(Float)
    
    # Enable Row Level Security
    __table_args__ = (
        Index('idx_stories_cauldron_embedding', 'cauldron_id', 'embedding'),
    )
```

### Vector Search Queries
```python
# Similarity search with tenant isolation
async def search_stories(cauldron_id: str, query_embedding: list[float], limit: int = 10):
    """
    Search for similar stories within a specific cauldron.
    Uses cosine similarity with pgvector.
    """
    result = await db.execute(
        text("""
            SELECT id, title, content, 
                   1 - (embedding <=> :query_embedding) as similarity
            FROM stories
            WHERE cauldron_id = :cauldron_id
            ORDER BY embedding <=> :query_embedding
            LIMIT :limit
        """),
        {
            "cauldron_id": cauldron_id,
            "query_embedding": query_embedding,
            "limit": limit
        }
    )
    return result.fetchall()
```

### pgvector Best Practices
- **Index Types**: Use HNSW for better performance on large datasets
- **Dimension Validation**: Always validate embedding dimensions match your model
- **Batch Operations**: Use COPY for bulk inserts of embeddings
- **Distance Metrics**: Choose between L2 (<->), cosine (<=>), or inner product (<#>)

## Clerk Authentication Integration

### FastAPI Middleware Setup
```python
from clerk_backend_api import Clerk
from fastapi import Depends, HTTPException, Header, status

clerk = Clerk(api_key=os.environ["CLERK_SECRET_KEY"])

async def get_current_user(authorization: str = Header(None)):
    """
    Validate Clerk session and extract user/organization info.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization")
    
    token = authorization.split(" ")[1]
    
    try:
        # Verify the session token with Clerk
        session = await clerk.sessions.verify_token(token)
        
        # Extract organization (cauldron) ID
        organization_id = session.organization_id
        if not organization_id:
            raise HTTPException(status_code=403, detail="No organization access")
            
        return {
            "user_id": session.user_id,
            "cauldron_id": organization_id,
            "email": session.email
        }
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=401, detail="Invalid session")
```

### Frontend Auth Pattern
```typescript
// Next.js with Clerk
import { useAuth, useOrganization } from '@clerk/nextjs';

export function useCurrentCauldron() {
  const { isLoaded, userId } = useAuth();
  const { organization } = useOrganization();
  
  if (!isLoaded || !userId || !organization) {
    return { isLoading: true, cauldronId: null };
  }
  
  return {
    isLoading: false,
    cauldronId: organization.id,
    cauldronName: organization.name
  };
}
```

## Sentry Configuration

### Backend Setup
```python
# In main.py or config.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    environment=os.environ.get("ENVIRONMENT", "development"),
    integrations=[
        FastApiIntegration(transaction_style="endpoint"),
        SqlalchemyIntegration(),
    ],
    traces_sample_rate=0.1,  # Adjust based on volume
    profiles_sample_rate=0.1,
    before_send=filter_sensitive_data,  # Custom function to scrub PII
)

def filter_sensitive_data(event, hint):
    """Remove sensitive data before sending to Sentry."""
    # Implement PII scrubbing logic
    return event
```

### Frontend Setup
```typescript
// In _app.tsx or sentry.client.config.ts
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NEXT_PUBLIC_ENVIRONMENT,
  integrations: [
    new Sentry.BrowserTracing(),
    new Sentry.Replay(),
  ],
  tracesSampleRate: 0.1,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
  beforeSend: (event) => {
    // Filter out sensitive data
    return event;
  },
});
```

### Error Tracking Patterns
```python
# Track specific AI operations
with sentry_sdk.start_transaction(op="ai.generate_story", name="Generate Story"):
    with sentry_sdk.start_span(op="ai.embed", description="Generate embeddings"):
        embedding = await generate_embedding(content)
    
    with sentry_sdk.start_span(op="db.insert", description="Store story"):
        await store_story(story_data)
```

## Railway Deployment Configuration

### railway.toml
```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "./docker/backend.Dockerfile"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3

[[services]]
name = "stonesoup-backend"
```

### Environment Variables (Railway)
```bash
# Database
DATABASE_URL=${{Postgres.DATABASE_URL}}
PGVECTOR_EXTENSION=true

# AI Services
GEMINI_API_KEY=
LANGCHAIN_API_KEY=

# Authentication
CLERK_SECRET_KEY=
CLERK_PUBLISHABLE_KEY=

# Monitoring
SENTRY_DSN=

# Application
ENVIRONMENT=production
CORS_ORIGINS=https://stonesoup.vercel.app
```