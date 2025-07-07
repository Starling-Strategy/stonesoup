"""
Security and authentication using Clerk.
"""
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
import jwt
from jwt import PyJWKClient

from app.core.config import settings


# HTTP Bearer for extracting JWT tokens
security = HTTPBearer()


class ClerkAuth:
    """Clerk authentication handler."""
    
    def __init__(self):
        self.publishable_key = settings.CLERK_PUBLISHABLE_KEY
        self.secret_key = settings.CLERK_SECRET_KEY
        self.jwks_url = "https://api.clerk.dev/v1/jwks"
        self.jwks_client = PyJWKClient(self.jwks_url)
    
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify Clerk JWT token."""
        try:
            # Get the signing key from Clerk's JWKS
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
            
            # Decode and verify the token
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                options={"verify_aud": False}  # Clerk doesn't use audience
            )
            
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Could not validate credentials: {str(e)}"
            )
    
    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get user information from Clerk."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.clerk.dev/v1/users/{user_id}",
                headers={
                    "Authorization": f"Bearer {self.secret_key}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not fetch user information"
                )
            
            return response.json()


# Create auth instance
clerk_auth = ClerkAuth()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Dependency to get the current authenticated user.
    
    Returns the decoded JWT payload with user information.
    """
    token = credentials.credentials
    payload = await clerk_auth.verify_token(token)
    return payload


async def get_current_user_id(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> str:
    """Get the current user's ID from the JWT payload."""
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token"
        )
    return user_id


async def require_admin(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Require the current user to have admin role."""
    # Check for admin role in public metadata or org membership
    public_metadata = current_user.get("public_metadata", {})
    if not public_metadata.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user