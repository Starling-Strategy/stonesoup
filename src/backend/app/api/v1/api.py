"""
API v1 router configuration.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import members, auth, search

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(members.router, prefix="/members", tags=["members"])
api_router.include_router(search.router, prefix="/search", tags=["search"])