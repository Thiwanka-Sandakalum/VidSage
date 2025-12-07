
import logging
from typing import List, Dict, Any, Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

import config

# Configure logging
logger = logging.getLogger(__name__)


class GenerationService:
    """Service for generating answers using RAG pipeline."""
    
    def __init__(self):
        """Initialize the generation service with LLM and prompts."""
        self.llm = self._initialize_llm()
        self.prompt_template = self._create_prompt_template()
        self.chain = self._build_chain()
        
    def _initialize_llm(self) -> ChatGoogleGenerativeAI:
        """Initialize the Google Gemini LLM."""
        try:
            llm = ChatGoogleGenerativeAI(
                model=config.LLM_MODEL,
                google_api_key=config.GOOGLE_API_KEY,
                temperature=config.LLM_TEMPERATURE,
                max_output_tokens=config.LLM_MAX_OUTPUT_TOKENS,
                convert_system_message_to_human=True  # Required for Gemini
            )
            logger.info(f"✅ Initialized LLM: {config.LLM_MODEL}")
            return llm
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM: {e}")
            raise
    
    def _create_prompt_template(self) -> ChatPromptTemplate:
        """Create the prompt template for video Q&A."""
        
        system_message = """You are a helpful AI assistant analyzing YouTube video content.

Your responsibilities:
1. Answer questions based ONLY on the provided video transcript chunks
2. Be concise, accurate, and informative
3. If the answer isn't in the context, clearly state "I don't have enough information from this video to answer that question"
4. Use natural language and maintain a friendly tone
5. When relevant, reference specific parts of the video

Remember: Only use information from the provided context. Do not make up information."""

        user_message = """Video Title: {video_title}

User Question: {query}

Relevant Video Segments:
{context}

Instructions:
- Answer the question using ONLY the video segments above
- Be specific and cite information when helpful
- If the segments don't contain the answer, acknowledge it honestly

Answer:"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", user_message)
        ])
        
        return prompt
    
    def _build_chain(self):
        """Build the LangChain LCEL chain for RAG."""
        
        chain = (
            {
                "context": lambda x: self._format_context(x["chunks"]),
                "query": lambda x: x["query"],
                "video_title": lambda x: x.get("video_title", "Unknown Video")
            }
            | self.prompt_template
            | self.llm
            | StrOutputParser()
        )
        
        return chain
    
    def _format_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Format retrieved chunks into a context string.
        
        Args:
            chunks: List of chunk dictionaries with 'text', 'chunk_id', 'score'
            
        Returns:
            Formatted context string
        """
        if not chunks:
            return "No relevant information found in the video."
        
        formatted_chunks = []
        for i, chunk in enumerate(chunks[:config.MAX_CONTEXT_CHUNKS], 1):
            chunk_text = chunk.get("text", "").strip()
            chunk_id = chunk.get("chunk_id", "unknown")
            score = chunk.get("score", 0.0)
            
            formatted_chunk = f"[Segment {i}] (Relevance: {score:.2f})\n{chunk_text}"
            formatted_chunks.append(formatted_chunk)
        
        return "\n\n".join(formatted_chunks)
    
    def generate_answer(
        self, 
        query: str, 
        chunks: List[Dict[str, Any]],
        video_title: Optional[str] = None
    ) -> str:
        """Generate an answer using the RAG chain.
        
        Args:
            query: User's question
            chunks: Retrieved context chunks from vector search
            video_title: Optional video title for context
            
        Returns:
            Generated answer string
        """
        try:
            logger.info(f"🔄 Generating answer for query: '{query[:50]}...'")
            logger.info(f"📊 Using {len(chunks)} context chunks")
            
            # Prepare input for the chain
            chain_input = {
                "query": query,
                "chunks": chunks,
                "video_title": video_title or "Unknown Video"
            }
            
            # Generate answer
            answer = self.chain.invoke(chain_input)
            
            logger.info(f"✅ Generated answer ({len(answer)} characters)")
            return answer
            
        except Exception as e:
            logger.error(f"❌ Error generating answer: {e}")
            raise RuntimeError(f"Failed to generate answer: {str(e)}")
    
    def prepare_sources(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare source chunk information for response.
        
        Args:
            chunks: Retrieved context chunks
            
        Returns:
            List of source chunk dictionaries
        """
        sources = []
        
        for chunk in chunks[:config.MAX_CONTEXT_CHUNKS]:
            text = chunk.get("text", "")
            text_preview = text[:100] + "..." if len(text) > 100 else text
            
            source = {
                "chunk_id": chunk.get("chunk_id", "unknown"),
                "relevance_score": round(chunk.get("score", 0.0), 4),
                "text_preview": text_preview
            }
            sources.append(source)
        
        return sources


# Singleton instance
_generation_service: Optional[GenerationService] = None


def get_generation_service() -> GenerationService:
    """Get or create the generation service singleton.
    
    Returns:
        GenerationService instance
    """
    global _generation_service
    
    if _generation_service is None:
        _generation_service = GenerationService()
    
    return _generation_service
