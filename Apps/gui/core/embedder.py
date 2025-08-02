#!/usr/bin/env python3
"""
Embedder Module

This module handles creating and managing text embeddings for transcripts.
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, BinaryIO
import logging
import pickle
from dotenv import load_dotenv

# LangChain components
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Default API key
DEFAULT_API_KEY = os.environ.get('GOOGLE_API_KEY', 'YOUR_API_KEY')

class Embedder:
    """Handles creating and managing embeddings for transcript text"""
    
    def __init__(self, api_key: Optional[str] = None, output_dir: Optional[Path] = None):
        """
        Initialize the embedder
        
        Args:
            api_key: Optional Gemini API key (uses environment variable if None)
            output_dir: Optional directory to save embeddings
        """
        self.api_key = api_key or DEFAULT_API_KEY
        
        # Set API key for Gemini
        os.environ['GOOGLE_API_KEY'] = self.api_key
        
        # Initialize embeddings model
        self.embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        
        # Text splitter for chunking documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100
        )
        
        # Set output directory
        self.output_dir = output_dir
        if self.output_dir:
            self.output_dir.mkdir(exist_ok=True)
        
        logger.info("Embedder initialized")
    
    def create_chunks(self, text: str) -> List[Document]:
        """
        Split text into chunks for embedding
        
        Args:
            text: Text to split into chunks
            
        Returns:
            List of document chunks
        """
        logger.info("Splitting text into chunks")
        
        # Split text into chunks
        docs = self.text_splitter.create_documents([text])
        
        logger.info(f"Created {len(docs)} chunks")
        return docs
    
    def create_embeddings(self, docs: List[Document]) -> List[List[float]]:
        """
        Create embeddings for document chunks
        
        Args:
            docs: List of document chunks
            
        Returns:
            List of embeddings
        """
        logger.info("Creating embeddings")
        
        try:
            # Extract text from documents
            texts = [doc.page_content for doc in docs]
            
            # Create embeddings
            embeddings = self.embedding_model.embed_documents(texts)
            
            logger.info(f"Created {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {str(e)}")
            raise
    
    def create_vectorstore(self, docs: List[Document]) -> Chroma:
        """
        Create a vector store from document chunks
        
        Args:
            docs: List of document chunks
            
        Returns:
            Chroma vector store
        """
        logger.info("Creating vector store")
        
        try:
            # Create vector store
            vectorstore = Chroma.from_documents(
                documents=docs,
                embedding=self.embedding_model
            )
            
            logger.info("Vector store created")
            return vectorstore
            
        except Exception as e:
            logger.error(f"Error creating vector store: {str(e)}")
            raise
    
    def save_embeddings(self, embeddings: List[List[float]], file_path: Optional[Path] = None) -> Path:
        """
        Save embeddings to a file
        
        Args:
            embeddings: List of embeddings
            file_path: Optional file path to save embeddings
            
        Returns:
            Path to saved embeddings
        """
        if file_path is None:
            if self.output_dir is None:
                raise ValueError("Either file_path or output_dir must be specified")
            file_path = self.output_dir / "embeddings.pkl"
        
        try:
            with open(file_path, 'wb') as f:
                pickle.dump(embeddings, f)
                
            logger.info(f"Embeddings saved to {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving embeddings: {str(e)}")
            raise
    
    def load_embeddings(self, file_path: Path) -> List[List[float]]:
        """
        Load embeddings from a file
        
        Args:
            file_path: Path to embeddings file
            
        Returns:
            List of embeddings
        """
        try:
            with open(file_path, 'rb') as f:
                embeddings = pickle.load(f)
                
            logger.info(f"Embeddings loaded from {file_path}")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error loading embeddings: {str(e)}")
            raise
    
    def save_vectorstore(self, vectorstore: Chroma, file_path: Optional[Path] = None) -> Path:
        """
        Save a vector store to a file
        
        Args:
            vectorstore: Chroma vector store
            file_path: Optional file path to save vector store
            
        Returns:
            Path to saved vector store
        """
        if file_path is None:
            if self.output_dir is None:
                raise ValueError("Either file_path or output_dir must be specified")
            file_path = self.output_dir / "vectorstore.pkl"
        
        try:
            with open(file_path, 'wb') as f:
                pickle.dump(vectorstore, f)
                
            logger.info(f"Vector store saved to {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving vector store: {str(e)}")
            raise
    
    def load_vectorstore(self, file_path: Path) -> Chroma:
        """
        Load a vector store from a file
        
        Args:
            file_path: Path to vector store file
            
        Returns:
            Chroma vector store
        """
        try:
            with open(file_path, 'rb') as f:
                vectorstore = pickle.load(f)
                
            logger.info(f"Vector store loaded from {file_path}")
            return vectorstore
            
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            raise
    
    def process_transcript(self, transcript: str, save_output: bool = True, 
                         output_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Process a transcript to create embeddings and vector store
        
        Args:
            transcript: Transcript text
            save_output: Whether to save embeddings and vector store
            output_path: Optional path to save output
            
        Returns:
            Dictionary with chunks, embeddings, and vector store
        """
        # Create output directory if needed
        save_dir = output_path or self.output_dir
        if save_output and save_dir is None:
            raise ValueError("Output directory must be specified to save output")
            
        if save_output and save_dir:
            save_dir.mkdir(exist_ok=True)
        
        # Process transcript
        chunks = self.create_chunks(transcript)
        embeddings = self.create_embeddings(chunks)
        vectorstore = self.create_vectorstore(chunks)
        
        # Save output if requested
        if save_output and save_dir:
            emb_path = self.save_embeddings(embeddings, save_dir / "embeddings.pkl")
            vec_path = self.save_vectorstore(vectorstore, save_dir / "vectorstore.pkl")
            
            return {
                "chunks": chunks,
                "embeddings": embeddings,
                "vectorstore": vectorstore,
                "embedding_path": emb_path,
                "vectorstore_path": vec_path
            }
        
        return {
            "chunks": chunks,
            "embeddings": embeddings,
            "vectorstore": vectorstore
        }
