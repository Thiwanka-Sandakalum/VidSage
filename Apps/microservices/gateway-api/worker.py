"""Gateway worker to consume completion/failure events and update job status in MongoDB."""
import time
import traceback
import sys
import os
import logging

# Ensure shared package importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.rabbitmq_utils import consume_events, close_connection
from shared.config import MONGODB_URI, MONGODB_DB_NAME
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_mongo_client():
    return MongoClient(MONGODB_URI)


# Initialize MongoDB
mongo_client = get_mongo_client()
db = mongo_client[MONGODB_DB_NAME]
jobs_coll = db["jobs"]


def handle_event(event_type: str, payload: dict):
    """Handle embedding.completed and processing.failed events."""
    job_id = payload.get("job_id")
    try:
        if event_type == "embedding.completed":
            jobs_coll.update_one(
                {"_id": job_id},
                {"$set": {
                    "status": "completed",
                    "current_step": "completed",
                    "chunk_count": payload.get("chunk_count", 0)
                }}
            )
            logger.info(f"✅ Job {job_id} marked completed")
            
        elif event_type == "processing.failed":
            jobs_coll.update_one(
                {"_id": job_id},
                {"$set": {
                    "status": "failed",
                    "current_step": payload.get("step"),
                    "error": payload.get("error")
                }}
            )
            logger.error(f"❌ Job {job_id} marked failed: {payload.get('error')}")
            
    except Exception as e:
        logger.error(f"❌ Error handling event for job {job_id}: {e}")
        traceback.print_exc()
        raise


def run_loop():
    """Run the consumer loop."""
    logger.info("🚀 Starting gateway worker...")
    
    try:
        consume_events(
            event_types=["embedding.completed", "processing.failed"],
            callback=handle_event,
            queue_name="gateway_status_updates"
        )
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down...")
    finally:
        close_connection()
        mongo_client.close()


if __name__ == "__main__":
    run_loop()
