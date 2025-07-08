"""
API Dependencies for STONESOUP.

This module provides FastAPI dependencies for:
- Database session management
- User authentication (integrated with Clerk)
- Permission checking
- Multi-tenant context

Educational Notes:
=================

FastAPI Dependencies:
- Dependencies are functions that provide common functionality
- They can be composed and reused across endpoints
- Support automatic injection and validation
- Enable clean separation of concerns

Database Dependencies:
- Provide database sessions to endpoints
- Handle connection lifecycle automatically
- Support transaction management
- Enable proper resource cleanup

Authentication Dependencies:
- Integrate with Clerk JWT authentication
- Provide user context to endpoints
- Support different permission levels
- Enable multi-tenant data scoping
"""

from typing import Optional

from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    get_current_user as get_current_user_from_security,
    get_current_active_user as get_current_active_user_from_security,
    require_admin as require_admin_from_security,
    CurrentUser,
    get_cauldron_id_from_request
)
from app.db.session import get_db


def get_current_user(
    request: Request
) -> CurrentUser:
    """
    Get current authenticated user from request context.
    
    This dependency integrates with the Clerk JWT middleware to provide
    authenticated user information to endpoints.
    
    Educational Notes:
    - Works with ClerkJWTMiddleware for token verification
    - Provides consistent user context across endpoints
    - Supports both middleware and direct token verification
    - Enables clean authentication patterns
    
    Usage:
        @app.get("/profile")
        def get_profile(current_user: CurrentUser = Depends(get_current_user)):
            return {"user_id": current_user.user_id}
    """
    return get_current_user_from_security(request, None)


def get_current_active_user(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """
    Get current active user with additional status checks.
    
    This dependency builds on get_current_user to add additional
    validation for user status (active, not banned, etc.).
    
    Educational Notes:
    - Composes with get_current_user dependency
    - Can be extended for complex user status checks
    - Provides additional security layer
    - Supports business logic validation
    
    Usage:
        @app.get("/sensitive-data")
        def get_sensitive_data(
            current_user: CurrentUser = Depends(get_current_active_user)
        ):
            return {"data": "sensitive information"}
    """
    return get_current_active_user_from_security(current_user)


def get_current_admin_user(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """
    Get current user with admin permissions.
    
    This dependency ensures the current user has admin privileges
    within their cauldron before allowing access to admin endpoints.
    
    Educational Notes:
    - Enforces role-based access control
    - Admin permissions are scoped to user's cauldron
    - Provides clear authorization patterns
    - Supports hierarchical permission models
    
    Usage:
        @app.delete("/admin/delete-member")
        def delete_member(
            current_user: CurrentUser = Depends(get_current_admin_user)
        ):
            # Only admins can execute this
            return {"message": "Member deleted"}
    """
    return require_admin_from_security(current_user)


def get_cauldron_context(
    request: Request,
    current_user: CurrentUser = Depends(get_current_user)
) -> tuple[str, CurrentUser]:
    """
    Get cauldron context and current user together.
    
    This dependency provides both the cauldron ID and user context
    in a single dependency, useful for endpoints that need both.
    
    Educational Notes:
    - Combines multiple context dependencies
    - Reduces boilerplate in endpoint functions
    - Ensures consistency between user and cauldron context
    - Supports complex multi-tenant patterns
    
    Usage:
        @app.get("/cauldron-data")
        def get_cauldron_data(
            context: tuple[str, CurrentUser] = Depends(get_cauldron_context)
        ):
            cauldron_id, current_user = context
            return {"cauldron": cauldron_id, "user": current_user.user_id}
    """
    cauldron_id = get_cauldron_id_from_request(request)
    if not cauldron_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cauldron context not found in request"
        )
    
    return cauldron_id, current_user


def get_db_with_cauldron(
    db: AsyncSession = Depends(get_db),
    context: tuple[str, CurrentUser] = Depends(get_cauldron_context)
) -> tuple[AsyncSession, str, CurrentUser]:
    """
    Get database session with cauldron context and user.
    
    This dependency provides everything needed for multi-tenant
    database operations in a single dependency.
    
    Educational Notes:
    - Combines database and authentication dependencies
    - Provides complete context for multi-tenant operations
    - Reduces parameter repetition in endpoints
    - Supports complex business logic patterns
    
    Usage:
        @app.get("/members")
        def get_members(
            deps: tuple[AsyncSession, str, CurrentUser] = Depends(get_db_with_cauldron)
        ):
            db, cauldron_id, current_user = deps
            return db.query(Member).filter_by(cauldron_id=cauldron_id).all()
    """
    cauldron_id, current_user = context
    return db, cauldron_id, current_user


class CauldronScopedDB:
    """
    Helper class for cauldron-scoped database operations.
    
    This class provides a convenient interface for database operations
    that are automatically scoped to the current user's cauldron.
    
    Educational Notes:
    - Encapsulates multi-tenant database patterns
    - Provides type-safe database operations
    - Reduces boilerplate and errors
    - Supports advanced ORM patterns
    """
    
    def __init__(self, db: AsyncSession, cauldron_id: str, current_user: CurrentUser):
        self.db = db
        self.cauldron_id = cauldron_id
        self.current_user = current_user
    
    def query(self, model):
        """Create a query automatically scoped to the current cauldron."""
        return self.db.query(model).filter_by(cauldron_id=self.cauldron_id)
    
    def create(self, model_instance):
        """Create a new model instance scoped to the current cauldron."""
        model_instance.cauldron_id = self.cauldron_id
        self.db.add(model_instance)
        return model_instance
    
    def commit(self):
        """Commit the current transaction."""
        self.db.commit()
    
    def rollback(self):
        """Rollback the current transaction."""
        self.db.rollback()


def get_cauldron_scoped_db(
    deps: tuple[AsyncSession, str, CurrentUser] = Depends(get_db_with_cauldron)
) -> CauldronScopedDB:
    """
    Get a cauldron-scoped database helper.
    
    This dependency provides a high-level interface for database
    operations that are automatically scoped to the user's cauldron.
    
    Educational Notes:
    - Abstracts multi-tenant database complexity
    - Provides consistent scoping patterns
    - Reduces errors in multi-tenant queries
    - Supports advanced database patterns
    
    Usage:
        @app.get("/members")
        def get_members(
            scoped_db: CauldronScopedDB = Depends(get_cauldron_scoped_db)
        ):
            members = scoped_db.query(Member).all()
            return [member.to_dict() for member in members]
    """
    db, cauldron_id, current_user = deps
    return CauldronScopedDB(db, cauldron_id, current_user)


# Legacy compatibility - these can be removed once all endpoints are updated
def get_current_user_legacy(*args, **kwargs):
    """Legacy function for backward compatibility."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Legacy authentication method. Please use Clerk authentication."
    )


def get_current_active_superuser(*args, **kwargs):
    """Legacy function for backward compatibility."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Legacy authentication method. Please use Clerk authentication with admin role."
    )