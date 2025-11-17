"""Unit tests for Prompt Generator Service"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from services import PromptGeneratorService


class TestPromptGeneratorServiceInitialization:
    """Test PromptGeneratorService initialization"""

    def test_initialization_with_api_key(self):
        """Service initializes with provided API key"""
        service = PromptGeneratorService(api_key="test-key-123")
        assert service.api_key == "test-key-123"
        assert service.model == "gpt-4"

    def test_initialization_with_env_var(self, monkeypatch):
        """Service initializes with API key from environment"""
        monkeypatch.setenv("OPENAI_API_KEY", "env-key-456")
        service = PromptGeneratorService()
        assert service.api_key == "env-key-456"

    def test_initialization_without_api_key_raises_error(self, monkeypatch):
        """Service raises error if no API key provided"""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        with pytest.raises(ValueError, match="API key required"):
            PromptGeneratorService()

    def test_initialization_with_custom_model(self):
        """Service can be initialized with custom model"""
        service = PromptGeneratorService(api_key="test-key", model="gpt-3.5-turbo")
        assert service.model == "gpt-3.5-turbo"

    def test_initialization_with_base_url(self):
        """Service can be initialized with custom base URL"""
        service = PromptGeneratorService(
            api_key="test-key",
            base_url="https://custom-api.example.com"
        )
        assert service.api_key == "test-key"


class TestMusicPromptGeneration:
    """Test music prompt generation"""

    @pytest.fixture
    def service(self):
        """Create PromptGeneratorService instance"""
        return PromptGeneratorService(api_key="test-key")

    @pytest.fixture
    def mock_music_prompts(self):
        """Sample 20 music prompts"""
        return [
            f"Track {i}: Unique musical composition with varied instruments, tempo, and mood"
            for i in range(1, 21)
        ]

    def test_generate_music_prompts_success(self, service, mock_music_prompts):
        """generate_music_prompts returns 20 unique prompts"""
        # Mock OpenAI client response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(mock_music_prompts)

        with patch.object(service.client.chat.completions, 'create', return_value=mock_response):
            result = service.generate_music_prompts(
                niche_label="Lo-fi Study Beats",
                mood_keywords=["calm", "focused", "relaxing"],
                target_duration_minutes=70
            )

        assert len(result) == 20
        assert all(isinstance(prompt, str) for prompt in result)

    def test_generate_music_prompts_with_markdown_response(self, service, mock_music_prompts):
        """generate_music_prompts handles markdown code blocks in response"""
        # Mock response with markdown code blocks
        mock_response = Mock()
        mock_response.choices = [Mock()]
        markdown_content = f"```json\n{json.dumps(mock_music_prompts)}\n```"
        mock_response.choices[0].message.content = markdown_content

        with patch.object(service.client.chat.completions, 'create', return_value=mock_response):
            result = service.generate_music_prompts(
                niche_label="Classical Piano",
                mood_keywords=["elegant", "peaceful"],
                target_duration_minutes=70
            )

        assert len(result) == 20

    def test_generate_music_prompts_invalid_json_raises_error(self, service):
        """generate_music_prompts raises error for invalid JSON"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This is not valid JSON"

        with patch.object(service.client.chat.completions, 'create', return_value=mock_response):
            with pytest.raises(RuntimeError, match="Failed to parse LLM response as JSON"):
                service.generate_music_prompts(
                    niche_label="Test",
                    mood_keywords=["test"],
                    target_duration_minutes=70
                )

    def test_generate_music_prompts_wrong_count_raises_error(self, service):
        """generate_music_prompts raises error if not 20 prompts"""
        wrong_count_prompts = ["Track 1", "Track 2", "Track 3"]  # Only 3 prompts

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(wrong_count_prompts)

        with patch.object(service.client.chat.completions, 'create', return_value=mock_response):
            with pytest.raises(RuntimeError, match="Expected 20 prompts, got 3"):
                service.generate_music_prompts(
                    niche_label="Test",
                    mood_keywords=["test"],
                    target_duration_minutes=70
                )

    def test_generate_music_prompts_api_error_raises_error(self, service):
        """generate_music_prompts raises error if API call fails"""
        with patch.object(service.client.chat.completions, 'create', side_effect=Exception("API Error")):
            with pytest.raises(RuntimeError, match="LLM API call failed"):
                service.generate_music_prompts(
                    niche_label="Test",
                    mood_keywords=["test"],
                    target_duration_minutes=70
                )


class TestVisualPromptGeneration:
    """Test visual prompt generation"""

    @pytest.fixture
    def service(self):
        return PromptGeneratorService(api_key="test-key")

    @pytest.fixture
    def mock_music_prompts(self):
        return [f"Music track {i}" for i in range(1, 21)]

    @pytest.fixture
    def mock_visual_prompts(self):
        return [
            f"Visual {i}: Unique 16:9 scene with varied composition, lighting, and atmosphere"
            for i in range(1, 21)
        ]

    def test_generate_visual_prompts_success(
        self, service, mock_music_prompts, mock_visual_prompts
    ):
        """generate_visual_prompts returns 20 unique prompts"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(mock_visual_prompts)

        with patch.object(service.client.chat.completions, 'create', return_value=mock_response):
            result = service.generate_visual_prompts(
                niche_label="Nature Soundscapes",
                mood_keywords=["peaceful", "natural"],
                music_prompts=mock_music_prompts
            )

        assert len(result) == 20
        assert all(isinstance(prompt, str) for prompt in result)

    def test_generate_visual_prompts_handles_markdown(
        self, service, mock_music_prompts, mock_visual_prompts
    ):
        """generate_visual_prompts handles markdown code blocks"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        markdown_content = f"```json\n{json.dumps(mock_visual_prompts)}\n```"
        mock_response.choices[0].message.content = markdown_content

        with patch.object(service.client.chat.completions, 'create', return_value=mock_response):
            result = service.generate_visual_prompts(
                niche_label="Test",
                mood_keywords=["test"],
                music_prompts=mock_music_prompts
            )

        assert len(result) == 20

    def test_generate_visual_prompts_wrong_count_raises_error(
        self, service, mock_music_prompts
    ):
        """generate_visual_prompts raises error if not 20 prompts"""
        wrong_count = ["Visual 1", "Visual 2"]

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(wrong_count)

        with patch.object(service.client.chat.completions, 'create', return_value=mock_response):
            with pytest.raises(RuntimeError, match="Expected 20 prompts, got 2"):
                service.generate_visual_prompts(
                    niche_label="Test",
                    mood_keywords=["test"],
                    music_prompts=mock_music_prompts
                )


class TestFullPromptGeneration:
    """Test full prompt generation (music + visuals)"""

    @pytest.fixture
    def service(self):
        return PromptGeneratorService(api_key="test-key")

    @pytest.fixture
    def mock_music_prompts(self):
        return [f"Music track {i}" for i in range(1, 21)]

    @pytest.fixture
    def mock_visual_prompts(self):
        return [f"Visual {i}" for i in range(1, 21)]

    def test_generate_prompts_success(
        self, service, mock_music_prompts, mock_visual_prompts
    ):
        """generate_prompts returns both music and visual prompts"""
        music_response = Mock()
        music_response.choices = [Mock()]
        music_response.choices[0].message.content = json.dumps(mock_music_prompts)

        visual_response = Mock()
        visual_response.choices = [Mock()]
        visual_response.choices[0].message.content = json.dumps(mock_visual_prompts)

        # Mock to return different responses for different calls
        with patch.object(
            service.client.chat.completions, 'create',
            side_effect=[music_response, visual_response]
        ):
            result = service.generate_prompts(
                niche_label="Ambient Electronic",
                mood_keywords=["atmospheric", "ethereal", "dreamy"],
                target_duration_minutes=70
            )

        assert "music_prompts" in result
        assert "visual_prompts" in result
        assert "metadata" in result

        assert len(result["music_prompts"]) == 20
        assert len(result["visual_prompts"]) == 20

        assert result["metadata"]["niche_label"] == "Ambient Electronic"
        assert result["metadata"]["num_tracks"] == 20
        assert result["metadata"]["num_visuals"] == 20

    def test_generate_prompts_validates_niche_label(self, service):
        """generate_prompts validates niche_label"""
        with pytest.raises(ValueError, match="niche_label cannot be empty"):
            service.generate_prompts(
                niche_label="",
                mood_keywords=["test"],
                target_duration_minutes=70
            )

    def test_generate_prompts_validates_mood_keywords(self, service):
        """generate_prompts validates mood_keywords"""
        with pytest.raises(ValueError, match="mood_keywords must contain at least one"):
            service.generate_prompts(
                niche_label="Test",
                mood_keywords=[],
                target_duration_minutes=70
            )

    def test_generate_prompts_validates_duration(self, service):
        """generate_prompts validates target_duration_minutes"""
        with pytest.raises(ValueError, match="must be between 60 and 90"):
            service.generate_prompts(
                niche_label="Test",
                mood_keywords=["test"],
                target_duration_minutes=50  # Too short
            )

        with pytest.raises(ValueError, match="must be between 60 and 90"):
            service.generate_prompts(
                niche_label="Test",
                mood_keywords=["test"],
                target_duration_minutes=100  # Too long
            )


class TestPromptGeneratorIntegration:
    """Integration tests for prompt generator"""

    @pytest.fixture
    def service(self):
        return PromptGeneratorService(api_key="test-key")

    def test_realistic_prompt_generation_scenario(self, service):
        """Test realistic scenario: Generate prompts for Regency Classical video"""
        mock_music = [
            f"Track {i}: Elegant classical composition with period instruments"
            for i in range(1, 21)
        ]
        mock_visuals = [
            f"Visual {i}: Regency ballroom scene with period-accurate details"
            for i in range(1, 21)
        ]

        music_response = Mock()
        music_response.choices = [Mock()]
        music_response.choices[0].message.content = json.dumps(mock_music)

        visual_response = Mock()
        visual_response.choices = [Mock()]
        visual_response.choices[0].message.content = json.dumps(mock_visuals)

        with patch.object(
            service.client.chat.completions, 'create',
            side_effect=[music_response, visual_response]
        ):
            result = service.generate_prompts(
                niche_label="Regency Era Classical Music",
                mood_keywords=["elegant", "romantic", "aristocratic", "refined"],
                target_duration_minutes=75
            )

        # Verify structure
        assert len(result["music_prompts"]) == 20
        assert len(result["visual_prompts"]) == 20

        # Verify metadata
        assert result["metadata"]["target_duration_minutes"] == 75
        assert "elegant" in result["metadata"]["mood_keywords"]

        # Verify content diversity (at least somewhat different)
        assert len(set(result["music_prompts"])) == 20  # All unique
        assert len(set(result["visual_prompts"])) == 20  # All unique
