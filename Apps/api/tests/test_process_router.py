"""
Unit tests for the process video router.

Tests cover:
- Successful video processing
- Already processed video detection
- Invalid YouTube URL handling
- Transcript fetching errors
- Chunking errors
- MongoDB storage errors
- Edge cases and error conditions
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException, status
from routers.process_router import process_video, set_mongodb_manager
from models import ProcessVideoRequest, ProcessVideoResponse
from services import TranscriptError, ChunkingError
from utils import InvalidYouTubeURLError


class TestProcessVideo:
    """Test suite for process_video endpoint."""

    @pytest.fixture
    def mock_mongodb_manager(self):
        """Create a mock MongoDB manager."""
        manager = Mock()
        manager.video_exists = Mock(return_value=False)
        manager.store_video = Mock(return_value={"chunks_count": 115})
        manager.list_videos = Mock(return_value=[])
        set_mongodb_manager(manager)
        return manager

    @pytest.fixture
    def valid_request(self):
        """Create a valid process video request."""
        return ProcessVideoRequest(
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )

    @pytest.fixture
    def valid_request_with_user(self):
        """Create a valid process video request with user_id."""
        request = ProcessVideoRequest(
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )
        request.user_id = "test_user_123"
        return request

    @pytest.mark.asyncio
    async def test_process_video_success(self, mock_mongodb_manager, valid_request):
        """Test successful video processing."""
        with patch('routers.process_router.extract_video_id') as mock_extract, \
             patch('routers.process_router.fetch_transcript') as mock_fetch, \
             patch('routers.process_router.chunk_text') as mock_chunk:
            
            # Setup mocks
            mock_extract.return_value = "dQw4w9WgXcQ"
            mock_fetch.return_value = "This is a sample transcript text for testing."
            mock_chunk.return_value = [
                "Chunk 1 text",
                "Chunk 2 text",
                "Chunk 3 text"
            ]
            
            # Execute
            response = await process_video(valid_request)
            
            # Verify
            assert isinstance(response, ProcessVideoResponse)
            assert response.video_id == "dQw4w9WgXcQ"
            assert response.status == "completed"
            assert response.chunks_count == 115
            
            # Verify function calls
            mock_extract.assert_called_once_with(valid_request.url)
            mock_fetch.assert_called_once_with("dQw4w9WgXcQ")
            mock_chunk.assert_called_once_with(
                text="This is a sample transcript text for testing.",
                chunk_size=500,
                chunk_overlap=100
            )
            mock_mongodb_manager.store_video.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_video_with_user_id(self, mock_mongodb_manager, valid_request_with_user):
        """Test video processing with user_id."""
        with patch('routers.process_router.extract_video_id') as mock_extract, \
             patch('routers.process_router.fetch_transcript') as mock_fetch, \
             patch('routers.process_router.chunk_text') as mock_chunk:
            
            mock_extract.return_value = "dQw4w9WgXcQ"
            mock_fetch.return_value = "Sample transcript"
            mock_chunk.return_value = ["Chunk 1"]
            
            response = await process_video(valid_request_with_user)
            
            # Verify user_id was passed to store_video
            call_args = mock_mongodb_manager.store_video.call_args
            assert call_args[1]['user_id'] == "test_user_123"
            assert response.status == "completed"

    @pytest.mark.asyncio
    async def test_process_video_already_processed(self, mock_mongodb_manager, valid_request):
        """Test handling of already processed video."""
        with patch('routers.process_router.extract_video_id') as mock_extract:
            
            # Setup: video already exists
            mock_extract.return_value = "dQw4w9WgXcQ"
            mock_mongodb_manager.video_exists.return_value = True
            mock_mongodb_manager.list_videos.return_value = [
                {
                    "video_id": "dQw4w9WgXcQ",
                    "chunks_count": 85,
                    "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                }
            ]
            
            # Execute
            response = await process_video(valid_request)
            
            # Verify
            assert response.video_id == "dQw4w9WgXcQ"
            assert response.status == "already_processed"
            assert response.chunks_count == 85
            
            # Should not fetch transcript or chunk
            mock_mongodb_manager.store_video.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_video_already_processed_not_found(self, mock_mongodb_manager, valid_request):
        """Test when video exists but not found in list (edge case)."""
        with patch('routers.process_router.extract_video_id') as mock_extract, \
             patch('routers.process_router.fetch_transcript') as mock_fetch, \
             patch('routers.process_router.chunk_text') as mock_chunk:
            
            # Setup: video exists but not returned in list
            mock_extract.return_value = "dQw4w9WgXcQ"
            mock_mongodb_manager.video_exists.return_value = True
            mock_mongodb_manager.list_videos.return_value = []
            
            # Should proceed with normal processing
            mock_fetch.return_value = "Transcript"
            mock_chunk.return_value = ["Chunk"]
            
            response = await process_video(valid_request)
            
            # Should process normally when video_info is None
            assert response.status == "completed"

    @pytest.mark.asyncio
    async def test_process_video_invalid_url(self, mock_mongodb_manager, valid_request):
        """Test handling of invalid YouTube URL."""
        with patch('routers.process_router.extract_video_id') as mock_extract:
            
            # Setup: invalid URL
            mock_extract.side_effect = InvalidYouTubeURLError("Invalid YouTube URL format")
            
            # Execute and verify
            with pytest.raises(HTTPException) as exc_info:
                await process_video(valid_request)
            
            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "Invalid YouTube URL format" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_process_video_transcript_error(self, mock_mongodb_manager, valid_request):
        """Test handling of transcript fetching errors."""
        with patch('routers.process_router.extract_video_id') as mock_extract, \
             patch('routers.process_router.fetch_transcript') as mock_fetch:
            
            # Setup: transcript error
            mock_extract.return_value = "dQw4w9WgXcQ"
            mock_fetch.side_effect = TranscriptError("No transcript available")
            
            # Execute and verify
            with pytest.raises(HTTPException) as exc_info:
                await process_video(valid_request)
            
            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "Transcript error" in str(exc_info.value.detail)
            assert "No transcript available" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_process_video_transcript_disabled_error(self, mock_mongodb_manager, valid_request):
        """Test handling of disabled transcript errors."""
        with patch('routers.process_router.extract_video_id') as mock_extract, \
             patch('routers.process_router.fetch_transcript') as mock_fetch:
            
            mock_extract.return_value = "dQw4w9WgXcQ"
            mock_fetch.side_effect = TranscriptError("Subtitles are disabled for this video")
            
            with pytest.raises(HTTPException) as exc_info:
                await process_video(valid_request)
            
            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "Subtitles are disabled" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_process_video_chunking_error(self, mock_mongodb_manager, valid_request):
        """Test handling of text chunking errors."""
        with patch('routers.process_router.extract_video_id') as mock_extract, \
             patch('routers.process_router.fetch_transcript') as mock_fetch, \
             patch('routers.process_router.chunk_text') as mock_chunk:
            
            # Setup: chunking error
            mock_extract.return_value = "dQw4w9WgXcQ"
            mock_fetch.return_value = "Sample transcript"
            mock_chunk.side_effect = ChunkingError("Failed to chunk text")
            
            # Execute and verify
            with pytest.raises(HTTPException) as exc_info:
                await process_video(valid_request)
            
            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Chunking error" in str(exc_info.value.detail)
            assert "Failed to chunk text" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_process_video_mongodb_error(self, mock_mongodb_manager, valid_request):
        """Test handling of MongoDB storage errors."""
        with patch('routers.process_router.extract_video_id') as mock_extract, \
             patch('routers.process_router.fetch_transcript') as mock_fetch, \
             patch('routers.process_router.chunk_text') as mock_chunk:
            
            # Setup: MongoDB error
            mock_extract.return_value = "dQw4w9WgXcQ"
            mock_fetch.return_value = "Sample transcript"
            mock_chunk.return_value = ["Chunk 1"]
            mock_mongodb_manager.store_video.side_effect = Exception("Database connection failed")
            
            # Execute and verify
            with pytest.raises(HTTPException) as exc_info:
                await process_video(valid_request)
            
            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Unexpected error" in str(exc_info.value.detail)
            assert "Database connection failed" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_process_video_empty_transcript(self, mock_mongodb_manager, valid_request):
        """Test handling of empty transcript."""
        with patch('routers.process_router.extract_video_id') as mock_extract, \
             patch('routers.process_router.fetch_transcript') as mock_fetch, \
             patch('routers.process_router.chunk_text') as mock_chunk:
            
            # Setup: empty transcript
            mock_extract.return_value = "dQw4w9WgXcQ"
            mock_fetch.return_value = ""
            mock_chunk.return_value = []
            
            # Execute
            response = await process_video(valid_request)
            
            # Should still complete successfully
            assert response.status == "completed"
            mock_chunk.assert_called_once_with(text="", chunk_size=500, chunk_overlap=100)

    @pytest.mark.asyncio
    async def test_process_video_large_transcript(self, mock_mongodb_manager, valid_request):
        """Test processing of large transcript."""
        with patch('routers.process_router.extract_video_id') as mock_extract, \
             patch('routers.process_router.fetch_transcript') as mock_fetch, \
             patch('routers.process_router.chunk_text') as mock_chunk:
            
            # Setup: large transcript
            mock_extract.return_value = "dQw4w9WgXcQ"
            large_transcript = "Sample text. " * 10000  # ~120KB transcript
            mock_fetch.return_value = large_transcript
            mock_chunk.return_value = ["Chunk"] * 500  # 500 chunks
            mock_mongodb_manager.store_video.return_value = {"chunks_count": 500}
            
            # Execute
            response = await process_video(valid_request)
            
            # Verify
            assert response.status == "completed"
            assert response.chunks_count == 500

    @pytest.mark.asyncio
    async def test_process_video_special_characters_in_url(self, mock_mongodb_manager):
        """Test processing with special characters in URL."""
        request = ProcessVideoRequest(
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=123s&list=PLtest"
        )
        
        with patch('routers.process_router.extract_video_id') as mock_extract, \
             patch('routers.process_router.fetch_transcript') as mock_fetch, \
             patch('routers.process_router.chunk_text') as mock_chunk:
            
            mock_extract.return_value = "dQw4w9WgXcQ"
            mock_fetch.return_value = "Transcript"
            mock_chunk.return_value = ["Chunk"]
            
            response = await process_video(request)
            
            assert response.video_id == "dQw4w9WgXcQ"
            assert response.status == "completed"

    @pytest.mark.asyncio
    async def test_process_video_short_url_format(self, mock_mongodb_manager):
        """Test processing with youtu.be short URL format."""
        request = ProcessVideoRequest(url="https://youtu.be/dQw4w9WgXcQ")
        
        with patch('routers.process_router.extract_video_id') as mock_extract, \
             patch('routers.process_router.fetch_transcript') as mock_fetch, \
             patch('routers.process_router.chunk_text') as mock_chunk:
            
            mock_extract.return_value = "dQw4w9WgXcQ"
            mock_fetch.return_value = "Transcript"
            mock_chunk.return_value = ["Chunk"]
            
            response = await process_video(request)
            
            assert response.status == "completed"

    @pytest.mark.asyncio
    async def test_process_video_video_exists_check_error(self, mock_mongodb_manager, valid_request):
        """Test when video_exists check raises an error."""
        with patch('routers.process_router.extract_video_id') as mock_extract:
            
            mock_extract.return_value = "dQw4w9WgXcQ"
            mock_mongodb_manager.video_exists.side_effect = Exception("MongoDB connection timeout")
            
            with pytest.raises(HTTPException) as exc_info:
                await process_video(valid_request)
            
            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Unexpected error" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_process_video_chunk_parameters(self, mock_mongodb_manager, valid_request):
        """Test that correct chunking parameters are used."""
        with patch('routers.process_router.extract_video_id') as mock_extract, \
             patch('routers.process_router.fetch_transcript') as mock_fetch, \
             patch('routers.process_router.chunk_text') as mock_chunk:
            
            mock_extract.return_value = "dQw4w9WgXcQ"
            mock_fetch.return_value = "Sample transcript"
            mock_chunk.return_value = ["Chunk"]
            
            await process_video(valid_request)
            
            # Verify chunking parameters
            mock_chunk.assert_called_once_with(
                text="Sample transcript",
                chunk_size=500,
                chunk_overlap=100
            )

    @pytest.mark.asyncio
    async def test_process_video_store_parameters(self, mock_mongodb_manager, valid_request):
        """Test that correct parameters are passed to store_video."""
        with patch('routers.process_router.extract_video_id') as mock_extract, \
             patch('routers.process_router.fetch_transcript') as mock_fetch, \
             patch('routers.process_router.chunk_text') as mock_chunk:
            
            mock_extract.return_value = "test_video_123"
            mock_fetch.return_value = "Transcript"
            mock_chunk.return_value = ["Chunk 1", "Chunk 2"]
            
            await process_video(valid_request)
            
            # Verify store_video was called with correct parameters
            call_kwargs = mock_mongodb_manager.store_video.call_args[1]
            assert call_kwargs['video_id'] == "test_video_123"
            assert call_kwargs['chunks'] == ["Chunk 1", "Chunk 2"]
            assert call_kwargs['video_url'] == valid_request.url
            assert call_kwargs['video_title'] == "Video test_video_123"
            assert call_kwargs['user_id'] is None

    @pytest.mark.asyncio
    async def test_process_video_without_user_id_attribute(self, mock_mongodb_manager):
        """Test processing when request doesn't have user_id attribute."""
        request = ProcessVideoRequest(
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )
        # Ensure no user_id attribute
        assert not hasattr(request, 'user_id')
        
        with patch('routers.process_router.extract_video_id') as mock_extract, \
             patch('routers.process_router.fetch_transcript') as mock_fetch, \
             patch('routers.process_router.chunk_text') as mock_chunk:
            
            mock_extract.return_value = "dQw4w9WgXcQ"
            mock_fetch.return_value = "Transcript"
            mock_chunk.return_value = ["Chunk"]
            
            response = await process_video(request)
            
            # Verify user_id is None
            call_kwargs = mock_mongodb_manager.store_video.call_args[1]
            assert call_kwargs['user_id'] is None
            assert response.status == "completed"

    @pytest.mark.asyncio
    async def test_set_mongodb_manager(self):
        """Test setting MongoDB manager."""
        from routers import process_router
        
        mock_manager = Mock()
        set_mongodb_manager(mock_manager)
        
        assert process_router.mongodb_manager is mock_manager

    @pytest.mark.asyncio
    async def test_process_video_response_format(self, mock_mongodb_manager, valid_request):
        """Test that response has correct format and types."""
        with patch('routers.process_router.extract_video_id') as mock_extract, \
             patch('routers.process_router.fetch_transcript') as mock_fetch, \
             patch('routers.process_router.chunk_text') as mock_chunk:
            
            mock_extract.return_value = "dQw4w9WgXcQ"
            mock_fetch.return_value = "Transcript"
            mock_chunk.return_value = ["Chunk"]
            
            response = await process_video(valid_request)
            
            # Verify response types
            assert isinstance(response.video_id, str)
            assert isinstance(response.status, str)
            assert isinstance(response.chunks_count, int)
            assert response.chunks_count >= 0

    @pytest.mark.asyncio
    async def test_process_video_concurrent_processing(self, mock_mongodb_manager):
        """Test that concurrent requests are handled independently."""
        request1 = ProcessVideoRequest(url="https://www.youtube.com/watch?v=video1")
        request2 = ProcessVideoRequest(url="https://www.youtube.com/watch?v=video2")
        
        with patch('routers.process_router.extract_video_id') as mock_extract, \
             patch('routers.process_router.fetch_transcript') as mock_fetch, \
             patch('routers.process_router.chunk_text') as mock_chunk:
            
            # Setup different responses for different videos
            mock_extract.side_effect = ["video1", "video2"]
            mock_fetch.side_effect = ["Transcript 1", "Transcript 2"]
            mock_chunk.side_effect = [["Chunk 1"], ["Chunk 2"]]
            
            # Process both requests
            response1 = await process_video(request1)
            response2 = await process_video(request2)
            
            # Verify each request was processed correctly
            assert response1.video_id == "video1"
            assert response2.video_id == "video2"
            assert mock_extract.call_count == 2
            assert mock_fetch.call_count == 2
