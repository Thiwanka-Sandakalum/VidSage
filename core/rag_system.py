#!/usr/bin/env python3
"""
RAG System Module

This module implements the Retrieval-Augmented Generation (RAG) functionality
using the Gemini AI model and Langchain.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union, TypedDict
import logging
from dotenv import load_dotenv

# LangChain components
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Default API key
DEFAULT_API_KEY = os.environ.get('GOOGLE_API_KEY', 'YOUR_API_KEY')

# Type definitions
class TranscriptSegment(TypedDict):
    """Type for transcript segments with timestamps"""
    text: str
    start: float
    end: float

class RAGSystem:
    """
    Core RAG implementation for VidSage
    Handles chunking, indexing, retrieval, and answer generation
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the RAG system
        
        Args:
            api_key: Optional Gemini API key (uses environment variable if None)
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
        
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
        
        # Vectorstore and retriever
        self.vectorstore = None
        self.retriever = None
        self.rag_chain = None
        
        # Metadata for transcript segments
        self.segments: List[TranscriptSegment] = []
        
        logger.info("RAG System initialized")
    
    def process_transcript(self, transcript_text: str, 
                         segments: Optional[List[Dict[str, Any]]] = None) -> List[Document]:
        """
        Process a transcript by splitting into chunks and preparing for indexing
        
        Args:
            transcript_text: Full transcript text
            segments: Optional list of transcript segments with timestamps
            
        Returns:
            List of Document objects ready for indexing
        """
        logger.info("Processing transcript into chunks")
        
        # Store segment information if provided
        if segments:
            self.segments = segments
            
        # Split text into chunks
        docs = self.text_splitter.create_documents([transcript_text])
        
        # Add metadata to documents if segments are available
        if segments:
            # Match chunks to segments by finding overlapping text
            for doc in docs:
                # For each document, find all segments that overlap with its content
                matching_segments = []
                for segment in segments:
                    if segment["text"] in doc.page_content:
                        matching_segments.append(segment)
                
                # If there are matching segments, add timestamp information
                if matching_segments:
                    start_time = min(segment["start"] for segment in matching_segments)
                    end_time = max(segment["end"] for segment in matching_segments)
                    doc.metadata = {
                        "start_time": start_time,
                        "end_time": end_time,
                        "timestamp": f"{int(start_time // 60):02d}:{int(start_time % 60):02d}"
                    }
        
        logger.info(f"Created {len(docs)} document chunks")
        return docs
    
    def create_vectorstore(self, docs: List[Document]) -> None:
        """
        Create vector store from document chunks
        
        Args:
            docs: List of document chunks
        """
        logger.info("Creating vector store")
        
        # Create vector store
        self.vectorstore = Chroma.from_documents(
            documents=docs,
            embedding=self.embedding_model
        )
        
        # Create retriever
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})
        
        logger.info("Vector store and retriever created")
    
    def _format_docs(self, docs: List[Document]) -> str:
        """
        Format retrieved documents into a context string
        
        Args:
            docs: List of retrieved documents
            
        Returns:
            Formatted context string
        """
        doc_strings = []
        for i, doc in enumerate(docs):
            timestamp = doc.metadata.get("timestamp", "00:00")
            doc_strings.append(f"[{timestamp}] {doc.page_content}")
        
        return "\n\n".join(doc_strings)
    
    def create_qa_chain(self) -> None:
        """Create the RAG chain for answering questions"""
        if not self.retriever:
            raise ValueError("Retriever not initialized. Call create_vectorstore first.")
            
        logger.info("Creating QA chain")
        
        # Create a prompt template
        qa_prompt = ChatPromptTemplate.from_template(
            """You are an AI assistant that provides detailed and accurate answers about YouTube videos.
            Answer the question based only on the following transcript segments from the video:
            
            {context}
            
            Question: {question}
            
            Answer in a clear and conversational style. Include relevant timestamps from the transcript when appropriate. 
            If the question cannot be answered using the context, indicate that you don't have enough information 
            from the video transcript to provide a complete answer.
            """
        )
        
        # Create the RAG chain
        self.rag_chain = (
            {"context": self.retriever | self._format_docs, "question": RunnablePassthrough()}
            | qa_prompt
            | self.llm
            | StrOutputParser()
        )
        
        logger.info("QA chain created")
    
    def answer_question(self, question: str) -> str:
        """
        Answer a question using the RAG chain
        
        Args:
            question: Question to answer
            
        Returns:
            Generated answer
        """
        if not self.rag_chain:
            raise ValueError("QA chain not initialized. Call create_qa_chain first.")
            
        logger.info(f"Answering question: {question}")
        
        try:
            # Get answer from RAG chain
            answer = self.rag_chain.invoke(question)
            return answer
            
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            return f"Error generating answer: {str(e)}"
    
    def get_citation_sources(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Get source citations for a particular query
        
        Args:
            query: Query to find sources for
            top_k: Number of top sources to return
            
        Returns:
            List of citation sources with timestamps
        """
        if not self.vectorstore:
            raise ValueError("Vector store not initialized")
            
        # Get relevant documents
        results = self.vectorstore.similarity_search_with_relevance_scores(query, k=top_k)
        
        # Format citations
        citations = []
        for doc, score in results:
            citation = {
                "text": doc.page_content,
                "timestamp": doc.metadata.get("timestamp", "00:00"),
                "start_time": doc.metadata.get("start_time", 0),
                "relevance": float(score)
            }
            citations.append(citation)
        
        return citations
