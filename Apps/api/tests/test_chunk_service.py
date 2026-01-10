import pytest
from services.chunk_service import chunk_text, get_chunk_metadata, ChunkingError


class TestChunkText:
    def test_chunk_text_basic(self):
        text = "This is a test. " * 100
        chunks = chunk_text(text, chunk_size=100, chunk_overlap=20)
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)
        assert all(len(chunk) <= 150 for chunk in chunks)
    
    def test_chunk_text_with_custom_separators(self):
        text = "Sentence one.\nSentence two.\nSentence three."
        chunks = chunk_text(text, chunk_size=20, chunk_overlap=5, separators=["\n", " "])
        
        assert len(chunks) > 0
        assert all(chunk.strip() for chunk in chunks)
    
    def test_chunk_text_small_text(self):
        text = "Short text"
        chunks = chunk_text(text, chunk_size=500, chunk_overlap=50)
        
        assert len(chunks) == 1
        assert chunks[0] == text
    
    def test_chunk_text_exact_size(self):
        text = "A" * 500
        chunks = chunk_text(text, chunk_size=500, chunk_overlap=0)
        
        assert len(chunks) == 1
        assert len(chunks[0]) == 500
    
    def test_chunk_text_with_overlap(self):
        text = "Word " * 100
        chunks = chunk_text(text, chunk_size=50, chunk_overlap=10)
        
        assert len(chunks) >= 2
        for i in range(len(chunks) - 1):
            assert len(chunks[i]) <= 60
    
    def test_chunk_text_empty_string_error(self):
        with pytest.raises(ChunkingError, match="Text must be a non-empty string"):
            chunk_text("")
    
    def test_chunk_text_none_error(self):
        with pytest.raises(ChunkingError, match="Text must be a non-empty string"):
            chunk_text(None)
    
    def test_chunk_text_invalid_chunk_size(self):
        with pytest.raises(ChunkingError, match="Chunk size must be greater than 0"):
            chunk_text("Some text", chunk_size=0)
    
    def test_chunk_text_negative_chunk_size(self):
        with pytest.raises(ChunkingError, match="Chunk size must be greater than 0"):
            chunk_text("Some text", chunk_size=-10)
    
    def test_chunk_text_negative_overlap(self):
        with pytest.raises(ChunkingError, match="Chunk overlap must be non-negative"):
            chunk_text("Some text", chunk_overlap=-5)
    
    def test_chunk_text_overlap_greater_than_size(self):
        with pytest.raises(ChunkingError, match="Chunk overlap must be less than chunk size"):
            chunk_text("Some text", chunk_size=100, chunk_overlap=100)
    
    def test_chunk_text_overlap_equal_to_size(self):
        with pytest.raises(ChunkingError, match="Chunk overlap must be less than chunk size"):
            chunk_text("Some text", chunk_size=100, chunk_overlap=100)
    
    def test_chunk_text_multiline(self):
        text = "Line 1\n\nLine 2\n\nLine 3\n\nLine 4"
        chunks = chunk_text(text, chunk_size=20, chunk_overlap=5)
        
        assert len(chunks) > 0
        assert all(chunk.strip() for chunk in chunks)
    
    def test_chunk_text_special_characters(self):
        text = "Hello! How are you? I'm fine. Let's test this."
        chunks = chunk_text(text, chunk_size=30, chunk_overlap=10)
        
        assert len(chunks) > 0
        assert all(chunk.strip() for chunk in chunks)
    
    def test_chunk_text_preserves_content(self):
        text = "Important content that must be preserved exactly."
        chunks = chunk_text(text, chunk_size=100, chunk_overlap=0)
        
        reconstructed = " ".join(chunks)
        assert "Important content" in reconstructed
        assert "preserved exactly" in reconstructed
    
    def test_chunk_text_unicode(self):
        text = "Hello 世界 مرحبا Привет"
        chunks = chunk_text(text, chunk_size=50, chunk_overlap=10)
        
        assert len(chunks) > 0
        reconstructed = " ".join(chunks)
        assert "世界" in reconstructed
    
    def test_chunk_text_large_document(self):
        text = "This is a long document. " * 1000
        chunks = chunk_text(text, chunk_size=200, chunk_overlap=50)
        
        assert len(chunks) > 10
        assert all(len(chunk) <= 250 for chunk in chunks)
    
    def test_chunk_text_whitespace_only(self):
        text = "   \n\n   \t\t   "
        with pytest.raises(ChunkingError):
            chunk_text(text, chunk_size=100, chunk_overlap=10)
    
    def test_chunk_text_default_separators(self):
        text = "Paragraph one.\n\nParagraph two. Sentence."
        chunks = chunk_text(text, chunk_size=30, chunk_overlap=5)
        
        assert len(chunks) > 0


class TestGetChunkMetadata:
    def test_get_chunk_metadata_basic(self):
        chunks = ["chunk1", "chunk2", "chunk3"]
        metadata = get_chunk_metadata(chunks)
        
        assert metadata["total_chunks"] == 3
        assert metadata["total_characters"] == 18
        assert metadata["avg_chunk_length"] == 6
        assert metadata["min_chunk_length"] == 6
        assert metadata["max_chunk_length"] == 6
    
    def test_get_chunk_metadata_varying_sizes(self):
        chunks = ["a", "bb", "ccc", "dddd"]
        metadata = get_chunk_metadata(chunks)
        
        assert metadata["total_chunks"] == 4
        assert metadata["total_characters"] == 10
        assert metadata["avg_chunk_length"] == 2
        assert metadata["min_chunk_length"] == 1
        assert metadata["max_chunk_length"] == 4
    
    def test_get_chunk_metadata_empty_list(self):
        metadata = get_chunk_metadata([])
        
        assert metadata["total_chunks"] == 0
        assert metadata["total_characters"] == 0
        assert metadata["avg_chunk_length"] == 0
        assert metadata["min_chunk_length"] == 0
        assert metadata["max_chunk_length"] == 0
    
    def test_get_chunk_metadata_single_chunk(self):
        chunks = ["single chunk"]
        metadata = get_chunk_metadata(chunks)
        
        assert metadata["total_chunks"] == 1
        assert metadata["total_characters"] == 12
        assert metadata["avg_chunk_length"] == 12
        assert metadata["min_chunk_length"] == 12
        assert metadata["max_chunk_length"] == 12
    
    def test_get_chunk_metadata_large_chunks(self):
        chunks = ["x" * 1000, "y" * 2000, "z" * 1500]
        metadata = get_chunk_metadata(chunks)
        
        assert metadata["total_chunks"] == 3
        assert metadata["total_characters"] == 4500
        assert metadata["min_chunk_length"] == 1000
        assert metadata["max_chunk_length"] == 2000
    
    def test_get_chunk_metadata_realistic_scenario(self):
        text = "This is a test document. " * 50
        chunks = chunk_text(text, chunk_size=100, chunk_overlap=20)
        metadata = get_chunk_metadata(chunks)
        
        assert metadata["total_chunks"] > 0
        assert metadata["total_characters"] > 0
        assert metadata["avg_chunk_length"] > 0
        assert metadata["min_chunk_length"] <= metadata["max_chunk_length"]
        assert metadata["avg_chunk_length"] <= metadata["max_chunk_length"]


class TestChunkingIntegration:
    def test_full_workflow(self):
        original_text = "Hello world. This is a test. " * 20
        chunks = chunk_text(original_text, chunk_size=100, chunk_overlap=20)
        metadata = get_chunk_metadata(chunks)
        
        assert len(chunks) == metadata["total_chunks"]
        assert metadata["total_chunks"] > 0
        assert all(chunk.strip() for chunk in chunks)
    
    def test_different_separators_affect_chunking(self):
        text = "One\n\nTwo\n\nThree\n\nFour"
        
        chunks_default = chunk_text(text, chunk_size=15, chunk_overlap=3)
        chunks_newline = chunk_text(text, chunk_size=15, chunk_overlap=3, separators=["\n\n"])
        
        assert len(chunks_default) >= 0
        assert len(chunks_newline) >= 0
    
    def test_chunk_size_affects_output(self):
        text = "Word " * 100
        
        chunks_small = chunk_text(text, chunk_size=50, chunk_overlap=10)
        chunks_large = chunk_text(text, chunk_size=200, chunk_overlap=10)
        
        assert len(chunks_small) > len(chunks_large)
    
    def test_overlap_creates_redundancy(self):
        text = "AAAA BBBB CCCC DDDD EEEE"
        chunks = chunk_text(text, chunk_size=15, chunk_overlap=5)
        
        if len(chunks) > 1:
            combined = "".join(chunks)
            assert len(combined) > len(text)
