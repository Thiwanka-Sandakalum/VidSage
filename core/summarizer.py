#!/usr/bin/env python3
"""
Summarizer Module

This module handles generating summaries of transcript content using both
Ollama LLM and Gemini.
"""

import os
import json
from typing import Dict, Any, Optional, List, Union, Literal
import logging
import time
from pathlib import Path
from dotenv import load_dotenv

# Import Gemini
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Default API key
DEFAULT_API_KEY = os.environ.get('GOOGLE_API_KEY', 'YOUR_API_KEY')

# Summary types
SummaryType = Literal["concise", "detailed", "bullet", "sections", "default"]

class Summarizer:
    """Generates summaries from transcripts using AI models"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the summarizer
        
        Args:
            api_key: Optional Gemini API key (uses environment variable if None)
        """
        self.api_key = api_key or DEFAULT_API_KEY
        
        # Create Gemini client
        self.gemini_client = genai.Client(api_key=self.api_key)
        
        logger.info("Summarizer initialized")
    
    def _create_summary_prompt(self, transcript: str, summary_type: SummaryType) -> str:
        """
        Create a prompt for generating a specific type of summary
        
        Args:
            transcript: Transcript text to summarize
            summary_type: Type of summary to generate
            
        Returns:
            Prompt text for the AI model
        """
        base_prompt = f"""Create a {summary_type} summary of the following video transcript.
        
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
    
    def _create_gemini_system_instruction(self, summary_type: SummaryType) -> str:
        """
        Create a system instruction for Gemini based on summary type
        
        Args:
            summary_type: Type of summary to generate
            
        Returns:
            System instruction text
        """
        if summary_type == "concise":
            return "You are a content summarizer creating brief, concise summaries that capture the main points in 3-5 sentences."
            
        elif summary_type == "detailed":
            return "You are a content summarizer creating comprehensive summaries that cover all key points while being about 30% of the original length."
            
        elif summary_type == "bullet":
            return "You are a content summarizer creating bullet-point summaries with 5-10 key points, organized in a logical flow."
            
        elif summary_type == "sections":
            return "You are a content summarizer creating sectioned summaries that organize content into logical topics or themes."
            
        else:  # default
            return "You are a content summarizer creating summaries that cover main points in a concise but comprehensive manner."
    
    def summarize_with_gemini(self, transcript: str, summary_type: SummaryType = "default",
                             stream: bool = False) -> str:
        """
        Generate a summary using Gemini AI
        
        Args:
            transcript: Transcript text to summarize
            summary_type: Type of summary to generate
            stream: Whether to stream the response
            
        Returns:
            Generated summary
        """
        # Create the prompt
        prompt = self._create_summary_prompt(transcript, summary_type)
        
        # Create system instruction
        system_instruction = self._create_gemini_system_instruction(summary_type)
        
        logger.info(f"Generating {summary_type} summary with Gemini")
        
        try:
            if stream:
                # Stream the response
                response = self.gemini_client.models.generate_content_stream(
                    model="gemini-2.0-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.2
                    )
                )
                
                # Collect response chunks
                summary = ""
                for chunk in response:
                    if chunk.text:
                        summary += chunk.text
                
                return summary
                
            else:
                # Generate response at once
                response = self.gemini_client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.2
                    )
                )
                
                return response.text
                
        except Exception as e:
            logger.error(f"Error generating summary with Gemini: {str(e)}")
            return f"Error generating summary: {str(e)}"
    
    def summarize_with_ollama(self, transcript: str, summary_type: SummaryType = "default",
                            model: str = "llama3") -> str:
        """
        Generate a summary using Ollama LLM
        
        Args:
            transcript: Transcript text to summarize
            summary_type: Type of summary to generate
            model: Ollama model to use
            
        Returns:
            Generated summary
        """
        # Check if Ollama is available
        try:
            import requests
            
            # Create the prompt
            prompt = self._create_summary_prompt(transcript, summary_type)
            
            logger.info(f"Generating {summary_type} summary with Ollama ({model})")
            
            # Call Ollama API
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "Error: No response from Ollama")
            else:
                error_msg = f"Ollama API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return error_msg
                
        except ImportError:
            return "Error: Requests library not available for Ollama API"
        except Exception as e:
            logger.error(f"Error generating summary with Ollama: {str(e)}")
            return f"Error generating summary: {str(e)}"
    
    def summarize(self, transcript: str, summary_type: SummaryType = "default", 
                engine: str = "gemini", stream: bool = False) -> str:
        """
        Generate a summary using the specified engine
        
        Args:
            transcript: Transcript text to summarize
            summary_type: Type of summary to generate
            engine: Summary engine to use (gemini or ollama)
            stream: Whether to stream the response (only for Gemini)
            
        Returns:
            Generated summary
        """
        # Validate summary type
        valid_types = ["concise", "detailed", "bullet", "sections", "default"]
        if summary_type not in valid_types:
            logger.warning(f"Invalid summary type '{summary_type}'. Using 'default'.")
            summary_type = "default"
        
        # Generate summary with the specified engine
        if engine.lower() == "ollama":
            return self.summarize_with_ollama(transcript, summary_type)
        else:
            # Default to Gemini
            return self.summarize_with_gemini(transcript, summary_type, stream)
