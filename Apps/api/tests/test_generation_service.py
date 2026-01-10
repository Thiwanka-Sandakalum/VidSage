import pytest
from unittest.mock import Mock, patch, MagicMock
from services.generation_service import (
    GenerationService,
    get_generation_service
)


class TestGenerationService:
    @patch('services.generation_service.ChatGoogleGenerativeAI')
    @patch('services.generation_service.config')
    def test_init_success(self, mock_config, mock_llm_class):
        mock_config.LLM_MODEL = "gemini-pro"
        mock_config.GOOGLE_API_KEY = "test_key"
        mock_config.LLM_TEMPERATURE = 0.3
        mock_config.LLM_MAX_OUTPUT_TOKENS = 1024
        mock_config.MAX_CONTEXT_CHUNKS = 5
        
        mock_llm_instance = MagicMock()
        mock_llm_class.return_value = mock_llm_instance
        
        service = GenerationService()
        
        assert service.llm is not None
        assert service.prompt_template is not None
        assert service.chain is not None
    
    @patch('services.generation_service.ChatGoogleGenerativeAI')
    @patch('services.generation_service.config')
    def test_initialize_llm_success(self, mock_config, mock_llm_class):
        mock_config.LLM_MODEL = "gemini-pro"
        mock_config.GOOGLE_API_KEY = "test_key"
        mock_config.LLM_TEMPERATURE = 0.3
        mock_config.LLM_MAX_OUTPUT_TOKENS = 1024
        mock_config.MAX_CONTEXT_CHUNKS = 5
        
        mock_llm_instance = MagicMock()
        mock_llm_class.return_value = mock_llm_instance
        
        service = GenerationService()
        llm = service._initialize_llm()
        
        assert llm is not None
    
    @patch('services.generation_service.ChatGoogleGenerativeAI')
    @patch('services.generation_service.config')
    def test_initialize_llm_failure(self, mock_config, mock_llm_class):
        mock_config.LLM_MODEL = "gemini-pro"
        mock_config.GOOGLE_API_KEY = "test_key"
        mock_config.LLM_TEMPERATURE = 0.3
        mock_config.LLM_MAX_OUTPUT_TOKENS = 1024
        
        mock_llm_class.side_effect = Exception("API Error")
        
        with pytest.raises(Exception):
            GenerationService()
    
    @patch('services.generation_service.ChatGoogleGenerativeAI')
    @patch('services.generation_service.config')
    def test_create_prompt_template(self, mock_config, mock_llm_class):
        mock_config.LLM_MODEL = "gemini-pro"
        mock_config.GOOGLE_API_KEY = "test_key"
        mock_config.LLM_TEMPERATURE = 0.3
        mock_config.LLM_MAX_OUTPUT_TOKENS = 1024
        mock_config.MAX_CONTEXT_CHUNKS = 5
        
        service = GenerationService()
        template = service._create_prompt_template()
        
        assert template is not None
        assert len(template.messages) == 2
    
    @patch('services.generation_service.ChatGoogleGenerativeAI')
    @patch('services.generation_service.config')
    def test_format_context_basic(self, mock_config, mock_llm_class):
        mock_config.LLM_MODEL = "gemini-pro"
        mock_config.GOOGLE_API_KEY = "test_key"
        mock_config.LLM_TEMPERATURE = 0.3
        mock_config.LLM_MAX_OUTPUT_TOKENS = 1024
        mock_config.MAX_CONTEXT_CHUNKS = 5
        
        service = GenerationService()
        
        chunks = [
            {"text": "First chunk", "chunk_id": "chunk_1", "score": 0.95},
            {"text": "Second chunk", "chunk_id": "chunk_2", "score": 0.88}
        ]
        
        context = service._format_context(chunks)
        
        assert "First chunk" in context
        assert "Second chunk" in context
        assert "[Segment 1]" in context
        assert "[Segment 2]" in context
    
    @patch('services.generation_service.ChatGoogleGenerativeAI')
    @patch('services.generation_service.config')
    def test_format_context_empty(self, mock_config, mock_llm_class):
        mock_config.LLM_MODEL = "gemini-pro"
        mock_config.GOOGLE_API_KEY = "test_key"
        mock_config.LLM_TEMPERATURE = 0.3
        mock_config.LLM_MAX_OUTPUT_TOKENS = 1024
        mock_config.MAX_CONTEXT_CHUNKS = 5
        
        service = GenerationService()
        
        context = service._format_context([])
        
        assert "No relevant information" in context
    
    @patch('services.generation_service.ChatGoogleGenerativeAI')
    @patch('services.generation_service.config')
    def test_format_context_max_chunks(self, mock_config, mock_llm_class):
        mock_config.LLM_MODEL = "gemini-pro"
        mock_config.GOOGLE_API_KEY = "test_key"
        mock_config.LLM_TEMPERATURE = 0.3
        mock_config.LLM_MAX_OUTPUT_TOKENS = 1024
        mock_config.MAX_CONTEXT_CHUNKS = 2
        
        service = GenerationService()
        
        chunks = [
            {"text": f"Chunk {i}", "chunk_id": f"chunk_{i}", "score": 0.9 - i*0.1}
            for i in range(5)
        ]
        
        context = service._format_context(chunks)
        
        assert "[Segment 1]" in context
        assert "[Segment 2]" in context
        assert "[Segment 3]" not in context
    
    @patch('services.generation_service.ChatGoogleGenerativeAI')
    @patch('services.generation_service.config')
    def test_format_context_includes_score(self, mock_config, mock_llm_class):
        mock_config.LLM_MODEL = "gemini-pro"
        mock_config.GOOGLE_API_KEY = "test_key"
        mock_config.LLM_TEMPERATURE = 0.3
        mock_config.LLM_MAX_OUTPUT_TOKENS = 1024
        mock_config.MAX_CONTEXT_CHUNKS = 5
        
        service = GenerationService()
        
        chunks = [{"text": "Test", "chunk_id": "1", "score": 0.85}]
        context = service._format_context(chunks)
        
        assert "0.85" in context
    
    @patch('services.generation_service.ChatGoogleGenerativeAI')
    @patch('services.generation_service.config')
    def test_generate_answer_success(self, mock_config, mock_llm_class):
        mock_config.LLM_MODEL = "gemini-pro"
        mock_config.GOOGLE_API_KEY = "test_key"
        mock_config.LLM_TEMPERATURE = 0.3
        mock_config.LLM_MAX_OUTPUT_TOKENS = 1024
        mock_config.MAX_CONTEXT_CHUNKS = 5
        
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "Generated answer"
        
        service = GenerationService()
        service.chain = mock_chain
        
        chunks = [{"text": "Context", "chunk_id": "1", "score": 0.9}]
        answer = service.generate_answer("What is this?", chunks, "Test Video")
        
        assert answer == "Generated answer"
        assert mock_chain.invoke.called
    
    @patch('services.generation_service.ChatGoogleGenerativeAI')
    @patch('services.generation_service.config')
    def test_generate_answer_no_video_title(self, mock_config, mock_llm_class):
        mock_config.LLM_MODEL = "gemini-pro"
        mock_config.GOOGLE_API_KEY = "test_key"
        mock_config.LLM_TEMPERATURE = 0.3
        mock_config.LLM_MAX_OUTPUT_TOKENS = 1024
        mock_config.MAX_CONTEXT_CHUNKS = 5
        
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "Answer"
        
        service = GenerationService()
        service.chain = mock_chain
        
        chunks = [{"text": "Context", "chunk_id": "1", "score": 0.9}]
        answer = service.generate_answer("Question", chunks)
        
        assert answer == "Answer"
    
    @patch('services.generation_service.ChatGoogleGenerativeAI')
    @patch('services.generation_service.config')
    def test_generate_answer_failure(self, mock_config, mock_llm_class):
        mock_config.LLM_MODEL = "gemini-pro"
        mock_config.GOOGLE_API_KEY = "test_key"
        mock_config.LLM_TEMPERATURE = 0.3
        mock_config.LLM_MAX_OUTPUT_TOKENS = 1024
        mock_config.MAX_CONTEXT_CHUNKS = 5
        
        mock_chain = MagicMock()
        mock_chain.invoke.side_effect = Exception("LLM Error")
        
        service = GenerationService()
        service.chain = mock_chain
        
        chunks = [{"text": "Context", "chunk_id": "1", "score": 0.9}]
        
        with pytest.raises(RuntimeError, match="Failed to generate answer"):
            service.generate_answer("Question", chunks)
    
    @patch('services.generation_service.ChatGoogleGenerativeAI')
    @patch('services.generation_service.config')
    def test_prepare_sources_basic(self, mock_config, mock_llm_class):
        mock_config.LLM_MODEL = "gemini-pro"
        mock_config.GOOGLE_API_KEY = "test_key"
        mock_config.LLM_TEMPERATURE = 0.3
        mock_config.LLM_MAX_OUTPUT_TOKENS = 1024
        mock_config.MAX_CONTEXT_CHUNKS = 5
        
        service = GenerationService()
        
        chunks = [
            {"text": "Short text", "chunk_id": "1", "score": 0.95},
            {"text": "Another short text", "chunk_id": "2", "score": 0.88}
        ]
        
        sources = service.prepare_sources(chunks)
        
        assert len(sources) == 2
        assert sources[0]["chunk_id"] == "1"
        assert sources[0]["relevance_score"] == 0.95
        assert "Short text" in sources[0]["text_preview"]
    
    @patch('services.generation_service.ChatGoogleGenerativeAI')
    @patch('services.generation_service.config')
    def test_prepare_sources_long_text(self, mock_config, mock_llm_class):
        mock_config.LLM_MODEL = "gemini-pro"
        mock_config.GOOGLE_API_KEY = "test_key"
        mock_config.LLM_TEMPERATURE = 0.3
        mock_config.LLM_MAX_OUTPUT_TOKENS = 1024
        mock_config.MAX_CONTEXT_CHUNKS = 5
        
        service = GenerationService()
        
        long_text = "A" * 150
        chunks = [{"text": long_text, "chunk_id": "1", "score": 0.9}]
        
        sources = service.prepare_sources(chunks)
        
        assert len(sources[0]["text_preview"]) == 103
        assert sources[0]["text_preview"].endswith("...")
    
    @patch('services.generation_service.ChatGoogleGenerativeAI')
    @patch('services.generation_service.config')
    def test_prepare_sources_max_chunks(self, mock_config, mock_llm_class):
        mock_config.LLM_MODEL = "gemini-pro"
        mock_config.GOOGLE_API_KEY = "test_key"
        mock_config.LLM_TEMPERATURE = 0.3
        mock_config.LLM_MAX_OUTPUT_TOKENS = 1024
        mock_config.MAX_CONTEXT_CHUNKS = 2
        
        service = GenerationService()
        
        chunks = [
            {"text": f"Text {i}", "chunk_id": str(i), "score": 0.9 - i*0.1}
            for i in range(5)
        ]
        
        sources = service.prepare_sources(chunks)
        
        assert len(sources) == 2
    
    @patch('services.generation_service.ChatGoogleGenerativeAI')
    @patch('services.generation_service.config')
    def test_prepare_sources_rounds_score(self, mock_config, mock_llm_class):
        mock_config.LLM_MODEL = "gemini-pro"
        mock_config.GOOGLE_API_KEY = "test_key"
        mock_config.LLM_TEMPERATURE = 0.3
        mock_config.LLM_MAX_OUTPUT_TOKENS = 1024
        mock_config.MAX_CONTEXT_CHUNKS = 5
        
        service = GenerationService()
        
        chunks = [{"text": "Test", "chunk_id": "1", "score": 0.123456789}]
        sources = service.prepare_sources(chunks)
        
        assert sources[0]["relevance_score"] == 0.1235


class TestGetGenerationService:
    @patch('services.generation_service.ChatGoogleGenerativeAI')
    @patch('services.generation_service.config')
    def test_get_generation_service_creates_singleton(self, mock_config, mock_llm_class):
        mock_config.LLM_MODEL = "gemini-pro"
        mock_config.GOOGLE_API_KEY = "test_key"
        mock_config.LLM_TEMPERATURE = 0.3
        mock_config.LLM_MAX_OUTPUT_TOKENS = 1024
        mock_config.MAX_CONTEXT_CHUNKS = 5
        
        import services.generation_service
        services.generation_service._generation_service = None
        
        service1 = get_generation_service()
        service2 = get_generation_service()
        
        assert service1 is service2
    
    @patch('services.generation_service.ChatGoogleGenerativeAI')
    @patch('services.generation_service.config')
    def test_get_generation_service_returns_instance(self, mock_config, mock_llm_class):
        mock_config.LLM_MODEL = "gemini-pro"
        mock_config.GOOGLE_API_KEY = "test_key"
        mock_config.LLM_TEMPERATURE = 0.3
        mock_config.LLM_MAX_OUTPUT_TOKENS = 1024
        mock_config.MAX_CONTEXT_CHUNKS = 5
        
        import services.generation_service
        services.generation_service._generation_service = None
        
        service = get_generation_service()
        
        assert isinstance(service, GenerationService)


class TestGenerationIntegration:
    @patch('services.generation_service.ChatGoogleGenerativeAI')
    @patch('services.generation_service.config')
    def test_full_generation_workflow(self, mock_config, mock_llm_class):
        mock_config.LLM_MODEL = "gemini-pro"
        mock_config.GOOGLE_API_KEY = "test_key"
        mock_config.LLM_TEMPERATURE = 0.3
        mock_config.LLM_MAX_OUTPUT_TOKENS = 1024
        mock_config.MAX_CONTEXT_CHUNKS = 5
        
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "Complete answer based on context"
        
        service = GenerationService()
        service.chain = mock_chain
        
        chunks = [
            {"text": "Context chunk 1", "chunk_id": "1", "score": 0.95},
            {"text": "Context chunk 2", "chunk_id": "2", "score": 0.88}
        ]
        
        answer = service.generate_answer(
            "What is the video about?",
            chunks,
            "Test Video Title"
        )
        
        sources = service.prepare_sources(chunks)
        
        assert answer == "Complete answer based on context"
        assert len(sources) == 2
        assert sources[0]["chunk_id"] == "1"
    
    @patch('services.generation_service.ChatGoogleGenerativeAI')
    @patch('services.generation_service.config')
    def test_context_formatting_and_generation(self, mock_config, mock_llm_class):
        mock_config.LLM_MODEL = "gemini-pro"
        mock_config.GOOGLE_API_KEY = "test_key"
        mock_config.LLM_TEMPERATURE = 0.3
        mock_config.LLM_MAX_OUTPUT_TOKENS = 1024
        mock_config.MAX_CONTEXT_CHUNKS = 3
        
        service = GenerationService()
        
        chunks = [
            {"text": "Important information", "chunk_id": "1", "score": 0.95},
            {"text": "Additional details", "chunk_id": "2", "score": 0.85},
            {"text": "More context", "chunk_id": "3", "score": 0.75}
        ]
        
        context = service._format_context(chunks)
        
        assert "Important information" in context
        assert "Additional details" in context
        assert "More context" in context
        assert context.count("[Segment") == 3
