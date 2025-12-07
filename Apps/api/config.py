
import os
from typing import Literal

# API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "vidsage")
MONGODB_VIDEOS_COLLECTION = "videos"
MONGODB_EMBEDDINGS_COLLECTION = "video_embeddings"
ATLAS_VECTOR_SEARCH_INDEX_NAME = os.getenv("ATLAS_VECTOR_SEARCH_INDEX_NAME", "vector_index")

# Embedding Model Configuration
EMBEDDING_MODEL = "models/text-embedding-004"  # Latest stable model
EMBEDDING_DIMENSIONS = 768  # Supported: 128-768 (recommend: 768)
EMBEDDING_TASK_TYPE: Literal[
    "RETRIEVAL_DOCUMENT",
    "RETRIEVAL_QUERY", 
    "SEMANTIC_SIMILARITY",
    "CLASSIFICATION",
    "CLUSTERING"
] = "RETRIEVAL_DOCUMENT"

# LLM Configuration for RAG Generation
LLM_MODEL = "gemini-2.5-pro"  # Fast and cost-effective
LLM_TEMPERATURE = 0.3  # Low temperature for factual responses
LLM_MAX_OUTPUT_TOKENS = 1024  # Maximum response length
MAX_CONTEXT_CHUNKS = 5  # Number of chunks to use as context
ENABLE_STREAMING = True  # Enable streaming responses

# Text Chunking Configuration
CHUNK_SIZE = 500  # Maximum characters per chunk
CHUNK_OVERLAP = 100  # Overlap between chunks in characters
CHUNK_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]  # Separators in priority order

# Transcript Configuration
DEFAULT_TRANSCRIPT_LANGUAGES = ['en', 'en-US']  # Preferred subtitle languages

# API Response Configuration
MAX_CHUNKS_IN_RESPONSE = 10  # Maximum chunks to return in API response

# Server Configuration
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000
SERVER_RELOAD = True  # Enable auto-reload for development

# CORS Configuration
CORS_ALLOW_ORIGINS = ["*"]  # In production, replace with specific origins
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]

# Logging Configuration
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Model Information
# Based on: https://ai.google.dev/gemini-api/docs/embeddings
SUPPORTED_MODELS = {
    "text-embedding-004": {
        "name": "Text Embedding 004",
        "max_tokens": 2048,
        "dimensions": "128-768",
        "recommended_dims": [256, 512, 768],
        "description": "Latest stable embedding model with improved performance"
    },
    "embedding-001": {
        "name": "Embedding 001", 
        "max_tokens": 2048,
        "dimensions": "128-3072",
        "recommended_dims": [768, 1536, 3072],
        "description": "Legacy model, deprecated in Oct 2025",
        "deprecated": True
    }
}

# Task Type Descriptions
TASK_TYPES = {
    "RETRIEVAL_DOCUMENT": "Optimized for indexing documents for search/RAG",
    "RETRIEVAL_QUERY": "Optimized for search queries against indexed documents",
    "SEMANTIC_SIMILARITY": "Optimized for assessing text similarity",
    "CLASSIFICATION": "Optimized for text classification tasks",
    "CLUSTERING": "Optimized for clustering texts by similarity",
    "CODE_RETRIEVAL_QUERY": "Optimized for code search queries",
    "QUESTION_ANSWERING": "Optimized for Q&A systems",
    "FACT_VERIFICATION": "Optimized for fact-checking tasks"
}
