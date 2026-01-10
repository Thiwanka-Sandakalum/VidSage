"""Integration endpoints for external tools (Google OAuth)."""

import os
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
import httpx
import logging

from src.core.security import get_current_user_id
from src.schemas import ErrorResponse

router = APIRouter(prefix="/integrations", tags=["integrations"])
logger = logging.getLogger(__name__)

# Tool integration service URL
TOOL_INTEGRATION_URL = os.getenv("TOOL_INTEGRATION_URL")


@router.get(
    "/google/auth",
    summary="Initialize Google OAuth",
    description="Start Google OAuth flow for account integration",
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)
async def google_auth_init(
    user_id: str = Depends(get_current_user_id)
):
    """
    Initialize Google OAuth flow.
    
    - **user_id**: Automatically extracted from JWT token
    
    Redirects to Google consent screen.
    """
    try:
        # Redirect to tool integration service
        auth_url = f"{TOOL_INTEGRATION_URL}/auth/google?userId={user_id}"
        return RedirectResponse(url=auth_url)
        
    except Exception as e:
        logger.exception(f"Error initiating Google OAuth: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error initiating Google authentication"
        )


@router.get(
    "/google/status",
    summary="Check Google OAuth status",
    description="Check if user has connected their Google account",
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)
async def google_auth_status(
    user_id: str = Depends(get_current_user_id)
):
    """
    Check Google OAuth connection status.
    
    Returns:
        - connected: Boolean indicating if Google account is connected
        - scopes: List of authorized scopes (if connected)
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{TOOL_INTEGRATION_URL}/google/status",
                params={"userId": user_id},
                timeout=10.0
            )
            
            if response.status_code == 404:
                return {
                    "connected": False,
                    "scopes": []
                }
            
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error checking Google status: {e}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail="Error checking Google authentication status"
        )
    except Exception as e:
        logger.exception(f"Error checking Google status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error checking Google authentication status"
        )


@router.delete(
    "/google/disconnect",
    summary="Disconnect Google account",
    description="Revoke Google OAuth access and delete stored tokens",
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": "Not Connected"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)
async def google_disconnect(
    user_id: str = Depends(get_current_user_id)
):
    """
    Disconnect Google account integration.
    
    Revokes OAuth access and deletes stored tokens.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{TOOL_INTEGRATION_URL}/google/disconnect",
                params={"userId": user_id},
                timeout=10.0
            )
            
            response.raise_for_status()
            return {
                "status": "success",
                "message": "Google account disconnected successfully"
            }
            
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Google account not connected"
            )
        logger.error(f"HTTP error disconnecting Google: {e}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail="Error disconnecting Google account"
        )
    except Exception as e:
        logger.exception(f"Error disconnecting Google: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error disconnecting Google account"
        )
