"""Video repository for database operations."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pymongo.database import Database

from src.repositories.base import BaseRepository


class VideoRepository(BaseRepository):
    """Repository for video operations."""
    
    def __init__(self, db: Database, collection_name: str = "videos"):
        """Initialize video repository."""
        super().__init__(db, collection_name)
    
    def find_by_video_id(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Find video by YouTube video ID.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Video document or None
        """
        return self.find_one({"video_id": video_id})
    
    def find_by_user(
        self,
        user_id: str,
        limit: int = 100,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Find all videos for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of videos
            skip: Number of videos to skip
            
        Returns:
            List of video documents
        """
        return self.find_many(
            {"users": user_id},
            limit=limit,
            skip=skip,
            sort=[("created_at", -1)]  # Most recent first
        )
    
    def user_has_access(self, user_id: str, video_id: str) -> bool:
        """
        Check if user has access to video.
        
        Args:
            user_id: User ID
            video_id: YouTube video ID
            
        Returns:
            True if user has access
        """
        return self.exists({
            "video_id": video_id,
            "users": user_id
        })
    
    def add_user_to_video(self, video_id: str, user_id: str) -> bool:
        """
        Add user to video's user list.
        
        Args:
            video_id: YouTube video ID
            user_id: User ID to add
            
        Returns:
            True if user was added
        """
        result = self.update_one(
            {"video_id": video_id},
            {
                "$addToSet": {"users": user_id},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        return result > 0
    
    def create_video(
        self,
        video_id: str,
        title: str,
        url: str,
        user_id: str,
        chunks_count: int,
        suggested_questions: List[str] = None,
        **kwargs
    ) -> str:
        """
        Create new video document.
        
        Args:
            video_id: YouTube video ID
            title: Video title
            url: Video URL
            user_id: User ID who processed the video
            chunks_count: Number of chunks created
            suggested_questions: AI-generated questions
            **kwargs: Additional fields
            
        Returns:
            Created document ID
        """
        document = {
            "video_id": video_id,
            "title": title,
            "url": url,
            "users": [user_id],
            "chunks_count": chunks_count,
            "suggested_questions": suggested_questions or [],
            "status": "completed",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            **kwargs
        }
        return self.insert_one(document)
    
    def get_all_stats(self) -> Dict[str, Any]:
        """
        Get statistics about all videos.
        
        Returns:
            Dictionary with stats
        """
        total_videos = self.count()
        
        # Aggregate total chunks
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_chunks": {"$sum": "$chunks_count"}
                }
            }
        ]
        result = list(self.collection.aggregate(pipeline))
        total_chunks = result[0]["total_chunks"] if result else 0
        
        return {
            "total_videos": total_videos,
            "total_chunks": total_chunks
        }
