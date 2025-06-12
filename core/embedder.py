import os
import json
from typing import List, Tuple, Dict, Optional
import numpy as np
from tqdm import tqdm

class Embedder:
    """Generate embeddings for text and store in a vector database."""
    
    def __init__(self, storage_manager, embedding_model: str = "all-MiniLM-L6-v2", chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize the Embedder.
        
        Args:
            storage_manager: Instance of StorageManager for file operations
            embedding_model: Name of the sentence-transformers model to use
            chunk_size: Size of text chunks for embedding
            chunk_overlap: Overlap between text chunks
        """
        self.storage_manager = storage_manager
        self.embedding_model_name = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embedder = None
        self.chroma_client = None
        
        # Lazy-load dependencies to avoid errors if not installed
        try:
            from sentence_transformers import SentenceTransformer
            import chromadb
            from chromadb.utils import embedding_functions
            
            self.SentenceTransformer = SentenceTransformer
            self.chromadb = chromadb
            self.embedding_functions = embedding_functions
            
            # Initialize embedding function
            self.sentence_transformer_ef = self.embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=embedding_model
            )
            
            # Initialize ChromaDB client
            self.chroma_client = self.chromadb.Client()
            
        except ImportError as e:
            print(f"Warning: Embedding functionality limited due to missing dependencies: {e}")
    
    def _load_embedder(self):
        """Load the sentence transformer model for embeddings."""
        if self.embedder is None:
            try:
                print(f"Loading embedding model {self.embedding_model_name}...")
                self.embedder = self.SentenceTransformer(self.embedding_model_name)
                print("Embedding model loaded successfully.")
            except Exception as e:
                print(f"Error loading embedding model: {e}")
                return False
        return True
    
    def _chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks of specified size.
        
        Args:
            text: Text to split into chunks
            
        Returns:
            List of text chunks
        """
        # Split text into paragraphs first
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # If adding this paragraph doesn't exceed chunk size, add it
            if len(current_chunk) + len(paragraph) <= self.chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                # Save current chunk and start a new one
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # If paragraph is larger than chunk size, split it by sentences
                if len(paragraph) > self.chunk_size:
                    words = paragraph.split()
                    current_chunk = ""
                    for word in words:
                        if len(current_chunk) + len(word) <= self.chunk_size:
                            current_chunk += word + " "
                        else:
                            chunks.append(current_chunk.strip())
                            current_chunk = word + " "
                else:
                    current_chunk = paragraph + "\n\n"
        
        # Add the last chunk if it exists
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # Add overlapping chunks
        overlapping_chunks = []
        for i in range(len(chunks)):
            overlapping_chunks.append(chunks[i])
            
            # If not the last chunk and overlap is specified
            if i < len(chunks) - 1 and self.chunk_overlap > 0:
                # Get the end of current chunk and start of next chunk
                words_current = chunks[i].split()
                words_next = chunks[i + 1].split()
                
                # Calculate words to overlap
                overlap_words_count = min(
                    len(words_current), 
                    len(words_next), 
                    self.chunk_overlap // 5  # Rough approximation: 5 chars per word
                )
                
                if overlap_words_count > 0:
                    overlap_text = " ".join(words_current[-overlap_words_count:]) + " " + " ".join(words_next[:overlap_words_count])
                    overlapping_chunks.append(overlap_text)
        
        return overlapping_chunks
    
    def generate_embeddings(self, video_id: str) -> Tuple[bool, Optional[str]]:
        """
        Generate embeddings for a video transcript and store them.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Tuple containing (success status, embeddings directory or None)
        """
        if self.chroma_client is None:
            print("Embedding generation not available: required dependencies missing.")
            return False, None
        
        transcript_path = self.storage_manager.get_transcript_path(video_id)
        embeddings_path = self.storage_manager.get_embeddings_path(video_id)
        
        # Check if transcript exists
        if not os.path.exists(transcript_path):
            print(f"Transcript not found: {transcript_path}")
            return False, None
        
        # Check if embeddings already exist
        if os.path.exists(embeddings_path):
            print("Using existing embeddings.")
            return True, embeddings_path
        
        # Load embedder if not loaded
        if not self._load_embedder():
            return False, None
        
        # Read transcript
        transcript = self.storage_manager.read_file(transcript_path)
        if not transcript:
            return False, None
        
        try:
            # Create embeddings directory
            os.makedirs(embeddings_path, exist_ok=True)
            
            # Chunk the transcript
            print("Chunking transcript...")
            chunks = self._chunk_text(transcript)
            
            # Create a collection for this video
            collection = self.chroma_client.create_collection(
                name=f"video_{video_id}",
                embedding_function=self.sentence_transformer_ef
            )
            
            # Generate and store embeddings
            print("Generating embeddings...")
            ids = [f"chunk_{i}" for i in range(len(chunks))]
            
            # Add documents to collection
            collection.add(
                documents=chunks,
                ids=ids,
                metadatas=[{"index": i, "video_id": video_id} for i in range(len(chunks))]
            )
            
            # Save chunks for later use
            chunks_file = os.path.join(embeddings_path, "chunks.json")
            with open(chunks_file, 'w') as f:
                json.dump({"chunks": chunks}, f)
            
            # Persist the collection to disk
            collection.persist()
            
            print(f"Embeddings generated and stored in {embeddings_path}")
            return True, embeddings_path
            
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            return False, None
    
    def search_similar_chunks(self, video_id: str, query: str, top_k: int = 3) -> List[str]:
        """
        Search for chunks similar to the query.
        
        Args:
            video_id: YouTube video ID
            query: Query string
            top_k: Number of similar chunks to return
            
        Returns:
            List of similar text chunks
        """
        if self.chroma_client is None:
            print("Similarity search not available: required dependencies missing.")
            return []
        
        embeddings_path = self.storage_manager.get_embeddings_path(video_id)
        
        # Check if embeddings exist
        if not os.path.exists(embeddings_path):
            print(f"Embeddings not found: {embeddings_path}")
            return []
        
        try:
            # Get the collection for this video
            collection = self.chroma_client.get_collection(
                name=f"video_{video_id}",
                embedding_function=self.sentence_transformer_ef
            )
            
            # Search for similar chunks
            results = collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            # Extract and return the chunks
            if results and 'documents' in results and results['documents']:
                return results['documents'][0]  # First query results
            
            return []
            
        except Exception as e:
            print(f"Error searching similar chunks: {e}")
            return []