"""Authentication and security utilities."""

import os
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer()


class TokenPayload(BaseModel):
    """JWT token payload structure."""
    sub: str  # User ID
    exp: Optional[int] = None  # Expiration time
    iat: Optional[int] = None  # Issued at
    iss: Optional[str] = None  # Issuer


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> str:
    """
    Validate JWT token and extract user ID.
    
    For development: Uses unverified tokens (Clerk integration)
    For production: Should verify with Clerk's public key
    
    Args:
        credentials: Bearer token from request
        
    Returns:
        User ID from token
        
    Raises:
        HTTPException: If token is invalid or missing user ID
    """
    token = credentials.credentials
    
    try:
        # IMPORTANT: In production, verify signature with Clerk public key
        # For now, using unverified decode for compatibility
        # TODO: Add CLERK_PUBLISHABLE_KEY to environment and verify signature
        payload = jwt.decode(
            token,
            key=os.getenv("CLERK_PUBLISHABLE_KEY", ""),
            options={
                "verify_signature": False,  # TODO: Enable in production
                "verify_exp": True,
                "verify_iat": True,
            }
        )
        
        # Validate payload structure
        token_data = TokenPayload(**payload)
        
        if not token_data.sub:
            logger.error("Token missing user ID (sub claim)")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return token_data.sub
        
    except JWTError as e:
        logger.error(f"JWT validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Optional: For testing without authentication
async def get_current_user_id_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[str]:
    """Get user ID from token, or None if no token provided."""
    if not credentials:
        return None
    
    try:
        return await get_current_user_id(credentials)
    except HTTPException:
        return None
