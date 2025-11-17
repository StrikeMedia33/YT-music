"""Unit tests for Metadata Generator Service"""
import pytest
import json
from unittest.mock import Mock, patch
from pathlib import Path
from services import MetadataGeneratorService


class TestMetadataGeneratorServiceInitialization:
    """Test MetadataGeneratorService initialization"""

    def test_initialization_with_api_key(self):
        """Service initializes with provided API key"""
        service = MetadataGeneratorService(api_key="test-key-123")
        assert service.api_key == "test-key-123"
        assert service.model == "gpt-4"

    def test_initialization_with_env_var(self, monkeypatch):
        """Service initializes with API key from environment"""
        monkeypatch.setenv("OPENAI_API_KEY", "env-key-456")
        service = MetadataGeneratorService()
        assert service.api_key == "env-key-456"

    def test_initialization_without_api_key_raises_error(self, monkeypatch):
        """Service raises error if no API key provided"""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        with pytest.raises(ValueError, match="API key required"):
            MetadataGeneratorService()


class TestTitleGeneration:
    """Test video title generation"""

    @pytest.fixture
    def service(self):
        return MetadataGeneratorService(api_key="test-key")

    def test_generate_title_success(self, service):
        """generate_title returns formatted title"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Ethereal Soundscapes: Ambient Electronic Mix for Focus"

        with patch.object(service.client.chat.completions, 'create', return_value=mock_response):
            result = service.generate_title(
                niche_label="Ambient Electronic",
                mood_keywords=["ethereal", "dreamy", "atmospheric"]
            )

        assert isinstance(result, str)
        assert len(result) > 0
        # Should use Mix/Album/Anthology terminology
        assert any(term in result.lower() for term in ["mix", "album", "anthology"])

    def test_generate_title_removes_quotes(self, service):
        """generate_title removes surrounding quotes"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '"Test Title: An Album"'

        with patch.object(service.client.chat.completions, 'create', return_value=mock_response):
            result = service.generate_title(
                niche_label="Test",
                mood_keywords=["test"]
            )

        assert not result.startswith('"')
        assert not result.endswith('"')

    def test_generate_title_api_error_raises_error(self, service):
        """generate_title raises error if API fails"""
        with patch.object(service.client.chat.completions, 'create', side_effect=Exception("API Error")):
            with pytest.raises(RuntimeError, match="Title generation failed"):
                service.generate_title(
                    niche_label="Test",
                    mood_keywords=["test"]
                )


class TestDescriptionGeneration:
    """Test video description generation"""

    @pytest.fixture
    def service(self):
        return MetadataGeneratorService(api_key="test-key")

    @pytest.fixture
    def sample_tracks(self):
        return [f"Track {i}" for i in range(1, 21)]

    @pytest.fixture
    def sample_durations(self):
        return [180.0] * 20  # 3 minutes each

    def test_generate_description_success(
        self, service, sample_tracks, sample_durations
    ):
        """generate_description returns complete description with timestamps"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This is a curated collection of ambient tracks perfect for focus and relaxation."

        with patch.object(service.client.chat.completions, 'create', return_value=mock_response):
            result = service.generate_description(
                niche_label="Ambient",
                mood_keywords=["calm", "peaceful"],
                track_titles=sample_tracks,
                track_durations=sample_durations
            )

        assert isinstance(result, str)
        assert len(result) > 0

        # Should contain introduction
        assert "curated" in result.lower() or "collection" in result.lower()

        # Should contain timestamps
        assert "00:00" in result  # First track at 0:00
        assert "03:00" in result  # Second track at 3:00

        # Should contain tracklist header
        assert "TRACKLIST" in result or "TIMESTAMPS" in result

        # Should contain reminder about synthetic content
        assert "Altered or synthetic content" in result

    def test_generate_description_includes_all_timestamps(
        self, service, sample_tracks, sample_durations
    ):
        """generate_description includes timestamps for all 20 tracks"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Introduction text."

        with patch.object(service.client.chat.completions, 'create', return_value=mock_response):
            result = service.generate_description(
                niche_label="Test",
                mood_keywords=["test"],
                track_titles=sample_tracks,
                track_durations=sample_durations
            )

        # Count timestamp markers
        timestamp_count = result.count(" - ")  # Timestamps format: "00:00 - Track"
        assert timestamp_count == 20  # All 20 tracks should have timestamps

    def test_generate_description_api_error_raises_error(
        self, service, sample_tracks, sample_durations
    ):
        """generate_description raises error if API fails"""
        with patch.object(service.client.chat.completions, 'create', side_effect=Exception("API Error")):
            with pytest.raises(RuntimeError, match="Description generation failed"):
                service.generate_description(
                    niche_label="Test",
                    mood_keywords=["test"],
                    track_titles=sample_tracks,
                    track_durations=sample_durations
                )


class TestTagsGeneration:
    """Test YouTube tags generation"""

    @pytest.fixture
    def service(self):
        return MetadataGeneratorService(api_key="test-key")

    def test_generate_tags_success(self, service):
        """generate_tags returns list of tags"""
        sample_tags = [
            "ambient music",
            "study music",
            "focus music",
            "relaxation",
            "background music",
            "lo-fi",
            "chill",
            "calm",
            "peaceful",
            "concentration"
        ]

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(sample_tags)

        with patch.object(service.client.chat.completions, 'create', return_value=mock_response):
            result = service.generate_tags(
                niche_label="Ambient",
                mood_keywords=["calm", "peaceful"]
            )

        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(tag, str) for tag in result)

    def test_generate_tags_handles_markdown(self, service):
        """generate_tags handles markdown code blocks"""
        sample_tags = ["tag1", "tag2", "tag3"]

        mock_response = Mock()
        mock_response.choices = [Mock()]
        markdown_content = f"```json\n{json.dumps(sample_tags)}\n```"
        mock_response.choices[0].message.content = markdown_content

        with patch.object(service.client.chat.completions, 'create', return_value=mock_response):
            result = service.generate_tags(
                niche_label="Test",
                mood_keywords=["test"]
            )

        assert isinstance(result, list)
        assert len(result) == 3

    def test_generate_tags_limits_to_20(self, service):
        """generate_tags limits output to 20 tags"""
        too_many_tags = [f"tag{i}" for i in range(1, 51)]  # 50 tags

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(too_many_tags)

        with patch.object(service.client.chat.completions, 'create', return_value=mock_response):
            result = service.generate_tags(
                niche_label="Test",
                mood_keywords=["test"]
            )

        assert len(result) <= 20


class TestCompleteMetadataGeneration:
    """Test complete metadata generation"""

    @pytest.fixture
    def service(self):
        return MetadataGeneratorService(api_key="test-key")

    @pytest.fixture
    def sample_tracks(self):
        return [f"Track {i}: Composition" for i in range(1, 21)]

    @pytest.fixture
    def sample_durations(self):
        return [210.0] * 20  # 3.5 minutes each

    def test_generate_metadata_success(
        self, service, sample_tracks, sample_durations
    ):
        """generate_metadata returns complete metadata"""
        title_response = Mock()
        title_response.choices = [Mock()]
        title_response.choices[0].message.content = "Ambient Mix: 70 Minutes of Calm"

        description_response = Mock()
        description_response.choices = [Mock()]
        description_response.choices[0].message.content = "A curated collection."

        tags_response = Mock()
        tags_response.choices = [Mock()]
        tags_response.choices[0].message.content = json.dumps(["ambient", "calm", "music"])

        with patch.object(
            service.client.chat.completions, 'create',
            side_effect=[title_response, description_response, tags_response]
        ):
            result = service.generate_metadata(
                niche_label="Ambient",
                mood_keywords=["calm", "peaceful"],
                track_titles=sample_tracks,
                track_durations=sample_durations
            )

        assert "title" in result
        assert "description" in result
        assert "tags" in result
        assert "metadata" in result

        assert isinstance(result["title"], str)
        assert isinstance(result["description"], str)
        assert isinstance(result["tags"], list)
        assert isinstance(result["metadata"], dict)

        # Check metadata fields
        assert result["metadata"]["num_tracks"] == 20
        assert result["metadata"]["total_duration_seconds"] == sum(sample_durations)

    def test_generate_metadata_validates_track_count(self, service):
        """generate_metadata validates track counts"""
        with pytest.raises(ValueError, match="Must have exactly 20 tracks"):
            service.generate_metadata(
                niche_label="Test",
                mood_keywords=["test"],
                track_titles=["Track 1"],  # Only 1 track
                track_durations=[180.0]
            )

    def test_generate_metadata_validates_matching_lengths(self, service):
        """generate_metadata validates matching lengths"""
        tracks = [f"Track {i}" for i in range(1, 21)]
        durations = [180.0] * 19  # Only 19 durations

        with pytest.raises(ValueError, match="must have same length"):
            service.generate_metadata(
                niche_label="Test",
                mood_keywords=["test"],
                track_titles=tracks,
                track_durations=durations
            )


class TestMetadataFileExport:
    """Test metadata file export"""

    @pytest.fixture
    def service(self):
        return MetadataGeneratorService(api_key="test-key")

    @pytest.fixture
    def sample_metadata(self):
        return {
            "title": "Test Album: 1 Hour Mix",
            "description": "Test description\n\n00:00 - Track 1\n03:00 - Track 2",
            "tags": ["ambient", "music", "calm"]
        }

    def test_save_metadata_to_file_creates_file(
        self, service, sample_metadata, tmp_path
    ):
        """save_metadata_to_file creates metadata file"""
        output_path = tmp_path / "metadata.txt"

        result = service.save_metadata_to_file(sample_metadata, output_path)

        assert result.exists()
        assert result == output_path

    def test_save_metadata_to_file_contains_all_sections(
        self, service, sample_metadata, tmp_path
    ):
        """save_metadata_to_file includes all metadata sections"""
        output_path = tmp_path / "metadata.txt"

        service.save_metadata_to_file(sample_metadata, output_path)

        content = output_path.read_text(encoding="utf-8")

        assert "TITLE:" in content
        assert sample_metadata["title"] in content

        assert "DESCRIPTION:" in content
        assert "00:00 - Track 1" in content

        assert "TAGS:" in content
        assert "ambient" in content

        assert "UPLOAD CHECKLIST:" in content
        assert "Altered or synthetic content" in content

    def test_save_metadata_creates_parent_directories(
        self, service, sample_metadata, tmp_path
    ):
        """save_metadata_to_file creates parent directories if needed"""
        nested_path = tmp_path / "deep" / "nested" / "path" / "metadata.txt"

        result = service.save_metadata_to_file(sample_metadata, nested_path)

        assert result.exists()
        assert nested_path.parent.exists()


class TestTimestampCalculation:
    """Test timestamp calculation"""

    @pytest.fixture
    def service(self):
        return MetadataGeneratorService(api_key="test-key")

    def test_calculate_timestamps_format(self, service):
        """_calculate_timestamps returns correctly formatted timestamps"""
        titles = ["Track 1", "Track 2", "Track 3"]
        durations = [180.0, 195.0, 210.0]  # 3, 3.25, 3.5 minutes

        result = service._calculate_timestamps(titles, durations)

        assert len(result) == 3
        assert result[0] == "00:00 - Track 1"
        assert result[1] == "03:00 - Track 2"
        assert result[2].startswith("06:15 - Track 3")

    def test_calculate_timestamps_handles_hours(self, service):
        """_calculate_timestamps handles durations over 1 hour"""
        titles = ["Track 1", "Track 2"]
        durations = [3600.0, 180.0]  # 60 minutes, then 3 minutes

        result = service._calculate_timestamps(titles, durations)

        assert result[0] == "00:00 - Track 1"
        assert result[1].startswith("1:00:00 - Track 2")

    def test_calculate_timestamps_truncates_long_titles(self, service):
        """_calculate_timestamps truncates very long titles"""
        long_title = "A" * 100  # 100 characters
        titles = [long_title]
        durations = [180.0]

        result = service._calculate_timestamps(titles, durations)

        assert len(result[0]) < len(long_title) + 10  # Should be truncated
        assert "..." in result[0]


class TestMetadataGeneratorIntegration:
    """Integration tests for metadata generator"""

    @pytest.fixture
    def service(self):
        return MetadataGeneratorService(api_key="test-key")

    def test_realistic_metadata_generation_scenario(self, service, tmp_path):
        """Test realistic scenario: Generate metadata for Regency Classical video"""
        tracks = [f"Track {i}: Elegant Classical Composition" for i in range(1, 21)]
        durations = [210.0] * 20  # 3.5 minutes each = 70 minutes total

        title_response = Mock()
        title_response.choices = [Mock()]
        title_response.choices[0].message.content = "Royal Court Ambience: A 1-Hour Regency Classical Mix"

        description_response = Mock()
        description_response.choices = [Mock()]
        description_response.choices[0].message.content = "Immerse yourself in the elegant world of Regency-era classical music."

        tags_response = Mock()
        tags_response.choices = [Mock()]
        tags_response.choices[0].message.content = json.dumps([
            "classical music",
            "regency era",
            "ambient classical",
            "study music",
            "elegant music"
        ])

        with patch.object(
            service.client.chat.completions, 'create',
            side_effect=[title_response, description_response, tags_response]
        ):
            metadata = service.generate_metadata(
                niche_label="Regency Era Classical",
                mood_keywords=["elegant", "romantic", "aristocratic"],
                track_titles=tracks,
                track_durations=durations
            )

            # Save to file
            output_path = tmp_path / "regency_metadata.txt"
            service.save_metadata_to_file(metadata, output_path)

        # Verify metadata structure
        assert "Regency" in metadata["title"]
        assert "20" in metadata["description"]  # Should mention 20 tracks somewhere
        assert "classical music" in metadata["tags"]

        # Verify file was created and contains expected content
        assert output_path.exists()
        content = output_path.read_text(encoding="utf-8")
        assert "Royal Court Ambience" in content
        assert "00:00" in content  # Timestamps present
        assert "Altered or synthetic content" in content
