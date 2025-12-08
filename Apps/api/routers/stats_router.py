
from fastapi import APIRouter, HTTPException, status
from services.mongodb_vector_store import MongoDBVectorStoreManager
from typing import Optional
from models import ErrorResponse

router = APIRouter()
mongodb_manager: Optional[MongoDBVectorStoreManager] = None

def set_mongodb_manager(manager):
    global mongodb_manager
    mongodb_manager = manager

@router.get(
    "/stats",
    status_code=status.HTTP_200_OK,
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)
async def get_stats():
    global mongodb_manager
    try:
        stats = mongodb_manager.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting stats: {str(e)}"
        )
