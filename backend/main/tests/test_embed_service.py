import pytest
from unittest.mock import Mock, patch, MagicMock
import os
from services.embed_service import (
    VectorStoreManager,
    create_embeddings,
    EmbeddingError
)


class TestVectorStoreManager:
    def test_init_with_api_key(self):
        with patch('services.embed_service.GoogleGenerativeAIEmbeddings'):
            manager = VectorStoreManager(api_key="test_key")
            
            assert manager.api_key == "test_key"
            assert manager.model == "models/text-embedding-004"
            assert manager.output_dimensionality == 768
            assert manager.task_type == "RETRIEVAL_DOCUMENT"
    
    def test_init_with_env_api_key(self):
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'env_key'}):
            with patch('services.embed_service.GoogleGenerativeAIEmbeddings'):
                manager = VectorStoreManager()
                
                assert manager.api_key == "env_key"
    
    def test_init_without_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(EmbeddingError, match="Google API key not found"):
                VectorStoreManager()
    
    def test_init_custom_model(self):
        with patch('services.embed_service.GoogleGenerativeAIEmbeddings'):
            manager = VectorStoreManager(
                api_key="test_key",
                model="models/custom-model",
                output_dimensionality=512
            )
            
            assert manager.model == "models/custom-model"
            assert manager.output_dimensionality == 512
    
    def test_init_custom_task_type(self):
        with patch('services.embed_service.GoogleGenerativeAIEmbeddings'):
            manager = VectorStoreManager(
                api_key="test_key",
                task_type="SEMANTIC_SIMILARITY"
            )
            
            assert manager.task_type == "SEMANTIC_SIMILARITY"
    
    def test_init_embedding_failure(self):
        with patch('services.embed_service.GoogleGenerativeAIEmbeddings') as mock_emb:
            mock_emb.side_effect = Exception("API Error")
            
            with pytest.raises(EmbeddingError, match="Failed to initialize embeddings"):
                VectorStoreManager(api_key="test_key")
    
    @patch('services.embed_service.GoogleGenerativeAIEmbeddings')
    @patch('services.embed_service.InMemoryVectorStore')
    def test_embed_chunks_success(self, mock_vector_store, mock_embeddings):
        manager = VectorStoreManager(api_key="test_key")
        
        chunks = ["chunk1", "chunk2", "chunk3"]
        mock_embeddings_instance = MagicMock()
        manager.embeddings = mock_embeddings_instance
        
        mock_embeddings_instance.embed_documents.return_value = [
            [0.1] * 768,
            [0.2] * 768,
            [0.3] * 768
        ]
        
        mock_vector_store.from_documents.return_value = MagicMock()
        
        vector_store, dimensions, embeddings = manager.embed_chunks(chunks)
        
        assert dimensions == 768
        assert len(embeddings) == 3
        assert mock_embeddings_instance.embed_documents.called
    
    @patch('services.embed_service.GoogleGenerativeAIEmbeddings')
    def test_embed_chunks_empty_list(self, mock_embeddings):
        manager = VectorStoreManager(api_key="test_key")
        
        with pytest.raises(EmbeddingError, match="No chunks provided"):
            manager.embed_chunks([])
    
    @patch('services.embed_service.GoogleGenerativeAIEmbeddings')
    @patch('services.embed_service.InMemoryVectorStore')
    def test_embed_chunks_with_metadata(self, mock_vector_store, mock_embeddings):
        manager = VectorStoreManager(api_key="test_key")
        
        chunks = ["chunk1", "chunk2"]
        metadata = [
            {"source": "doc1"},
            {"source": "doc2"}
        ]
        
        mock_embeddings_instance = MagicMock()
        manager.embeddings = mock_embeddings_instance
        mock_embeddings_instance.embed_documents.return_value = [[0.1] * 768, [0.2] * 768]
        mock_vector_store.from_documents.return_value = MagicMock()
        
        vector_store, dimensions, embeddings = manager.embed_chunks(chunks, metadata)
        
        assert len(embeddings) == 2
    
    @patch('services.embed_service.GoogleGenerativeAIEmbeddings')
    @patch('services.embed_service.InMemoryVectorStore')
    def test_embed_chunks_failure(self, mock_vector_store, mock_embeddings):
        manager = VectorStoreManager(api_key="test_key")
        
        chunks = ["chunk1", "chunk2"]
        mock_embeddings_instance = MagicMock()
        manager.embeddings = mock_embeddings_instance
        mock_embeddings_instance.embed_documents.side_effect = Exception("API Error")
        
        with pytest.raises(EmbeddingError, match="Failed to generate embeddings"):
            manager.embed_chunks(chunks)
    
    @patch('services.embed_service.GoogleGenerativeAIEmbeddings')
    def test_search_similar_no_vector_store(self, mock_embeddings):
        manager = VectorStoreManager(api_key="test_key")
        
        with pytest.raises(EmbeddingError, match="Vector store not initialized"):
            manager.search_similar("query")
    
    @patch('services.embed_service.GoogleGenerativeAIEmbeddings')
    @patch('services.embed_service.InMemoryVectorStore')
    def test_search_similar_success(self, mock_vector_store, mock_embeddings):
        manager = VectorStoreManager(api_key="test_key")
        
        chunks = ["test chunk"]
        mock_embeddings_instance = MagicMock()
        manager.embeddings = mock_embeddings_instance
        mock_embeddings_instance.embed_documents.return_value = [[0.1] * 768]
        
        mock_vs_instance = MagicMock()
        mock_vector_store.from_documents.return_value = mock_vs_instance
        
        manager.embed_chunks(chunks)
        
        mock_vs_instance.similarity_search_with_score.return_value = [
            (MagicMock(), 0.95)
        ]
        
        results = manager.search_similar("query", k=1)
        
        assert len(results) == 1
        assert mock_vs_instance.similarity_search_with_score.called
    
    @patch('services.embed_service.GoogleGenerativeAIEmbeddings')
    @patch('services.embed_service.InMemoryVectorStore')
    def test_search_similar_custom_k(self, mock_vector_store, mock_embeddings):
        manager = VectorStoreManager(api_key="test_key")
        
        chunks = ["chunk1", "chunk2", "chunk3"]
        mock_embeddings_instance = MagicMock()
        manager.embeddings = mock_embeddings_instance
        mock_embeddings_instance.embed_documents.return_value = [[0.1] * 768] * 3
        
        mock_vs_instance = MagicMock()
        mock_vector_store.from_documents.return_value = mock_vs_instance
        
        manager.embed_chunks(chunks)
        
        mock_vs_instance.similarity_search_with_score.return_value = [
            (MagicMock(), 0.9),
            (MagicMock(), 0.8),
            (MagicMock(), 0.7)
        ]
        
        results = manager.search_similar("query", k=3)
        
        assert len(results) == 3
    
    @patch('services.embed_service.GoogleGenerativeAIEmbeddings')
    @patch('services.embed_service.InMemoryVectorStore')
    def test_search_similar_failure(self, mock_vector_store, mock_embeddings):
        manager = VectorStoreManager(api_key="test_key")
        
        chunks = ["test chunk"]
        mock_embeddings_instance = MagicMock()
        manager.embeddings = mock_embeddings_instance
        mock_embeddings_instance.embed_documents.return_value = [[0.1] * 768]
        
        mock_vs_instance = MagicMock()
        mock_vector_store.from_documents.return_value = mock_vs_instance
        manager.embed_chunks(chunks)
        
        mock_vs_instance.similarity_search_with_score.side_effect = Exception("Search failed")
        
        with pytest.raises(EmbeddingError, match="Failed to search vector store"):
            manager.search_similar("query")
    
    @patch('services.embed_service.GoogleGenerativeAIEmbeddings')
    def test_get_all_documents_no_vector_store(self, mock_embeddings):
        manager = VectorStoreManager(api_key="test_key")
        
        with pytest.raises(EmbeddingError, match="Vector store not initialized"):
            manager.get_all_documents()
    
    @patch('services.embed_service.GoogleGenerativeAIEmbeddings')
    @patch('services.embed_service.InMemoryVectorStore')
    def test_get_all_documents_success(self, mock_vector_store, mock_embeddings):
        manager = VectorStoreManager(api_key="test_key")
        
        chunks = ["chunk1", "chunk2"]
        mock_embeddings_instance = MagicMock()
        manager.embeddings = mock_embeddings_instance
        mock_embeddings_instance.embed_documents.return_value = [[0.1] * 768, [0.2] * 768]
        
        mock_vs_instance = MagicMock()
        mock_vector_store.from_documents.return_value = mock_vs_instance
        
        manager.embed_chunks(chunks)
        
        mock_vs_instance.similarity_search.return_value = [MagicMock(), MagicMock()]
        
        results = manager.get_all_documents()
        
        assert len(results) == 2
    
    @patch('services.embed_service.GoogleGenerativeAIEmbeddings')
    @patch('services.embed_service.InMemoryVectorStore')
    def test_get_all_documents_failure(self, mock_vector_store, mock_embeddings):
        manager = VectorStoreManager(api_key="test_key")
        
        chunks = ["test"]
        mock_embeddings_instance = MagicMock()
        manager.embeddings = mock_embeddings_instance
        mock_embeddings_instance.embed_documents.return_value = [[0.1] * 768]
        
        mock_vs_instance = MagicMock()
        mock_vector_store.from_documents.return_value = mock_vs_instance
        manager.embed_chunks(chunks)
        
        mock_vs_instance.similarity_search.side_effect = Exception("Retrieval failed")
        
        with pytest.raises(EmbeddingError, match="Failed to retrieve documents"):
            manager.get_all_documents()


class TestCreateEmbeddings:
    @patch('services.embed_service.VectorStoreManager')
    def test_create_embeddings_success(self, mock_manager_class):
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        
        mock_manager.embed_chunks.return_value = (
            MagicMock(),
            768,
            [[0.1] * 768, [0.2] * 768]
        )
        
        chunks = ["chunk1", "chunk2"]
        embeddings, dimensions = create_embeddings(chunks, api_key="test_key")
        
        assert dimensions == 768
        assert len(embeddings) == 2
    
    @patch('services.embed_service.VectorStoreManager')
    def test_create_embeddings_custom_model(self, mock_manager_class):
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        
        mock_manager.embed_chunks.return_value = (
            MagicMock(),
            512,
            [[0.1] * 512]
        )
        
        chunks = ["chunk1"]
        embeddings, dimensions = create_embeddings(
            chunks,
            api_key="test_key",
            model="models/custom-model"
        )
        
        assert dimensions == 512
        mock_manager_class.assert_called_once_with(
            api_key="test_key",
            model="models/custom-model"
        )
    
    @patch('services.embed_service.VectorStoreManager')
    def test_create_embeddings_no_api_key(self, mock_manager_class):
        mock_manager_class.side_effect = EmbeddingError("API key required")
        
        with pytest.raises(EmbeddingError):
            create_embeddings(["chunk1"])
    
    @patch('services.embed_service.VectorStoreManager')
    def test_create_embeddings_empty_chunks(self, mock_manager_class):
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        mock_manager.embed_chunks.side_effect = EmbeddingError("No chunks provided")
        
        with pytest.raises(EmbeddingError):
            create_embeddings([], api_key="test_key")


class TestVectorStoreIntegration:
    @patch('services.embed_service.GoogleGenerativeAIEmbeddings')
    @patch('services.embed_service.InMemoryVectorStore')
    def test_full_workflow(self, mock_vector_store, mock_embeddings):
        manager = VectorStoreManager(api_key="test_key")
        
        chunks = ["First chunk", "Second chunk", "Third chunk"]
        mock_embeddings_instance = MagicMock()
        manager.embeddings = mock_embeddings_instance
        
        mock_embeddings_instance.embed_documents.return_value = [
            [0.1] * 768,
            [0.2] * 768,
            [0.3] * 768
        ]
        
        mock_vs_instance = MagicMock()
        mock_vector_store.from_documents.return_value = mock_vs_instance
        
        vs, dims, embs = manager.embed_chunks(chunks)
        
        assert dims == 768
        assert len(embs) == 3
        
        mock_vs_instance.similarity_search_with_score.return_value = [
            (MagicMock(), 0.9)
        ]
        
        results = manager.search_similar("test query", k=1)
        assert len(results) == 1
    
    @patch('services.embed_service.GoogleGenerativeAIEmbeddings')
    @patch('services.embed_service.InMemoryVectorStore')
    def test_embed_and_retrieve(self, mock_vector_store, mock_embeddings):
        manager = VectorStoreManager(api_key="test_key")
        
        chunks = ["chunk1", "chunk2"]
        mock_embeddings_instance = MagicMock()
        manager.embeddings = mock_embeddings_instance
        mock_embeddings_instance.embed_documents.return_value = [[0.1] * 768, [0.2] * 768]
        
        mock_vs_instance = MagicMock()
        mock_vector_store.from_documents.return_value = mock_vs_instance
        
        manager.embed_chunks(chunks)
        
        mock_vs_instance.similarity_search.return_value = [MagicMock(), MagicMock()]
        
        docs = manager.get_all_documents()
        assert len(docs) == 2
