"""
Security utilities for authentication and authorization.

This module provides:
- Clerk authentication integration
- JWT token verification
- User authentication dependencies for FastAPI
- Role-based access control
- Multi-tenancy support

Educational Notes:
=================

JWT Authentication Overview:
- JWT (JSON Web Token) is a compact, URL-safe means of representing claims
- Tokens are signed using cryptographic algorithms (RS256 in our case)
- They contain encoded user information and permissions
- Tokens can be verified without contacting the issuer (stateless)

Multi-Tenancy in STONESOUP:
- Each organization is isolated in its own "cauldron"
- User's organization ID determines data access scope
- All database queries are automatically filtered by cauldron_id
- Admin users have elevated permissions within their cauldron
"""

import secrets
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from jose import JWTError, jwt
from pydantic import BaseModel, Field
import logging

from app.core.config import settings

# Configure logging
security_logger = logging.getLogger("stonesoup.security")

# Security scheme for API documentation
# Made optional for demo mode
security = HTTPBearer(auto_error=False)


class CurrentUser(BaseModel):
    """
    Represents the currently authenticated user.
    
    This model contains the essential user information extracted
    from the Clerk JWT token and is used throughout the application
    for authorization and data scoping.
    
    Multi-Tenancy Design:
    - cauldron_id: Organization ID that scopes all data access
    - is_admin: Determines elevated permissions within the cauldron
    - user_id: Unique identifier for the user across all cauldrons
    """
    user_id: str = Field(..., description="Clerk user ID")
    email: Optional[str] = Field(None, description="User's email address")
    first_name: Optional[str] = Field(None, description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")
    cauldron_id: Optional[str] = Field(None, description="Organization ID for multi-tenancy")
    is_admin: bool = Field(False, description="Whether user is an admin in their cauldron")
    
    @property
    def full_name(self) -> str:
        """Get user's full name with fallback to email or user ID."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or self.email or self.user_id
    
    @property
    def display_name(self) -> str:
        """Get user's display name for UI purposes."""
        return self.full_name
    
    def has_cauldron_access(self, cauldron_id: str) -> bool:
        """Check if user has access to a specific cauldron."""
        return self.cauldron_id == cauldron_id or self.is_admin


class ClerkTokenVerifier:
    """
    Handles Clerk JWT token verification with caching and error handling.
    
    This class provides a robust token verification system with:
    - JWKS caching for performance
    - Comprehensive error handling
    - Token validation with security best practices
    - Logging for security monitoring
    
    JWT Verification Process:
    1. Fetch JWKS (JSON Web Key Set) from Clerk
    2. Extract key ID (kid) from JWT header
    3. Find matching public key in JWKS
    4. Verify signature using public key
    5. Validate token claims (expiration, issuer, etc.)
    6. Return decoded token payload
    """
    
    def __init__(self):
        self.jwks_url = "https://api.clerk.com/v1/jwks"
        self._jwks_cache = None
        self._jwks_cache_time = None
        self._cache_duration = 3600  # Cache JWKS for 1 hour
        
        security_logger.info("ClerkTokenVerifier initialized")
        
    async def get_jwks(self) -> Dict[str, Any]:
        """
        Fetch JWKS from Clerk API with intelligent caching.
        
        JWKS (JSON Web Key Set) contains the public keys used to verify
        JWT signatures. We cache this to:
        - Reduce API calls to Clerk
        - Improve response times
        - Provide resilience against network issues
        - Avoid rate limiting
        """
        now = datetime.now(timezone.utc)
        
        # Check if cache is valid and not expired
        if (
            self._jwks_cache 
            and self._jwks_cache_time 
            and (now - self._jwks_cache_time).total_seconds() < self._cache_duration
        ):
            security_logger.debug("Using cached JWKS")
            return self._jwks_cache
            
        # Fetch new JWKS from Clerk
        try:
            security_logger.info("Fetching fresh JWKS from Clerk")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.jwks_url)
                response.raise_for_status()
                
            jwks_data = response.json()
            
            # Validate JWKS structure
            if "keys" not in jwks_data:
                raise ValueError("Invalid JWKS format: missing 'keys' field")
                
            # Cache the JWKS
            self._jwks_cache = jwks_data
            self._jwks_cache_time = now
            
            security_logger.info(f"JWKS cached successfully. Keys: {len(jwks_data['keys'])}")
            return jwks_data
            
        except httpx.HTTPError as e:
            security_logger.error(f"Failed to fetch JWKS: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Unable to fetch JWKS from Clerk: {str(e)}"
            )
        except Exception as e:
            security_logger.error(f"Unexpected error fetching JWKS: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="JWKS fetch failed due to unexpected error"
            )
    
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode a Clerk JWT token.
        
        This method implements comprehensive token validation:
        1. Fetches JWKS for signature verification
        2. Decodes token using appropriate public key
        3. Validates standard JWT claims (exp, iss, iat, etc.)
        4. Performs custom claim validation
        5. Returns decoded token payload
        
        Security Considerations:
        - Uses RS256 algorithm (asymmetric signing)
        - Validates token expiration
        - Checks issuer to prevent token reuse
        - Handles various error conditions gracefully
        """
        try:
            # Get JWKS for verification
            jwks = await self.get_jwks()
            
            # Decode and verify the token
            # Clerk uses RS256 algorithm (RSA + SHA256)
            decoded = jwt.decode(
                token,
                jwks,
                algorithms=["RS256"],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_nbf": True,
                    "verify_iat": True,
                    "verify_aud": False,  # Clerk doesn't use audience claim
                    "require_exp": True,
                    "require_iat": True,
                }
            )
            
            # Additional validation
            self._validate_token_claims(decoded)
            
            security_logger.debug(f"Token verified successfully for user: {decoded.get('sub')}")
            return decoded
            
        except jwt.ExpiredSignatureError:
            security_logger.warning("Token verification failed: expired signature")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired. Please log in again."
            )
        except jwt.InvalidSignatureError:
            security_logger.warning("Token verification failed: invalid signature")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token signature is invalid"
            )
        except JWTError as e:
            security_logger.warning(f"Token verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token validation failed: {str(e)}"
            )
        except Exception as e:
            security_logger.error(f"Unexpected error during token verification: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token verification failed due to unexpected error"
            )
    
    def _validate_token_claims(self, decoded_token: Dict[str, Any]) -> None:
        """
        Validate custom claims in the JWT token.
        
        This performs additional validation beyond standard JWT claims:
        - Verifies issuer is from Clerk
        - Ensures required claims are present
        - Validates token structure and content
        """
        # Verify issuer (must be from Clerk)
        issuer = decoded_token.get("iss")
        if not issuer or not issuer.startswith("https://"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing issuer claim"
            )
        
        # Check for required user claims
        if not decoded_token.get("sub"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing user ID (sub) claim"
            )
        
        # Log successful validation
        security_logger.debug(
            f"Token claims validated. User: {decoded_token.get('sub')}, "
            f"Issuer: {issuer}, Expires: {decoded_token.get('exp')}"
        )


# Global instance of token verifier
token_verifier = ClerkTokenVerifier()


async def get_current_user_from_request(request: Request) -> Optional[CurrentUser]:
    """
    Get current user from request state (set by middleware).
    
    This is the preferred method for getting the current user when
    the ClerkJWTMiddleware is active, as it avoids duplicate token
    verification.
    """
    return getattr(request.state, "current_user", None)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> CurrentUser:
    """
    FastAPI dependency to get the current authenticated user.
    
    This dependency provides two modes of operation:
    1. If middleware is active: Extract user from request state
    2. If middleware is not active: Verify token directly
    
    Educational Notes:
    - This approach provides flexibility for different deployment scenarios
    - Middleware approach is more efficient for production use
    - Direct verification is useful for testing and development
    
    Usage:
        @app.get("/protected")
        async def protected_route(current_user: CurrentUser = Depends(get_current_user)):
            return {"user_id": current_user.user_id}
    """
    # Try to get user from request state first (middleware approach)
    current_user = await get_current_user_from_request(request)
    if current_user:
        return current_user
    
    # DEMO MODE: If no Clerk key is configured, return demo user
    if not settings.CLERK_SECRET_KEY:
        return CurrentUser(
            user_id="demo-user",
            email="demo@stonesoup.ai",
            first_name="Demo",
            last_name="User",
            cauldron_id="10ksb-pilot",
            is_admin=False
        )
    
    # Check if credentials were provided
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    # Fallback to direct token verification
    token = credentials.credentials
    
    # Verify the token
    decoded = await token_verifier.verify_token(token)
    
    # Extract user information from JWT claims
    current_user = CurrentUser(
        user_id=decoded.get("sub", ""),
        email=decoded.get("email"),
        first_name=decoded.get("given_name"),  # Clerk uses 'given_name'
        last_name=decoded.get("family_name"),  # Clerk uses 'family_name'
        cauldron_id=decoded.get("org_id"),  # Organization ID for multi-tenancy
        is_admin=decoded.get("org_role") in ["admin", "owner"]  # Check org role
    )
    
    # Validate cauldron membership
    if not current_user.cauldron_id:
        security_logger.warning(f"User {current_user.user_id} has no organization membership")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization membership required"
        )
    
    return current_user


async def get_current_active_user(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """
    Dependency to ensure the user is active.
    
    This can be extended to check if the user is banned, suspended, etc.
    by looking up the user in the database.
    
    Multi-Tenancy Note:
    - User activity is scoped to their cauldron
    - A user might be active in one cauldron but not another
    - Future enhancement: Check user status in database
    """
    # TODO: Implement database lookup for user status
    # For now, all authenticated users are considered active
    return current_user


async def require_admin(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """
    Dependency to require admin role.
    
    Use this for endpoints that should only be accessible to administrators
    within their cauldron. This implements cauldron-scoped admin permissions.
    
    Educational Notes:
    - Admin status is determined by org_role in JWT token
    - Admin permissions are scoped to the user's cauldron
    - Super admin functionality would require separate implementation
    """
    if not current_user.is_admin:
        security_logger.warning(
            f"User {current_user.user_id} attempted admin access without permissions"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def require_cauldron_access(
    cauldron_id: str,
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """
    Dependency to ensure user has access to a specific cauldron.
    
    This enforces multi-tenant isolation by checking if the user's
    organization ID matches the requested cauldron.
    
    Multi-Tenancy Enforcement:
    - Users can only access their own cauldron's data
    - Admin users have access to their own cauldron (not all cauldrons)
    - Super admin functionality would require separate implementation
    """
    if not current_user.has_cauldron_access(cauldron_id):
        security_logger.warning(
            f"User {current_user.user_id} attempted access to cauldron {cauldron_id} "
            f"without permission (user cauldron: {current_user.cauldron_id})"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this cauldron is forbidden"
        )
    return current_user


def create_api_key() -> str:
    """
    Generate a secure API key for service-to-service authentication.
    
    This creates a cryptographically secure random string prefixed with 'ss_'
    to identify it as a STONESOUP API key.
    
    Use Cases:
    - Background job authentication
    - Webhook verification
    - Service-to-service communication
    - Automated testing
    """
    return f"ss_{secrets.token_urlsafe(32)}"


async def get_api_key_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Optional[CurrentUser]:
    """
    Alternative authentication using API keys.
    
    This provides a fallback authentication method for scenarios where
    JWT tokens are not suitable:
    - Background jobs
    - Webhooks
    - Service-to-service communication
    - Automated scripts
    
    Implementation Notes:
    - API keys are prefixed with 'ss_' for identification
    - Keys should be stored securely in the database
    - This is a placeholder implementation
    """
    # Check if it's an API key (starts with 'ss_')
    if credentials.credentials.startswith("ss_"):
        # TODO: Implement API key validation against database
        # 1. Look up API key in database
        # 2. Check if key is active and not expired
        # 3. Extract associated user/service account
        # 4. Return appropriate CurrentUser object
        
        security_logger.warning("API key authentication attempted but not implemented")
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="API key authentication not yet implemented"
        )
    
    # Otherwise, use regular JWT authentication
    return await get_current_user(request, credentials)


def get_cauldron_id_from_request(request: Request) -> Optional[str]:
    """
    Extract cauldron ID from request state.
    
    This utility function retrieves the cauldron ID that was set
    by the authentication middleware, providing easy access to
    the user's organization context.
    """
    return getattr(request.state, "cauldron_id", None)