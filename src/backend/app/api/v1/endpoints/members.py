"""
Member endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.base import get_db
from app.models.member import Member
from app.core.security import get_current_user_id

router = APIRouter()


@router.get("/", response_model=List[dict])
async def get_members(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_available: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
) -> List[dict]:
    """Get list of members."""
    query = select(Member).where(Member.is_active == True)
    
    if is_available is not None:
        query = query.where(Member.is_available == is_available)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    members = result.scalars().all()
    
    return [member.to_dict() for member in members]


@router.get("/me", response_model=dict)
async def get_my_profile(
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Get current user's member profile."""
    query = select(Member).where(Member.clerk_user_id == current_user_id)
    result = await db.execute(query)
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(status_code=404, detail="Member profile not found")
    
    return member.to_dict()


@router.get("/{member_id}", response_model=dict)
async def get_member(
    member_id: str,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Get a specific member by ID."""
    query = select(Member).where(Member.id == member_id)
    result = await db.execute(query)
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    return member.to_dict()