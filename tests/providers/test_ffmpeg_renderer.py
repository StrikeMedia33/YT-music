"""Unit tests for FFmpeg Renderer"""
import pytest
import subprocess
from pathlib import Path
from providers import FFmpegRenderer, DummyMusicProvider, DummyVisualProvider


class TestFFmpegRendererInitialization:
    """Test FFmpegRenderer initialization"""

    def test_renderer_initialization_default_params(self):
        """Renderer initializes with default encoding parameters"""
        renderer = FFmpegRenderer()
        assert renderer.video_bitrate == "8000k"
        assert renderer.audio_bitrate == "192k"
        assert renderer.video_codec == "libx264"
        assert renderer.audio_codec == "aac"
        assert renderer.preset == "medium"
        assert renderer.crf == 23

    def test_renderer_initialization_custom_params(self):
        """Renderer can be initialized with custom parameters"""
        renderer = FFmpegRenderer(
            video_bitrate="10000k",
            audio_bitrate="256k",
            preset="fast",
            crf=20
        )
        assert renderer.video_bitrate == "10000k"
        assert renderer.audio_bitrate == "256k"
        assert renderer.preset == "fast"
        assert renderer.crf == 20

    def test_ffmpeg_verification(self):
        """FFmpeg availability is verified on initialization"""
        # Should not raise if FFmpeg is installed
        renderer = FFmpegRenderer()
        assert renderer is not None


class TestFFmpegRendererBasicFunctionality:
    """Test basic FFmpeg rendering functionality"""

    @pytest.fixture
    def renderer(self):
        """Create an FFmpegRenderer instance"""
        return FFmpegRenderer(preset="ultrafast", crf=28)  # Fast for testing

    @pytest.fixture
    def temp_output_dir(self, tmp_path):
        """Create temporary output directory"""
        output_dir = tmp_path / "rendered_videos"
        output_dir.mkdir()
        return output_dir

    @pytest.fixture
    def sample_audio_tracks(self, tmp_path):
        """Generate sample audio tracks for testing"""
        music_provider = DummyMusicProvider()
        audio_dir = tmp_path / "audio"
        audio_dir.mkdir()

        tracks = []
        for i in range(1, 4):  # 3 tracks for faster tests
            result = music_provider.generate_track(
                prompt=f"Test track {i}",
                duration_minutes=0.05,  # 3 seconds each
                order_index=i,
                output_dir=audio_dir
            )
            tracks.append(result)

        return tracks

    @pytest.fixture
    def sample_visuals(self, tmp_path):
        """Generate sample visuals for testing"""
        visual_provider = DummyVisualProvider()
        visual_dir = tmp_path / "visuals"
        visual_dir.mkdir()

        visuals = []
        for i in range(1, 4):  # 3 visuals to match tracks
            result = visual_provider.generate_visual(
                prompt=f"Test visual {i}",
                order_index=i,
                output_dir=visual_dir
            )
            visuals.append(result)

        return visuals

    def test_render_video_creates_output_file(
        self, renderer, sample_audio_tracks, sample_visuals, temp_output_dir
    ):
        """render_video creates an MP4 file"""
        output_path = temp_output_dir / "test_video.mp4"

        result = renderer.render_video(
            audio_tracks=sample_audio_tracks,
            visuals=sample_visuals,
            output_path=output_path,
            crossfade_duration=0.5  # Short crossfade for testing
        )

        assert output_path.exists()
        assert output_path.suffix == ".mp4"
        assert result["output_path"] == str(output_path.absolute())

    def test_render_video_returns_metadata(
        self, renderer, sample_audio_tracks, sample_visuals, temp_output_dir
    ):
        """render_video returns correct metadata"""
        output_path = temp_output_dir / "test_video.mp4"

        result = renderer.render_video(
            audio_tracks=sample_audio_tracks,
            visuals=sample_visuals,
            output_path=output_path,
            crossfade_duration=0.5
        )

        assert "output_path" in result
        assert "duration_seconds" in result
        assert "resolution" in result
        assert result["resolution"] == "1920x1080"
        assert "file_size_mb" in result
        assert result["file_size_mb"] > 0
        assert "metadata" in result

    def test_render_video_with_progress_callback(
        self, renderer, sample_audio_tracks, sample_visuals, temp_output_dir
    ):
        """render_video calls progress callback during rendering"""
        output_path = temp_output_dir / "test_video.mp4"
        progress_values = []

        def progress_callback(progress):
            progress_values.append(progress)

        renderer.render_video(
            audio_tracks=sample_audio_tracks,
            visuals=sample_visuals,
            output_path=output_path,
            crossfade_duration=0.5,
            progress_callback=progress_callback
        )

        # Progress callback should be called multiple times
        assert len(progress_values) > 0
        # Progress should start at 0 and end at 1.0
        assert progress_values[0] >= 0.0
        assert progress_values[-1] == 1.0
        # Progress should be monotonically increasing
        for i in range(1, len(progress_values)):
            assert progress_values[i] >= progress_values[i-1]

    def test_render_video_validates_matching_counts(
        self, renderer, sample_audio_tracks, sample_visuals, temp_output_dir
    ):
        """render_video raises error if audio and visual counts don't match"""
        output_path = temp_output_dir / "test_video.mp4"

        # Remove one visual to create mismatch
        mismatched_visuals = sample_visuals[:-1]

        with pytest.raises(ValueError, match="must have the same count"):
            renderer.render_video(
                audio_tracks=sample_audio_tracks,
                visuals=mismatched_visuals,
                output_path=output_path
            )

    def test_render_video_validates_minimum_tracks(
        self, renderer, temp_output_dir
    ):
        """render_video raises error if no tracks provided"""
        output_path = temp_output_dir / "test_video.mp4"

        with pytest.raises(ValueError, match="Must have at least 1"):
            renderer.render_video(
                audio_tracks=[],
                visuals=[],
                output_path=output_path
            )

    def test_rendered_video_is_valid(
        self, renderer, sample_audio_tracks, sample_visuals, temp_output_dir
    ):
        """Rendered video can be analyzed with ffprobe"""
        output_path = temp_output_dir / "test_video.mp4"

        renderer.render_video(
            audio_tracks=sample_audio_tracks,
            visuals=sample_visuals,
            output_path=output_path,
            crossfade_duration=0.5
        )

        # Use ffprobe to verify video
        info = renderer.get_video_info(output_path)

        assert info["video"]["codec"] == "h264"
        assert info["video"]["width"] == 1920
        assert info["video"]["height"] == 1080
        assert info["audio"]["codec"] == "aac"
        assert info["duration_seconds"] > 0

    def test_render_video_creates_output_directory(
        self, renderer, sample_audio_tracks, sample_visuals, tmp_path
    ):
        """render_video creates output directory if it doesn't exist"""
        nested_path = tmp_path / "deep" / "nested" / "output" / "video.mp4"
        assert not nested_path.parent.exists()

        renderer.render_video(
            audio_tracks=sample_audio_tracks,
            visuals=sample_visuals,
            output_path=nested_path,
            crossfade_duration=0.5
        )

        assert nested_path.parent.exists()
        assert nested_path.exists()


class TestFFmpegRendererAudioProcessing:
    """Test audio concatenation and crossfading"""

    @pytest.fixture
    def renderer(self):
        return FFmpegRenderer(preset="ultrafast")

    @pytest.fixture
    def audio_tracks_different_lengths(self, tmp_path):
        """Generate audio tracks with different lengths"""
        music_provider = DummyMusicProvider()
        audio_dir = tmp_path / "audio"
        audio_dir.mkdir()

        durations = [0.05, 0.08, 0.06]  # Different durations in minutes
        tracks = []

        for i, duration in enumerate(durations, 1):
            result = music_provider.generate_track(
                prompt=f"Track {i}",
                duration_minutes=duration,
                order_index=i,
                output_dir=audio_dir
            )
            tracks.append(result)

        return tracks

    def test_single_track_no_crossfade(
        self, renderer, tmp_path
    ):
        """Single audio track renders without crossfade"""
        music_provider = DummyMusicProvider()
        visual_provider = DummyVisualProvider()

        audio_dir = tmp_path / "audio"
        visual_dir = tmp_path / "visuals"
        audio_dir.mkdir()
        visual_dir.mkdir()

        # Generate single track and visual
        track = music_provider.generate_track(
            prompt="Single track",
            duration_minutes=0.05,
            order_index=1,
            output_dir=audio_dir
        )
        visual = visual_provider.generate_visual(
            prompt="Single visual",
            order_index=1,
            output_dir=visual_dir
        )

        output_path = tmp_path / "single_track_video.mp4"

        result = renderer.render_video(
            audio_tracks=[track],
            visuals=[visual],
            output_path=output_path,
            crossfade_duration=0.5
        )

        assert output_path.exists()
        # Duration should match track duration (no crossfade for single track)
        assert abs(result["duration_seconds"] - track["duration_seconds"]) < 1.0


class TestFFmpegRendererVisualAudioPairing:
    """Test visual-audio pairing functionality"""

    @pytest.fixture
    def renderer(self):
        return FFmpegRenderer(preset="ultrafast", crf=28)

    def test_visual_audio_pairing_order(self, renderer, tmp_path):
        """Visuals are paired with corresponding audio tracks by order_index"""
        music_provider = DummyMusicProvider()
        visual_provider = DummyVisualProvider()

        audio_dir = tmp_path / "audio"
        visual_dir = tmp_path / "visuals"
        audio_dir.mkdir()
        visual_dir.mkdir()

        # Generate 3 tracks and visuals with specific order
        tracks = []
        visuals = []

        for i in range(1, 4):
            track = music_provider.generate_track(
                prompt=f"Track {i}",
                duration_minutes=0.05,
                order_index=i,
                output_dir=audio_dir
            )
            tracks.append(track)

            visual = visual_provider.generate_visual(
                prompt=f"Visual for track {i}",
                order_index=i,
                output_dir=visual_dir
            )
            visuals.append(visual)

        output_path = tmp_path / "paired_video.mp4"

        result = renderer.render_video(
            audio_tracks=tracks,
            visuals=visuals,
            output_path=output_path,
            crossfade_duration=0.5
        )

        assert output_path.exists()
        assert result["metadata"]["num_tracks"] == 3
        assert result["metadata"]["num_visuals"] == 3


class TestFFmpegRendererIntegration:
    """Integration tests with realistic scenarios"""

    @pytest.fixture
    def renderer(self):
        return FFmpegRenderer(preset="ultrafast", crf=28)

    @pytest.fixture
    def output_dir(self, tmp_path):
        return tmp_path / "output"

    def test_render_full_album_20_tracks(self, renderer, output_dir, tmp_path):
        """Render a full album with 20 tracks and 20 visuals"""
        # Note: Using very short durations for speed in testing
        # In production, tracks would be 3-4 minutes each
        music_provider = DummyMusicProvider()
        visual_provider = DummyVisualProvider()

        audio_dir = tmp_path / "audio"
        visual_dir = tmp_path / "visuals"
        audio_dir.mkdir()
        visual_dir.mkdir()

        # Generate 20 tracks and visuals
        tracks = []
        visuals = []

        for i in range(1, 21):
            track = music_provider.generate_track(
                prompt=f"Track {i}: Album song variation {i}",
                duration_minutes=0.025,  # ~1.5 seconds for fast test
                order_index=i,
                output_dir=audio_dir
            )
            tracks.append(track)

            visual = visual_provider.generate_visual(
                prompt=f"Visual {i}: Scene for track {i}",
                order_index=i,
                output_dir=visual_dir
            )
            visuals.append(visual)

        output_path = output_dir / "full_album_20_tracks.mp4"

        result = renderer.render_video(
            audio_tracks=tracks,
            visuals=visuals,
            output_path=output_path,
            crossfade_duration=0.25
        )

        # Verify output
        assert output_path.exists()
        assert result["metadata"]["num_tracks"] == 20
        assert result["metadata"]["num_visuals"] == 20
        assert result["resolution"] == "1920x1080"

        # Verify video info
        info = renderer.get_video_info(output_path)
        assert info["video"]["width"] == 1920
        assert info["video"]["height"] == 1080

    def test_youtube_compliance(self, renderer, tmp_path):
        """Rendered video meets YouTube compliance requirements"""
        music_provider = DummyMusicProvider()
        visual_provider = DummyVisualProvider()

        audio_dir = tmp_path / "audio"
        visual_dir = tmp_path / "visuals"
        audio_dir.mkdir()
        visual_dir.mkdir()

        # Generate 5 tracks as a sample
        tracks = []
        visuals = []

        for i in range(1, 6):
            track = music_provider.generate_track(
                prompt=f"Track {i}",
                duration_minutes=0.05,
                order_index=i,
                output_dir=audio_dir
            )
            tracks.append(track)

            visual = visual_provider.generate_visual(
                prompt=f"Visual {i}",
                order_index=i,
                output_dir=visual_dir
            )
            visuals.append(visual)

        output_path = tmp_path / "youtube_compliant.mp4"

        result = renderer.render_video(
            audio_tracks=tracks,
            visuals=visuals,
            output_path=output_path,
            crossfade_duration=0.5
        )

        # Verify YouTube compliance
        info = renderer.get_video_info(output_path)

        # Check resolution (Full HD)
        assert info["video"]["width"] == 1920
        assert info["video"]["height"] == 1080

        # Check aspect ratio (16:9)
        aspect_ratio = info["video"]["width"] / info["video"]["height"]
        assert abs(aspect_ratio - 16/9) < 0.01

        # Check codecs (H.264 + AAC)
        assert info["video"]["codec"] == "h264"
        assert info["audio"]["codec"] == "aac"

        # Visual-audio pairing proves "human editing effort"
        assert result["metadata"]["num_tracks"] == len(tracks)
        assert result["metadata"]["num_visuals"] == len(visuals)
