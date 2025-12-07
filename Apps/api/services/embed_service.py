
import os
from typing import List, Tuple, Dict, Any, Optional
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingError(Exception):
    """Custom exception for embedding-related errors."""
    pass


class VectorStoreManager:
    """Manager for embedding generation and in-memory vector storage."""
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        model: str = "models/text-embedding-004",
        output_dimensionality: int = 768,
        task_type: str = "RETRIEVAL_DOCUMENT"
    ):
        """
        Initialize the vector store manager.
        
        Args:
            api_key: Google API key (if None, will use GOOGLE_API_KEY env var)
            model: Embedding model to use (default: models/text-embedding-004)
            output_dimensionality: Size of output embeddings (128-768, default: 768)
            task_type: Task type for embeddings (default: RETRIEVAL_DOCUMENT)
            
        Raises:
            EmbeddingError: If API key is not provided
        """
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            raise EmbeddingError(
                "Google API key not found. Please set GOOGLE_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.model = model
        self.output_dimensionality = output_dimensionality
        self.task_type = task_type
        
        logger.info(f"Initializing embeddings with model: {model}, dimensions: {output_dimensionality}")
        
        try:
            # Initialize embeddings with proper configuration
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model=self.model,
                google_api_key=self.api_key,
                task_type=self.task_type
            )
        except Exception as e:
            raise EmbeddingError(f"Failed to initialize embeddings: {str(e)}")
        
        # Vector store will be created when chunks are added
        self.vector_store: InMemoryVectorStore = None
        self.embedding_dimensions: int = output_dimensionality
    
    def embed_chunks(
        self,
        chunks: List[str],
        metadata: List[Dict[str, Any]] = None
    ) -> Tuple[InMemoryVectorStore, int, List[List[float]]]:
        """
        Generate embeddings for text chunks and store in InMemoryVectorStore.
        
        Args:
            chunks: List of text chunks to embed
            metadata: Optional metadata for each chunk
            
        Returns:
            Tuple of (vector_store, embedding_dimensions, embeddings_list)
            
        Raises:
            EmbeddingError: If embedding generation fails
        """
        if not chunks:
            raise EmbeddingError("No chunks provided for embedding")
        
        logger.info(f"Embedding {len(chunks)} chunks...")
        
        try:
            # Create documents from chunks
            documents = []
            for i, chunk in enumerate(chunks):
                doc_metadata = metadata[i] if metadata and i < len(metadata) else {}
                doc_metadata["chunk_id"] = f"chunk_{i + 1}"
                doc_metadata["chunk_index"] = i
                
                documents.append(Document(
                    page_content=chunk,
                    metadata=doc_metadata
                ))
            
            logger.info("Creating vector store from documents...")
            
            # Create vector store from documents
            self.vector_store = InMemoryVectorStore.from_documents(
                documents=documents,
                embedding=self.embeddings
            )
            
            logger.info("Generating embeddings for return...")
            
            # Get all embeddings for return
            all_embeddings = self.embeddings.embed_documents(chunks)
            
            logger.info(f"Successfully created {len(all_embeddings)} embeddings")
            
            return self.vector_store, self.embedding_dimensions, all_embeddings
            
        except Exception as e:
            logger.error(f"Embedding error: {str(e)}")
            raise EmbeddingError(f"Failed to generate embeddings: {str(e)}")
    
    def search_similar(
        self,
        query: str,
        k: int = 4
    ) -> List[Tuple[Document, float]]:
        """
        Search for similar documents in the vector store.
        
        Args:
            query: Query text
            k: Number of results to return (default: 4)
            
        Returns:
            List of (Document, similarity_score) tuples
            
        Raises:
            EmbeddingError: If search fails or vector store not initialized
        """
        if not self.vector_store:
            raise EmbeddingError(
                "Vector store not initialized. Please embed chunks first."
            )
        
        try:
            # Perform similarity search with scores
            results = self.vector_store.similarity_search_with_score(
                query=query,
                k=k
            )
            return results
            
        except Exception as e:
            raise EmbeddingError(f"Failed to search vector store: {str(e)}")
    
    def get_all_documents(self) -> List[Document]:
        """
        Get all documents from the vector store.
        
        Returns:
            List of all documents
            
        Raises:
            EmbeddingError: If vector store not initialized
        """
        if not self.vector_store:
            raise EmbeddingError(
                "Vector store not initialized. Please embed chunks first."
            )
        
        try:
            # Get all documents (search with empty query and large k)
            # This is a workaround since InMemoryVectorStore doesn't have a direct method
            return self.vector_store.similarity_search("", k=10000)
        except Exception as e:
            raise EmbeddingError(f"Failed to retrieve documents: {str(e)}")


def create_embeddings(
    chunks: List[str],
    api_key: str = None,
    model: str = "models/embedding-001"
) -> Tuple[List[List[float]], int]:
    """
    Standalone function to generate embeddings for chunks.
    
    Args:
        chunks: List of text chunks
        api_key: Google API key (if None, will use GOOGLE_API_KEY env var)
        model: Embedding model to use
        
    Returns:
        Tuple of (embeddings_list, embedding_dimensions)
        
    Raises:
        EmbeddingError: If embedding generation fails
    """
    manager = VectorStoreManager(api_key=api_key, model=model)
    _, dimensions, embeddings = manager.embed_chunks(chunks)
    return embeddings, dimensions
