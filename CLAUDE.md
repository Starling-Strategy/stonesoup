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

### Gemini API Integration
- Always include error handling for API calls
- Log API usage and costs
- Implement retry logic with exponential backoff
- Document prompt engineering decisions

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

try:
    response = await gemini_client.generate_content(prompt)
    if response.confidence < CONFIDENCE_THRESHOLD:
        # Queue for human review
        await queue_for_review(response)
except APIException as e:
    # Capture in Sentry with context
    sentry_sdk.set_context("ai_request", {
        "cauldron_id": cauldron_id,
        "prompt_type": prompt_type,
        "model": "gemini-pro"
    })
    capture_exception(e)
    
    logger.error(f"Gemini API error: {e}", extra={"cauldron_id": cauldron_id})
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

## Learning Resources Integration
- Include links to relevant documentation in comments
- Explain complex concepts with examples
- Use meaningful variable names that describe purpose
- Write tests that demonstrate intended behavior
- Create documentation that teaches, not just describes

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