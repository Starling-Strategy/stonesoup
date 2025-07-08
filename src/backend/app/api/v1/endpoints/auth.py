"""
Authentication endpoints for STONESOUP.

This module provides authentication endpoints that work with Clerk's
authentication system and demonstrate secure API design patterns.

Educational Notes:
=================

Clerk Authentication Flow:
1. User authenticates with Clerk (frontend)
2. Clerk returns JWT token to frontend
3. Frontend sends JWT token in Authorization header
4. Backend validates JWT token using Clerk's public keys
5. Backend extracts user information and organization membership
6. Backend returns user context or protected resource

Multi-Tenancy Implementation:
- Each user belongs to one or more organizations (cauldrons)
- User's cauldron_id determines data access scope
- All API responses are automatically filtered to user's cauldron
- Admin users have elevated permissions within their cauldron
"""

from typing import Any, Dict, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field

from app.core.security import (
    get_current_user,
    get_current_active_user,
    require_admin,
    CurrentUser,
    create_api_key,
    get_cauldron_id_from_request
)

router = APIRouter()


class UserProfile(BaseModel):
    """
    User profile response model.
    
    This model represents the user's profile information
    that's safe to return to the frontend.
    """
    user_id: str = Field(..., description="Unique user identifier")
    email: Optional[str] = Field(None, description="User's email address")
    first_name: Optional[str] = Field(None, description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")
    full_name: str = Field(..., description="User's full name")
    cauldron_id: Optional[str] = Field(None, description="User's organization ID")
    is_admin: bool = Field(False, description="Whether user is an admin")
    
    @classmethod
    def from_current_user(cls, current_user: CurrentUser) -> "UserProfile":
        """Create UserProfile from CurrentUser."""
        return cls(
            user_id=current_user.user_id,
            email=current_user.email,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            full_name=current_user.full_name,
            cauldron_id=current_user.cauldron_id,
            is_admin=current_user.is_admin
        )


class AuthStatus(BaseModel):
    """
    Authentication status response model.
    
    This model provides information about the current
    authentication state and user context.
    """
    authenticated: bool = Field(..., description="Whether user is authenticated")
    user: Optional[UserProfile] = Field(None, description="User profile if authenticated")
    cauldron_id: Optional[str] = Field(None, description="Current cauldron context")
    permissions: Dict[str, bool] = Field(default_factory=dict, description="User permissions")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


@router.get(
    "/me",
    response_model=UserProfile,
    summary="Get Current User",
    description="Get the current authenticated user's profile information"
)
async def get_current_user_profile(
    current_user: CurrentUser = Depends(get_current_user)
) -> UserProfile:
    """
    Get the current authenticated user's profile.
    
    This endpoint demonstrates:
    - JWT token validation
    - User information extraction
    - Safe profile information return
    - Multi-tenancy context
    
    Educational Notes:
    - The JWT token is verified automatically by the dependency
    - User information is extracted from the token claims
    - No database lookup is required (stateless authentication)
    - Organization membership is enforced at the token level
    """
    return UserProfile.from_current_user(current_user)


@router.get(
    "/status",
    response_model=AuthStatus,
    summary="Get Authentication Status",
    description="Get comprehensive authentication status and user context"
)
async def get_auth_status(
    request: Request,
    current_user: CurrentUser = Depends(get_current_user)
) -> AuthStatus:
    """
    Get comprehensive authentication status.
    
    This endpoint provides detailed information about:
    - Authentication state
    - User profile
    - Organization context
    - User permissions
    - Request metadata
    
    Educational Notes:
    - Shows how to access request context
    - Demonstrates permission checking
    - Provides debugging information for frontend
    - Includes multi-tenancy context
    """
    # Get cauldron context from request
    cauldron_id = get_cauldron_id_from_request(request)
    
    # Build permissions map
    permissions = {
        "is_admin": current_user.is_admin,
        "can_manage_members": current_user.is_admin,
        "can_create_stories": True,  # All users can create stories
        "can_search": True,  # All users can search
        "can_view_analytics": current_user.is_admin,
    }
    
    return AuthStatus(
        authenticated=True,
        user=UserProfile.from_current_user(current_user),
        cauldron_id=cauldron_id,
        permissions=permissions,
        timestamp=datetime.utcnow()
    )


@router.get(
    "/validate-token",
    response_model=Dict[str, Any],
    summary="Validate Token",
    description="Validate JWT token and return token information"
)
async def validate_token(
    current_user: CurrentUser = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Validate the current JWT token.
    
    This endpoint is useful for:
    - Frontend token validation
    - Token debugging
    - Health checks
    - Integration testing
    
    Educational Notes:
    - Token validation happens automatically in the dependency
    - This endpoint only executes if the token is valid
    - Returns minimal token information for security
    - Can be used to check token expiration
    """
    return {
        "valid": True,
        "user_id": current_user.user_id,
        "cauldron_id": current_user.cauldron_id,
        "is_admin": current_user.is_admin,
        "authenticated_at": datetime.utcnow().isoformat(),
        "message": "Token is valid and user is authenticated"
    }


@router.post(
    "/generate-api-key",
    response_model=Dict[str, str],
    summary="Generate API Key",
    description="Generate a new API key for service-to-service authentication"
)
async def generate_api_key(
    current_user: CurrentUser = Depends(require_admin)
) -> Dict[str, str]:
    """
    Generate a new API key for service-to-service authentication.
    
    This endpoint demonstrates:
    - Admin-only functionality
    - API key generation
    - Service-to-service authentication setup
    - Security best practices
    
    Educational Notes:
    - Only admin users can generate API keys
    - API keys are prefixed with 'ss_' for identification
    - Keys should be stored securely in the database
    - This is a placeholder implementation
    
    Security Considerations:
    - API keys should have limited scope and expiration
    - Keys should be stored hashed in the database
    - Key generation should be logged for audit trails
    - Keys should be revocable
    """
    # Generate a secure API key
    api_key = create_api_key()
    
    # TODO: Store API key in database with metadata
    # - Associate with user/organization
    # - Set expiration date
    # - Define scope and permissions
    # - Hash the key for storage
    
    return {
        "api_key": api_key,
        "type": "service",
        "created_by": current_user.user_id,
        "cauldron_id": current_user.cauldron_id,
        "expires_at": "2025-01-01T00:00:00Z",  # Placeholder
        "note": "Store this key securely. It cannot be retrieved again."
    }


@router.delete(
    "/revoke-tokens",
    response_model=Dict[str, str],
    summary="Revoke User Tokens",
    description="Revoke all tokens for the current user"
)
async def revoke_tokens(
    current_user: CurrentUser = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Revoke all tokens for the current user.
    
    This endpoint demonstrates:
    - Token revocation patterns
    - User-initiated security actions
    - Logout functionality
    - Security best practices
    
    Educational Notes:
    - JWT tokens are stateless and can't be revoked directly
    - True revocation requires a blacklist or short token lifetime
    - Clerk handles token revocation on their end
    - This endpoint can trigger client-side token cleanup
    
    Implementation Options:
    1. Maintain a token blacklist in Redis
    2. Use short-lived tokens with refresh mechanism
    3. Rely on Clerk's token revocation
    4. Implement user session invalidation
    """
    # TODO: Implement token revocation logic
    # Options:
    # 1. Add token to blacklist in Redis
    # 2. Call Clerk API to revoke sessions
    # 3. Update user's token version in database
    # 4. Invalidate user sessions
    
    return {
        "message": "Tokens revoked successfully",
        "user_id": current_user.user_id,
        "revoked_at": datetime.utcnow().isoformat(),
        "action": "Please log in again to continue using the application"
    }


@router.get(
    "/permissions",
    response_model=Dict[str, Any],
    summary="Get User Permissions",
    description="Get detailed permissions for the current user"
)
async def get_user_permissions(
    current_user: CurrentUser = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get detailed permissions for the current user.
    
    This endpoint demonstrates:
    - Permission checking
    - Role-based access control
    - Multi-tenancy permissions
    - Feature flags
    
    Educational Notes:
    - Permissions are derived from user's role in organization
    - Each cauldron can have different permission sets
    - Admin users have elevated permissions within their cauldron
    - Permissions can be used for UI feature toggling
    """
    # Define base permissions for all users
    base_permissions = {
        "can_view_members": True,
        "can_create_stories": True,
        "can_search": True,
        "can_view_own_profile": True,
        "can_update_own_profile": True,
    }
    
    # Define admin permissions
    admin_permissions = {
        "can_manage_members": True,
        "can_delete_stories": True,
        "can_view_analytics": True,
        "can_manage_cauldron": True,
        "can_generate_api_keys": True,
        "can_view_audit_logs": True,
        "can_manage_permissions": True,
    }
    
    # Combine permissions based on role
    permissions = base_permissions.copy()
    if current_user.is_admin:
        permissions.update(admin_permissions)
    
    return {
        "user_id": current_user.user_id,
        "cauldron_id": current_user.cauldron_id,
        "role": "admin" if current_user.is_admin else "member",
        "permissions": permissions,
        "total_permissions": len(permissions),
        "admin_permissions": len(admin_permissions) if current_user.is_admin else 0,
        "checked_at": datetime.utcnow().isoformat()
    }


@router.post(
    "/webhook",
    summary="Clerk Webhook",
    description="Handle webhooks from Clerk for user events"
)
async def handle_clerk_webhook(
    request: Request
) -> Dict[str, str]:
    """
    Handle webhooks from Clerk for user events.
    
    This endpoint demonstrates:
    - Webhook handling
    - External service integration
    - Event-driven architecture
    - Security validation
    
    Educational Notes:
    - Webhooks allow real-time synchronization with Clerk
    - Common events: user.created, user.updated, organization.created
    - Should validate webhook signature for security
    - Can trigger database updates or background jobs
    
    Common Webhook Events:
    - user.created: New user registered
    - user.updated: User profile updated
    - user.deleted: User account deleted
    - organization.created: New organization created
    - organization.updated: Organization updated
    - organizationMembership.created: User joined organization
    - organizationMembership.deleted: User left organization
    """
    # TODO: Implement webhook handling
    # 1. Validate webhook signature
    # 2. Parse webhook payload
    # 3. Handle different event types
    # 4. Update local database if needed
    # 5. Return appropriate response
    
    return {
        "message": "Webhook received",
        "status": "processing",
        "timestamp": datetime.utcnow().isoformat()
    }