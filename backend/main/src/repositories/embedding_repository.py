"""Embedding repository for vector operations."""

from typing import List, Dict, Any, Optional
from pymongo.database import Database

from src.repositories.base import BaseRepository


class EmbeddingRepository(BaseRepository):
    """Repository for embedding operations."""
    
    def __init__(self, db: Database, collection_name: str = "video_embeddings"):
        """Initialize embedding repository."""
        super().__init__(db, collection_name)
    
    def find_by_video_id(
        self,
        video_id: str,
        limit: int = None
    ) -> List[Dict[str, Any]]:
        """
        Find all embeddings for a video.
        
        Args:
            video_id: YouTube video ID
            limit: Maximum number of embeddings (optional)
            
        Returns:
            List of embedding documents
        """
        filter_query = {"video_id": video_id}
        if limit:
            return self.find_many(
                filter_query,
                limit=limit,
                sort=[("chunk_index", 1)]
            )
        else:
            cursor = self.collection.find(filter_query).sort("chunk_index", 1)
            return list(cursor)
    
    def delete_by_video_id(self, video_id: str) -> int:
        """
        Delete all embeddings for a video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Number of documents deleted
        """
        return self.delete_many({"video_id": video_id})
    
    def create_embeddings(
        self,
        video_id: str,
        chunks: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Create multiple embedding documents.
        
        Args:
            video_id: YouTube video ID
            chunks: List of chunk dictionaries with text, embedding, etc.
            
        Returns:
            List of created document IDs
        """
        documents = []
        for i, chunk in enumerate(chunks):
            doc = {
                "video_id": video_id,
                "chunk_id": chunk.get("chunk_id", f"chunk_{i}"),
                "text": chunk["text"],
                "embedding": chunk["embedding"],
                "chunk_index": i,
                "metadata": chunk.get("metadata", {})
            }
            documents.append(doc)
        
        return self.insert_many(documents)
