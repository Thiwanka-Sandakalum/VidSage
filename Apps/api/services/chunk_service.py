
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter


class ChunkingError(Exception):
    """Custom exception for chunking-related errors."""
    pass


def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100,
    separators: List[str] = None
) -> List[str]:
    """
    Split text into chunks using RecursiveCharacterTextSplitter.
    
    Args:
        text: Text to split into chunks
        chunk_size: Maximum size of each chunk in characters (default: 500)
        chunk_overlap: Number of characters to overlap between chunks (default: 100)
        separators: List of separators to use for splitting (default: ["\n\n", "\n", " ", ""])
        
    Returns:
        List of text chunks
        
    Raises:
        ChunkingError: If chunking fails
    """
    if not text or not isinstance(text, str):
        raise ChunkingError("Text must be a non-empty string")
    
    if chunk_size <= 0:
        raise ChunkingError("Chunk size must be greater than 0")
    
    if chunk_overlap < 0:
        raise ChunkingError("Chunk overlap must be non-negative")
    
    if chunk_overlap >= chunk_size:
        raise ChunkingError("Chunk overlap must be less than chunk size")
    
    try:
        # Use default separators if none provided
        if separators is None:
            separators = ["\n\n", "\n", ". ", " ", ""]
        
        # Create the text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            length_function=len,
            is_separator_regex=False
        )
        
        # Split the text
        chunks = text_splitter.split_text(text)
        
        if not chunks:
            raise ChunkingError("No chunks created from text")
        
        # Filter out empty chunks
        chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
        
        if not chunks:
            raise ChunkingError("All chunks were empty after filtering")
        
        return chunks
        
    except ChunkingError:
        raise
    except Exception as e:
        raise ChunkingError(f"Failed to chunk text: {str(e)}")


def get_chunk_metadata(chunks: List[str]) -> dict:
    """
    Get metadata about the chunked text.
    
    Args:
        chunks: List of text chunks
        
    Returns:
        Dictionary with metadata about chunks
    """
    if not chunks:
        return {
            "total_chunks": 0,
            "total_characters": 0,
            "avg_chunk_length": 0,
            "min_chunk_length": 0,
            "max_chunk_length": 0
        }
    
    chunk_lengths = [len(chunk) for chunk in chunks]
    
    return {
        "total_chunks": len(chunks),
        "total_characters": sum(chunk_lengths),
        "avg_chunk_length": sum(chunk_lengths) // len(chunks),
        "min_chunk_length": min(chunk_lengths),
        "max_chunk_length": max(chunk_lengths)
    }
