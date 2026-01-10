"""MongoDB database connection and management."""

from typing import Generator
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
import logging

from src.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


class MongoDB:
    """MongoDB connection manager."""
    
    def __init__(self, uri: str, db_name: str):
        """Initialize MongoDB connection."""
        self.uri = uri
        self.db_name = db_name
        self.client: MongoClient = None
        self.db: Database = None
        
    def connect(self):
        """Establish MongoDB connection."""
        try:
            self.client = MongoClient(self.uri)
            self.db = self.client[self.db_name]
            # Test connection
            self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB: {self.db_name}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
    
    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    def get_database(self) -> Database:
        """Get database instance."""
        if self.db is None:
            raise RuntimeError("MongoDB not connected. Call connect() first.")
        return self.db
    
    def get_collection(self, name: str) -> Collection:
        """Get collection by name."""
        return self.get_database()[name]


# Global MongoDB instance
_mongodb: MongoDB = None


def init_mongodb(settings: Settings = None) -> MongoDB:
    """Initialize MongoDB connection."""
    global _mongodb
    
    if settings is None:
        settings = get_settings()
    
    _mongodb = MongoDB(settings.MONGODB_URI, settings.MONGODB_DB_NAME)
    _mongodb.connect()
    return _mongodb


def close_mongodb():
    """Close MongoDB connection."""
    global _mongodb
    if _mongodb:
        _mongodb.close()
        _mongodb = None


def get_mongodb() -> Generator[Database, None, None]:
    """
    FastAPI dependency for MongoDB database.
    
    Usage:
        @router.get("/items")
        def get_items(db: Database = Depends(get_mongodb)):
            return db.items.find()
    """
    if _mongodb is None:
        raise RuntimeError("MongoDB not initialized. Call init_mongodb() in lifespan.")
    
    yield _mongodb.get_database()
