# STONESOUP Implementation Plan - Detailed Technical Roadmap

**Last Updated**: Current Session  
**Target**: Working MVP Demo in 3 Weeks  
**Audience**: Technical Team & Stakeholders

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Current State Analysis](#current-state-analysis)
3. [Technical Architecture](#technical-architecture)
4. [Detailed Implementation Plan](#detailed-implementation-plan)
5. [Risk Assessment & Mitigation](#risk-assessment--mitigation)
6. [Questions for Technical Review](#questions-for-technical-review)
7. [Success Metrics](#success-metrics)

## Executive Summary

STONESOUP aims to transform scattered community information into searchable, AI-enhanced member profiles. We're building an MVP that demonstrates the core value proposition: **finding the right community member in seconds, not hours**.

### What We're Building (MVP Scope)
- **Search Interface**: Natural language search for community members
- **AI Summaries**: Auto-generated 3-bullet summaries of expertise
- **Member Profiles**: Rich profiles built from multiple data sources
- **Confidence Scoring**: Transparency about AI-generated content quality

### What We're NOT Building (Yet)
- Complex AI pipelines (using direct API calls instead)
- Multi-tenant architecture (hardcoded for 10KSB pilot)
- Background processing (synchronous for now)
- Advanced features (see [Postponed Features](./postponed-features.md))

## Current State Analysis

**Last Updated**: July 8, 2025 - Demo Mode Implementation

### ✅ Completed Components

#### 1. Project Structure & Configuration
```
✓ Monorepo structure (frontend/backend/agents)
✓ Docker configurations
✓ Environment variable templates (.env.example)
✓ Git repository with proper .gitignore
```

#### 2. Backend Foundation
```python
# What exists:
✓ FastAPI application skeleton
✓ Database models with pgvector support
✓ OpenRouter AI client (tested and working)
✓ Railway auto-configuration system
✓ Sentry error tracking setup

# What works:
- Server starts: uvicorn app.main:app
- Health check endpoint: GET /health
- OpenRouter can generate text and embeddings
- Railway can auto-configure database URLs
```

#### 3. Frontend Foundation
```typescript
// What exists:
✓ Next.js 14 with TypeScript
✓ Clerk authentication pages (/sign-in, /sign-up)
✓ Tailwind CSS configuration
✓ Basic routing structure

// What works:
- Dev server runs: npm run dev
- Auth pages render
- TypeScript compilation
```

#### 4. AI Integration
```python
# Fully implemented OpenRouter client:
- Text generation with multiple models
- Embedding generation (1536 dimensions)
- Cost tracking per request
- Retry logic with exponential backoff
- Test script confirms it works
```

### ✅ Recently Completed (Demo Mode)

1. **Database Running**
   - PostgreSQL installed with pgvector extension ✓
   - All tables created with HNSW indexes ✓
   - Seed data populated (10 members, 50 stories) ✓
   - Multi-tenant schema with cauldron_id ✓

2. **Authentication Flow (Demo Mode)**
   - Clerk middleware implemented with demo bypass ✓
   - Demo mode allows testing without JWT tokens ✓
   - Default cauldron_id set to "10ksb-pilot" ✓
   - Frontend runs without Clerk keys ✓

3. **Search Infrastructure**
   - POST /api/v1/search/quick endpoint exists ✓
   - API responds without authentication ✓
   - Frontend buttons are clickable ✓
   - CORS properly configured ✓

4. **UI Components Built**
   - Search interface with input and buttons ✓
   - Member card components ready ✓
   - Results display components ✓
   - Loading and error states ✓

### ⚠️ Partially Working

1. **Search Implementation**
   - Endpoints exist but search logic incomplete
   - Missing methods: _generate_search_summary, _text_search_members
   - OpenRouter embeddings return 404 (endpoint issue)
   - Need to implement actual search algorithms

2. **Frontend-Backend Integration**
   - API calls work but return errors
   - Data flow established
   - Error handling in place
   - Need to complete search service methods

## Technical Architecture

### Simplified MVP Architecture
```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Next.js 14    │────▶│   FastAPI        │────▶│  PostgreSQL     │
│   + Clerk       │     │   + Pydantic     │     │  + pgvector     │
│   + Tailwind    │     │   + SQLAlchemy   │     │  (3 tables)     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                │
                                ▼
                        ┌──────────────────┐
                        │   OpenRouter     │
                        │ (Gemini + OpenAI)│
                        └──────────────────┘
```

### Data Flow for Search
```
1. User enters query: "sustainable manufacturing"
2. Frontend sends POST /api/v1/search
3. Backend:
   a. Generates embedding for query
   b. Performs vector similarity search
   c. Performs text search
   d. Combines and ranks results
   e. Generates AI summaries for top results
4. Frontend displays member cards with summaries
```

### Database Schema (Minimal MVP)
```sql
-- Table 1: members
CREATE TABLE members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cauldron_id VARCHAR(50) DEFAULT '10ksb-pilot',
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    bio TEXT,
    skills TEXT[], -- Array of skills
    company VARCHAR(255),
    role VARCHAR(255),
    embedding vector(1536), -- For semantic search
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Table 2: stories
CREATE TABLE stories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cauldron_id VARCHAR(50) DEFAULT '10ksb-pilot' NOT NULL, -- CRITICAL: Added for multi-tenancy
    member_id UUID REFERENCES members(id),
    title VARCHAR(500),
    content TEXT NOT NULL,
    summary TEXT, -- AI-generated summary
    confidence_score FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 1),
    source_url TEXT,
    embedding vector(1536) NOT NULL, -- Story content embedding (primary search)
    summary_cache TEXT, -- Cached AI summaries for performance
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table 3: cauldrons (placeholder for future multi-tenancy)
CREATE TABLE cauldrons (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    config JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes optimized for multi-tenancy and search
-- HNSW indexes for better production performance (upgrade from ivfflat)
CREATE INDEX idx_members_cauldron_embedding ON members(cauldron_id) 
    INCLUDE (embedding) USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_stories_cauldron_embedding ON stories(cauldron_id) 
    INCLUDE (embedding) USING hnsw (embedding vector_cosine_ops);

-- Composite indexes for efficient multi-tenant queries
CREATE INDEX idx_stories_cauldron_member ON stories(cauldron_id, member_id);
CREATE INDEX idx_members_cauldron_name ON members(cauldron_id, name);

-- GIN index for skills array search
CREATE INDEX idx_members_skills ON members USING GIN (skills);
```

## Detailed Implementation Plan

### Phase 1: Database Foundation (Days 1-3) ✅ COMPLETED

#### Day 1: PostgreSQL Setup ✅
**Goal**: Get database running with pgvector

```bash
# Step 1: Install PostgreSQL with pgvector
# macOS:
brew install postgresql@15
brew install pgvector

# Ubuntu/Debian:
sudo apt install postgresql-15 postgresql-15-pgvector

# Step 2: Create database
createdb stonesoup_dev
psql stonesoup_dev -c "CREATE EXTENSION vector;"

# Step 3: Verify pgvector
psql stonesoup_dev -c "SELECT vector_version();"
```

**Deliverables**:
- [x] PostgreSQL running locally
- [x] pgvector extension installed
- [x] Connection verified from Python

**Answers**:
- Docker not used for simplicity in MVP
- Local PostgreSQL installation working well

#### Day 2: Schema Implementation
**Goal**: Create tables and initial migrations

```python
# app/models/member.py with learning notes
class Member(Base):
    """
    Member model representing a community member.
    
    Learning Note: Vector Embeddings
    ================================
    The 'embedding' field stores a 1536-dimensional vector that represents
    the semantic meaning of the member's profile. This allows us to find
    similar members using mathematical distance calculations.
    
    Think of it like plot points on a map - members with similar expertise
    will be "closer" in this 1536-dimensional space.
    """
    __tablename__ = "members"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cauldron_id = Column(String(50), default="10ksb-pilot", nullable=False)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    bio = Column(Text)
    skills = Column(ARRAY(String), default=[])  # PostgreSQL array type
    company = Column(String(255))
    role = Column(String(255))
    
    # Vector embedding for semantic search (member profile aggregation)
    # 1536 dimensions = OpenAI text-embedding-3-small output size
    # Learning Note: This represents the member's overall professional identity
    # Generated from: bio + skills + role. Used for "find similar members"
    embedding = Column(Vector(1536))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    stories = relationship("Story", back_populates="member")
```

**Deliverables**:
- [ ] SQLAlchemy models created
- [ ] Alembic migrations generated
- [ ] Tables created in database
- [ ] Indexes optimized for search

#### Day 3: Seed Data & Testing
**Goal**: Create sample data for development

```python
# scripts/seed_data.py
async def create_sample_members():
    """
    Create 10 diverse sample members for testing.
    
    Learning Note: Embedding Generation
    ==================================
    We generate embeddings for each member based on their bio and skills.
    This is a one-time cost per member (~$0.0001) but enables instant
    semantic search later.
    """
    sample_members = [
        {
            "name": "Elena Rodriguez",
            "email": "elena@example.com",
            "bio": "Pioneered sustainable manufacturing practices...",
            "skills": ["sustainable manufacturing", "workforce development", "lean processes"],
            "company": "GreenTech Industries",
            "role": "VP of Operations"
        },
        # ... 9 more diverse profiles
    ]
    
    for member_data in sample_members:
        # Generate embedding from bio + skills
        text = f"{member_data['bio']} Skills: {', '.join(member_data['skills'])}"
        embedding = await openrouter_client.generate_embedding(text)
        
        member = Member(**member_data, embedding=embedding.embedding)
        db.add(member)
    
    await db.commit()
```

**Deliverables**:
- [ ] Seed script created
- [ ] 10 sample members with embeddings
- [ ] 3-5 stories per member
- [ ] Verify vector search works

### Phase 2: Authentication Implementation (Days 4-5)

#### Day 4: Backend Authentication
**Goal**: Implement Clerk JWT verification

```python
# app/core/security.py
async def get_current_user(
    authorization: str = Header(None)
) -> dict:
    """
    Verify Clerk JWT and extract user info.
    
    Learning Note: JWT Authentication Flow
    =====================================
    1. User logs in via Clerk (handled by frontend)
    2. Clerk issues a JWT token
    3. Frontend sends token in Authorization header
    4. We verify the token using Clerk's public key
    5. Extract user info and organization (cauldron)
    
    This gives us secure, stateless authentication.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        # Verify with Clerk's public key
        payload = jwt.decode(
            token,
            key=CLERK_PUBLIC_KEY,
            algorithms=["RS256"],
            audience=CLERK_AUDIENCE
        )
        
        return {
            "user_id": payload["sub"],
            "email": payload.get("email"),
            "cauldron_id": payload.get("org_id", "10ksb-pilot")
        }
    except jwt.InvalidTokenError as e:
        raise HTTPException(401, f"Invalid token: {str(e)}")
```

**Deliverables**:
- [ ] JWT verification working
- [ ] Protected endpoint example
- [ ] User context extraction
- [ ] Error handling

#### Day 5: Frontend Authentication
**Goal**: Complete auth flow end-to-end

```typescript
// app/providers/auth-provider.tsx
export function AuthProvider({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider
      publishableKey={process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY!}
      appearance={{
        // Custom theme matching our design
        elements: {
          formButtonPrimary: 'bg-blue-600 hover:bg-blue-700',
        }
      }}
    >
      {children}
    </ClerkProvider>
  );
}

// hooks/use-api.ts
export function useAPI() {
  const { getToken } = useAuth();
  
  const apiCall = async (endpoint: string, options: RequestInit = {}) => {
    const token = await getToken();
    
    return fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options.headers,
      }
    });
  };
  
  return { apiCall };
}
```

**Deliverables**:
- [ ] Clerk provider configured
- [ ] Protected routes working
- [ ] API client with auth
- [ ] Login/logout flow tested

### Phase 3: Search Implementation (Days 6-10)

#### Day 6-7: Search Endpoints
**Goal**: Build hybrid search API

```python
# app/api/v1/endpoints/search.py
@router.post("/search", response_model=SearchResponse)
async def search_members(
    query: SearchQuery,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Hybrid search combining text and vector similarity.
    
    Learning Note: Hybrid Search Strategy
    ====================================
    We use a two-pronged approach:
    1. Text search: Finds exact matches in names, companies, skills
    2. Vector search: Finds conceptually similar members
    
    Example: Searching "AI in manufacturing"
    - Text search finds: Members with "AI" or "manufacturing" in profile
    - Vector search finds: Members with related concepts like "automation",
      "machine learning", "industry 4.0", etc.
    
    We combine both with weighted scoring for best results.
    """
    
    # Step 1: Generate embedding for semantic search
    query_embedding = await openrouter_client.generate_embedding(query.text)
    
    # Step 2: Vector similarity search (search stories, not members!)
    # Learning Note: We search story embeddings for specific expertise
    # This is more precise than searching member profile embeddings
    story_results = await db.execute(
        select(Story, Member)
        .join(Member)
        .where(Story.cauldron_id == current_user["cauldron_id"])
        .order_by(Story.embedding.cosine_distance(query_embedding.embedding))
        .limit(20)
    )
    
    # Step 3: Text search (PostgreSQL full-text search) 
    # Also include cauldron_id for multi-tenancy
    text_results = await db.execute(
        select(Member)
        .where(
            and_(
                Member.cauldron_id == current_user["cauldron_id"],
                or_(
                    Member.name.ilike(f"%{query.text}%"),
                    Member.bio.ilike(f"%{query.text}%"),
                    Member.skills.contains([query.text])
                )
            )
        )
        .limit(20)
    )
    
    # Step 4: Combine and rank results
    # Group story results by member (since multiple stories per member)
    story_grouped = group_stories_by_member(story_results)
    
    combined_results = combine_search_results(
        story_grouped,  # Members from story search
        text_results.scalars().all(),  # Members from text search
        weights=(0.7, 0.3)  # Favor semantic similarity from stories
    )
    
    # Step 5: Generate AI summaries for top results
    enriched_results = []
    for member, relevant_story in combined_results[:10]:
        # Generate summary focused on the query, using the most relevant story
        summary = await generate_member_summary(member, query.text, relevant_story)
        enriched_results.append({
            "member": member,
            "relevant_story": relevant_story,  # Show which story matched
            "summary": summary,
            "relevance_score": calculate_relevance(member, query.text)
        })
    
    return SearchResponse(results=enriched_results)
```

**Deliverables**:
- [ ] POST /api/v1/search endpoint
- [ ] GET /api/v1/members endpoint
- [ ] Hybrid search algorithm
- [ ] Relevance scoring
- [ ] Response pagination

#### Day 8-9: AI Summary Generation
**Goal**: Create compelling member summaries

```python
async def generate_member_summary(
    member: Member, 
    query: str
) -> MemberSummary:
    """
    Generate a 3-bullet summary highlighting relevant expertise.
    
    Learning Note: Prompt Engineering
    ================================
    The prompt is carefully crafted to:
    1. Focus on relevance to the search query
    2. Extract concrete achievements
    3. Maintain factual accuracy
    4. Be concise but informative
    
    We include the query to ensure summaries are contextual.
    """
    
    prompt = f"""
    Based on this community member's profile, create a 3-bullet summary 
    highlighting their expertise relevant to "{query}".
    
    Member Profile:
    Name: {member.name}
    Role: {member.role} at {member.company}
    Bio: {member.bio}
    Skills: {', '.join(member.skills)}
    
    Requirements:
    - Exactly 3 bullets
    - Each bullet should be specific and concrete
    - Focus on achievements and expertise
    - Relate to the search query when possible
    - Be factual, not promotional
    
    Format as:
    • First bullet
    • Second bullet  
    • Third bullet
    """
    
    response = await openrouter_client.generate_text(
        prompt=prompt,
        temperature=0.3,  # Lower temperature for factual consistency
        model="google/gemini-pro-1.5"
    )
    
    return MemberSummary(
        bullets=parse_bullets(response.text),
        confidence_score=response.confidence_score,
        generated_at=datetime.utcnow()
    )
```

**Deliverables**:
- [ ] Summary generation function
- [ ] Prompt templates
- [ ] Confidence scoring
- [ ] Caching strategy
- [ ] Error handling

#### Day 10: Frontend Search Interface
**Goal**: Build the search UI

```typescript
// app/search/page.tsx
export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const { apiCall } = useAPI();
  
  const handleSearch = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await apiCall('/api/v1/search', {
        method: 'POST',
        body: JSON.stringify({ text: query })
      });
      
      const data = await response.json();
      setResults(data.results);
    } catch (error) {
      console.error('Search failed:', error);
      // Show error toast
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Search Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-4">Find Community Members</h1>
        <form onSubmit={handleSearch} className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Try 'sustainable manufacturing' or 'AI expertise'..."
            className="w-full px-4 py-3 border rounded-lg pr-12"
          />
          <button
            type="submit"
            disabled={loading}
            className="absolute right-2 top-2 p-2 bg-blue-600 text-white rounded"
          >
            {loading ? <Spinner /> : <SearchIcon />}
          </button>
        </form>
      </div>
      
      {/* Results */}
      <div className="space-y-4">
        {results.map((result) => (
          <MemberCard key={result.member.id} result={result} />
        ))}
      </div>
    </div>
  );
}

// components/member-card.tsx
function MemberCard({ result }: { result: SearchResult }) {
  const { member, summary, relevance_score } = result;
  
  return (
    <div className="border rounded-lg p-6 hover:shadow-lg transition">
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-xl font-semibold">{member.name}</h3>
          <p className="text-gray-600">{member.role} at {member.company}</p>
        </div>
        <div className="flex items-center gap-2">
          <ConfidenceIndicator score={summary.confidence_score} />
          <button className="text-gray-400 hover:text-yellow-500">
            <StarIcon className="w-5 h-5" />
          </button>
        </div>
      </div>
      
      {/* AI Summary */}
      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-700 mb-2">
          AI Summary
        </h4>
        <ul className="space-y-1">
          {summary.bullets.map((bullet, i) => (
            <li key={i} className="flex items-start">
              <span className="text-blue-600 mr-2">•</span>
              <span className="text-gray-800">{bullet}</span>
            </li>
          ))}
        </ul>
      </div>
      
      {/* Skills */}
      <div className="flex flex-wrap gap-2">
        {member.skills.map((skill) => (
          <span
            key={skill}
            className="px-3 py-1 bg-gray-100 rounded-full text-sm"
          >
            {skill}
          </span>
        ))}
      </div>
    </div>
  );
}
```

**Deliverables**:
- [ ] Search interface component
- [ ] Member card component
- [ ] Loading states
- [ ] Error handling
- [ ] Responsive design

### Phase 4: Polish & Deploy (Days 11-14) ⬅️ CURRENT PHASE

#### Day 11-12: Testing & Bug Fixes
**Goal**: Ensure everything works end-to-end

**Test Checklist**:
- [x] Demo mode authentication working
- [ ] Search returns relevant results (in progress)
- [ ] AI summaries generate correctly
- [ ] Confidence scores display
- [x] Error states handled gracefully
- [x] Mobile responsive
- [ ] Performance acceptable (<2s search)

**Current Status (July 8, 2025)**:
- Running in demo mode without Clerk authentication
- Frontend buttons are clickable and trigger API calls
- Search service needs implementation of missing methods
- OpenRouter embeddings endpoint needs correction

#### Day 13: Railway Deployment
**Goal**: Deploy to production

```yaml
# railway.yaml
services:
  backend:
    build:
      dockerfile: src/backend/Dockerfile
    env:
      - DATABASE_URL=${{Postgres.DATABASE_URL}}
      - REDIS_URL=${{Redis.REDIS_URL}}
    healthcheck:
      path: /health
      
  frontend:
    build:
      dockerfile: src/frontend/Dockerfile
    env:
      - NEXT_PUBLIC_API_BASE_URL=${{backend.RAILWAY_PUBLIC_URL}}
      
databases:
  postgres:
    plugin: postgresql
    version: 15
    
  redis:
    plugin: redis
```

**Deployment Steps**:
1. Create Railway project
2. Add PostgreSQL service
3. Deploy backend
4. Deploy frontend to Vercel
5. Configure custom domain
6. Test in production

#### Day 14: Demo Preparation
**Goal**: Prepare for stakeholder demo

**Demo Checklist**:
- [ ] Import 50 real member profiles
- [ ] Generate stories for each
- [ ] Prepare demo script
- [ ] Test all happy paths
- [ ] Identify impressive examples
- [ ] Prepare backup plan

### Phase 5: Documentation & Handoff (Days 15)

**Documentation Deliverables**:
- [ ] API documentation (OpenAPI)
- [ ] Deployment guide
- [ ] Architecture diagrams
- [ ] Troubleshooting guide
- [ ] Future roadmap

## Risk Assessment & Mitigation

### High-Risk Areas

1. **Vector Search Performance**
   - **Risk**: Slow queries with more data
   - **Mitigation**: Proper indexing, query optimization
   - **Backup**: Limit to 1000 members for demo

2. **AI Generation Costs**
   - **Risk**: Expensive if generating for all results
   - **Mitigation**: Cache summaries, generate only for top 10
   - **Backup**: Pre-generate summaries for demo

3. **Clerk Integration**
   - **Risk**: Authentication complexity
   - **Mitigation**: Extensive testing, clear error messages
   - **Backup**: Basic auth for demo if needed

4. **Deployment Issues**
   - **Risk**: Railway configuration problems
   - **Mitigation**: Test deployment early (Day 10)
   - **Backup**: Local demo option

## 🚩 Critical Issues Addressed from Technical Review

### Flag 1: Multi-Tenancy Preparation ✅ FIXED
**Issue**: Missing `cauldron_id` in stories table would cause massive migration pain later  
**Solution**: Added `cauldron_id NOT NULL` to ALL tables from day one  
**Reference**: [ADR-002: Multi-Tenancy Preparation](./architecture/decisions/ADR-002-multi-tenancy-preparation.md)

### Flag 2: Embedding Strategy Clarified ✅ IMPROVED  
**Issue**: Unclear what member embeddings represent vs story embeddings  
**Solution**: Dual embedding strategy - stories for expertise search, members for similarity  
**Reference**: [ADR-003: Embedding Strategy](./architecture/decisions/ADR-003-embedding-strategy.md)

### Recommendation: HNSW Index ✅ IMPLEMENTED
**Issue**: ivfflat indexes may not be optimal for production  
**Solution**: Updated schema to use HNSW indexes for better speed/accuracy balance

### Recommendation: Database Caching ✅ IMPLEMENTED  
**Issue**: Need caching strategy that doesn't add complexity  
**Solution**: Added `summary_cache` field to stories table, Redis later if needed

## Questions for Technical Review

### Architecture Questions ✅ ADDRESSED
1. **Database Choice**: PostgreSQL with pgvector confirmed as optimal choice
2. **Search Strategy**: Story-first search implemented with member profile fallback  
3. **Caching Strategy**: Database caching with `summary_cache` field (Redis later if needed)
4. **Multi-tenancy**: Schema designed for multi-tenancy, hardcoded logic for MVP

### NEW Architecture Questions
1. **Vector Index Type**: Start with HNSW instead of ivfflat for better production performance?
2. **Story Grouping**: How to handle members with many stories - show top story or aggregate?
3. **Cache Invalidation**: When should we regenerate cached summaries?
4. **Search Ranking**: Should story recency factor into relevance scoring?

### Implementation Questions
1. **Testing Strategy**: What's the minimum test coverage needed for MVP?
2. **Error Handling**: How detailed should error messages be for users vs logs?
3. **Rate Limiting**: Should we implement rate limiting for the search API?
4. **Monitoring**: Beyond Sentry, what metrics should we track?

### AI/ML Questions
1. **Embedding Model**: OpenAI text-embedding-3-small (1536 dims) vs alternatives?
2. **Summary Quality**: How do we measure/ensure summary quality?
3. **Confidence Scoring**: Our approach is simple - should it be more sophisticated?
4. **Prompt Engineering**: Should prompts be configurable per cauldron?

### Deployment Questions
1. **Environment Strategy**: How many environments (dev, staging, prod)?
2. **Database Migrations**: Automated in deployment or manual?
3. **Secrets Management**: Railway's approach sufficient or need HashiCorp Vault?
4. **Backup Strategy**: How often should we backup the database?

## Success Metrics

### Technical Success (Week 3)
- [ ] Search returns relevant results in <2 seconds
- [ ] 95% uptime during demo week
- [ ] Zero critical bugs in production
- [ ] All core features working end-to-end

### User Success (Demo)
- [ ] Users find relevant members in <30 seconds
- [ ] AI summaries rated helpful by test users
- [ ] Confidence scores understood and trusted
- [ ] Overall positive feedback from stakeholders

### Learning Success
- [ ] Code is understandable by junior developers
- [ ] Documentation answers common questions
- [ ] Architecture decisions are clear
- [ ] Extension points are obvious

## Next Steps After MVP

Based on feedback, prioritize:
1. **Enhanced Search**: Facets, filters, sorting
2. **Story Pipeline**: Automated ingestion from sources
3. **User Features**: Profile claiming, edit suggestions
4. **Scale Preparation**: Multi-tenancy, caching, optimization

---

## Appendix: Daily Standup Template

```markdown
**Day X Update**

**Completed**:
- [ ] Task 1
- [ ] Task 2

**In Progress**:
- [ ] Current task (X% complete)

**Blockers**:
- Issue: [Description]
- Need: [What would unblock]

**Tomorrow**:
- [ ] Next task
- [ ] Following task

**Confidence**: Green/Yellow/Red
```

---

This plan represents our path from current state to working MVP. We welcome all feedback and questions to ensure we build the right thing, the right way.