# StoneSoup Backend

FastAPI backend for the StoneSoup AI Talent Marketplace.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and fill in your configuration.

4. Run database migrations:
```bash
alembic upgrade head
```

5. Start the development server:
```bash
uvicorn app.main:app --reload --port 8000
```

## Project Structure

```
backend/
   app/
      api/          # API endpoints
      core/         # Core functionality (config, security)
      models/       # SQLAlchemy models
      schemas/      # Pydantic schemas
      services/     # Business logic
      db/           # Database configuration
      ai/           # AI/LLM integrations
      background/   # Background tasks
      main.py       # FastAPI app
   alembic/          # Database migrations
   tests/            # Test files
   requirements.txt  # Python dependencies
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc