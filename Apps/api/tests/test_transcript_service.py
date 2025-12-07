import pytest
from unittest.mock import Mock, patch, MagicMock
from services.transcript_service import (
    fetch_transcript,
    extract_subtitle_text,
    fetch_available_transcripts,
    TranscriptError
)


class TestFetchTranscript:
    @patch('services.transcript_service.yt_dlp.YoutubeDL')
    @patch('services.transcript_service.tempfile.TemporaryDirectory')
    def test_fetch_transcript_success(self, mock_temp_dir, mock_ytdl):
        mock_temp_path = MagicMock()
        mock_temp_path.__truediv__ = lambda self, other: f"/tmp/{other}"
        mock_temp_dir.return_value.__enter__.return_value = "/tmp"
        
        mock_ytdl_instance = MagicMock()
        mock_ytdl.return_value.__enter__.return_value = mock_ytdl_instance
        
        mock_info = {
            'subtitles': {'en': [{'url': 'test'}]},
            'automatic_captions': {}
        }
        mock_ytdl_instance.extract_info.return_value = mock_info
        
        with patch('services.transcript_service.Path') as mock_path:
            mock_path.return_value.glob.return_value = [MagicMock(name='video.en.srt')]
            
            with patch('builtins.open', create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = """1
00:00:00,000 --> 00:00:02,000
Hello world

2
00:00:02,000 --> 00:00:04,000
This is a test"""
                
                result = fetch_transcript('test_video_id')
                
                assert isinstance(result, str)
                assert len(result) > 0
    
    @patch('services.transcript_service.yt_dlp.YoutubeDL')
    def test_fetch_transcript_no_video_info(self, mock_ytdl):
        mock_ytdl_instance = MagicMock()
        mock_ytdl.return_value.__enter__.return_value = mock_ytdl_instance
        mock_ytdl_instance.extract_info.return_value = None
        
        with pytest.raises(TranscriptError, match="Could not retrieve video info"):
            fetch_transcript('invalid_video')
    
    @patch('services.transcript_service.yt_dlp.YoutubeDL')
    def test_fetch_transcript_no_subtitles(self, mock_ytdl):
        mock_ytdl_instance = MagicMock()
        mock_ytdl.return_value.__enter__.return_value = mock_ytdl_instance
        
        mock_info = {
            'subtitles': {},
            'automatic_captions': {}
        }
        mock_ytdl_instance.extract_info.return_value = mock_info
        
        with pytest.raises(TranscriptError, match="No subtitles available"):
            fetch_transcript('no_subs_video')
    
    @patch('services.transcript_service.yt_dlp.YoutubeDL')
    @patch('services.transcript_service.tempfile.TemporaryDirectory')
    def test_fetch_transcript_custom_language(self, mock_temp_dir, mock_ytdl):
        mock_temp_dir.return_value.__enter__.return_value = "/tmp"
        
        mock_ytdl_instance = MagicMock()
        mock_ytdl.return_value.__enter__.return_value = mock_ytdl_instance
        
        mock_info = {
            'subtitles': {'es': [{'url': 'test'}]},
            'automatic_captions': {}
        }
        mock_ytdl_instance.extract_info.return_value = mock_info
        
        with patch('services.transcript_service.Path') as mock_path:
            mock_path.return_value.glob.return_value = [MagicMock(name='video.es.srt')]
            
            with patch('builtins.open', create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = """1
00:00:00,000 --> 00:00:02,000
Hola mundo"""
                
                result = fetch_transcript('test_video', languages=['es'])
                
                assert isinstance(result, str)
                assert len(result) > 0
    
    @patch('services.transcript_service.yt_dlp.YoutubeDL')
    def test_fetch_transcript_automatic_captions(self, mock_ytdl):
        mock_ytdl_instance = MagicMock()
        mock_ytdl.return_value.__enter__.return_value = mock_ytdl_instance
        
        mock_info = {
            'subtitles': {},
            'automatic_captions': {'en': [{'url': 'test'}]}
        }
        mock_ytdl_instance.extract_info.return_value = mock_info
        
        with patch('services.transcript_service.tempfile.TemporaryDirectory'):
            with patch('services.transcript_service.Path') as mock_path:
                mock_path.return_value.glob.return_value = [MagicMock(name='video.en.srt')]
                
                with patch('builtins.open', create=True) as mock_open:
                    mock_open.return_value.__enter__.return_value.read.return_value = "1\n00:00:00,000 --> 00:00:02,000\nAuto caption"
                    
                    result = fetch_transcript('auto_caption_video')
                    assert isinstance(result, str)
    
    @patch('services.transcript_service.yt_dlp.YoutubeDL')
    @patch('services.transcript_service.tempfile.TemporaryDirectory')
    def test_fetch_transcript_empty_result(self, mock_temp_dir, mock_ytdl):
        mock_temp_dir.return_value.__enter__.return_value = "/tmp"
        
        mock_ytdl_instance = MagicMock()
        mock_ytdl.return_value.__enter__.return_value = mock_ytdl_instance
        
        mock_info = {
            'subtitles': {'en': [{'url': 'test'}]},
            'automatic_captions': {}
        }
        mock_ytdl_instance.extract_info.return_value = mock_info
        
        with patch('services.transcript_service.Path') as mock_path:
            mock_path.return_value.glob.return_value = [MagicMock(name='video.en.srt')]
            
            with patch('builtins.open', create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = ""
                
                with pytest.raises(TranscriptError, match="Transcript is empty"):
                    fetch_transcript('empty_video')


class TestExtractSubtitleText:
    def test_extract_subtitle_text_basic(self):
        srt_content = """1
00:00:00,000 --> 00:00:02,000
Hello world

2
00:00:02,000 --> 00:00:04,000
This is a test"""
        
        result = extract_subtitle_text(srt_content)
        
        assert "Hello world" in result
        assert "This is a test" in result
        assert "-->" not in result
        assert "00:00" not in result
    
    def test_extract_subtitle_text_removes_timestamps(self):
        srt_content = """1
00:00:00,000 --> 00:00:05,000
First line

2
00:00:05,000 --> 00:00:10,000
Second line"""
        
        result = extract_subtitle_text(srt_content)
        
        assert "00:00:00" not in result
        assert "00:00:05" not in result
        assert "-->" not in result
    
    def test_extract_subtitle_text_removes_counters(self):
        srt_content = """1
00:00:00,000 --> 00:00:02,000
Line one

2
00:00:02,000 --> 00:00:04,000
Line two"""
        
        result = extract_subtitle_text(srt_content)
        
        assert result.strip().startswith("Line")
        assert "Line one" in result
    
    def test_extract_subtitle_text_removes_html_tags(self):
        srt_content = """1
00:00:00,000 --> 00:00:02,000
<i>Italic text</i>

2
00:00:02,000 --> 00:00:04,000
<b>Bold text</b>"""
        
        result = extract_subtitle_text(srt_content)
        
        assert "<i>" not in result
        assert "</i>" not in result
        assert "Italic text" in result
        assert "Bold text" in result
    
    def test_extract_subtitle_text_multiple_spaces(self):
        srt_content = """1
00:00:00,000 --> 00:00:02,000
Text   with    multiple     spaces"""
        
        result = extract_subtitle_text(srt_content)
        
        assert "Text with multiple spaces" in result
        assert "   " not in result
    
    def test_extract_subtitle_text_empty_lines(self):
        srt_content = """1
00:00:00,000 --> 00:00:02,000
First line


2
00:00:02,000 --> 00:00:04,000
Second line"""
        
        result = extract_subtitle_text(srt_content)
        
        assert "First line" in result
        assert "Second line" in result
    
    def test_extract_subtitle_text_unicode(self):
        srt_content = """1
00:00:00,000 --> 00:00:02,000
Hello 世界

2
00:00:02,000 --> 00:00:04,000
مرحبا العالم"""
        
        result = extract_subtitle_text(srt_content)
        
        assert "世界" in result
        assert "مرحبا" in result
    
    def test_extract_subtitle_text_special_characters(self):
        srt_content = """1
00:00:00,000 --> 00:00:02,000
Question? Answer!

2
00:00:02,000 --> 00:00:04,000
Email: test@example.com"""
        
        result = extract_subtitle_text(srt_content)
        
        assert "Question?" in result
        assert "Answer!" in result
        assert "test@example.com" in result
    
    def test_extract_subtitle_text_empty_content(self):
        result = extract_subtitle_text("")
        assert result == ""


class TestFetchAvailableTranscripts:
    @patch('services.transcript_service.yt_dlp.YoutubeDL')
    def test_fetch_available_transcripts_manual_only(self, mock_ytdl):
        mock_ytdl_instance = MagicMock()
        mock_ytdl.return_value.__enter__.return_value = mock_ytdl_instance
        
        mock_info = {
            'subtitles': {
                'en': [{'url': 'test'}],
                'es': [{'url': 'test'}]
            },
            'automatic_captions': {}
        }
        mock_ytdl_instance.extract_info.return_value = mock_info
        
        result = fetch_available_transcripts('test_video')
        
        assert len(result) == 2
        assert any(t['language_code'] == 'en' for t in result)
        assert any(t['language_code'] == 'es' for t in result)
        assert all(not t['is_generated'] for t in result)
    
    @patch('services.transcript_service.yt_dlp.YoutubeDL')
    def test_fetch_available_transcripts_auto_only(self, mock_ytdl):
        mock_ytdl_instance = MagicMock()
        mock_ytdl.return_value.__enter__.return_value = mock_ytdl_instance
        
        mock_info = {
            'subtitles': {},
            'automatic_captions': {
                'en': [{'url': 'test'}],
                'fr': [{'url': 'test'}]
            }
        }
        mock_ytdl_instance.extract_info.return_value = mock_info
        
        result = fetch_available_transcripts('test_video')
        
        assert len(result) == 2
        assert all(t['is_generated'] for t in result)
        assert all(t['is_translatable'] for t in result)
    
    @patch('services.transcript_service.yt_dlp.YoutubeDL')
    def test_fetch_available_transcripts_mixed(self, mock_ytdl):
        mock_ytdl_instance = MagicMock()
        mock_ytdl.return_value.__enter__.return_value = mock_ytdl_instance
        
        mock_info = {
            'subtitles': {
                'en': [{'url': 'test'}]
            },
            'automatic_captions': {
                'es': [{'url': 'test'}],
                'fr': [{'url': 'test'}]
            }
        }
        mock_ytdl_instance.extract_info.return_value = mock_info
        
        result = fetch_available_transcripts('test_video')
        
        assert len(result) == 3
        en_transcript = next(t for t in result if t['language_code'] == 'en')
        assert not en_transcript['is_generated']
        
        es_transcript = next(t for t in result if t['language_code'] == 'es')
        assert es_transcript['is_generated']
    
    @patch('services.transcript_service.yt_dlp.YoutubeDL')
    def test_fetch_available_transcripts_no_duplicates(self, mock_ytdl):
        mock_ytdl_instance = MagicMock()
        mock_ytdl.return_value.__enter__.return_value = mock_ytdl_instance
        
        mock_info = {
            'subtitles': {
                'en': [{'url': 'test'}]
            },
            'automatic_captions': {
                'en': [{'url': 'test'}]
            }
        }
        mock_ytdl_instance.extract_info.return_value = mock_info
        
        result = fetch_available_transcripts('test_video')
        
        en_transcripts = [t for t in result if t['language_code'] == 'en']
        assert len(en_transcripts) == 1
    
    @patch('services.transcript_service.yt_dlp.YoutubeDL')
    def test_fetch_available_transcripts_no_info(self, mock_ytdl):
        mock_ytdl_instance = MagicMock()
        mock_ytdl.return_value.__enter__.return_value = mock_ytdl_instance
        mock_ytdl_instance.extract_info.return_value = None
        
        with pytest.raises(TranscriptError, match="Could not retrieve video info"):
            fetch_available_transcripts('invalid_video')
    
    @patch('services.transcript_service.yt_dlp.YoutubeDL')
    def test_fetch_available_transcripts_empty(self, mock_ytdl):
        mock_ytdl_instance = MagicMock()
        mock_ytdl.return_value.__enter__.return_value = mock_ytdl_instance
        
        mock_info = {
            'subtitles': {},
            'automatic_captions': {}
        }
        mock_ytdl_instance.extract_info.return_value = mock_info
        
        result = fetch_available_transcripts('test_video')
        
        assert result == []
    
    @patch('services.transcript_service.yt_dlp.YoutubeDL')
    def test_fetch_available_transcripts_exception_handling(self, mock_ytdl):
        mock_ytdl.return_value.__enter__.side_effect = Exception("Network error")
        
        with pytest.raises(TranscriptError, match="Failed to list available transcripts"):
            fetch_available_transcripts('test_video')


class TestTranscriptIntegration:
    def test_extract_and_clean_workflow(self):
        srt = """1
00:00:00,000 --> 00:00:02,000
<i>First subtitle</i>

2
00:00:02,000 --> 00:00:04,000
Second  subtitle"""
        
        result = extract_subtitle_text(srt)
        
        assert "First subtitle" in result
        assert "Second subtitle" in result
        assert "<i>" not in result
        assert "-->" not in result
