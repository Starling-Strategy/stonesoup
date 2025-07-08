"""Main API router that combines all v1 endpoints."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, members, search, stories

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(members.router, prefix="/members", tags=["members"])
api_router.include_router(stories.router, prefix="/stories", tags=["stories"])
api_router.include_router(search.router, prefix="/search", tags=["search"])