"""
Test user-based video isolation and save video feature.
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Example JWTs for two users (replace with real test tokens)
USER1_TOKEN = "Bearer testtoken_user1"
USER2_TOKEN = "Bearer testtoken_user2"

VIDEO_ID = "dQw4w9WgXcQ"

@pytest.fixture
def user1_headers():
    return {"Authorization": USER1_TOKEN}

@pytest.fixture
def user2_headers():
    return {"Authorization": USER2_TOKEN}

def test_process_and_list_videos_user_isolation(user1_headers, user2_headers):
    # User1 processes a video
    resp = client.post("/process", json={"url": f"https://youtube.com/watch?v={VIDEO_ID}"}, headers=user1_headers)
    assert resp.status_code == 200
    # User1 should see the video
    resp = client.get("/videos", headers=user1_headers)
    assert resp.status_code == 200
    assert any(v["video_id"] == VIDEO_ID for v in resp.json()["videos"])
    # User2 should NOT see the video
    resp = client.get("/videos", headers=user2_headers)
    assert resp.status_code == 200
    assert all(v["video_id"] != VIDEO_ID for v in resp.json()["videos"])

def test_save_video_for_another_user(user1_headers, user2_headers):
    # User2 saves the video processed by User1
    resp = client.post("/videos/save", json={"video_id": VIDEO_ID}, headers=user2_headers)
    assert resp.status_code == 200
    # Now User2 should see the video
    resp = client.get("/videos", headers=user2_headers)
    assert resp.status_code == 200
    assert any(v["video_id"] == VIDEO_ID for v in resp.json()["videos"])
