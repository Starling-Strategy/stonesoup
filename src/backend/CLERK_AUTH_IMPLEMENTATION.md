# Clerk Authentication Implementation for STONESOUP

This document provides a comprehensive guide to the Clerk authentication implementation in the STONESOUP backend, including educational notes about JWT security, multi-tenancy, and best practices.

## Architecture Overview

### Components

1. **ClerkJWTMiddleware** (`app/middleware/auth.py`)
   - Handles JWT token verification for all requests
   - Caches JWKS for performance
   - Extracts user and organization context
   - Adds security headers to responses

2. **Security Utilities** (`app/core/security.py`)
   - CurrentUser model for user context
   - ClerkTokenVerifier for JWT validation
   - FastAPI dependencies for authentication
   - Role-based access control functions

3. **Protected Endpoints** (`app/api/v1/endpoints/`)
   - Authentication endpoints (`auth.py`)
   - Member management with multi-tenancy (`members.py`)
   - Demonstrates various protection levels

## JWT Authentication Flow

### 1. Client Authentication
```
User → Clerk (Frontend) → JWT Token → Client Application
```

### 2. API Request Flow
```
Client → Authorization Header → Middleware → Token Verification → User Context → Endpoint
```

### 3. Token Verification Process
```
JWT Token → JWKS Fetch → Signature Verification → Claims Validation → User Extraction
```

## Multi-Tenancy Design

### Core Principles
- **Data Isolation**: Each organization (cauldron) has completely isolated data
- **Automatic Scoping**: All database queries are automatically scoped to user's cauldron
- **Token-Based Context**: Organization membership comes from JWT token claims
- **Admin Permissions**: Admin status is scoped to user's cauldron

### Implementation Details
```python
# User's cauldron_id is extracted from JWT token
current_user.cauldron_id  # From org_id claim in JWT

# All database queries are automatically scoped
members = crud.member.get_multi_by_cauldron(cauldron_id=current_user.cauldron_id)

# Admin permissions are cauldron-scoped
if current_user.is_admin:  # Admin in their cauldron only
    # Perform admin actions
```

## Security Features

### JWT Token Security
- **RS256 Algorithm**: Asymmetric signing using RSA keys
- **JWKS Caching**: Public keys cached for performance and resilience
- **Token Validation**: Comprehensive claim validation including expiration
- **Issuer Verification**: Ensures tokens come from Clerk

### Multi-Tenancy Security
- **Automatic Isolation**: No risk of cross-tenant data access
- **Token-Based Scoping**: Organization context from cryptographically verified token
- **Admin Restrictions**: Admin permissions limited to user's organization
- **Audit Logging**: All security events logged for monitoring

### Additional Security Measures
- **HTTPS Enforcement**: Security headers for HTTPS-only operation
- **CORS Configuration**: Proper cross-origin request handling
- **Rate Limiting**: Can be implemented at middleware level
- **Error Handling**: Secure error responses that don't leak information

## Usage Examples

### Basic Protected Endpoint
```python
@router.get("/protected")
async def protected_endpoint(
    current_user: CurrentUser = Depends(get_current_user)
):
    return {"user_id": current_user.user_id, "cauldron": current_user.cauldron_id}
```

### Admin-Only Endpoint
```python
@router.delete("/admin-only")
async def admin_endpoint(
    current_user: CurrentUser = Depends(require_admin)
):
    # Only admins in their cauldron can access this
    return {"message": "Admin action completed"}
```

### Multi-Tenant Data Access
```python
@router.get("/members")
async def get_members(
    request: Request,
    current_user: CurrentUser = Depends(get_current_user)
):
    cauldron_id = get_cauldron_id_from_request(request)
    # Data automatically scoped to user's cauldron
    members = await crud.member.get_by_cauldron(cauldron_id)
    return members
```

### Cauldron-Specific Access Control
```python
@router.get("/cauldron/{cauldron_id}/data")
async def get_cauldron_data(
    cauldron_id: str,
    current_user: CurrentUser = Depends(require_cauldron_access(cauldron_id))
):
    # Ensures user has access to the specified cauldron
    return {"cauldron_id": cauldron_id, "data": "..."}
```

## Error Handling

### Authentication Errors
- **401 Unauthorized**: Invalid or expired tokens
- **403 Forbidden**: Valid user but insufficient permissions
- **503 Service Unavailable**: JWKS fetch failures

### Multi-Tenancy Errors
- **403 Forbidden**: Attempting to access different cauldron's data
- **400 Bad Request**: Missing organization membership

## Configuration

### Environment Variables
```bash
# Clerk Configuration
CLERK_SECRET_KEY=clerk_secret_key_here
CLERK_PUBLISHABLE_KEY=pk_live_...
CLERK_JWT_VERIFICATION_KEY=optional_verification_key

# CORS Origins
BACKEND_CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### FastAPI Setup
```python
# Add middleware to FastAPI app
from app.middleware.auth import ClerkJWTMiddleware
app.add_middleware(ClerkJWTMiddleware)

# Use dependencies in routes
from app.core.security import get_current_user, require_admin
```

## Best Practices

### Security Best Practices
1. **Always verify JWT signatures** - Never trust client-provided data
2. **Use HTTPS in production** - Protect tokens in transit
3. **Implement proper CORS** - Prevent unauthorized cross-origin requests
4. **Log security events** - Monitor for unusual activity
5. **Cache JWKS efficiently** - Balance security and performance

### Multi-Tenancy Best Practices
1. **Automatic scoping** - Don't rely on client-provided tenant IDs
2. **Token-based context** - Extract tenant information from verified tokens
3. **Database-level isolation** - Ensure queries are always scoped
4. **Admin permission scoping** - Limit admin powers to their organization
5. **Audit all actions** - Track who did what in which organization

### Performance Best Practices
1. **JWKS caching** - Cache public keys to avoid repeated API calls
2. **Middleware efficiency** - Process authentication once per request
3. **Database indexing** - Index on cauldron_id for multi-tenant queries
4. **Connection pooling** - Efficient database connection management

## Testing

### Unit Tests
```python
def test_jwt_verification():
    # Test JWT token verification
    pass

def test_multi_tenancy():
    # Test data isolation between cauldrons
    pass

def test_admin_permissions():
    # Test admin permission scoping
    pass
```

### Integration Tests
```python
def test_protected_endpoint():
    # Test endpoint with valid JWT token
    pass

def test_unauthorized_access():
    # Test endpoint without valid token
    pass

def test_cross_tenant_access():
    # Test that users can't access other cauldrons
    pass
```

## Monitoring and Logging

### Security Events to Monitor
- Failed authentication attempts
- Cross-tenant access attempts
- Admin permission escalations
- Unusual token patterns
- JWKS fetch failures

### Logging Configuration
```python
import logging

# Configure security logger
security_logger = logging.getLogger("stonesoup.security")
security_logger.setLevel(logging.INFO)

# Log successful authentications
security_logger.info(f"User {user_id} authenticated successfully")

# Log security violations
security_logger.warning(f"Cross-tenant access attempt: {user_id}")
```

## Troubleshooting

### Common Issues

1. **Token Verification Failures**
   - Check JWKS URL accessibility
   - Verify token format and claims
   - Ensure proper algorithm (RS256)

2. **Multi-Tenancy Issues**
   - Verify organization membership in token
   - Check cauldron_id extraction
   - Validate database query scoping

3. **Permission Errors**
   - Confirm admin role in JWT token
   - Check permission scoping logic
   - Verify endpoint protection levels

### Debug Mode
```python
# Enable debug logging
import logging
logging.getLogger("stonesoup.security").setLevel(logging.DEBUG)

# Add debug endpoints (development only)
@router.get("/debug/token")
async def debug_token(current_user: CurrentUser = Depends(get_current_user)):
    return {"user": current_user.dict(), "debug": True}
```

## Security Considerations

### Production Deployment
1. **Environment Variables**: Store sensitive configuration in environment variables
2. **HTTPS Only**: Enforce HTTPS for all API communication
3. **Token Expiration**: Use short-lived tokens with refresh mechanisms
4. **Rate Limiting**: Implement rate limiting to prevent abuse
5. **Monitoring**: Set up comprehensive security monitoring

### Compliance
- **Data Privacy**: Ensure GDPR/CCPA compliance for user data
- **Audit Trails**: Maintain comprehensive audit logs
- **Access Controls**: Implement principle of least privilege
- **Data Retention**: Follow data retention policies

This implementation provides a robust, secure, and scalable authentication system for STONESOUP with comprehensive multi-tenancy support and educational value for understanding JWT security and modern API authentication patterns.