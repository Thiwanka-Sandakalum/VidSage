#!/usr/bin/env python3
"""
RAG Agents Module

This module implements specialized agents and tools that work with the RAG system.
Includes Query Analyzer, Content Summarizer, and Citation Manager.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
import logging
from dotenv import load_dotenv

# LangChain components
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser 
from langchain.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Default API key
DEFAULT_API_KEY = os.environ.get('GOOGLE_API_KEY', 'YOUR_API_KEY')

class QueryAnalyzer:
    """
    Analyzes and improves user queries for better RAG retrieval
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the query analyzer
        
        Args:
            api_key: Optional Gemini API key (uses environment variable if None)
        """
        self.api_key = api_key or DEFAULT_API_KEY
        
        # Set API key for Gemini
        os.environ['GOOGLE_API_KEY'] = self.api_key
        
        # Initialize LLM for query analysis
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)
        
        # Create prompt template for query analysis
        self.query_analysis_prompt = ChatPromptTemplate.from_template(
            """You are an AI assistant that helps improve user questions for retrieval from a video transcript.
            Your job is to analyze the user's question and rewrite it to be more specific and effective for 
            retrieving relevant information.
            
            Guidelines for rewriting:
            - Make the question more specific and focused
            - Include key terms that might appear in the transcript
            - Avoid overly broad questions
            - Make sure the rewritten question has the same intent as the original
            - Do not add information that wasn't in the original question
            
            Original Question: {question}
            
            Rewritten Question:"""
        )
        
        # Create query analysis chain
        self.query_analysis_chain = (
            self.query_analysis_prompt 
            | self.llm 
            | StrOutputParser()
        )
        
        logger.info("Query Analyzer initialized")
    
    def improve_query(self, query: str) -> str:
        """
        Improve a user query for better RAG retrieval
        
        Args:
            query: Original user query
            
        Returns:
            Improved query
        """
        logger.info(f"Analyzing query: {query}")
        
        try:
            # Generate improved query
            improved_query = self.query_analysis_chain.invoke({"question": query})
            
            logger.info(f"Improved query: {improved_query}")
            return improved_query
            
        except Exception as e:
            logger.error(f"Error improving query: {str(e)}")
            return query  # Return original query on error


class ContentSummarizer:
    """
    Generates various types of content summaries from transcripts
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the content summarizer
        
        Args:
            api_key: Optional Gemini API key (uses environment variable if None)
        """
        self.api_key = api_key or DEFAULT_API_KEY
        
        # Initialize Gemini client
        genai.configure(api_key=self.api_key)
        
        # Create model client
        self.client = genai.Client(api_key=self.api_key)
        
        logger.info("Content Summarizer initialized")
    
    def _create_summary_prompt(self, summary_type: str, transcript: str) -> str:
        """
        Create a prompt for generating a specific type of summary
        
        Args:
            summary_type: Type of summary to generate
            transcript: Transcript text
            
        Returns:
            Prompt text
        """
        base_prompt = f"""You are a professional content summarizer. Your task is to create a {summary_type} summary of the following video transcript.
        
        Transcript:
        {transcript}
        
        """
        
        if summary_type == "concise":
            return base_prompt + "Create a brief 3-5 sentence summary that captures the main points of the video."
            
        elif summary_type == "detailed":
            return base_prompt + "Create a comprehensive summary that covers all key points in the video while being about 30% of the original length."
            
        elif summary_type == "bullet":
            return base_prompt + "Create a bullet-point summary with 5-10 key points from the video, organized in a logical flow."
            
        elif summary_type == "sections":
            return base_prompt + "Create a sectioned summary that organizes the video content into logical topics or themes, with a brief summary of each section."
            
        else:  # default
            return base_prompt + "Create a summary that covers the main points of the video in a concise but comprehensive manner."
    
    def generate_summary(self, transcript: str, summary_type: str = "default", 
                          stream: bool = False) -> str:
        """
        Generate a summary of the transcript
        
        Args:
            transcript: Transcript text to summarize
            summary_type: Type of summary to generate (concise, detailed, bullet, sections)
            stream: Whether to stream the response
            
        Returns:
            Generated summary
        """
        # Create the prompt for the desired summary type
        prompt = self._create_summary_prompt(summary_type, transcript)
        
        logger.info(f"Generating {summary_type} summary")
        
        try:
            # Configure system instructions based on summary type
            system_instruction = f"You are a professional content summarizer specializing in {summary_type} summaries."
            
            if stream:
                # Stream the response
                response = self.client.models.generate_content_stream(
                    model="gemini-2.5-flash",
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.2
                    ),
                    contents=[prompt]
                )
                
                # Collect response chunks
                summary = ""
                for chunk in response:
                    if chunk.text:
                        summary += chunk.text
                
                return summary
                
            else:
                # Generate response at once
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.2
                    ),
                    contents=[prompt]
                )
                
                return response.text
                
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return f"Error generating summary: {str(e)}"


class CitationManager:
    """
    Tracks and manages citations and references to source content
    """
    
    def __init__(self):
        """Initialize the citation manager"""
        # Store citation data
        self.citations = {}
        self.feedback = {}
        
        logger.info("Citation Manager initialized")
    
    def add_citation(self, query_id: str, citations: List[Dict[str, Any]]) -> None:
        """
        Add citation for a query
        
        Args:
            query_id: Unique ID for the query
            citations: List of citation sources
        """
        self.citations[query_id] = citations
        logger.info(f"Added {len(citations)} citations for query {query_id}")
    
    def get_citations(self, query_id: str) -> List[Dict[str, Any]]:
        """
        Get citations for a query
        
        Args:
            query_id: Unique ID for the query
            
        Returns:
            List of citation sources
        """
        return self.citations.get(query_id, [])
    
    def add_feedback(self, query_id: str, feedback: Dict[str, Any]) -> None:
        """
        Add user feedback for a citation
        
        Args:
            query_id: Unique ID for the query
            feedback: Feedback information
        """
        self.feedback[query_id] = feedback
        logger.info(f"Added feedback for query {query_id}")
    
    def get_feedback(self, query_id: str) -> Dict[str, Any]:
        """
        Get feedback for a query
        
        Args:
            query_id: Unique ID for the query
            
        Returns:
            Feedback information
        """
        return self.feedback.get(query_id, {})
    
    def format_citations(self, citations: List[Dict[str, Any]], 
                         format_type: str = "text") -> str:
        """
        Format citations in a specific format
        
        Args:
            citations: List of citation sources
            format_type: Format type (text, markdown, html)
            
        Returns:
            Formatted citations
        """
        if not citations:
            return "No citations available"
        
        if format_type == "markdown":
            result = "### Citations\n\n"
            for i, citation in enumerate(citations):
                result += f"**[{citation['timestamp']}]** {citation['text']}\n\n"
            return result
            
        elif format_type == "html":
            result = "<h3>Citations</h3><ul>"
            for citation in citations:
                result += f"<li><strong>[{citation['timestamp']}]</strong> {citation['text']}</li>"
            result += "</ul>"
            return result
            
        else:  # text
            result = "Citations:\n\n"
            for citation in citations:
                result += f"[{citation['timestamp']}] {citation['text']}\n\n"
            return result
    
    def export_citations(self, query_id: str, file_path: str, 
                       format_type: str = "json") -> bool:
        """
        Export citations to a file
        
        Args:
            query_id: Unique ID for the query
            file_path: Path to export file
            format_type: Format type (json, csv, text)
            
        Returns:
            True if export successful, False otherwise
        """
        citations = self.get_citations(query_id)
        if not citations:
            logger.warning(f"No citations found for query {query_id}")
            return False
        
        try:
            if format_type == "json":
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(citations, f, ensure_ascii=False, indent=4)
                
            elif format_type == "csv":
                import csv
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=["text", "timestamp", "start_time", "relevance"])
                    writer.writeheader()
                    writer.writerows(citations)
                
            else:  # text
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.format_citations(citations, "text"))
            
            logger.info(f"Citations exported to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting citations: {str(e)}")
            return False
