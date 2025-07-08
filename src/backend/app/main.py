"""
Main FastAPI application for STONESOUP.

This module sets up the FastAPI application with:
- CORS configuration
- Sentry error tracking
- API routers
- Health check endpoint
- Startup/shutdown events
"""
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.core.config import settings
from app.core.auto_config import ensure_railway_config
from app.api.v1.api import api_router
from app.db.session import init_db
from app.middleware.auth import ClerkJWTMiddleware


# Initialize Sentry for error tracking
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        _experiments={
            "profiles_sample_rate": 0.1,
        },
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle.
    
    This context manager handles:
    - Database initialization on startup
    - Resource cleanup on shutdown
    """
    # Startup
    print("🚀 Starting STONESOUP backend...")
    
    # Auto-configure from Railway if available
    print("🔧 Configuring database connections...")
    await ensure_railway_config()
    
    # Initialize database (create tables, check migrations, etc.)
    await init_db()
    
    print("✅ STONESOUP backend started successfully!")
    
    yield
    
    # Shutdown
    print("👋 Shutting down STONESOUP backend...")
    # Add any cleanup code here (close connections, etc.)


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
    STONESOUP is an AI-powered community intelligence platform that transforms 
    scattered information into rich, searchable, narrative-driven profiles of 
    community members.
    
    ## Key Features
    
    * **Multi-tenant Architecture** - Complete data isolation per organization (cauldron)
    * **AI-Powered Story Generation** - Automatic narrative creation from various sources
    * **Semantic Search** - Find members by expertise using natural language
    * **Confidence Scoring** - All AI-generated content includes confidence metrics
    * **Human-in-the-Loop** - Review queues for low-confidence content
    
    ## Authentication
    
    This API uses Clerk for authentication. Include your JWT token in the 
    Authorization header as a Bearer token.
    
    ## Multi-tenancy
    
    All endpoints are scoped to your organization (cauldron). The API automatically
    filters data based on your organization membership.
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add Clerk JWT Authentication Middleware FIRST
# This middleware handles JWT verification for all protected endpoints
# Note: Middleware is executed in reverse order of registration
app.add_middleware(ClerkJWTMiddleware)

# Configure CORS AFTER auth middleware
# This ensures CORS headers are added to responses after auth processing
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom exception handler for better error responses
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for uncaught exceptions.
    
    This ensures that all errors are:
    1. Logged to Sentry
    2. Returned in a consistent format
    3. Don't leak sensitive information
    """
    # Log to Sentry
    sentry_sdk.capture_exception(exc)
    
    # Return generic error response
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred",
            "type": "internal_server_error",
            "sentry_event_id": sentry_sdk.last_event_id(),
        }
    )


# Health check endpoint
@app.get(
    "/health",
    tags=["Health"],
    summary="Health Check",
    description="Check if the API is running and healthy",
)
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint.
    
    This endpoint is used by:
    - Docker health checks
    - Load balancers
    - Monitoring systems
    
    Returns basic information about the service status.
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


# Include API routers
app.include_router(api_router, prefix=settings.API_V1_STR)


# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> Dict[str, str]:
    """
    Root endpoint.
    
    Provides basic information about the API.
    """
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": "STONESOUP - AI-powered community intelligence platform",
        "docs": "/docs",
        "health": "/health",
    }


# Startup event for logging
@app.on_event("startup")
async def startup_event():
    """Log startup information."""
    print(f"""
    ╔══════════════════════════════════════════╗
    ║         STONESOUP Backend API            ║
    ╠══════════════════════════════════════════╣
    ║  Version: {settings.VERSION:<30} ║
    ║  Environment: {settings.ENVIRONMENT:<26} ║
    ║  API Docs: http://localhost:8000/docs    ║
    ╚══════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    # This is only for development
    # In production, use: uvicorn app.main:app
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )