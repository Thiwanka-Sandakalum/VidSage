"""Generation Service - Microservice for RAG-based answer generation."""

import os
import sys
import logging
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import google.generativeai as genai
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Add parent directory to path for shared imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.config import (
    GOOGLE_API_KEY,
    MONGODB_URI,
    MONGODB_DB_NAME,
    MONGODB_COLLECTION,
    EMBEDDING_MODEL,
    LLM_MODEL,
    LLM_TEMPERATURE,
    LLM_MAX_OUTPUT_TOKENS
)
from shared.models import GenerateRequest, GenerateResponse, SourceChunk
from shared.utils import format_error_message


# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("generation-service")

app = FastAPI(
    title="Generation Service",
    description="Microservice for RAG-based answer generation",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.debug(f"Response status: {response.status_code} for {request.method} {request.url}")
    return response

# Initialize Google AI
genai.configure(api_key=GOOGLE_API_KEY)

# MongoDB client (lazy initialization)
mongodb_client = None


def get_mongodb_client():
    """Get or create MongoDB client."""
    global mongodb_client
    if mongodb_client is None:
        logger.debug(f"Creating new MongoDB client connection to: {MONGODB_URI}")
        mongodb_client = MongoClient(MONGODB_URI)
        logger.info("MongoDB client created successfully for generation service")
    return mongodb_client


# Initialize LLM with quota-friendly settings
try:
    llm = ChatGoogleGenerativeAI(
        model=LLM_MODEL,
        google_api_key=GOOGLE_API_KEY,
        temperature=LLM_TEMPERATURE,
        max_output_tokens=LLM_MAX_OUTPUT_TOKENS,
        convert_system_message_to_human=True,
        request_timeout=30,  # Reduce timeout to fail faster
        retry_delay=1,  # Shorter retry delay
        max_retries=1   # Fewer retries to avoid extended quota usage
    )
    logger.info(f"✅ LLM initialized successfully with model: {LLM_MODEL}")
except Exception as e:
    logger.warning(f"⚠️ Failed to initialize LLM: {e}")
    # Create a basic LLM instance as fallback
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",  # Most quota-friendly model
        google_api_key=GOOGLE_API_KEY,
        temperature=0.3,
        max_output_tokens=512,
        convert_system_message_to_human=True
    )
    logger.info("🔄 Fallback LLM initialized with gemini-1.5-flash")

# Create prompt template
prompt_template = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful AI assistant that answers questions about YouTube videos.
Your task is to provide accurate, concise answers based ONLY on the video transcript segments provided.

RULES:
1. Answer ONLY based on the provided video segments
2. If the information isn't in the segments, say "I don't have enough information"
3. Be concise and factual
4. Cite which segments you used in your answer
5. Maintain a helpful, professional tone"""),
    ("user", """Video Title: {video_title}

User Question: {query}

Relevant Video Segments:
{context}

Please answer the question based on these segments.""")
])

# Build chain
output_parser = StrOutputParser()
chain = prompt_template | llm | output_parser


@app.get("/")
async def root():
    """Root endpoint with service information."""
    logger.info("Root endpoint accessed.")
    return {
        "service": "Generation Service",
        "version": "1.0.0",
        "status": "healthy",
        "configuration": {
            "llm_model": LLM_MODEL,
            "temperature": LLM_TEMPERATURE,
            "max_tokens": LLM_MAX_OUTPUT_TOKENS
        },
        "endpoints": {
            "/generate": "POST - Generate answers using RAG",
            "/health": "GET - Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    logger.info("Health check endpoint accessed.")
    try:
        client = get_mongodb_client()
        client.admin.command('ping')
        mongodb_status = "connected"
        logger.debug("MongoDB connection successful.")
    except Exception as e:
        mongodb_status = "disconnected"
        logger.error(f"MongoDB connection failed: {e}")
    return {
        "status": "healthy",
        "service": "generation-service",
        "mongodb": mongodb_status,
        "llm_model": LLM_MODEL,
        "google_api_key": "configured" if GOOGLE_API_KEY else "missing"
    }


def vector_search(video_id: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Perform vector search in MongoDB.
    """
    logger.info(f"🔍 Starting vector search for video_id={video_id}, query='{query[:50]}...', top_k={top_k}")
    
    # Generate query embedding
    logger.debug("🧠 Generating query embedding using Google AI...")
    embedding_result = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=query,
        task_type="retrieval_query"
    )
    query_embedding = embedding_result['embedding']
    logger.debug(f"✅ Query embedding generated with {len(query_embedding)} dimensions")
    
    # Perform vector search using MongoDB aggregation
    logger.debug("📊 Connecting to MongoDB for vector search...")
    client = get_mongodb_client()
    db = client[MONGODB_DB_NAME]
    collection = db[MONGODB_COLLECTION]
    
    logger.debug(f"🔎 Building aggregation pipeline with numCandidates={top_k * 10}")
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": top_k * 10,
                "limit": top_k,
                "filter": {"video_id": video_id}
            }
        },
        {
            "$project": {
                "_id": 0,
                "chunk_id": 1,
                "text": 1,
                "score": {"$meta": "vectorSearchScore"},
                "metadata": 1
            }
        }
    ]
    
    logger.debug("🚀 Executing vector search aggregation pipeline...")
    results = list(collection.aggregate(pipeline))
    logger.info(f"✅ Vector search completed - found {len(results)} relevant chunks")
    
    # Log relevance scores for debugging
    if results:
        scores = [chunk.get('score', 0.0) for chunk in results]
        logger.debug(f"📊 Relevance scores: min={min(scores):.3f}, max={max(scores):.3f}, avg={sum(scores)/len(scores):.3f}")
    
    return results


def format_context(chunks: List[Dict[str, Any]]) -> str:
    """Format chunks into context string for LLM."""
    logger.debug("🔧 Starting context formatting process...")
    
    if not chunks:
        logger.warning("⚠️ No chunks to format, returning empty context")
        return "No relevant information found."
    
    logger.debug(f"📝 Formatting {len(chunks)} chunks into context")
    context_parts = []
    total_chars = 0
    
    for i, chunk in enumerate(chunks, 1):
        score = chunk.get('score', 0.0)
        text = chunk.get('text', '')
        text_length = len(text)
        total_chars += text_length
        
        context_part = f"[Segment {i}] (Relevance: {score:.2f})\n{text}\n"
        context_parts.append(context_part)
        
        logger.debug(f"📄 Segment {i}: {text_length} chars, relevance: {score:.3f}")
    
    context = "\n".join(context_parts)
    logger.info(f"✅ Context formatted: {len(context_parts)} segments, {total_chars} total characters")
    
    return context


@app.post("/generate", response_model=GenerateResponse)
async def generate_answer(request: GenerateRequest):
    """
    Generate an answer using RAG pipeline.
    """
    logger.info(f"/generate called for video_id={request.video_id}, query='{request.query}', top_k={request.top_k}")
    try:
        # Step 1: Vector search
        try:
            logger.debug("Starting vector search...")
            search_results = vector_search(
                video_id=request.video_id,
                query=request.query,
                top_k=request.top_k
            )
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Vector search failed: {str(e)}"
            )
        if not search_results:
            logger.warning(f"No relevant content found for query: '{request.query}'")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No relevant content found for query: '{request.query}'"
            )
        # Step 2: Get video metadata
        logger.debug("📋 Retrieving video metadata from MongoDB...")
        try:
            client = get_mongodb_client()
            db = client[MONGODB_DB_NAME]
            collection = db[MONGODB_COLLECTION]
            video_doc = collection.find_one({"video_id": request.video_id})
            video_title = video_doc.get("metadata", {}).get("title", "Unknown Video") if video_doc else "Unknown Video"
            logger.debug(f"✅ Video title resolved: {video_title}")
        except Exception as e:
            video_title = "Unknown Video"
            logger.warning(f"⚠️ Failed to get video metadata, using default: {e}")
            
        # Step 3: Format context
        logger.debug("📝 Formatting context for LLM input...")
        context = format_context(search_results)
        context_length = len(context)
        logger.debug(f"📊 Context prepared - {context_length} characters, {len(search_results)} segments")
        
        # Step 4: Generate answer
        logger.info(f"🤖 Starting LLM generation with model: {LLM_MODEL}")
        try:
            logger.debug("🔄 Invoking LangChain pipeline...")
            answer = chain.invoke({
                "query": request.query,
                "context": context,
                "video_title": video_title
            })
            answer_length = len(answer)
            logger.info(f"✅ LLM answer generated successfully ({answer_length} characters)")
            logger.debug(f"📤 Generated answer preview: {answer[:100]}...")
        except Exception as e:
            error_str = str(e)
            logger.error(f"❌ LLM generation failed: {error_str}")
            
            # Handle quota exceeded errors specifically
            if "quota" in error_str.lower() or "429" in error_str:
                logger.warning("🚫 Google AI quota exceeded - providing fallback response")
                answer = f"""I found relevant information from the video "{video_title}" but I'm currently unable to generate a detailed response due to API limitations. 

Here's what I found from the transcript:

{context[:1000]}...

Please try again in a few minutes or contact support if the issue persists."""
                logger.info("✅ Fallback response generated due to quota limits")
            else:
                # Other errors should still raise exceptions
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"LLM generation failed: {str(e)}"
                )
        # Step 5: Prepare sources
        sources = [
            SourceChunk(
                chunk_id=chunk["chunk_id"],
                relevance_score=chunk.get("score", 0.0),
                text_preview=chunk["text"][:100] + "..." if len(chunk["text"]) > 100 else chunk["text"]
            )
            for chunk in search_results
        ]
        logger.debug(f"Prepared {len(sources)} source chunks.")
        logger.info("Answer generation completed successfully.")
        return GenerateResponse(
            answer=answer,
            sources=sources,
            model=LLM_MODEL
        )
    except HTTPException:
        raise
    except Exception as e:
        error_info = format_error_message(e, "Answer generation failed")
        logger.error(f"Unexpected error in /generate: {error_info['detail']}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_info["detail"]
        )


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Service shutting down. Closing MongoDB client.")
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        logger.debug("MongoDB client closed.")


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Generation Service...")
    port = int(os.getenv("PORT", "8003"))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
