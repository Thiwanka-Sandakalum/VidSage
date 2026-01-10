import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.infrastructure.database.vector_store import MongoDBVectorStoreManager


class TestMongoDBVectorStoreManager:
    @patch('src.infrastructure.database.vector_store.MongoClient')
    @patch('src.infrastructure.database.vector_store.GoogleGenerativeAIEmbeddings')
    @patch('src.infrastructure.database.vector_store.MongoDBAtlasVectorSearch')
    def test_init_success(self, mock_vector_search, mock_embeddings, mock_mongo_client):
        mock_db = MagicMock()
        mock_client_instance = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client_instance
        
        manager = MongoDBVectorStoreManager(
            api_key="test_key",
            mongodb_uri="mongodb://localhost:27017"
        )
        
        assert manager.api_key == "test_key"
        assert manager.mongodb_uri == "mongodb://localhost:27017"
        mock_mongo_client.assert_called_once()
    
    @patch('services.mongodb_vector_store.MongoClient')
    @patch('services.mongodb_vector_store.GoogleGenerativeAIEmbeddings')
    @patch('services.mongodb_vector_store.MongoDBAtlasVectorSearch')
    def test_video_exists_true(self, mock_vector_search, mock_embeddings, mock_mongo_client):
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = {"video_id": "test123"}
        
        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        
        mock_client_instance = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client_instance
        
        manager = MongoDBVectorStoreManager(api_key="test_key")
        
        result = manager.video_exists("test123")
        
        assert result is True
        mock_collection.find_one.assert_called_with({"video_id": "test123"})
    
    @patch('services.mongodb_vector_store.MongoClient')
    @patch('services.mongodb_vector_store.GoogleGenerativeAIEmbeddings')
    @patch('services.mongodb_vector_store.MongoDBAtlasVectorSearch')
    def test_video_exists_false(self, mock_vector_search, mock_embeddings, mock_mongo_client):
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = None
        
        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        
        mock_client_instance = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client_instance
        
        manager = MongoDBVectorStoreManager(api_key="test_key")
        
        result = manager.video_exists("nonexistent")
        
        assert result is False
    
    @patch('services.mongodb_vector_store.MongoClient')
    @patch('services.mongodb_vector_store.GoogleGenerativeAIEmbeddings')
    @patch('services.mongodb_vector_store.MongoDBAtlasVectorSearch')
    def test_get_video_metadata_found(self, mock_vector_search, mock_embeddings, mock_mongo_client):
        expected_metadata = {
            "video_id": "test123",
            "title": "Test Video",
            "chunks_count": 10
        }
        
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = expected_metadata
        
        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        
        mock_client_instance = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client_instance
        
        manager = MongoDBVectorStoreManager(api_key="test_key")
        
        result = manager.get_video_metadata("test123")
        
        assert result == expected_metadata
    
    @patch('services.mongodb_vector_store.MongoClient')
    @patch('services.mongodb_vector_store.GoogleGenerativeAIEmbeddings')
    @patch('services.mongodb_vector_store.MongoDBAtlasVectorSearch')
    def test_get_video_metadata_not_found(self, mock_vector_search, mock_embeddings, mock_mongo_client):
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = None
        
        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        
        mock_client_instance = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client_instance
        
        manager = MongoDBVectorStoreManager(api_key="test_key")
        
        result = manager.get_video_metadata("nonexistent")
        
        assert result is None
    
    @patch('services.mongodb_vector_store.MongoClient')
    @patch('services.mongodb_vector_store.GoogleGenerativeAIEmbeddings')
    @patch('services.mongodb_vector_store.MongoDBAtlasVectorSearch')
    @patch('services.mongodb_vector_store.datetime')
    def test_store_video_new(self, mock_datetime, mock_vector_search, mock_embeddings_class, mock_mongo_client):
        mock_datetime.utcnow.return_value = datetime(2024, 1, 1)
        
        mock_embeddings_collection = MagicMock()
        mock_embeddings_collection.insert_many.return_value.inserted_ids = [1, 2, 3]
        
        mock_videos_collection = MagicMock()
        mock_videos_collection.find_one.return_value = None
        mock_videos_collection.insert_one.return_value = MagicMock()
        
        mock_db = MagicMock()
        def getitem_side_effect(key):
            if "embedding" in key:
                return mock_embeddings_collection
            else:
                return mock_videos_collection
        mock_db.__getitem__.side_effect = getitem_side_effect
        
        mock_client_instance = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client_instance
        
        mock_embeddings_instance = MagicMock()
        mock_embeddings_instance.embed_documents.return_value = [
            [0.1] * 768,
            [0.2] * 768,
            [0.3] * 768
        ]
        mock_embeddings_class.return_value = mock_embeddings_instance
        
        manager = MongoDBVectorStoreManager(api_key="test_key")
        manager.videos_collection = mock_videos_collection
        manager.embeddings_collection = mock_embeddings_collection
        
        chunks = ["chunk1", "chunk2", "chunk3"]
        result = manager.store_video(
            video_id="test123",
            chunks=chunks,
            video_url="https://youtube.com/watch?v=test123",
            video_title="Test Video"
        )
        
        assert result["video_id"] == "test123"
        assert result["chunks_count"] == 3
        assert result["status"] == "success"
    
    @patch('services.mongodb_vector_store.MongoClient')
    @patch('services.mongodb_vector_store.GoogleGenerativeAIEmbeddings')
    @patch('services.mongodb_vector_store.MongoDBAtlasVectorSearch')
    def test_store_video_existing(self, mock_vector_search, mock_embeddings, mock_mongo_client):
        existing_metadata = {
            "video_id": "test123",
            "chunks_count": 10,
            "users": []
        }
        
        mock_videos_collection = MagicMock()
        mock_videos_collection.find_one.return_value = existing_metadata
        
        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_videos_collection
        
        mock_client_instance = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client_instance
        
        manager = MongoDBVectorStoreManager(api_key="test_key")
        manager.videos_collection = mock_videos_collection
        
        chunks = ["chunk1", "chunk2"]
        result = manager.store_video(
            video_id="test123",
            chunks=chunks,
            video_url="https://youtube.com/watch?v=test123"
        )
        
        assert result["status"] == "already_exists"
        assert result["chunks_count"] == 10
    
    @patch('services.mongodb_vector_store.MongoClient')
    @patch('services.mongodb_vector_store.GoogleGenerativeAIEmbeddings')
    @patch('services.mongodb_vector_store.MongoDBAtlasVectorSearch')
    def test_search_video_success(self, mock_vector_search_class, mock_embeddings, mock_mongo_client):
        mock_videos_collection = MagicMock()
        mock_videos_collection.find_one.return_value = {"video_id": "test123"}
        
        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_videos_collection
        
        mock_client_instance = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client_instance
        
        mock_doc1 = MagicMock()
        mock_doc1.page_content = "Content 1"
        mock_doc1.metadata = {"chunk_id": "chunk_1"}
        
        mock_doc2 = MagicMock()
        mock_doc2.page_content = "Content 2"
        mock_doc2.metadata = {"chunk_id": "chunk_2"}
        
        mock_vector_search_instance = MagicMock()
        mock_vector_search_instance.similarity_search_with_score.return_value = [
            (mock_doc1, 0.95),
            (mock_doc2, 0.88)
        ]
        mock_vector_search_class.return_value = mock_vector_search_instance
        
        manager = MongoDBVectorStoreManager(api_key="test_key")
        manager.videos_collection = mock_videos_collection
        manager.vector_store = mock_vector_search_instance
        
        results = manager.search_video("test123", "test query", top_k=2)
        
        assert len(results) == 2
        assert results[0]["chunk_id"] == "chunk_1"
        assert results[0]["text"] == "Content 1"
        assert results[0]["score"] == 0.95
    
    @patch('services.mongodb_vector_store.MongoClient')
    @patch('services.mongodb_vector_store.GoogleGenerativeAIEmbeddings')
    @patch('services.mongodb_vector_store.MongoDBAtlasVectorSearch')
    def test_search_video_not_found(self, mock_vector_search, mock_embeddings, mock_mongo_client):
        mock_videos_collection = MagicMock()
        mock_videos_collection.find_one.return_value = None
        
        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_videos_collection
        
        mock_client_instance = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client_instance
        
        manager = MongoDBVectorStoreManager(api_key="test_key")
        manager.videos_collection = mock_videos_collection
        
        with pytest.raises(ValueError, match="not found in database"):
            manager.search_video("nonexistent", "query")
    
    @patch('services.mongodb_vector_store.MongoClient')
    @patch('services.mongodb_vector_store.GoogleGenerativeAIEmbeddings')
    @patch('services.mongodb_vector_store.MongoDBAtlasVectorSearch')
    def test_list_videos_all(self, mock_vector_search, mock_embeddings, mock_mongo_client):
        mock_videos = [
            {"video_id": "v1", "title": "Video 1"},
            {"video_id": "v2", "title": "Video 2"}
        ]
        
        mock_cursor = MagicMock()
        mock_cursor.limit.return_value.sort.return_value = mock_videos
        
        mock_videos_collection = MagicMock()
        mock_videos_collection.find.return_value = mock_cursor
        
        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_videos_collection
        
        mock_client_instance = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client_instance
        
        manager = MongoDBVectorStoreManager(api_key="test_key")
        manager.videos_collection = mock_videos_collection
        
        results = manager.list_videos()
        
        assert len(results) == 2
        assert results[0]["video_id"] == "v1"
    
    @patch('services.mongodb_vector_store.MongoClient')
    @patch('services.mongodb_vector_store.GoogleGenerativeAIEmbeddings')
    @patch('services.mongodb_vector_store.MongoDBAtlasVectorSearch')
    def test_list_videos_by_user(self, mock_vector_search, mock_embeddings, mock_mongo_client):
        mock_videos = [{"video_id": "v1", "users": ["user1"]}]
        
        mock_cursor = MagicMock()
        mock_cursor.limit.return_value.sort.return_value = mock_videos
        
        mock_videos_collection = MagicMock()
        mock_videos_collection.find.return_value = mock_cursor
        
        mock_db = MagicMock()
        mock_db.__getitem__.return_value = mock_videos_collection
        
        mock_client_instance = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client_instance
        
        manager = MongoDBVectorStoreManager(api_key="test_key")
        manager.videos_collection = mock_videos_collection
        
        results = manager.list_videos(user_id="user1")
        
        assert len(results) == 1
        mock_videos_collection.find.assert_called_with({"users": "user1"}, {"_id": 0})
    
    @patch('services.mongodb_vector_store.MongoClient')
    @patch('services.mongodb_vector_store.GoogleGenerativeAIEmbeddings')
    @patch('services.mongodb_vector_store.MongoDBAtlasVectorSearch')
    def test_delete_video_success(self, mock_vector_search, mock_embeddings, mock_mongo_client):
        mock_embeddings_collection = MagicMock()
        mock_embeddings_collection.delete_many.return_value.deleted_count = 10
        
        mock_videos_collection = MagicMock()
        mock_videos_collection.delete_one.return_value.deleted_count = 1
        
        mock_db = MagicMock()
        def getitem_side_effect(key):
            if "embedding" in key:
                return mock_embeddings_collection
            else:
                return mock_videos_collection
        mock_db.__getitem__.side_effect = getitem_side_effect
        
        mock_client_instance = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client_instance
        
        manager = MongoDBVectorStoreManager(api_key="test_key")
        manager.embeddings_collection = mock_embeddings_collection
        manager.videos_collection = mock_videos_collection
        
        result = manager.delete_video("test123")
        
        assert result["video_id"] == "test123"
        assert result["chunks_deleted"] == 10
        assert result["metadata_deleted"] is True
        assert result["status"] == "success"
    
    @patch('services.mongodb_vector_store.MongoClient')
    @patch('services.mongodb_vector_store.GoogleGenerativeAIEmbeddings')
    @patch('services.mongodb_vector_store.MongoDBAtlasVectorSearch')
    def test_get_stats(self, mock_vector_search, mock_embeddings, mock_mongo_client):
        mock_videos_collection = MagicMock()
        mock_videos_collection.count_documents.return_value = 5
        
        mock_embeddings_collection = MagicMock()
        mock_embeddings_collection.count_documents.return_value = 50
        
        mock_db = MagicMock()
        def getitem_side_effect(key):
            if "embedding" in key:
                return mock_embeddings_collection
            else:
                return mock_videos_collection
        mock_db.__getitem__.side_effect = getitem_side_effect
        mock_db.command.return_value = {
            "dataSize": 1024 * 1024 * 10,
            "storageSize": 1024 * 1024 * 15
        }
        
        mock_client_instance = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        mock_mongo_client.return_value = mock_client_instance
        
        manager = MongoDBVectorStoreManager(api_key="test_key")
        manager.videos_collection = mock_videos_collection
        manager.embeddings_collection = mock_embeddings_collection
        manager.db = mock_db
        
        stats = manager.get_stats()
        
        assert stats["total_videos"] == 5
        assert stats["total_chunks"] == 50
        assert stats["avg_chunks_per_video"] == 10
    
    @patch('services.mongodb_vector_store.MongoClient')
    @patch('services.mongodb_vector_store.GoogleGenerativeAIEmbeddings')
    @patch('services.mongodb_vector_store.MongoDBAtlasVectorSearch')
    def test_close_connection(self, mock_vector_search, mock_embeddings, mock_mongo_client):
        mock_client_instance = MagicMock()
        mock_mongo_client.return_value = mock_client_instance
        
        mock_db = MagicMock()
        mock_client_instance.__getitem__.return_value = mock_db
        
        manager = MongoDBVectorStoreManager(api_key="test_key")
        
        manager.close()
        
        mock_client_instance.close.assert_called_once()
