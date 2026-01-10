"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import List, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Environment
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    
    # API Settings
    PROJECT_NAME: str = "VidSage - YouTube RAG Pipeline API"
    VERSION: str = "1.0.0"
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [origin.strip() for origin in v.split(",")]
        elif isinstance(v, list):
            return v
        return ["*"]
    
    # Authentication (Clerk)
    CLERK_JWT_PUBLIC_KEY: str = ""
    CLERK_ISSUER: str = ""
    JWT_ALGORITHM: str = "RS256"
    
    # Google AI
    GOOGLE_API_KEY: str
    
    # MongoDB
    MONGODB_URI: str
    MONGODB_DB_NAME: str = "vidsage"
    MONGODB_VIDEOS_COLLECTION: str = "videos"
    MONGODB_EMBEDDINGS_COLLECTION: str = "video_embeddings"
    ATLAS_VECTOR_SEARCH_INDEX_NAME: str = "vector_index"
    
    # Embedding Configuration
    EMBEDDING_MODEL: str = "models/text-embedding-004"
    EMBEDDING_DIMENSIONS: int = 768
    EMBEDDING_TASK_TYPE: str = "RETRIEVAL_DOCUMENT"
    
    # LLM Configuration
    LLM_MODEL: str = "gemini-2.0-flash"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_OUTPUT_TOKENS: int = 512
    MAX_CONTEXT_CHUNKS: int = 2
    ENABLE_STREAMING: bool = True
    
    # Text Chunking
    CHUNK_SIZE: int = 300
    CHUNK_OVERLAP: int = 50
    CHUNK_SEPARATORS: List[str] = ["\n\n", "\n", ". ", " ", ""]
    
    # Transcript
    DEFAULT_TRANSCRIPT_LANGUAGES: List[str] = ["en", "en-US"]
    
    # Cache Configuration
    CACHE_ENABLED: bool = True
    CACHE_TTL_MINUTES: int = 30
    REDIS_URL: str = ""
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: Literal["json", "text"] = "text"
    
    # API Response
    MAX_CHUNKS_IN_RESPONSE: int = 10
    
    @validator("GOOGLE_API_KEY")
    def validate_google_api_key(cls, v):
        """Validate Google API key is set."""
        if not v:
            raise ValueError("GOOGLE_API_KEY must be set in environment variables")
        return v
    
    @validator("MONGODB_URI")
    def validate_mongodb_uri(cls, v):
        """Validate MongoDB URI format."""
        if not v:
            raise ValueError("MONGODB_URI must be set in environment variables")
        if not v.startswith("mongodb"):
            raise ValueError("MONGODB_URI must be a valid MongoDB connection string")
        return v
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT == "production"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Using lru_cache ensures settings are loaded only once.
    """
    return Settings()


# Global settings instance for backward compatibility
settings = get_settings()
