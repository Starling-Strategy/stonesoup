# STONESOUP MVP Action Plan - Search Interface for 10KSB Alumni

## Executive Summary
Build a minimal viable product (MVP) search interface for Goldman Sachs 10,000 Small Businesses alumni data. The system will allow users to search through 16,982 alumni profiles and their associated companies, with AI-powered summaries.

## Current State
- **Database**: Live PostgreSQL on Railway with `murmuration` schema containing:
  - 16,982 people (alumni profiles)
  - 16,956 companies
  - 65 stories
  - No vector embeddings yet
- **Frontend**: Next.js 15 with shadcn/ui components partially built
- **Backend**: FastAPI structure exists but needs simplification
- **Status**: No working connection between frontend and backend

## MVP Goal
Create a working search interface that:
1. Searches alumni by name, company, location, or skills
2. Displays results with member cards
3. Shows basic AI-generated summaries (using dummy data for now)
4. Runs locally without complex infrastructure

## Simplifications for MVP
- **REMOVE**: Redis, Celery, LangGraph agents, multi-tenancy, complex authentication
- **USE**: Direct database queries, simple API endpoints, local development only
- **DEFER**: Vector search, embeddings, real AI integration

## Step-by-Step Implementation Plan

### Phase 1: Backend Setup (2 hours)

#### 1.1 Simplify FastAPI Backend
```bash
cd src/backend
```

**Tasks:**
1. Create `app/api/v1/search_simple.py` with basic endpoints:
   - `GET /api/v1/search/people?q={query}` - Search people by name
   - `GET /api/v1/people/{id}` - Get person details
   - `GET /api/v1/people` - List all people (paginated)

2. Create `app/models/murmuration.py` to map existing database:
   ```python
   # SQLAlchemy models for murmuration schema
   class Person(Base):
       __tablename__ = "people"
       __table_args__ = {"schema": "murmuration"}
       
       id = Column(Integer, primary_key=True)
       first_name = Column(String)
       last_name = Column(String)
       email = Column(String)
       city = Column(String)
       state = Column(String)
       cohort_year = Column(Integer)
       # ... other fields
   ```

3. Update `app/core/config.py`:
   - Remove Redis, Celery configuration
   - Simplify to just DATABASE_URL and basic settings

4. Create `app/services/search_service.py`:
   - Simple SQL-based search using ILIKE
   - Return mock AI summaries for now

#### 1.2 Test Backend Locally
```bash
# Install dependencies
uv pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv

# Run server
uvicorn app.main:app --reload --port 8000
```

Test endpoints:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/api/v1/search/people?q=john
- http://localhost:8000/api/v1/people/1

### Phase 2: Frontend Connection (2 hours)

#### 2.1 Update Frontend API Client
```bash
cd src/frontend
```

**Tasks:**
1. Create `lib/api/search.ts`:
   ```typescript
   const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
   
   export async function searchPeople(query: string) {
     const response = await fetch(`${API_BASE}/api/v1/search/people?q=${query}`);
     return response.json();
   }
   ```

2. Update `components/search/search-bar.tsx`:
   - Remove complex state management
   - Direct API calls on search

3. Update `components/search/member-card.tsx`:
   - Display real data fields from murmuration schema
   - Show mock AI summary

4. Create simple search page `app/page.tsx`:
   - Search bar at top
   - Results grid below
   - No authentication required

#### 2.2 Configure CORS in Backend
Update FastAPI to allow frontend connections:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Phase 3: Data Display (1 hour)

#### 3.1 Create Member Profile Display
1. Map murmuration fields to display:
   - Name: `first_name + last_name`
   - Company: Join with companies table
   - Location: `city, state`
   - Cohort: `cohort_year`
   - Email/Phone: Hide for privacy in MVP

2. Add mock AI insights:
   ```typescript
   const mockInsights = [
     "Experienced small business owner",
     "Active in the alumni community",
     "Graduated from Cohort {year}"
   ];
   ```

#### 3.2 Implement Search Results
- Display 20 results per page
- Show: Name, Company, Location, Cohort
- Click to expand for more details

### Phase 4: Run and Test (30 minutes)

#### 4.1 Start Both Services
Terminal 1 - Backend:
```bash
cd src/backend
source .venv/bin/activate  # or: uv venv && source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Terminal 2 - Frontend:
```bash
cd src/frontend
npm install
npm run dev
```

#### 4.2 Test Search Functionality
1. Navigate to http://localhost:3000
2. Search for common names (e.g., "John", "Smith", "New York")
3. Verify results display correctly
4. Test pagination

## File Structure for MVP

```
src/backend/
  app/
    api/v1/
      search_simple.py      # NEW: Simple search endpoints
    models/
      murmuration.py        # NEW: Map existing DB schema
    services/
      search_service.py     # NEW: Basic search logic
    core/
      config.py            # MODIFY: Remove Redis/Celery
    main.py               # MODIFY: Simplify, add CORS

src/frontend/
  app/
    page.tsx              # MODIFY: Simple search page
  components/
    search/
      search-bar.tsx      # MODIFY: Direct API calls
      member-card.tsx     # MODIFY: Display real data
  lib/
    api/
      search.ts          # NEW: API client functions
```

## Database Queries for Reference

```sql
-- Search people by name
SELECT p.*, c.name as company_name 
FROM murmuration.people p
LEFT JOIN murmuration.companies c ON p.id_primary_company = c.id
WHERE p.first_name ILIKE '%john%' 
   OR p.last_name ILIKE '%john%'
LIMIT 20;

-- Get person with company
SELECT p.*, c.*, s.title as story_title
FROM murmuration.people p
LEFT JOIN murmuration.companies c ON p.id_primary_company = c.id
LEFT JOIN murmuration.people_stories ps ON p.id = ps.id_person
LEFT JOIN murmuration.stories s ON ps.id_story = s.id
WHERE p.id = 123;
```

## Success Criteria
1. ✅ Can search for alumni by name
2. ✅ Results display within 2 seconds
3. ✅ Shows person name, company, location
4. ✅ Runs locally without Docker/Redis/Celery
5. ✅ Frontend and backend communicate successfully

## Next Steps After MVP
1. Add real AI summaries using OpenRouter
2. Implement vector search with pgvector
3. Add authentication with Clerk
4. Deploy to Railway (backend) and Vercel (frontend)
5. Import more comprehensive data

## Quick Start Commands
```bash
# Terminal 1 - Backend
cd src/backend
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
uvicorn app.main:app --reload

# Terminal 2 - Frontend  
cd src/frontend
npm install
npm run dev

# Visit http://localhost:3000
```

## Time Estimate
- Total: 5-6 hours for working MVP
- Backend setup: 2 hours
- Frontend connection: 2 hours
- Data display: 1 hour
- Testing/debugging: 30 minutes

## Key Decisions
1. **No vector search initially** - Use SQL ILIKE for text search
2. **Mock AI summaries** - Hardcoded insights to demonstrate UI
3. **No authentication** - Open access for local development
4. **Direct DB queries** - Skip ORM complexity for reads
5. **Minimal dependencies** - Just FastAPI, SQLAlchemy, Next.js

This plan prioritizes getting a working search interface quickly while laying groundwork for future enhancements.