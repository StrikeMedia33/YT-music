"""Unit tests for Music Provider"""
import pytest
import os
import wave
from pathlib import Path
from providers import MusicProvider, DummyMusicProvider, get_music_provider


class TestMusicProviderInterface:
    """Test the MusicProvider abstract interface"""

    def test_cannot_instantiate_abstract_class(self):
        """MusicProvider is abstract and cannot be instantiated directly"""
        with pytest.raises(TypeError):
            MusicProvider()

    def test_subclass_must_implement_generate_track(self):
        """Subclasses must implement generate_track method"""

        class IncompleteProvider(MusicProvider):
            pass

        with pytest.raises(TypeError):
            IncompleteProvider()


class TestDummyMusicProvider:
    """Test the DummyMusicProvider implementation"""

    @pytest.fixture
    def provider(self):
        """Create a DummyMusicProvider instance"""
        return DummyMusicProvider()

    @pytest.fixture
    def temp_output_dir(self, tmp_path):
        """Create a temporary output directory"""
        output_dir = tmp_path / "test_audio"
        output_dir.mkdir()
        return output_dir

    def test_provider_initialization(self, provider):
        """Provider initializes with correct audio settings"""
        assert provider.sample_rate == 44100
        assert provider.channels == 2
        assert provider.sample_width == 2

    def test_generate_track_creates_file(self, provider, temp_output_dir):
        """generate_track creates a WAV file in the output directory"""
        result = provider.generate_track(
            prompt="Test ambient music",
            duration_minutes=0.1,  # 6 seconds for fast test
            order_index=1,
            output_dir=temp_output_dir
        )

        assert "file_path" in result
        file_path = Path(result["file_path"])
        assert file_path.exists()
        assert file_path.suffix == ".wav"
        assert file_path.parent == temp_output_dir

    def test_generate_track_correct_duration(self, provider, temp_output_dir):
        """Generated track has the correct duration"""
        duration_minutes = 0.05  # 3 seconds
        result = provider.generate_track(
            prompt="Test track",
            duration_minutes=duration_minutes,
            order_index=1,
            output_dir=temp_output_dir
        )

        # Check returned duration
        expected_seconds = duration_minutes * 60
        assert result["duration_seconds"] == pytest.approx(expected_seconds, rel=0.01)

        # Verify actual WAV file duration
        with wave.open(result["file_path"], 'rb') as wav_file:
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            actual_duration = frames / float(rate)
            assert actual_duration == pytest.approx(expected_seconds, rel=0.01)

    def test_generate_track_correct_format(self, provider, temp_output_dir):
        """Generated track has correct audio format (44.1kHz, 16-bit, stereo)"""
        result = provider.generate_track(
            prompt="Test track",
            duration_minutes=0.05,
            order_index=1,
            output_dir=temp_output_dir
        )

        with wave.open(result["file_path"], 'rb') as wav_file:
            assert wav_file.getnchannels() == 2  # Stereo
            assert wav_file.getsampwidth() == 2  # 16-bit
            assert wav_file.getframerate() == 44100  # 44.1kHz

    def test_generate_track_metadata(self, provider, temp_output_dir):
        """Generated track returns correct metadata"""
        prompt = "Energetic electronic dance music"
        order_index = 5
        duration_minutes = 3.5

        result = provider.generate_track(
            prompt=prompt,
            duration_minutes=duration_minutes,
            order_index=order_index,
            output_dir=temp_output_dir
        )

        assert result["order_index"] == order_index
        assert result["prompt_text"] == prompt
        assert result["duration_seconds"] == pytest.approx(duration_minutes * 60)

        # Check metadata dict
        assert "metadata" in result
        assert result["metadata"]["provider"] == "dummy"
        assert result["metadata"]["sample_rate"] == 44100
        assert result["metadata"]["channels"] == 2
        assert result["metadata"]["bit_depth"] == 16
        assert "generated_at" in result["metadata"]

    def test_generate_track_creates_output_dir(self, provider, tmp_path):
        """generate_track creates output directory if it doesn't exist"""
        non_existent_dir = tmp_path / "nested" / "audio" / "output"
        assert not non_existent_dir.exists()

        result = provider.generate_track(
            prompt="Test",
            duration_minutes=0.05,
            order_index=1,
            output_dir=non_existent_dir
        )

        assert non_existent_dir.exists()
        assert Path(result["file_path"]).exists()

    def test_generate_multiple_tracks(self, provider, temp_output_dir):
        """Can generate multiple unique tracks with different order indices"""
        results = []
        for i in range(1, 4):
            result = provider.generate_track(
                prompt=f"Track {i}",
                duration_minutes=0.05,
                order_index=i,
                output_dir=temp_output_dir
            )
            results.append(result)

        # All files should exist and be unique
        file_paths = [r["file_path"] for r in results]
        assert len(file_paths) == len(set(file_paths))  # All unique
        for file_path in file_paths:
            assert Path(file_path).exists()

        # Order indices should be correct
        assert [r["order_index"] for r in results] == [1, 2, 3]

    def test_generate_track_typical_duration(self, provider, temp_output_dir):
        """Can generate track with typical 3-4 minute duration"""
        # Test with 0.05 minutes (3 seconds) to keep test fast
        # In production, this would be 3-4 minutes
        result = provider.generate_track(
            prompt="Typical production track",
            duration_minutes=0.05,  # Fast test equivalent of 3 minutes
            order_index=10,
            output_dir=temp_output_dir
        )

        assert result["duration_seconds"] == pytest.approx(3.0, rel=0.01)
        assert Path(result["file_path"]).exists()


class TestMusicProviderFactory:
    """Test the get_music_provider factory function"""

    def test_default_provider_is_dummy(self, monkeypatch):
        """Default provider is DummyMusicProvider when no env var set"""
        monkeypatch.delenv("MUSIC_PROVIDER", raising=False)
        provider = get_music_provider()
        assert isinstance(provider, DummyMusicProvider)

    def test_explicit_dummy_provider(self, monkeypatch):
        """Can explicitly request dummy provider"""
        monkeypatch.setenv("MUSIC_PROVIDER", "dummy")
        provider = get_music_provider()
        assert isinstance(provider, DummyMusicProvider)

    def test_case_insensitive_provider_name(self, monkeypatch):
        """Provider name is case-insensitive"""
        monkeypatch.setenv("MUSIC_PROVIDER", "DUMMY")
        provider = get_music_provider()
        assert isinstance(provider, DummyMusicProvider)

    def test_mubert_provider_not_implemented(self, monkeypatch):
        """Mubert provider raises NotImplementedError"""
        monkeypatch.setenv("MUSIC_PROVIDER", "mubert")
        with pytest.raises(NotImplementedError, match="Mubert provider not yet implemented"):
            get_music_provider()

    def test_beatoven_provider_not_implemented(self, monkeypatch):
        """Beatoven provider raises NotImplementedError"""
        monkeypatch.setenv("MUSIC_PROVIDER", "beatoven")
        with pytest.raises(NotImplementedError, match="Beatoven provider not yet implemented"):
            get_music_provider()

    def test_unknown_provider_raises_error(self, monkeypatch):
        """Unknown provider name raises ValueError"""
        monkeypatch.setenv("MUSIC_PROVIDER", "unknown_provider")
        with pytest.raises(ValueError, match="Unknown music provider: unknown_provider"):
            get_music_provider()


class TestMusicProviderIntegration:
    """Integration tests for music provider in realistic scenarios"""

    @pytest.fixture
    def provider(self):
        return DummyMusicProvider()

    @pytest.fixture
    def output_dir(self, tmp_path):
        return tmp_path / "output" / "audio"

    def test_generate_album_of_20_tracks(self, provider, output_dir):
        """Simulate generating 20 unique tracks for a full album"""
        tracks = []

        # Generate 20 tracks with typical durations (using 0.05 min for speed)
        for i in range(1, 21):
            result = provider.generate_track(
                prompt=f"Track {i}: Ambient electronic music variation {i}",
                duration_minutes=0.05,  # In production: 3-4 minutes
                order_index=i,
                output_dir=output_dir
            )
            tracks.append(result)

        # Verify all 20 tracks generated successfully
        assert len(tracks) == 20

        # All should have unique file paths
        file_paths = [t["file_path"] for t in tracks]
        assert len(file_paths) == len(set(file_paths))

        # All should have correct order indices (1-20)
        order_indices = [t["order_index"] for t in tracks]
        assert order_indices == list(range(1, 21))

        # All files should exist
        for track in tracks:
            assert Path(track["file_path"]).exists()

    def test_tracks_saved_to_correct_directory(self, provider, output_dir):
        """All tracks are saved to the specified output directory"""
        num_tracks = 5

        for i in range(1, num_tracks + 1):
            result = provider.generate_track(
                prompt=f"Track {i}",
                duration_minutes=0.05,
                order_index=i,
                output_dir=output_dir
            )
            file_path = Path(result["file_path"])
            assert file_path.parent == output_dir
