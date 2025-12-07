import os
import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_api_key():
    return "test_google_api_key_12345"


@pytest.fixture
def mock_mongodb_uri():
    return "mongodb://localhost:27017/test_db"


@pytest.fixture
def mock_video_id():
    return "test_video_123"


@pytest.fixture
def sample_chunks():
    return [
        "This is the first chunk of text.",
        "This is the second chunk of text.",
        "This is the third chunk of text."
    ]


@pytest.fixture
def sample_transcript():
    return """This is a sample transcript from a YouTube video.
It contains multiple lines of text that will be processed.
The transcript should be split into manageable chunks for embedding."""


@pytest.fixture
def mock_mongodb_client():
    client = MagicMock()
    db = MagicMock()
    videos_collection = MagicMock()
    embeddings_collection = MagicMock()
    
    client.__getitem__.return_value = db
    db.__getitem__.side_effect = lambda x: embeddings_collection if "embedding" in x else videos_collection
    
    return {
        "client": client,
        "db": db,
        "videos_collection": videos_collection,
        "embeddings_collection": embeddings_collection
    }


@pytest.fixture(autouse=True)
def setup_env():
    os.environ["GOOGLE_API_KEY"] = "test_api_key"
    os.environ["MONGODB_URI"] = "mongodb://localhost:27017/test"
    yield
    os.environ.pop("GOOGLE_API_KEY", None)
    os.environ.pop("MONGODB_URI", None)
