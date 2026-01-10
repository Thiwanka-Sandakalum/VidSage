import logging
from typing import List, Dict, Any, Optional, Generator
import hashlib
from src.core.config import get_settings
from google import genai

from src.repositories.vector_repository import VectorRepository
from src.repositories.embedding_repository import EmbeddingRepository
from src.repositories.video_repository import VideoRepository

# Get settings instance
settings = get_settings()
logger = logging.getLogger(__name__)


class GenerationService:
    """Service for generating answers using Google Gemini API with markdown-formatted responses."""
    
    def __init__(
        self, 
        vector_repository: VectorRepository, 
        embedding_repository: EmbeddingRepository, 
        video_repository: VideoRepository
    ):
        self.api_key = settings.GOOGLE_API_KEY
        self.model = "gemma-3-27b-it"
        self.max_output_tokens = settings.LLM_MAX_OUTPUT_TOKENS or 512
        self.client = genai.Client(api_key=self.api_key)
        self.cache = {}  # In-memory response cache
        self.vector_repository = vector_repository
        self.embedding_repository = embedding_repository
        self.video_repository = video_repository
        logger.info(f"✅ Initialized Gemini API client: {self.model}")

    def _create_answer_prompt(self, query: str, context: str, video_title: str) -> str:
        """Create a prompt for answering questions with markdown formatting."""
        system_message = """You are an expert AI assistant analyzing YouTube video content.

## Your Responsibilities:
1. **Answer questions based ONLY on the provided video transcript segments**
2. **Provide clear, well-structured responses using markdown formatting**
3. **Be concise, accurate, and informative**
4. **If the answer isn't in the context, clearly state that you don't have enough information**
5. **Reference specific parts of the video when relevant**

## Formatting Guidelines:
- Use **bold** for emphasis on key points
- Use bullet points or numbered lists for clarity when listing items
- Use `code blocks` for technical terms or specific quotes
- Use headers (##, ###) to organize longer responses
- Keep paragraphs concise and readable

## Critical Rule:
Only use information from the provided context. Do not make up information or use external knowledge."""

        user_message = f"""# Video Title: {video_title}

## User Question:
{query}

## Relevant Video Segments:
{context}

---

**Instructions:**
- Answer the question using ONLY the video segments above
- Format your response in clean, readable markdown
- Be specific and cite information when helpful
- If the segments don't contain the answer, acknowledge it honestly
- Structure your answer with appropriate headers, lists, and emphasis

**Your Answer:**"""

        return f"{system_message}\n\n{user_message}"

    def _create_question_prompt(self, context: str, video_title: str) -> str:
        """Create a prompt for generating suggested questions with markdown formatting."""
        system_message = """You are an AI assistant that generates insightful questions about video content.

## Your Task:
Generate 5 engaging, diverse questions that viewers might want to ask about this video.

## Guidelines:
1. **Specificity**: Questions should be specific to the video content
2. **Diversity**: Cover different aspects (summary, key points, details, practical applications)
3. **Natural Language**: Make questions conversational and engaging
4. **Answerability**: Ensure questions can be answered from the video content
5. **Variety**: Use different question types (what, how, why, when, who, etc.)

## Format Requirements:
Return ONLY a numbered list of questions (1-5), one per line.
No additional text, explanations, or formatting."""

        user_message = f"""# Video Title: {video_title}

## Video Content Summary:
{context}

---

**Generate 5 insightful questions viewers might ask about this video:**"""

        return f"{system_message}\n\n{user_message}"

    def _create_summary_prompt(self, context: str, video_title: str) -> str:
        """Create a prompt for generating comprehensive summaries with markdown formatting."""
        prompt = f"""You are an expert content summarizer specializing in video analysis.

## Task:
Create a comprehensive, well-structured summary of the YouTube video based on the transcript segments provided.

## Guidelines:
- Focus on main ideas, key points, and important details
- Use clear markdown formatting with headers and bullet points
- Organize information logically
- Exclude irrelevant information
- Make the summary scannable and easy to read

## Format:
Structure your summary with:
- A brief **overview** (2-3 sentences)
- **Key Points** (bullet list)
- **Main Topics** covered (with sub-bullets if needed)
- **Conclusion** or takeaway (1-2 sentences)

---

# Video Title: {video_title}

## Transcript Segments:
{context}

---

**Your Comprehensive Summary:**"""
        return prompt

    def _create_qa_generation_prompt(
        self, 
        context: str, 
        video_title: str, 
        num_pairs: int
    ) -> str:
        """Create a prompt for generating Q&A pairs with markdown formatting."""
        prompt = f"""You are an AI assistant analyzing YouTube video content for FAQ generation.

## Task:
Generate {num_pairs} common questions viewers might ask about this video, along with concise, well-formatted answers based ONLY on the provided content.

## Guidelines:
- Questions should cover diverse aspects of the video
- Answers should be clear, concise, and markdown-formatted
- Use **bold** for emphasis, bullet points for lists
- Only use information from the provided transcript

## Format Requirements:
**Strictly follow this format:**

**Q1:** [Your question here]
**A1:** [Your answer here with proper markdown formatting]

**Q2:** [Your question here]
**A2:** [Your answer here with proper markdown formatting]

Continue for all {num_pairs} pairs.

---

# Video Title: {video_title or 'Unknown Video'}

## Video Content:
{context}

---

**Generate {num_pairs} Q&A Pairs:**"""
        return prompt

    def _format_context(
        self, 
        chunks: List[Dict[str, Any]], 
        max_chunks: Optional[int] = None
    ) -> str:
        """Format context chunks with enhanced structure."""
        if not chunks:
            return "No relevant information found in the video."
        
        chunk_limit = max_chunks if max_chunks else min(len(chunks), 10)
        formatted_chunks = []
        
        for i, chunk in enumerate(chunks[:chunk_limit], 1):
            chunk_text = chunk.get("text", "").strip()
            score = chunk.get("score", 0.0)
            formatted_chunk = (
                f"### Segment {i} (Relevance: {score:.2f})\n"
                f"{chunk_text}"
            )
            formatted_chunks.append(formatted_chunk)
        
        return "\n\n".join(formatted_chunks)

    def _format_context_for_questions(self, chunks: List[Dict[str, Any]]) -> str:
        """Format context for question generation - use 5 chunks."""
        if not chunks:
            return "No content available."
        
        formatted_chunks = []
        for i, chunk in enumerate(chunks[:5], 1):
            chunk_text = chunk.get("text", "").strip()
            if len(chunk_text) > 300:
                chunk_text = chunk_text[:300] + "..."
            formatted_chunks.append(f"**Segment {i}:** {chunk_text}")
        
        return "\n\n".join(formatted_chunks)

    def _invoke_llm(self, prompt: str) -> str:
        """Unified LLM invocation method."""
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        return getattr(response, "text", str(response))
    
    def _invoke_llm_stream(self, prompt: str) -> Generator[str, None, None]:
        """Streaming LLM invocation for better UX."""
        response = self.client.models.generate_content_stream(
            model=self.model,
            contents=prompt
        )
        for chunk in response:
            chunk_text = getattr(chunk, "text", "")
            if chunk_text:
                yield chunk_text
    
    def _get_cache_key(self, query: str, context: str) -> str:
        """Generate cache key for response caching."""
        content = f"{query}|{context[:500]}"
        return hashlib.md5(content.encode()).hexdigest()

    def _parse_questions(self, questions_text: str) -> List[str]:
        """Parse questions from LLM response."""
        questions = []
        for line in questions_text.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                question = line.lstrip('0123456789.-•) ').strip()
                if question and len(question) > 10:
                    questions.append(question)
        return questions

    def _parse_qa_pairs(self, response_text: str, num_pairs: int) -> List[Dict[str, str]]:
        """Parse Q&A pairs from LLM response."""
        qa_pairs = []
        lines = response_text.split('\n')
        current_q = None
        current_a = []
        
        for line in lines:
            line = line.strip()
            
            # Detect question line
            if line.startswith('**Q') and ':**' in line:
                # Save previous pair if exists
                if current_q and current_a:
                    qa_pairs.append({
                        "question": current_q,
                        "answer": ' '.join(current_a).strip()
                    })
                # Start new question
                current_q = line.split(':**', 1)[1].strip()
                current_a = []
            
            # Detect answer line
            elif line.startswith('**A') and ':**' in line and current_q:
                answer_text = line.split(':**', 1)[1].strip()
                current_a = [answer_text] if answer_text else []
            
            # Continue multiline answer
            elif current_q and current_a is not None and line and not line.startswith('**Q'):
                current_a.append(line)
        
        # Add last pair
        if current_q and current_a:
            qa_pairs.append({
                "question": current_q,
                "answer": ' '.join(current_a).strip()
            })
        
        return qa_pairs[:num_pairs]

    def generate_suggested_questions(
        self,
        chunks: List[Dict[str, Any]],
        video_title: Optional[str] = None
    ) -> List[str]:
        """Generate suggested questions with markdown formatting."""
        fallback_questions = [
            "What is this video about?",
            "What are the main points discussed?",
            "Can you summarize the key takeaways?",
            "What important topics are covered?",
            "What should I know from this video?"
        ]
        
        try:
            logger.info("🔄 Generating suggested questions")
            
            if not chunks:
                logger.warning("⚠️ No chunks available for question generation")
                return fallback_questions
            
            context = self._format_context_for_questions(chunks)
            prompt = self._create_question_prompt(context, video_title or "Unknown Video")
            questions_text = self._invoke_llm(prompt)
            
            questions = self._parse_questions(questions_text)
            result = questions[:5] if questions else fallback_questions
            
            logger.info(f"✅ Generated {len(result)} suggested questions")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error generating questions: {e}", exc_info=True)
            return fallback_questions


    def _remove_segment_markers(self, text: str) -> str:
        import re
        return re.sub(r'\(Segment \d+\)', '', text, flags=re.IGNORECASE)

    def generate_answer(
        self, 
        query: str, 
        chunks: List[Dict[str, Any]],
        video_title: Optional[str] = None,
        use_cache: bool = True
    ) -> str:
        """Generate markdown-formatted answer with caching support."""
        try:
            logger.info(f"🔄 Generating answer for query: '{query[:50]}...'")
            logger.info(f"📊 Using {len(chunks)} context chunks")
            
            if not chunks:
                return ("## No Information Available\n\n"
                       "I don't have any relevant information from this video to answer your question. "
                       "Please try asking about different aspects of the video content.")
            
            context = self._format_context(chunks, max_chunks=10)
            
            # Check cache
            if use_cache:
                cache_key = self._get_cache_key(query, context)
                if cache_key in self.cache:
                    logger.info("💾 Cache HIT - returning cached answer")
                    return self._remove_segment_markers(self.cache[cache_key])
                logger.info("🔄 Cache MISS - generating new answer")
            
            prompt = self._create_answer_prompt(query, context, video_title or "Unknown Video")
            answer = self._invoke_llm(prompt)
            answer = self._remove_segment_markers(answer)
            
            # Store in cache
            if use_cache:
                cache_key = self._get_cache_key(query, context)
                self.cache[cache_key] = answer
                logger.info("💾 Cached answer for future requests")
            
            logger.info(f"✅ Generated answer ({len(answer)} characters)")
            return answer
            
        except Exception as e:
            logger.error(f"❌ Error generating answer: {e}", exc_info=True)
            return ("## ⚠️ Error\n\n"
                   "An unexpected error occurred while generating the answer. "
                   "Please try again in a moment. If the issue persists, please contact support.")

    def generate_answer_stream(
        self, 
        query: str, 
        chunks: List[Dict[str, Any]],
        video_title: Optional[str] = None
    ) -> Generator[str, None, None]:
        """Stream markdown-formatted answer for better UX."""
        try:
            logger.info(f"🔄 Streaming answer for query: '{query[:50]}...'")
            
            if not chunks:
                yield ("## No Information Available\n\n"
                      "I don't have any relevant information from this video to answer your question.")
                return
            
            context = self._format_context(chunks, max_chunks=10)
            prompt = self._create_answer_prompt(query, context, video_title or "Unknown Video")
            
            import re
            for chunk_text in self._invoke_llm_stream(prompt):
                # Remove (Segment N) markers from each streamed chunk
                yield re.sub(r'\(Segment \d+\)', '', chunk_text, flags=re.IGNORECASE)
            
            logger.info("✅ Completed streaming response")
            
        except Exception as e:
            logger.error(f"❌ Error streaming answer: {e}", exc_info=True)
            yield "## ⚠️ Error\n\nAn error occurred while generating the answer."
    
    def generate_qa_pairs(
        self,
        chunks: List[Dict[str, Any]],
        video_title: Optional[str] = None,
        num_pairs: int = 5
    ) -> List[Dict[str, str]]:
        """Pre-generate markdown-formatted Q&A pairs in a single API call."""
        try:
            logger.info(f"🔄 Pre-generating {num_pairs} Q&A pairs")
            
            if not chunks:
                logger.warning("⚠️ No chunks available for Q&A generation")
                return []
            
            context = self._format_context(chunks, max_chunks=10)
            prompt = self._create_qa_generation_prompt(context, video_title, num_pairs)
            response_text = self._invoke_llm(prompt)
            
            qa_pairs = self._parse_qa_pairs(response_text, num_pairs)
            
            logger.info(f"✅ Pre-generated {len(qa_pairs)} Q&A pairs in 1 API call")
            return qa_pairs
            
        except Exception as e:
            logger.error(f"❌ Error generating Q&A pairs: {e}", exc_info=True)
            return []
        
    def generate_summary(
        self,
        chunks: List[Dict[str, Any]],
        video_title: Optional[str] = None
    ) -> str:
        """Generate a comprehensive markdown-formatted summary of the video."""
        try:
            logger.info(f"🔄 Generating full summary for video: {video_title}")
            
            if not chunks:
                return "## No Content Available\n\nNo content available to summarize."
            
            context = self._format_context(chunks, max_chunks=20)
            prompt = self._create_summary_prompt(context, video_title or "Unknown Video")
            summary = self._invoke_llm(prompt)
            
            logger.info(f"✅ Generated summary ({len(summary)} characters)")
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error generating summary: {e}", exc_info=True)
            return "## ⚠️ Error\n\nAn error occurred while generating the summary."

    def prepare_sources(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare source references from context chunks."""
        sources = []
        for chunk in chunks[:settings.MAX_CONTEXT_CHUNKS]:
            text = chunk.get("text", "")
            text_preview = text[:100] + "..." if len(text) > 100 else text
            source = {
                "chunk_id": chunk.get("chunk_id", "unknown"),
                "relevance_score": round(chunk.get("score", 0.0), 4),
                "text_preview": text_preview
            }
            sources.append(source)
        return sources


def get_generation_service() -> GenerationService:
    """Dependency provider for GenerationService with repository injection."""
    from src.api.dependencies import (
        get_vector_repository, 
        get_embedding_repository, 
        get_video_repository
    )
    
    vector_repo = get_vector_repository()
    embedding_repo = get_embedding_repository()
    video_repo = get_video_repository()
    
    return GenerationService(vector_repo, embedding_repo, video_repo)