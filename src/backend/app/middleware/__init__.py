"""
Middleware package for STONESOUP backend.

This package contains all middleware components for:
- Authentication and authorization
- Request/response processing
- Security enhancements
- Multi-tenancy enforcement
"""

from .auth import ClerkJWTMiddleware

__all__ = ["ClerkJWTMiddleware"]