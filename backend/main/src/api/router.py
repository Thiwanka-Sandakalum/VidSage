"""API v1 router combining all endpoints."""

from fastapi import APIRouter

from src.api.endpoints import health, videos, search, generation, stats, suggestions, integrations, summary,tools

# Create API v1 router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router)
api_router.include_router(videos.router)
api_router.include_router(search.router)
api_router.include_router(generation.router)
api_router.include_router(stats.router)
api_router.include_router(suggestions.router)
api_router.include_router(integrations.router)
api_router.include_router(summary.router)
api_router.include_router(tools.router)
