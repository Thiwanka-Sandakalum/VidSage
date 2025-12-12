"""Transcript Worker - Queue-only service for downloading YouTube transcripts."""
import os
import sys
import traceback
import logging
import re
import requests
import yt_dlp

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable
)

# Allow importing shared utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.rabbitmq_utils import consume_events, publish_event, close_connection
from shared.utils import extract_video_id, InvalidYouTubeURLError

# Logging setup
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("transcript-worker")


# ---------------------------------------------------------------------
# CLEAN BROWSER HEADERS (fixes “Google Sorry… automated queries” issue)
# ---------------------------------------------------------------------
HEADERS = {
    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/118.0.5993.70 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


def download_transcript_direct(video_url: str, video_id: str):
    """Download transcript using yt-dlp first, then fallback."""
    logger.debug(f"📥 Starting transcript download for video: {video_id}")

    try:
        logger.debug("🔄 Trying yt-dlp subtitle extraction...")

        # What languages to look for
        langs = ["en", "en-US", "en-GB"]

        ydl_opts = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": langs,
            "quiet": True,
            "no_warnings": True,
            "subtitlesformat": "srt",
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

        title = info.get("title") or f"Video {video_id}"
        manual = info.get("subtitles", {})
        auto = info.get("automatic_captions", {})

        subtitle_url = None

        # Prefer manual
        for lang in langs:
            if lang in manual and manual[lang]:
                subtitle_url = manual[lang][0]["url"]
                break

        # Fallback to auto captions
        if not subtitle_url:
            for lang in langs:
                if lang in auto and auto[lang]:
                    subtitle_url = auto[lang][0]["url"]
                    break

        if not subtitle_url:
            logger.info("⚠ No subtitles available using yt-dlp")
            raise Exception("No subtitles via yt-dlp")

        # ------------------------------------------------------
        # FIX: requests.get() MUST include real browser headers
        # ------------------------------------------------------
        r = requests.get(subtitle_url, headers=HEADERS)
        if "GoogleSorry" in r.text or "automated queries" in r.text:
            raise Exception("Google blocked subtitle download")

        srt_text = clean_srt_text(r.text)

        return {
            "video_id": video_id,
            "transcript": srt_text,
            "metadata": {
                "video_id": video_id,
                "video_url": f"https://www.youtube.com/watch?v={video_id}",
                "method": "yt-dlp",
                "transcript_length": len(srt_text),
                "title": title,
            },
        }

    except Exception as e:
        logger.warning(f"⚠ yt-dlp failed: {e}")

    # ---------------------------------------------------------------------
    # FALLBACK: YOUTUBE TRANSCRIPT API
    # ---------------------------------------------------------------------
    try:
        logger.debug("🔄 Trying fallback: YouTubeTranscriptApi")
        transcript_raw = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([entry["text"] for entry in transcript_raw])

        return {
            "video_id": video_id,
            "transcript": text,
            "metadata": {
                "video_id": video_id,
                "video_url": f"https://www.youtube.com/watch?v={video_id}",
                "method": "youtube-transcript-api",
                "transcript_length": len(text),
                "title": f"Video {video_id}",
            },
        }

    except Exception as e:
        raise Exception(f"Transcript download failed: {str(e)}")


# ---------------------------------------------------------------------
# CLEAN SRT SANITIZER
# ---------------------------------------------------------------------
def clean_srt_text(srt: str) -> str:
    lines = srt.split("\n")
    clean = []
    for line in lines:
        line = line.strip()

        if line.isdigit():
            continue
        if "-->" in line:
            continue

        if line:
            clean.append(line)

    text = " ".join(clean)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ---------------------------------------------------------------------
# EVENT HANDLER
# ---------------------------------------------------------------------
def handle_video_submitted(event_type: str, payload: dict):
    job_id = payload.get("job_id")
    video_url = payload.get("video_url")
    video_id = payload.get("video_id")

    logger.info(f"📥 Handling transcript job {job_id} ({video_id})")

    try:
        if not video_id:
            video_id = extract_video_id(video_url)
            logger.debug(f"Extracted video_id: {video_id}")

        result = download_transcript_direct(video_url, video_id)

        publish_event(
            "transcript.downloaded",
            {
                "job_id": job_id,
                "video_id": video_id,
                "transcript": result["transcript"],
                "metadata": result["metadata"],
            },
        )

        logger.info(f"✅ Transcript delivered for job {job_id}")

    except Exception as e:
        logger.error(f"❌ Transcript processing failed: {e}")
        publish_event(
            "processing.failed",
            {
                "job_id": job_id,
                "service": "transcript-worker",
                "error": str(e),
                "step": "transcript_download",
            }
        )
        raise


# ---------------------------------------------------------------------
# RUN LOOP
# ---------------------------------------------------------------------
def run_loop():
    logger.info("🚀 Transcript worker started")
    try:
        consume_events(
            event_types=["video.submitted"],
            callback=handle_video_submitted,
            queue_name="transcript_queue",
        )
    except KeyboardInterrupt:
        logger.info("🛑 Transcript worker stopping...")
    finally:
        close_connection()


if __name__ == "__main__":
    run_loop()
