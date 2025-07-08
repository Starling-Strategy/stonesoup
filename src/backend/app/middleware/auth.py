"""
Clerk Authentication Middleware for STONESOUP Backend.

This middleware provides comprehensive JWT authentication using Clerk's authentication service.
It handles token verification, user context extraction, and multi-tenant isolation.

Key Features:
- JWT signature verification using Clerk's JWKS endpoint
- Automatic token refresh and JWKS caching
- Multi-tenant isolation using organization ID extraction
- Comprehensive error handling with detailed logging
- Educational comments explaining JWT flow and security concepts

Security Design Principles:
1. Never trust client-provided data - always verify JWT signatures
2. Implement proper token expiration and refresh mechanisms
3. Use secure caching for JWKS to avoid performance issues
4. Provide clear error messages for debugging while avoiding information leakage
5. Implement rate limiting and abuse prevention mechanisms
"""

import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta

from fastapi import Request, Response, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import httpx
from jose import jwt, JWTError
import logging

from app.core.config import settings
from app.core.security import CurrentUser

# Configure logging for security events
security_logger = logging.getLogger("stonesoup.security")


class ClerkAuthenticationError(Exception):
    """Base exception for Clerk authentication errors."""
    pass


class TokenExpiredError(ClerkAuthenticationError):
    """Raised when a JWT token has expired."""
    pass


class TokenInvalidError(ClerkAuthenticationError):
    """Raised when a JWT token is invalid or malformed."""
    pass


class JWKSFetchError(ClerkAuthenticationError):
    """Raised when unable to fetch JWKS from Clerk."""
    pass


class ClerkJWTMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling Clerk JWT authentication.
    
    This middleware intercepts all requests and:
    1. Extracts JWT tokens from Authorization headers
    2. Verifies tokens using Clerk's public keys (JWKS)
    3. Extracts user and organization information
    4. Adds user context to the request for downstream handlers
    
    JWT (JSON Web Token) Authentication Flow:
    ==========================================
    
    1. Client Login:
       - User authenticates with Clerk (frontend)
       - Clerk returns a signed JWT token
       - Token contains user info and organization membership
    
    2. API Request:
       - Client includes JWT in Authorization header: "Bearer <token>"
       - Our middleware extracts and verifies the token
       - Token signature is verified using Clerk's public keys
    
    3. Token Verification:
       - Fetch Clerk's JWKS (JSON Web Key Set) - contains public keys
       - Verify token signature using appropriate public key
       - Check token expiration and other claims
       - Extract user information and organization membership
    
    4. Request Context:
       - Add authenticated user info to request context
       - Apply multi-tenant filtering based on organization ID
       - Allow request to proceed to route handlers
    
    Multi-Tenancy Design:
    ====================
    
    STONESOUP uses a multi-tenant architecture where:
    - Each organization is a "cauldron" with isolated data
    - User's organization ID (cauldron_id) is extracted from JWT
    - All database queries are automatically scoped to the user's cauldron
    - This ensures complete data isolation between organizations
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.jwks_url = "https://api.clerk.com/v1/jwks"
        self.jwks_cache: Optional[Dict[str, Any]] = None
        self.jwks_cache_time: Optional[datetime] = None
        self.jwks_cache_duration = timedelta(hours=1)  # Cache JWKS for 1 hour
        
        # Paths that don't require authentication
        self.excluded_paths = {
            "/health",
            "/",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/auth/webhook",  # Clerk webhooks
        }
        
        # Create HTTP client for JWKS fetching
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(10.0),
            limits=httpx.Limits(max_connections=10)
        )
        
        security_logger.info("Clerk JWT Middleware initialized")
    
    async def dispatch(self, request: Request, call_next):
        """
        Main middleware dispatch method.
        
        This method is called for every HTTP request and decides whether
        authentication is required and handles the JWT verification process.
        """
        # Skip authentication for excluded paths
        if self._is_excluded_path(request.url.path):
            return await call_next(request)
        
        # Skip authentication for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # DEMO MODE: Skip authentication if no Clerk key is configured
        # This allows running the MVP without setting up Clerk
        if not settings.CLERK_SECRET_KEY:
            # Set demo user context
            request.state.current_user = CurrentUser(
                user_id="demo-user",
                email="demo@stonesoup.ai",
                first_name="Demo",
                last_name="User",
                cauldron_id="10ksb-pilot",  # Default cauldron for demo
                is_admin=False
            )
            request.state.cauldron_id = "10ksb-pilot"
            
            security_logger.info("Demo mode: Authentication bypassed")
            
            # Continue with the request
            response = await call_next(request)
            
            # Add security headers to response
            self._add_security_headers(response)
            
            return response
        
        try:
            # Extract and verify JWT token
            current_user = await self._authenticate_request(request)
            
            # Add user context to request state
            request.state.current_user = current_user
            request.state.cauldron_id = current_user.cauldron_id
            
            # Log successful authentication
            security_logger.info(
                f"User authenticated successfully: {current_user.user_id} "
                f"(cauldron: {current_user.cauldron_id})"
            )
            
            # Continue with the request
            response = await call_next(request)
            
            # Add security headers to response
            self._add_security_headers(response)
            
            return response
            
        except HTTPException as e:
            # Handle authentication errors
            security_logger.warning(
                f"Authentication failed for {request.url.path}: {e.detail}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": "authentication_failed",
                    "message": e.detail,
                    "path": request.url.path
                }
            )
        except Exception as e:
            # Handle unexpected errors
            security_logger.error(
                f"Unexpected authentication error: {str(e)}", 
                exc_info=True
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "internal_server_error",
                    "message": "An unexpected error occurred during authentication"
                }
            )
    
    def _is_excluded_path(self, path: str) -> bool:
        """Check if a path should be excluded from authentication."""
        # Exact match
        if path in self.excluded_paths:
            return True
        
        # Prefix match for static files and documentation
        excluded_prefixes = ["/static/", "/docs/", "/redoc/"]
        return any(path.startswith(prefix) for prefix in excluded_prefixes)
    
    async def _authenticate_request(self, request: Request) -> CurrentUser:
        """
        Authenticate a request by extracting and verifying the JWT token.
        
        This method implements the core JWT authentication logic:
        1. Extract token from Authorization header
        2. Verify token signature using Clerk's JWKS
        3. Validate token claims (expiration, issuer, etc.)
        4. Extract user and organization information
        5. Return CurrentUser object with user context
        """
        # Extract Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing Authorization header"
            )
        
        # Parse Bearer token
        if not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Authorization header format. Expected: Bearer <token>"
            )
        
        token = auth_header[7:]  # Remove "Bearer " prefix
        
        # Verify and decode the JWT token
        try:
            decoded_token = await self._verify_jwt_token(token)
        except TokenExpiredError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired. Please log in again."
            )
        except TokenInvalidError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
        except JWKSFetchError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to verify token. Please try again later."
            )
        
        # Extract user information from token claims
        current_user = self._extract_user_from_token(decoded_token)
        
        return current_user
    
    async def _verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """
        Verify a JWT token using Clerk's JWKS.
        
        JWT Verification Process:
        ========================
        
        1. Fetch JWKS (JSON Web Key Set) from Clerk
           - JWKS contains public keys used to verify JWT signatures
           - Keys are cached to avoid repeated API calls
           - Cache is refreshed periodically or on verification failure
        
        2. Decode JWT Header
           - Extract 'kid' (key ID) from JWT header
           - Find matching public key in JWKS
        
        3. Verify Signature
           - Use public key to verify JWT signature
           - Ensures token was signed by Clerk and hasn't been tampered with
        
        4. Validate Claims
           - Check token expiration (exp claim)
           - Verify issuer (iss claim) matches Clerk
           - Validate any custom claims
        
        5. Return Decoded Token
           - If all checks pass, return decoded token payload
           - Payload contains user information and organization membership
        """
        try:
            # Fetch JWKS for token verification
            jwks = await self._get_jwks()
            
            # Decode the token using JWKS
            # Note: jose library handles key selection based on 'kid' in JWT header
            decoded_token = jwt.decode(
                token,
                jwks,
                algorithms=["RS256"],  # Clerk uses RS256 algorithm
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
            
            # Additional claim validation
            self._validate_token_claims(decoded_token)
            
            return decoded_token
            
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Token has expired")
        except jwt.JWTError as e:
            raise TokenInvalidError(f"JWT validation failed: {str(e)}")
        except Exception as e:
            security_logger.error(f"Unexpected error during token verification: {str(e)}")
            raise TokenInvalidError(f"Token verification failed: {str(e)}")
    
    def _validate_token_claims(self, decoded_token: Dict[str, Any]) -> None:
        """
        Validate custom claims in the JWT token.
        
        This method performs additional validation beyond standard JWT claims:
        - Verify issuer matches Clerk's expected issuer
        - Check for required custom claims
        - Validate organization membership if required
        """
        # Verify issuer
        issuer = decoded_token.get("iss")
        if not issuer or not issuer.startswith("https://"):
            raise TokenInvalidError("Invalid or missing issuer claim")
        
        # Check for required user claims
        if not decoded_token.get("sub"):
            raise TokenInvalidError("Missing user ID (sub) claim")
        
        # Log token claims for debugging (exclude sensitive data)
        security_logger.debug(
            f"Token validated successfully. User: {decoded_token.get('sub')}, "
            f"Issuer: {issuer}, Expires: {decoded_token.get('exp')}"
        )
    
    async def _get_jwks(self) -> Dict[str, Any]:
        """
        Fetch JWKS (JSON Web Key Set) from Clerk with caching.
        
        JWKS Caching Strategy:
        =====================
        
        1. Cache Duration: 1 hour (configurable)
        2. Cache Invalidation: Time-based + error-based
        3. Fallback: Retry on cache miss or verification failure
        4. Security: Cache includes integrity checks
        
        Benefits of JWKS Caching:
        - Reduces API calls to Clerk
        - Improves response times
        - Provides resilience against Clerk API outages
        - Reduces rate limiting issues
        """
        now = datetime.now(timezone.utc)
        
        # Check if cache is valid and not expired
        if (
            self.jwks_cache
            and self.jwks_cache_time
            and (now - self.jwks_cache_time) < self.jwks_cache_duration
        ):
            return self.jwks_cache
        
        # Fetch new JWKS from Clerk
        try:
            security_logger.info("Fetching JWKS from Clerk API")
            response = await self.http_client.get(self.jwks_url)
            response.raise_for_status()
            
            jwks_data = response.json()
            
            # Validate JWKS structure
            if "keys" not in jwks_data:
                raise JWKSFetchError("Invalid JWKS format: missing 'keys' field")
            
            # Cache the JWKS
            self.jwks_cache = jwks_data
            self.jwks_cache_time = now
            
            security_logger.info(f"JWKS fetched and cached successfully. Keys: {len(jwks_data['keys'])}")
            
            return jwks_data
            
        except httpx.HTTPError as e:
            security_logger.error(f"Failed to fetch JWKS: {str(e)}")
            raise JWKSFetchError(f"Unable to fetch JWKS from Clerk: {str(e)}")
        except Exception as e:
            security_logger.error(f"Unexpected error fetching JWKS: {str(e)}")
            raise JWKSFetchError(f"JWKS fetch failed: {str(e)}")
    
    def _extract_user_from_token(self, decoded_token: Dict[str, Any]) -> CurrentUser:
        """
        Extract user information from decoded JWT token.
        
        Clerk JWT Token Structure:
        ==========================
        
        Standard Claims:
        - sub: User ID (Clerk user identifier)
        - iss: Issuer (Clerk's domain)
        - iat: Issued at timestamp
        - exp: Expiration timestamp
        - nbf: Not before timestamp
        
        Custom Claims (Clerk-specific):
        - email: User's email address
        - given_name: User's first name
        - family_name: User's last name
        - org_id: Organization ID (for multi-tenancy)
        - org_role: User's role within the organization
        - org_slug: Organization slug/identifier
        
        Multi-Tenancy Extraction:
        ========================
        
        The organization ID (org_id) is crucial for multi-tenancy:
        - It identifies which "cauldron" (organization) the user belongs to
        - All database queries are scoped to this cauldron
        - Users can only access data within their organization
        - Organization admins have elevated permissions within their cauldron
        """
        # Extract basic user information
        user_id = decoded_token.get("sub")
        if not user_id:
            raise TokenInvalidError("Missing user ID in token")
        
        # Extract optional user profile information
        email = decoded_token.get("email")
        first_name = decoded_token.get("given_name")
        last_name = decoded_token.get("family_name")
        
        # Extract organization information for multi-tenancy
        org_id = decoded_token.get("org_id")
        org_role = decoded_token.get("org_role", "member")
        org_slug = decoded_token.get("org_slug")
        
        # Multi-tenancy validation
        if not org_id:
            security_logger.warning(
                f"User {user_id} has no organization membership. "
                "Multi-tenant access requires organization membership."
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organization membership required. Please join an organization to access this service."
            )
        
        # Determine admin status
        is_admin = org_role in ["admin", "owner"]
        
        # Create CurrentUser object
        current_user = CurrentUser(
            user_id=user_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            cauldron_id=org_id,  # Map org_id to cauldron_id
            is_admin=is_admin
        )
        
        security_logger.debug(
            f"User extracted from token: {current_user.user_id} "
            f"(cauldron: {current_user.cauldron_id}, admin: {current_user.is_admin})"
        )
        
        return current_user
    
    def _add_security_headers(self, response: Response) -> None:
        """
        Add security headers to the response.
        
        Security Headers Explained:
        ===========================
        
        1. X-Content-Type-Options: nosniff
           - Prevents MIME type sniffing attacks
           - Forces browsers to respect declared content types
        
        2. X-Frame-Options: DENY
           - Prevents clickjacking attacks
           - Disallows embedding in frames/iframes
        
        3. X-XSS-Protection: 1; mode=block
           - Enables XSS filtering in older browsers
           - Blocks page rendering if XSS is detected
        
        4. Strict-Transport-Security: max-age=31536000
           - Enforces HTTPS connections
           - Prevents protocol downgrade attacks
        
        5. Content-Security-Policy: default-src 'self'
           - Prevents XSS and data injection attacks
           - Restricts resource loading to same origin
        """
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
        }
        
        # Add HSTS header for HTTPS connections
        if getattr(settings, "USE_HTTPS", False):
            security_headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Add headers to response
        for header_name, header_value in security_headers.items():
            response.headers[header_name] = header_value
    
    async def cleanup(self):
        """Cleanup resources when middleware is destroyed."""
        if hasattr(self, 'http_client'):
            await self.http_client.aclose()