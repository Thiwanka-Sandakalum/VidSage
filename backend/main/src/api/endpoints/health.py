"""Health check endpoint."""

from fastapi import APIRouter
import os

router = APIRouter(tags=["health"])


@router.get("/health", summary="Health Check", description="Check if the API is running")
def health_check():
    """
    Simple health check endpoint.
    
    Returns:
        Status message indicating the API is operational
    """
    return {
        "status": "healthy",
        "service": "VidSage Backend API",
        "version": "1.0.0"
    }


@router.get("/", summary="API Root", description="Root endpoint with API information")
def root():
    """
    Root endpoint with basic API information.
    
    Returns:
        Welcome message and links
    """
    return {
        "message": "Welcome to VidSage - YouTube RAG Pipeline API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
