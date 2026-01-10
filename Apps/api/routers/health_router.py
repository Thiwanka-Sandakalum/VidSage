from fastapi import APIRouter
import os

router = APIRouter()

@router.get("/health")
async def health_check():
    api_key_set = bool(os.getenv("GOOGLE_API_KEY"))
    mongodb_uri_set = bool(os.getenv("MONGODB_URI"))
    from routers.process_router import mongodb_manager as process_mongodb_manager
    mongodb_connected = process_mongodb_manager is not None
    return {
        "status": "healthy" if (api_key_set and mongodb_connected) else "degraded",
        "api_key_configured": api_key_set,
        "mongodb_uri_configured": mongodb_uri_set,
        "mongodb_connected": mongodb_connected
    }
