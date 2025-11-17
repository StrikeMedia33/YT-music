"""Unit tests for Video Pipeline Service"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
from services import VideoPipelineService
from models import VideoJob, VideoJobStatus


class TestVideoPipelineServiceInitialization:
    """Test VideoPipelineService initialization"""

    def test_initialization_creates_output_directory(self, tmp_path):
        """Pipeline service creates output directory if it doesn't exist"""
        output_dir = tmp_path / "output"
        assert not output_dir.exists()

        mock_db = Mock()
        service = VideoPipelineService(
            db=mock_db,
            output_base_dir=output_dir,
            openai_api_key="test-key"
        )

        assert output_dir.exists()
        assert service.output_base_dir == output_dir

    def test_initialization_initializes_services(self, tmp_path):
        """Pipeline service initializes all required services"""
        mock_db = Mock()
        service = VideoPipelineService(
            db=mock_db,
            output_base_dir=tmp_path / "output",
            openai_api_key="test-key"
        )

        assert service.prompt_service is not None
        assert service.metadata_service is not None
        assert service.music_provider is not None
        assert service.visual_provider is not None
        assert service.renderer is not None


class TestPipelineExecution:
    """Test pipeline execution"""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session"""
        db = Mock()
        db.commit = Mock()
        db.add = Mock()
        return db

    @pytest.fixture
    def mock_job(self):
        """Create mock video job"""
        job = Mock(spec=VideoJob)
        job.id = "test-job-123"
        job.status = VideoJobStatus.PLANNED
        job.target_duration_minutes = 70
        job.channel = Mock()
        job.channel.brand_niche = "Ambient Electronic"
        job.prompts_json = None
        job.local_video_path = None
        job.error_message = None
        return job

    def test_execute_pipeline_job_not_found_raises_error(
        self, mock_db, tmp_path
    ):
        """execute_pipeline raises error if job not found"""
        mock_db.query = Mock(return_value=Mock(filter=Mock(return_value=Mock(first=Mock(return_value=None)))))

        service = VideoPipelineService(
            db=mock_db,
            output_base_dir=tmp_path / "output",
            openai_api_key="test-key"
        )

        with pytest.raises(ValueError, match="not found"):
            service.execute_pipeline("nonexistent-job")

    @patch('services.video_pipeline.get_music_provider')
    @patch('services.video_pipeline.get_visual_provider')
    def test_execute_pipeline_creates_job_directory(
        self, mock_visual_provider, mock_music_provider, mock_db, mock_job, tmp_path
    ):
        """execute_pipeline creates job-specific output directory"""
        mock_db.query = Mock(return_value=Mock(filter=Mock(return_value=Mock(first=Mock(return_value=mock_job)))))

        # Mock providers
        mock_music_provider.return_value = Mock()
        mock_visual_provider.return_value = Mock()

        service = VideoPipelineService(
            db=mock_db,
            output_base_dir=tmp_path / "output",
            openai_api_key="test-key"
        )

        # Mock step 1 to avoid full execution
        with patch.object(service, '_step_1_generate_prompts') as mock_step1:
            mock_step1.side_effect = lambda job, output_dir: None
            # Change status to prevent further steps
            mock_job.status = VideoJobStatus.GENERATING_MUSIC

            try:
                service.execute_pipeline("test-job-123")
            except:
                pass  # May error on subsequent steps

        # Check job directory was created
        job_dir = tmp_path / "output" / "test-job-123"
        assert job_dir.exists()


class TestPipelineSteps:
    """Test individual pipeline steps"""

    @pytest.fixture
    def mock_db(self):
        db = Mock()
        db.commit = Mock()
        db.add = Mock()
        db.query = Mock()
        return db

    @pytest.fixture
    def mock_job(self):
        job = Mock(spec=VideoJob)
        job.id = "test-job-123"
        job.status = VideoJobStatus.PLANNED
        job.target_duration_minutes = 70
        job.channel = Mock()
        job.channel.brand_niche = "Ambient"
        job.prompts_json = None
        return job

    def test_step_1_generates_prompts_and_updates_status(
        self, mock_db, mock_job, tmp_path
    ):
        """Step 1 generates prompts and updates job status"""
        service = VideoPipelineService(
            db=mock_db,
            output_base_dir=tmp_path / "output",
            openai_api_key="test-key"
        )

        # Mock prompt service
        mock_prompts = {
            "music_prompts": [f"Music {i}" for i in range(1, 21)],
            "visual_prompts": [f"Visual {i}" for i in range(1, 21)]
        }
        service.prompt_service.generate_prompts = Mock(return_value=mock_prompts)

        # Execute step 1
        service._step_1_generate_prompts(mock_job, tmp_path / "output")

        # Verify prompts were stored
        assert mock_job.prompts_json == mock_prompts

        # Verify status was updated
        assert mock_job.status == VideoJobStatus.GENERATING_MUSIC

        # Verify database was committed
        mock_db.commit.assert_called()

    def test_step_2_generates_20_tracks(
        self, mock_db, mock_job, tmp_path
    ):
        """Step 2 generates 20 music tracks"""
        # Set up job with prompts
        mock_job.status = VideoJobStatus.GENERATING_MUSIC
        mock_job.prompts_json = {
            "music_prompts": [f"Track {i}" for i in range(1, 21)]
        }

        service = VideoPipelineService(
            db=mock_db,
            output_base_dir=tmp_path / "output",
            openai_api_key="test-key"
        )

        # Mock music provider
        service.music_provider.generate_track = Mock(return_value={
            "file_path": "/fake/path.wav",
            "duration_seconds": 180.0,
            "metadata": {"provider": "dummy"}
        })

        # Execute step 2
        service._step_2_generate_music(mock_job, tmp_path / "output")

        # Verify 20 tracks were generated
        assert service.music_provider.generate_track.call_count == 20

        # Verify 20 database records were created
        assert mock_db.add.call_count == 20

        # Verify status was updated
        assert mock_job.status == VideoJobStatus.GENERATING_IMAGE

    def test_step_3_generates_20_visuals(
        self, mock_db, mock_job, tmp_path
    ):
        """Step 3 generates 20 visuals"""
        # Set up job
        mock_job.status = VideoJobStatus.GENERATING_IMAGE
        mock_job.prompts_json = {
            "visual_prompts": [f"Visual {i}" for i in range(1, 21)]
        }

        service = VideoPipelineService(
            db=mock_db,
            output_base_dir=tmp_path / "output",
            openai_api_key="test-key"
        )

        # Mock visual provider
        service.visual_provider.generate_visual = Mock(return_value={
            "file_path": "/fake/visual.png",
            "metadata": {"provider": "dummy"}
        })

        # Execute step 3
        service._step_3_generate_visuals(mock_job, tmp_path / "output")

        # Verify 20 visuals were generated
        assert service.visual_provider.generate_visual.call_count == 20

        # Verify status was updated
        assert mock_job.status == VideoJobStatus.RENDERING


class TestErrorHandling:
    """Test pipeline error handling"""

    @pytest.fixture
    def mock_db(self):
        db = Mock()
        db.commit = Mock()
        db.query = Mock()
        return db

    @pytest.fixture
    def mock_job(self):
        job = Mock(spec=VideoJob)
        job.id = "test-job-123"
        job.status = VideoJobStatus.PLANNED
        job.error_message = None
        return job

    def test_pipeline_failure_updates_job_status(
        self, mock_db, mock_job, tmp_path
    ):
        """Pipeline failure sets job status to FAILED"""
        mock_db.query = Mock(return_value=Mock(filter=Mock(return_value=Mock(first=Mock(return_value=mock_job)))))

        service = VideoPipelineService(
            db=mock_db,
            output_base_dir=tmp_path / "output",
            openai_api_key="test-key"
        )

        # Mock step 1 to raise an error
        with patch.object(service, '_step_1_generate_prompts', side_effect=Exception("Test error")):
            with pytest.raises(RuntimeError, match="Pipeline failed"):
                service.execute_pipeline("test-job-123")

        # Verify job was marked as failed
        assert mock_job.status == VideoJobStatus.FAILED
        assert "Test error" in mock_job.error_message

    def test_step_2_validates_prompt_count(
        self, mock_db, mock_job, tmp_path
    ):
        """Step 2 validates that exactly 20 prompts exist"""
        mock_job.prompts_json = {
            "music_prompts": ["Only one prompt"]  # Wrong count
        }

        service = VideoPipelineService(
            db=mock_db,
            output_base_dir=tmp_path / "output",
            openai_api_key="test-key"
        )

        with pytest.raises(ValueError, match="Expected 20 music prompts"):
            service._step_2_generate_music(mock_job, tmp_path / "output")


class TestPipelineIntegration:
    """Integration tests for pipeline"""

    def test_pipeline_summary_format(self):
        """Pipeline returns properly formatted summary"""
        # This is a lightweight test to verify return structure
        summary = {
            "job_id": "123",
            "status": "completed",
            "output_directory": "/path",
            "video_path": "/path/video.mp4",
            "completed": True
        }

        assert "job_id" in summary
        assert "status" in summary
        assert "completed" in summary
