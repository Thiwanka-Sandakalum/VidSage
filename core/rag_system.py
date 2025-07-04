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
        
        # Initialize enhanced components
        try:
            from .rag_agents import QueryAnalyzer, ContentSummarizer
            from .response_formatter import ResponseFormatter
            
            self.query_analyzer = QueryAnalyzer(api_key=self.api_key)
            self.content_analyzer = None  # Not implemented yet
            self.response_formatter = ResponseFormatter()  # No api_key parameter needed
            self.summarizer = ContentSummarizer(api_key=self.api_key)
        except ImportError as e:
            logger.warning(f"Enhanced components not available: {e}")
            self.query_analyzer = None
            self.content_analyzer = None
            self.response_formatter = None
            self.summarizer = None
        
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
    
    def create_vectorstore(self, docs: List[Document], persist_directory: Optional[str] = None) -> None:
        """
        Create vector store from document chunks with persistence
        
        Args:
            docs: List of document chunks
            persist_directory: Optional directory to persist vector store
        """
        logger.info("Creating vector store")
        
        # Create vector store with persistence
        if persist_directory:
            self.vectorstore = Chroma.from_documents(
                documents=docs,
                embedding=self.embedding_model,
                persist_directory=persist_directory
            )
        else:
            # Create in-memory vectorstore
            self.vectorstore = Chroma.from_documents(
                documents=docs,
                embedding=self.embedding_model
            )
        
        # Create retriever
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})
        
        logger.info("Vector store and retriever created")
    
    def load_vectorstore(self, persist_directory: str) -> None:
        """
        Load an existing vector store from disk
        
        Args:
            persist_directory: Directory where the vector store is persisted
        """
        logger.info(f"Loading vector store from {persist_directory}")
        
        # Load vector store
        self.vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embedding_model
        )
        
        # Create retriever
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})
        
        logger.info("Vector store and retriever loaded from disk")
        
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
        
        # Create enhanced prompt template for better responses
        qa_prompt = ChatPromptTemplate.from_template(
            """You are VidSage, an advanced AI assistant that provides comprehensive, well-structured answers about YouTube videos.

CONTEXT FROM VIDEO:
{context}

USER QUESTION: {question}

RESPONSE FORMATTING INSTRUCTIONS:
Based on the question type, structure your response appropriately:

FOR COMPARISON QUESTIONS (vs, difference, compare, better/worse):
- Create clear comparisons with specific aspects
- Use structured format: "**Aspect**: Details for each item"
- Highlight key differences and similarities
- Include pros/cons when relevant

FOR LIST QUESTIONS (types, examples, features, benefits):
- Use clear numbered lists or bullet points
- Group related items together
- Provide brief explanations for each item
- Use consistent formatting

FOR PROCESS/HOW-TO QUESTIONS (steps, process, method, procedure):
- Break down into clear sequential steps
- Use numbered format for procedures
- Include important details and tips for each step
- Mention any prerequisites or requirements

FOR TECHNICAL QUESTIONS (implementation, code, algorithms):
- Provide technical details and specifications
- Include any code examples or technical terms mentioned
- Explain complex concepts clearly
- Structure with appropriate headers

FOR DEFINITION QUESTIONS (what is, define, explain):
- Start with a clear, concise definition
- Provide detailed explanation with context
- Include examples when mentioned in the video
- Explain significance or importance

GENERAL FORMATTING RULES:
- Use **bold** for key terms and important points
- Include relevant timestamps [MM:SS] for specific references
- Use bullet points (•) or numbers (1., 2., 3.) for lists
- Create logical sections with clear structure
- Be comprehensive but concise
- Base ALL information strictly on the provided video transcript segments
- If information is not available in the transcript, clearly state this limitation

MARKDOWN FORMATTING:
- Use ## for main section headers
- Use **text** for emphasis and key terms
- Use bullet points or numbered lists appropriately
- Use tables (| Column | Column |) for structured comparisons when beneficial
- Use `code` formatting for technical terms

Remember: Provide detailed, accurate answers based ONLY on the video transcript segments above. Structure your response to match the question type and user's information needs.
            """
        )
        
        # Create the RAG chain
        self.rag_chain = (
            {"context": self.retriever | self._format_docs, "question": RunnablePassthrough()}
            | qa_prompt
            | self.llm
            | StrOutputParser()
        )
        
        logger.info("Enhanced QA chain created")
    
    def answer_question(self, question: str) -> str:
        """Answer questions using RAG"""
        if not self.rag_chain:
            raise ValueError("RAG chain not initialized. Please call create_qa_chain first.")
        
        # Use the pre-created RAG chain
        return self.rag_chain.invoke(question)
    
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
