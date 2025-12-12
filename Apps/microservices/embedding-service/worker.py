"""Embedding Worker - Queue-only service for text chunking and embedding generation."""
import os
import sys
import time
import traceback
import logging
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
import google.generativeai as genai
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Ensure shared package is importable (parent directory)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.rabbitmq_utils import consume_events, publish_event, close_connection
from shared.config import (
    GOOGLE_API_KEY,
    MONGODB_URI,
    MONGODB_DB_NAME,
    MONGODB_COLLECTION,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP
)

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("embedding-worker")

# Initialize Google AI
genai.configure(api_key=GOOGLE_API_KEY)

# MongoDB client (lazy initialization)
mongodb_client = None


def get_mongodb_client():
    """Get or create MongoDB client."""
    global mongodb_client
    if mongodb_client is None:
        logger.debug(f"Creating new MongoDB client connection to: {MONGODB_URI}")
        mongodb_client = MongoClient(MONGODB_URI)
        logger.info("MongoDB client created successfully for embedding worker")
    return mongodb_client


def generate_embeddings_direct(video_id: str, transcript: str, metadata: dict):
    """Generate embeddings directly without API calls."""
    logger.info(f"🔄 Starting text chunking for video_id={video_id}")
    logger.debug(f"📏 Transcript length: {len(transcript)} characters")
    logger.debug(f"⚙️ Chunk settings - Size: {CHUNK_SIZE}, Overlap: {CHUNK_OVERLAP}")
    
    # Step 1: Chunk the transcript
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )
    
    logger.debug("✂️ Splitting transcript into chunks...")
    chunks = text_splitter.split_text(transcript)
    logger.info(f"✅ Transcript split into {len(chunks)} chunks")
    
    if not chunks:
        logger.error("❌ No chunks created from transcript - transcript may be empty")
        raise Exception("No chunks created from transcript")
    
    # Log chunk size distribution
    chunk_sizes = [len(chunk) for chunk in chunks]
    avg_chunk_size = sum(chunk_sizes) / len(chunk_sizes)
    logger.debug(f"📊 Chunk statistics - Avg size: {avg_chunk_size:.0f}, Min: {min(chunk_sizes)}, Max: {max(chunk_sizes)}")
    
    # Step 2: Generate embeddings for each chunk
    logger.info(f"🧠 Starting embedding generation for {len(chunks)} chunks")
    chunk_documents = []
    
    for i, chunk_text in enumerate(chunks):
        try:
            logger.debug(f"🔄 Processing chunk {i+1}/{len(chunks)} (size: {len(chunk_text)} chars)")
            
            # Generate embedding using Google AI
            logger.debug(f"🤖 Calling Google AI embedding API for chunk {i}")
            embedding_result = genai.embed_content(
                model=EMBEDDING_MODEL,
                content=chunk_text,
                task_type="retrieval_document"
            )
            embedding = embedding_result['embedding']
            logger.debug(f"✅ Generated embedding with {len(embedding)} dimensions for chunk {i}")
            
            # Create document for MongoDB
            doc = {
                "video_id": video_id,
                "chunk_id": f"chunk_{i}",
                "chunk_index": i,
                "text": chunk_text,
                "embedding": embedding,
                "metadata": {
                    **metadata,
                    "chunk_index": i,
                    "chunk_size": len(chunk_text)
                }
            }
            chunk_documents.append(doc)
            logger.debug(f"📦 Created document for chunk {i}")
            
        except Exception as e:
            logger.error(f"❌ Failed to generate embedding for chunk {i}: {e}")
            raise Exception(f"Failed to generate embedding for chunk {i}: {str(e)}")
    
    logger.info(f"✅ Successfully generated embeddings for {len(chunk_documents)} chunks")
    
    # Step 3: Store in MongoDB
    logger.info(f"💾 Starting MongoDB storage for video_id={video_id}")
    try:
        logger.debug("🔌 Getting MongoDB client connection...")
        client = get_mongodb_client()
        db = client[MONGODB_DB_NAME]
        collection = db[MONGODB_COLLECTION]
        
        logger.debug(f"🗑️ Deleting existing embeddings for video_id={video_id}")
        delete_result = collection.delete_many({"video_id": video_id})
        logger.debug(f"🗑️ Deleted {delete_result.deleted_count} existing documents")
        
        logger.debug(f"💾 Inserting {len(chunk_documents)} new embedding documents")
        insert_result = collection.insert_many(chunk_documents)
        logger.info(f"✅ Successfully stored {len(insert_result.inserted_ids)} embeddings in MongoDB for video_id={video_id}")
        
    except PyMongoError as e:
        logger.error(f"❌ MongoDB storage failed: {e}")
        raise Exception(f"MongoDB storage failed: {str(e)}")
    
    return {
        "video_id": video_id,
        "chunk_count": len(chunks),
        "status": "completed"
    }


def handle_transcript_downloaded(event_type: str, payload: dict):
    """Handle transcript.downloaded event by generating embeddings directly."""
    job_id = payload.get("job_id")
    video_id = payload.get("video_id")
    transcript = payload.get("transcript")
    metadata = payload.get("metadata", {})
    logger.info(f"📥 Handling job {job_id} for video {video_id}")

    try:
        # Generate embeddings directly (no API call)
        embed_data = generate_embeddings_direct(video_id, transcript, metadata)

        # Publish embedding.completed event
        event_payload = {
            "job_id": job_id,
            "video_id": video_id,
            "chunk_count": embed_data.get("chunk_count", 0)
        }
        publish_event("embedding.completed", event_payload)
        logger.info(f"✅ Published embedding.completed for job {job_id}")

    except Exception as e:
        logger.error(f"❌ Failed to handle job {job_id}: {e}")
        traceback.print_exc()
        publish_event(
            "processing.failed",
            {
                "job_id": job_id,
                "service": "embedding-worker",
                "error": str(e),
                "step": "embedding_generation"
            }
        )
        raise  # Re-raise to trigger requeue


def run_loop():
    """Run the consumer loop."""
    logger.info("🚀 Starting embedding worker...")
    
    try:
        consume_events(
            event_types=["transcript.downloaded"],
            callback=handle_transcript_downloaded,
            queue_name="embedding_queue"
        )
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down...")
    finally:
        close_connection()


if __name__ == "__main__":
    run_loop()
