from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from pymongo import MongoClient
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from src.core.config import get_settings

# Get settings instance
settings = get_settings()
MONGODB_URI = settings.MONGODB_URI
MONGODB_DB_NAME = settings.MONGODB_DB_NAME
MONGODB_VIDEOS_COLLECTION = settings.MONGODB_VIDEOS_COLLECTION
MONGODB_EMBEDDINGS_COLLECTION = settings.MONGODB_EMBEDDINGS_COLLECTION
ATLAS_VECTOR_SEARCH_INDEX_NAME = settings.ATLAS_VECTOR_SEARCH_INDEX_NAME
EMBEDDING_MODEL = settings.EMBEDDING_MODEL
EMBEDDING_DIMENSIONS = settings.EMBEDDING_DIMENSIONS
EMBEDDING_TASK_TYPE = settings.EMBEDDING_TASK_TYPE

logger = logging.getLogger(__name__)


class MongoDBVectorStoreManager:
    """
    Manages video embeddings in MongoDB Atlas with Vector Search.
    
    Architecture:
    - videos collection: Video metadata (title, chunks_count, users, etc.)
    - video_embeddings collection: Chunks with 768-dim embeddings
    - Vector Search Index: Enables fast similarity search
    """
    
    def __init__(self, api_key: str, mongodb_uri: str = None):
        """
        Initialize MongoDB Vector Store Manager.
        
        Args:
            api_key: Google API key for embeddings
            mongodb_uri: MongoDB connection string (optional, uses config default)
        """
        self.api_key = api_key
        self.mongodb_uri = mongodb_uri or MONGODB_URI
        
        # Initialize MongoDB client
        self.client: MongoClient = MongoClient(self.mongodb_uri)
        self.db: Database = self.client[MONGODB_DB_NAME]
        self.videos_collection: Collection = self.db[MONGODB_VIDEOS_COLLECTION]
        self.embeddings_collection: Collection = self.db[MONGODB_EMBEDDINGS_COLLECTION]
        
        # Initialize embeddings model
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=EMBEDDING_MODEL,
            google_api_key=api_key,
            output_dimensionality=EMBEDDING_DIMENSIONS,
            task_type=EMBEDDING_TASK_TYPE
        )
        
        # Initialize vector store (for search operations)
        self.vector_store = MongoDBAtlasVectorSearch(
            embedding=self.embeddings,
            collection=self.embeddings_collection,
            index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
            relevance_score_fn="cosine"
        )
        
        logger.info(f"✅ Connected to MongoDB: {MONGODB_DB_NAME}")
        logger.info(f"✅ Collections: {MONGODB_VIDEOS_COLLECTION}, {MONGODB_EMBEDDINGS_COLLECTION}")
    
    def video_exists(self, video_id: str) -> bool:
        """
        Check if video has already been processed.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            True if video exists in database
        """
        return self.videos_collection.find_one({"video_id": video_id}) is not None
    
    def user_has_video(self, user_id: str, video_id: str) -> bool:
        """
        Check if user has access to a specific video.
        
        Args:
            user_id: User ID
            video_id: YouTube video ID
            
        Returns:
            True if user has access to the video
        """
        video = self.videos_collection.find_one({
            "video_id": video_id,
            "users": user_id
        })
        return video is not None
    
    def get_video_metadata(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Get video metadata.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Video metadata dict or None if not found
        """
        return self.videos_collection.find_one(
            {"video_id": video_id},
            {"_id": 0}  # Exclude MongoDB _id field
        )
    
    def get_suggested_questions(self, video_id: str) -> List[str]:
        """
        Get pre-generated suggested questions for a video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            List of suggested questions, or empty list if none found
        """
        video_metadata = self.get_video_metadata(video_id)
        if video_metadata:
            return video_metadata.get("suggested_questions", [])
        return []
    
    def store_video(
        self,
        video_id: str,
        chunks: List[str],
        video_url: str,
        user_id: Optional[str] = None,
        video_title: Optional[str] = None,
        suggested_questions: Optional[List[str]] = None,
        summary: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process and store video chunks with embeddings in MongoDB.
        
        This method:
        1. Checks if video already exists (avoid re-processing)
        2. Generates embeddings for all chunks
        3. Stores chunks + embeddings in video_embeddings collection
        4. Stores metadata in videos collection (including suggested questions)
        
        Args:
            video_id: YouTube video ID
            chunks: List of text chunks
            video_url: YouTube video URL
            user_id: Optional user ID who processed the video
            video_title: Optional video title
            suggested_questions: Optional list of pre-generated questions about the video
            
        Returns:
            Dict with processing results
        """
        try:
            # Check if video already exists
            existing_video = self.get_video_metadata(video_id)
            if existing_video:
                logger.info(f"✅ Video {video_id} already exists, skipping processing")
                
                # Update users list if user_id provided
                if user_id and user_id not in existing_video.get("users", []):
                    self.videos_collection.update_one(
                        {"video_id": video_id},
                        {"$addToSet": {"users": user_id}}
                    )
                
                return {
                    "video_id": video_id,
                    "chunks_count": existing_video["chunks_count"],
                    "status": "already_exists",
                    "message": "Video already processed, using existing embeddings"
                }
            
            # Generate embeddings for all chunks
            logger.info(f"📊 Generating embeddings for {len(chunks)} chunks...")
            embeddings_list = self.embeddings.embed_documents(chunks)
            
            # Prepare documents for MongoDB
            documents = []
            for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings_list)):
                doc = {
                    "video_id": video_id,
                    "chunk_id": f"chunk_{i + 1}",
                    "text": chunk_text,
                    "embedding": embedding,
                    "metadata": {
                        "chunk_index": i + 1,
                        "total_chunks": len(chunks),
                        "video_url": video_url,
                        "video_title": video_title,
                        "processed_at": datetime.utcnow(),
                        "user_id": user_id
                    }
                }
                documents.append(doc)
            
            # Insert chunks into MongoDB
            logger.info(f"💾 Storing {len(documents)} chunks in MongoDB...")
            result = self.embeddings_collection.insert_many(documents)
            logger.info(f"✅ Inserted {len(result.inserted_ids)} chunks")
            
            # Store video metadata
            video_metadata = {
                "video_id": video_id,
                "title": video_title or f"Video {video_id}",
                "url": video_url,
                "chunks_count": len(chunks),
                "embedding_dimensions": EMBEDDING_DIMENSIONS,
                "processed_at": datetime.utcnow(),
                "users": [user_id] if user_id else [],
                "status": "ready",
                "transcript_length": sum(len(chunk) for chunk in chunks),
                "suggested_questions": suggested_questions or [],
                "summary": summary or ""
            }
            self.videos_collection.insert_one(video_metadata)
            logger.info(f"✅ Stored metadata for video {video_id}")
            
            return {
                "video_id": video_id,
                "chunks_count": len(chunks),
                "status": "success",
                "message": "Video processed and stored successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Error storing video {video_id}: {str(e)}")
            raise
    
    def search_video(
        self,
        video_id: str,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks in a specific video.
        
        This method:
        1. Generates query embedding
        2. Uses MongoDB Atlas Vector Search
        3. Filters by video_id
        4. Returns top K similar chunks
        
        Args:
            video_id: YouTube video ID to search in
            query: Search query text
            top_k: Number of results to return
            
        Returns:
            List of dicts with chunk_id, text, and similarity score
        """
        try:
            # Check if video exists
            if not self.video_exists(video_id):
                raise ValueError(f"Video {video_id} not found in database")
            
            # Perform vector search with filter
            logger.info(f"🔍 Searching video {video_id} for: '{query}'")
            
            # Use LangChain's similarity_search with filter
            results = self.vector_store.similarity_search_with_score(
                query=query,
                k=top_k if top_k else 3,
                pre_filter={"video_id": video_id}
            )
            
            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "chunk_id": doc.metadata.get("chunk_id", "unknown"),
                    "text": doc.page_content,
                    "score": float(score),
                    "metadata": doc.metadata
                })
            
            logger.info(f"✅ Found {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Error searching video {video_id}: {str(e)}")
            raise
    
    def list_videos(
        self,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List all processed videos.
        
        Args:
            user_id: Optional filter by user who processed the video
            limit: Maximum number of videos to return
            
        Returns:
            List of video metadata dicts
        """
        query = {}
        if user_id:
            query["users"] = user_id
        
        videos = list(
            self.videos_collection.find(
                query,
                {"_id": 0}
            ).limit(limit).sort("processed_at", -1)
        )
        
        return videos
    
    def delete_video(self, video_id: str) -> Dict[str, Any]:
        """
        Delete video and all its chunks from database.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dict with deletion results
        """
        try:
            # Delete chunks
            chunks_result = self.embeddings_collection.delete_many({"video_id": video_id})
            
            # Delete metadata
            metadata_result = self.videos_collection.delete_one({"video_id": video_id})
            
            logger.info(f"🗑️ Deleted video {video_id}: {chunks_result.deleted_count} chunks")
            
            return {
                "video_id": video_id,
                "chunks_deleted": chunks_result.deleted_count,
                "metadata_deleted": metadata_result.deleted_count > 0,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"❌ Error deleting video {video_id}: {str(e)}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dict with stats about videos and chunks
        """
        total_videos = self.videos_collection.count_documents({})
        total_chunks = self.embeddings_collection.count_documents({})
        
        # Get storage size estimates
        db_stats = self.db.command("dbStats")
        
        return {
            "total_videos": total_videos,
            "total_chunks": total_chunks,
            "avg_chunks_per_video": total_chunks / total_videos if total_videos > 0 else 0,
            "database_size_mb": db_stats.get("dataSize", 0) / (1024 * 1024),
            "storage_size_mb": db_stats.get("storageSize", 0) / (1024 * 1024)
        }
    
    def close(self):
        """Close MongoDB connection."""
        self.client.close()
        logger.info("🔌 MongoDB connection closed")
