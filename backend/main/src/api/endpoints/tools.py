import os
from fastapi import APIRouter, HTTPException, Query, status, Depends
from pydantic import BaseModel
from src.api.dependencies import get_mongodb_manager
from src.core.security import get_current_user_id
from src.infrastructure.database.vector_store import MongoDBVectorStoreManager
from src.schemas import ErrorResponse
import requests

router = APIRouter(prefix="/tools", tags=["tools"])

class SaveSummaryRequest(BaseModel):
    video_id: str

@router.post(
    "/save-summary-to-doc",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Save video summary to Google Doc",
    description="Fetches the video summary and saves it as a new Google Doc via the tool API.",
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Video Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)
async def save_summary_to_doc(
    request: SaveSummaryRequest,
    user_id: str = Depends(get_current_user_id),
    mongodb_manager: MongoDBVectorStoreManager = Depends(get_mongodb_manager)
):
    # Fetch video summary
    video_metadata = mongodb_manager.get_video_metadata(request.video_id)
    if not video_metadata:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found.")
    if user_id not in video_metadata.get("users", []):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this video.")
    summary = video_metadata.get("summary", "No summary available.")
    title = video_metadata.get("title", f"Video {request.video_id}")
    # Call tool API to create Google Doc (per OpenAPI: POST /google/docs)
    tool_api_url = f"{os.getenv('TOOL_INTEGRATION_URL', 'http://localhost:4000')}/google/docs"
    payload = {
        "userId": user_id,
        "content": summary,
        "title": title
    }
    try:
        response = requests.post(tool_api_url, json=payload, timeout=10)
        response.raise_for_status()
        doc_data = response.json()
        doc_link = doc_data.get("doc_link") or doc_data.get("id")
        return {"video_id": request.video_id, "doc_link": doc_link}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create Google Doc: {e}")

@router.get(
    "/summary-doc-link",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Check if video summary is saved to Google Doc",
    description="Checks if a Google Doc for the video summary already exists for the user.",
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Video Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)
async def get_summary_doc_link(
    video_id: str = Query(..., description="Video ID to check"),
    user_id: str = Depends(get_current_user_id),
    mongodb_manager: MongoDBVectorStoreManager = Depends(get_mongodb_manager)
):
    # Fetch video metadata
    video_metadata = mongodb_manager.get_video_metadata(video_id)
    if not video_metadata:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found.")
    if user_id not in video_metadata.get("users", []):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have access to this video.")
    title = video_metadata.get("title", f"Video {video_id}")
    # Call tool API to list Google Docs (GET, userId as query param)
    tool_api_url = f"{os.getenv('TOOL_INTEGRATION_URL', 'http://localhost:4000')}/google/docs/list"
    params = {"userId": user_id}
    try:
        response = requests.get(tool_api_url, params=params, timeout=10)
        response.raise_for_status()
        # The response has 'documents' as a list of Google Docs
        data = response.json()
        docs = data.get("documents") or []
        # Filter all docs where name matches title or video_id is in name
        matching_docs = [
            doc for doc in docs
            if doc.get("name", "") == title or video_id in doc.get("name", "")
        ]
        if matching_docs:
            # Return only the first matching doc's webViewLink
            doc_link = next((doc.get("webViewLink") for doc in matching_docs if doc.get("webViewLink")), None)
            return {
                "video_id": video_id,
                "exists": True,
                "doc_link": doc_link,
            }
        else:
            return {
                "video_id": video_id,
                "exists": False,
                "doc_link": None,
            }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to check Google Docs: {e}")