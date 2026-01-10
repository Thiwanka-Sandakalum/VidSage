import logging
from typing import List, Dict, Any, Optional, Generator
import hashlib
import config
from google import genai

logger = logging.getLogger(__name__)

class GenerationService:
    """Service for generating answers using Google Gemini API (official client)."""

    def __init__(self):
        self.api_key = config.GOOGLE_API_KEY
        self.model = "gemini-2.5-flash-lite"
        self.max_output_tokens = config.LLM_MAX_OUTPUT_TOKENS or 512
        self.client = genai.Client(api_key=self.api_key)
        self.cache = {}  # In-memory response cache
        logger.info(f"✅ Initialized Gemini API client: {self.model}")

    def _create_answer_prompt(self, query: str, context: str, video_title: str) -> str:
        system_message = (
            "You are a helpful AI assistant analyzing YouTube video content.\n\n"
            "Your responsibilities:\n"
            "1. Answer questions based ONLY on the provided video transcript chunks\n"
            "2. Be concise, accurate, and informative\n"
            "3. If the answer isn't in the context, clearly state 'I don't have enough information from this video to answer that question'\n"
            "4. Use natural language and maintain a friendly tone\n"
            "5. When relevant, reference specific parts of the video\n\n"
            "Remember: Only use information from the provided context. Do not make up information."
        )
        user_message = (
            f"Video Title: {video_title}\n\n"
            f"User Question: {query}\n\n"
            f"Relevant Video Segments:\n{context}\n\n"
            "Instructions:\n"
            "- Answer the question using ONLY the video segments above\n"
            "- Be specific and cite information when helpful\n"
            "- If the segments don't contain the answer, acknowledge it honestly\n\n"
            "Answer:"
        )
        return f"{system_message}\n\n{user_message}"

    def _create_question_prompt(self, context: str, video_title: str) -> str:
        system_message = (
            "You are an AI assistant that generates insightful questions about video content.\n\n"
            "Your task: Generate 4-5 engaging, diverse questions that a viewer might want to ask about this video.\n\n"
            "Guidelines:\n"
            "1. Questions should be specific to the video content\n"
            "2. Cover different aspects: summary, key points, details, practical applications\n"
            "3. Make questions natural and conversational\n"
            "4. Ensure questions can be answered from the video content\n"
            "5. Vary question types (what, how, why, etc.)\n\n"
            "Format: Return ONLY the questions, one per line, numbered 1-5."
        )
        user_message = (
            f"Video Title: {video_title}\n\n"
            f"Video Content Summary:\n{context}\n\n"
            "Generate 5 insightful questions viewers might ask about this video:"
        )
        return f"{system_message}\n\n{user_message}"

    def _format_context(self, chunks: List[Dict[str, Any]], max_chunks: int = None) -> str:
        """Strategy 3: Use MORE context chunks (increase from default to utilize TPM better)"""
        if not chunks:
            return "No relevant information found in the video."
        
        # Use more chunks if max_chunks not specified (utilize available TPM)
        chunk_limit = max_chunks if max_chunks else min(len(chunks), 10)  # Increased from config.MAX_CONTEXT_CHUNKS
        
        formatted_chunks = []
        for i, chunk in enumerate(chunks[:chunk_limit], 1):
            chunk_text = chunk.get("text", "").strip()
            score = chunk.get("score", 0.0)
            formatted_chunk = f"[Segment {i}] (Relevance: {score:.2f})\n{chunk_text}"
            formatted_chunks.append(formatted_chunk)
        return "\n\n".join(formatted_chunks)

    def _format_context_for_questions(self, chunks: List[Dict[str, Any]]) -> str:
        """Format context for question generation - use 5 chunks instead of 3"""
        if not chunks:
            return "No content available."
        formatted_chunks = []
        for chunk in chunks[:5]:  # Increased from 3 to 5
            chunk_text = chunk.get("text", "").strip()
            if len(chunk_text) > 300:
                chunk_text = chunk_text[:300] + "..."
            formatted_chunks.append(chunk_text)
        return "\n\n".join(formatted_chunks)

    def _invoke_llm_for_questions(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        return getattr(response, "text", str(response))

    def _invoke_llm_for_answer(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        return getattr(response, "text", str(response))
    
    def _invoke_llm_for_answer_stream(self, prompt: str) -> Generator[str, None, None]:
        """Strategy 5: Streaming responses for better UX"""
        response = self.client.models.generate_content_stream(
            model=self.model,
            contents=prompt
        )
        for chunk in response:
            chunk_text = getattr(chunk, "text", "")
            if chunk_text:
                yield chunk_text
    
    def _get_cache_key(self, query: str, context: str) -> str:
        """Generate cache key for response caching"""
        content = f"{query}|{context[:500]}"  # Use first 500 chars of context
        return hashlib.md5(content.encode()).hexdigest()

    def generate_suggested_questions(
        self,
        chunks: List[Dict[str, Any]],
        video_title: Optional[str] = None
    ) -> List[str]:
        fallback_questions = [
            "What is this video about?",
            "What are the main points discussed?",
            "Can you summarize the key takeaways?",
            "What important topics are covered?",
            "What should I know from this video?"
        ]
        try:
            logger.info(f"🔄 Generating suggested questions")
            if not chunks:
                logger.warning("⚠️ No chunks available for question generation")
                return fallback_questions
            context = self._format_context_for_questions(chunks)
            prompt = self._create_question_prompt(context, video_title or "Unknown Video")
            questions_text = self._invoke_llm_for_questions(prompt)
            questions = []
            for line in questions_text.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    question = line.lstrip('0123456789.-•) ').strip()
                    if question and len(question) > 10:
                        questions.append(question)
            result = questions[:5] if questions else fallback_questions
            logger.info(f"✅ Generated {len(result)} suggested questions")
            return result
        except Exception as e:
            logger.error(f"❌ Error generating questions: {e}")
            return fallback_questions

    def generate_answer(
        self, 
        query: str, 
        chunks: List[Dict[str, Any]],
        video_title: Optional[str] = None,
        use_cache: bool = True
    ) -> str:
        """Generate answer with caching support (Strategy 3: More context, implicit caching)"""
        try:
            logger.info(f"🔄 Generating answer for query: '{query[:50]}...'")
            logger.info(f"📊 Using {len(chunks)} context chunks")
            
            if not chunks:
                return "I don't have any relevant information from this video to answer your question. Please try asking about different aspects of the video content."
            
            # Strategy 3: Use more context chunks (10 instead of default)
            context = self._format_context(chunks, max_chunks=10)
            
            # Check cache first (implicit caching strategy)
            if use_cache:
                cache_key = self._get_cache_key(query, context)
                if cache_key in self.cache:
                    logger.info("💾 Cache HIT - returning cached answer")
                    return self.cache[cache_key]
                logger.info("🔄 Cache MISS - generating new answer")
            
            prompt = self._create_answer_prompt(query, context, video_title or "Unknown Video")
            answer = self._invoke_llm_for_answer(prompt)
            
            # Store in cache
            if use_cache:
                cache_key = self._get_cache_key(query, context)
                self.cache[cache_key] = answer
                logger.info("💾 Cached answer for future requests")
            
            logger.info(f"✅ Generated answer ({len(answer)} characters)")
            return answer
        except Exception as e:
            logger.error(f"❌ Error generating answer: {e}")
            return (
                "⚠️ An unexpected error occurred while generating the answer. "
                "Please try again in a moment. If the issue persists, please contact support."
            )

    def prepare_sources(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
    
    def generate_answer_stream(
        self, 
        query: str, 
        chunks: List[Dict[str, Any]],
        video_title: Optional[str] = None
    ) -> Generator[str, None, None]:
        """Strategy 5: Streaming response for better UX"""
        try:
            logger.info(f"🔄 Streaming answer for query: '{query[:50]}...'")
            
            if not chunks:
                yield "I don't have any relevant information from this video to answer your question."
                return
            
            # Use more context chunks
            context = self._format_context(chunks, max_chunks=10)
            prompt = self._create_answer_prompt(query, context, video_title or "Unknown Video")
            
            # Stream the response
            for chunk_text in self._invoke_llm_for_answer_stream(prompt):
                yield chunk_text
                
            logger.info("✅ Completed streaming response")
        except Exception as e:
            logger.error(f"❌ Error streaming answer: {e}")
            yield "⚠️ An error occurred while generating the answer."
    
    def generate_qa_pairs(
        self,
        chunks: List[Dict[str, Any]],
        video_title: Optional[str] = None,
        num_pairs: int = 5
    ) -> List[Dict[str, str]]:
        """Strategy 4: Pre-generate Q&A pairs during video processing (1 API call instead of N)"""
        try:
            logger.info(f"🔄 Pre-generating {num_pairs} Q&A pairs")
            
            if not chunks:
                logger.warning("⚠️ No chunks available for Q&A generation")
                return []
            
            # Use rich context for better Q&A
            context = self._format_context(chunks, max_chunks=10)
            
            # Generate questions AND answers in ONE API call
            prompt = (
                f"You are an AI assistant analyzing YouTube video content.\n\n"
                f"Video Title: {video_title or 'Unknown Video'}\n\n"
                f"Video Content:\n{context}\n\n"
                f"Generate {num_pairs} common questions viewers might ask about this video, "
                f"along with concise answers based ONLY on the provided content.\n\n"
                f"Format your response as:\n"
                f"Q1: [question]\nA1: [answer]\n\n"
                f"Q2: [question]\nA2: [answer]\n\n"
                f"...and so on."
            )
            
            response_text = self._invoke_llm_for_answer(prompt)
            
            # Parse Q&A pairs
            qa_pairs = []
            lines = response_text.split('\n')
            current_q = None
            current_a = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('Q') and ':' in line:
                    if current_q and current_a:
                        qa_pairs.append({"question": current_q, "answer": current_a})
                    current_q = line.split(':', 1)[1].strip()
                    current_a = None
                elif line.startswith('A') and ':' in line and current_q:
                    current_a = line.split(':', 1)[1].strip()
                elif current_a and line:  # Continue multiline answer
                    current_a += " " + line
            
            # Add last pair
            if current_q and current_a:
                qa_pairs.append({"question": current_q, "answer": current_a})
            
            logger.info(f"✅ Pre-generated {len(qa_pairs)} Q&A pairs in 1 API call")
            return qa_pairs[:num_pairs]
            
        except Exception as e:
            logger.error(f"❌ Error generating Q&A pairs: {e}")
            return []

# Singleton instance
_generation_service: Optional[GenerationService] = None

def get_generation_service() -> GenerationService:
    global _generation_service
    if _generation_service is None:
        _generation_service = GenerationService()
    return _generation_service
