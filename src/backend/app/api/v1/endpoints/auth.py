"""
Authentication endpoints.
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any

from app.core.security import get_current_user, get_current_user_id

router = APIRouter()


@router.get("/me")
async def get_current_user_info(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get current authenticated user information."""
    return {
        "user": current_user,
        "status": "authenticated"
    }


@router.get("/verify")
async def verify_token(
    user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """Verify authentication token."""
    return {
        "user_id": user_id,
        "status": "valid"
    }