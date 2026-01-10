"""Vector repository for embedding and search operations."""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from src.repositories.base import BaseRepository
from src.infrastructure.database.vector_store import MongoDBVectorStoreManager

logger = logging.getLogger(__name__)


class VectorRepository:
    """
    Repository for vector search and embedding operations.
    Abstracts the infrastructure layer (MongoDBVectorStoreManager).
    """
    
    def __init__(self, vector_store: MongoDBVectorStoreManager):
        """
        Initialize vector repository.
        
        Args:
            vector_store: MongoDB vector store infrastructure instance
        """
        self.vector_store = vector_store
    
    def search_similar_chunks(
        self,
        query: str,
        video_id: str,
        user_id: str,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using vector similarity.
        
        Args:
            query: Search query
            video_id: YouTube video ID
            user_id: User ID
            k: Number of results
            
        Returns:
            List of similar chunks with scores
        """
        return self.vector_store.search_similar_chunks(
            query=query,
            video_id=video_id,
            user_id=user_id,
            k=k
        )
    
    def save_video_embeddings(
        self,
        video_id: str,
        chunks: List[Dict[str, Any]],
        user_id: str
    ) -> int:
        """
        Save video chunks with embeddings.
        
        Args:
            video_id: YouTube video ID
            chunks: List of text chunks
            user_id: User ID
            
        Returns:
            Number of embeddings saved
        """
        return self.vector_store.save_video_embeddings(
            video_id=video_id,
            chunks=chunks,
            user_id=user_id
        )
    
    def get_video_chunks(
        self,
        video_id: str,
        user_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get all chunks for a video.
        
        Args:
            video_id: YouTube video ID
            user_id: User ID
            limit: Maximum chunks to return
            
        Returns:
            List of chunk documents
        """
        return self.vector_store.get_video_chunks(
            video_id=video_id,
            user_id=user_id,
            limit=limit
        )
    
    def delete_video_embeddings(self, video_id: str, user_id: str) -> int:
        """
        Delete all embeddings for a video.
        
        Args:
            video_id: YouTube video ID
            user_id: User ID
            
        Returns:
            Number of embeddings deleted
        """
        return self.vector_store.delete_video_embeddings(
            video_id=video_id,
            user_id=user_id
        )
    
    def get_embedding_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get embedding statistics for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with statistics
        """
        return self.vector_store.get_embedding_stats(user_id=user_id)
