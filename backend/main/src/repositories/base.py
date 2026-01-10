"""Base repository with common database operations."""

from abc import ABC
from typing import Dict, Any, List, Optional
from pymongo.database import Database
from pymongo.collection import Collection


class BaseRepository(ABC):
    """Base repository with common database operations."""
    
    def __init__(self, db: Database, collection_name: str):
        """
        Initialize repository.
        
        Args:
            db: MongoDB database instance
            collection_name: Name of the collection
        """
        self.db = db
        self.collection: Collection = db[collection_name]
    
    def find_one(self, filter: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find single document.
        
        Args:
            filter: MongoDB filter query
            
        Returns:
            Document or None if not found
        """
        return self.collection.find_one(filter)
    
    def find_many(
        self,
        filter: Dict[str, Any],
        limit: int = 100,
        skip: int = 0,
        sort: Optional[List[tuple]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find multiple documents.
        
        Args:
            filter: MongoDB filter query
            limit: Maximum number of documents to return
            skip: Number of documents to skip
            sort: Sort specification
            
        Returns:
            List of documents
        """
        cursor = self.collection.find(filter).limit(limit).skip(skip)
        if sort:
            cursor = cursor.sort(sort)
        return list(cursor)
    
    def insert_one(self, document: Dict[str, Any]) -> str:
        """
        Insert single document.
        
        Args:
            document: Document to insert
            
        Returns:
            Inserted document ID as string
        """
        result = self.collection.insert_one(document)
        return str(result.inserted_id)
    
    def insert_many(self, documents: List[Dict[str, Any]]) -> List[str]:
        """
        Insert multiple documents.
        
        Args:
            documents: List of documents to insert
            
        Returns:
            List of inserted document IDs as strings
        """
        if not documents:
            return []
        result = self.collection.insert_many(documents)
        return [str(id) for id in result.inserted_ids]
    
    def update_one(
        self,
        filter: Dict[str, Any],
        update: Dict[str, Any]
    ) -> int:
        """
        Update single document.
        
        Args:
            filter: MongoDB filter query
            update: Update operations
            
        Returns:
            Number of documents modified
        """
        result = self.collection.update_one(filter, update)
        return result.modified_count
    
    def update_many(
        self,
        filter: Dict[str, Any],
        update: Dict[str, Any]
    ) -> int:
        """
        Update multiple documents.
        
        Args:
            filter: MongoDB filter query
            update: Update operations
            
        Returns:
            Number of documents modified
        """
        result = self.collection.update_many(filter, update)
        return result.modified_count
    
    def delete_one(self, filter: Dict[str, Any]) -> int:
        """
        Delete single document.
        
        Args:
            filter: MongoDB filter query
            
        Returns:
            Number of documents deleted
        """
        result = self.collection.delete_one(filter)
        return result.deleted_count
    
    def delete_many(self, filter: Dict[str, Any]) -> int:
        """
        Delete multiple documents.
        
        Args:
            filter: MongoDB filter query
            
        Returns:
            Number of documents deleted
        """
        result = self.collection.delete_many(filter)
        return result.deleted_count
    
    def exists(self, filter: Dict[str, Any]) -> bool:
        """
        Check if document exists.
        
        Args:
            filter: MongoDB filter query
            
        Returns:
            True if at least one document matches the filter
        """
        return self.collection.count_documents(filter, limit=1) > 0
    
    def count(self, filter: Dict[str, Any] = None) -> int:
        """
        Count documents matching filter.
        
        Args:
            filter: MongoDB filter query (default: empty filter)
            
        Returns:
            Number of matching documents
        """
        if filter is None:
            filter = {}
        return self.collection.count_documents(filter)
