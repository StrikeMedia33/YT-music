"""Unit tests for Video Job Worker"""
import pytest
import signal
import time
from unittest.mock import Mock, MagicMock, patch, call
from pathlib import Path

from workers import VideoJobWorker
from models import VideoJob, VideoJobStatus, Channel


class TestVideoJobWorkerInitialization:
    """Test VideoJobWorker initialization"""

    def test_initialization_with_defaults(self):
        """Worker initializes with default configuration"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            worker = VideoJobWorker()

            assert worker.poll_interval == 30
            assert worker.max_retries == 3
            assert worker.should_stop is False

    def test_initialization_with_custom_params(self):
        """Worker initializes with custom parameters"""
        worker = VideoJobWorker(
            poll_interval=60,
            max_retries=5,
            output_dir="/custom/path",
            openai_api_key="custom-key"
        )

        assert worker.poll_interval == 60
        assert worker.max_retries == 5
        assert worker.output_dir == "/custom/path"
        assert worker.openai_api_key == "custom-key"

    def test_initialization_loads_from_env(self):
        """Worker loads configuration from environment variables"""
        env_vars = {
            'OUTPUT_DIRECTORY': '/env/output',
            'OPENAI_API_KEY': 'env-key'
        }

        with patch.dict('os.environ', env_vars):
            worker = VideoJobWorker()

            assert worker.output_dir == '/env/output'
            assert worker.openai_api_key == 'env-key'

    def test_signal_handlers_registered(self):
        """Worker registers signal handlers for graceful shutdown"""
        with patch('signal.signal') as mock_signal:
            worker = VideoJobWorker(openai_api_key="test-key")

            # Verify SIGTERM and SIGINT handlers were registered
            assert mock_signal.call_count >= 2

            # Get the calls
            calls = mock_signal.call_args_list
            signals_registered = [call_args[0][0] for call_args in calls]

            assert signal.SIGTERM in signals_registered
            assert signal.SIGINT in signals_registered


class TestJobPolling:
    """Test job polling and discovery"""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session"""
        db = Mock()
        return db

    @pytest.fixture
    def mock_get_db(self, mock_db):
        """Mock get_db generator"""
        def generator():
            yield mock_db
        return generator

    def test_process_pending_jobs_finds_planned_jobs(self, mock_db):
        """Worker finds and processes jobs in 'planned' status"""
        # Create mock job
        mock_job = Mock(spec=VideoJob)
        mock_job.id = "test-job-123"
        mock_job.status = VideoJobStatus.PLANNED
        mock_job.created_at = Mock()
        mock_job.channel = Mock(name="Test Channel", brand_niche="Ambient")
        mock_job.target_duration_minutes = 70

        # Mock query chain
        query_mock = Mock()
        query_mock.filter.return_value.order_by.return_value.all.return_value = [mock_job]
        mock_db.query.return_value = query_mock

        worker = VideoJobWorker(openai_api_key="test-key")

        # Mock _execute_job to avoid actual execution
        with patch.object(worker, '_execute_job') as mock_execute:
            with patch('workers.video_job_worker.get_db', return_value=iter([mock_db])):
                worker._process_pending_jobs()

                # Verify job was executed
                mock_execute.assert_called_once_with(mock_db, mock_job)

    def test_process_pending_jobs_handles_no_jobs(self, mock_db):
        """Worker handles case when no pending jobs exist"""
        # Mock empty query result
        query_mock = Mock()
        query_mock.filter.return_value.order_by.return_value.all.return_value = []
        mock_db.query.return_value = query_mock

        worker = VideoJobWorker(openai_api_key="test-key")

        with patch('workers.video_job_worker.get_db', return_value=iter([mock_db])):
            # Should not raise error
            worker._process_pending_jobs()

    def test_process_pending_jobs_processes_oldest_first(self, mock_db):
        """Worker processes jobs in order of creation (oldest first)"""
        # Create mock jobs with different timestamps
        job1 = Mock(id="job-1", created_at="2024-01-01")
        job2 = Mock(id="job-2", created_at="2024-01-02")

        query_mock = Mock()
        query_mock.filter.return_value.order_by.return_value.all.return_value = [job1, job2]
        mock_db.query.return_value = query_mock

        worker = VideoJobWorker(openai_api_key="test-key")

        with patch.object(worker, '_execute_job') as mock_execute:
            with patch('workers.video_job_worker.get_db', return_value=iter([mock_db])):
                worker._process_pending_jobs()

                # Verify jobs executed in order
                calls = mock_execute.call_args_list
                assert calls[0][0][1] == job1
                assert calls[1][0][1] == job2


class TestJobExecution:
    """Test job execution"""

    @pytest.fixture
    def mock_db(self):
        db = Mock()
        db.commit = Mock()
        db.refresh = Mock()
        return db

    @pytest.fixture
    def mock_job(self):
        job = Mock(spec=VideoJob)
        job.id = "test-job-123"
        job.status = VideoJobStatus.PLANNED
        job.channel = Mock(name="Test Channel", brand_niche="Ambient")
        job.target_duration_minutes = 70
        job.error_message = None
        return job

    @patch('workers.video_job_worker.VideoPipelineService')
    def test_execute_job_runs_pipeline(
        self, mock_pipeline_class, mock_db, mock_job
    ):
        """Worker executes pipeline for a job"""
        # Mock pipeline service
        mock_pipeline = Mock()
        mock_pipeline.execute_pipeline.return_value = {
            'job_id': 'test-job-123',
            'status': 'completed',
            'output_directory': '/output/test-job-123',
            'video_path': '/output/test-job-123/video.mp4',
            'completed': True
        }
        mock_pipeline_class.return_value = mock_pipeline

        worker = VideoJobWorker(
            output_dir="/test/output",
            openai_api_key="test-key"
        )

        # Execute job
        worker._execute_job(mock_db, mock_job)

        # Verify pipeline was created and executed
        mock_pipeline_class.assert_called_once_with(
            db=mock_db,
            output_base_dir="/test/output",
            openai_api_key="test-key"
        )
        mock_pipeline.execute_pipeline.assert_called_once_with("test-job-123")

    @patch('workers.video_job_worker.VideoPipelineService')
    def test_execute_job_handles_pipeline_failure(
        self, mock_pipeline_class, mock_db, mock_job
    ):
        """Worker handles pipeline execution failures"""
        # Mock pipeline to raise error
        mock_pipeline = Mock()
        mock_pipeline.execute_pipeline.side_effect = Exception("Pipeline error")
        mock_pipeline_class.return_value = mock_pipeline

        worker = VideoJobWorker(openai_api_key="test-key")

        # Execute job (should not raise)
        worker._execute_job(mock_db, mock_job)

        # Verify database was refreshed to get latest job state
        mock_db.refresh.assert_called_once_with(mock_job)


class TestRetryLogic:
    """Test retry logic"""

    @pytest.fixture
    def failed_job(self):
        job = Mock(spec=VideoJob)
        job.id = "failed-job-123"
        job.status = VideoJobStatus.FAILED
        job.error_message = None
        return job

    def test_should_retry_job_with_transient_error(self, failed_job):
        """Worker retries jobs with transient errors"""
        transient_errors = [
            "Connection timeout",
            "Network error",
            "Rate limit exceeded",
            "503 Service Unavailable",
            "502 Bad Gateway"
        ]

        worker = VideoJobWorker(openai_api_key="test-key")

        for error_msg in transient_errors:
            failed_job.error_message = error_msg
            assert worker._should_retry_job(failed_job) is True

    def test_should_retry_job_with_permanent_error(self, failed_job):
        """Worker does not retry jobs with permanent errors"""
        permanent_errors = [
            "Invalid API key",
            "File not found",
            "Invalid configuration",
            "ValueError: Invalid prompt count"
        ]

        worker = VideoJobWorker(openai_api_key="test-key")

        for error_msg in permanent_errors:
            failed_job.error_message = error_msg
            assert worker._should_retry_job(failed_job) is False

    def test_schedule_retry_resets_job_status(self, failed_job):
        """Worker resets job status when scheduling retry"""
        mock_db = Mock()
        mock_db.commit = Mock()

        worker = VideoJobWorker(openai_api_key="test-key")
        worker._schedule_retry(mock_db, failed_job)

        # Verify job was reset to planned status
        assert failed_job.status == VideoJobStatus.PLANNED
        assert failed_job.error_message is None

        # Verify changes were committed
        mock_db.commit.assert_called_once()


class TestGracefulShutdown:
    """Test graceful shutdown"""

    def test_handle_shutdown_sets_flag(self):
        """Worker sets should_stop flag on shutdown signal"""
        worker = VideoJobWorker(openai_api_key="test-key")

        assert worker.should_stop is False

        # Simulate shutdown signal
        worker._handle_shutdown(signal.SIGTERM, None)

        assert worker.should_stop is True

    def test_run_stops_on_shutdown_signal(self):
        """Worker stops polling loop on shutdown signal"""
        worker = VideoJobWorker(
            poll_interval=1,  # Short interval for testing
            openai_api_key="test-key"
        )

        with patch.object(worker, '_process_pending_jobs') as mock_process:
            # Set should_stop after first iteration
            def set_stop_flag():
                worker.should_stop = True

            mock_process.side_effect = set_stop_flag

            # Run worker (should stop after one iteration)
            worker.run()

            # Verify only one iteration occurred
            assert mock_process.call_count == 1

    def test_process_pending_jobs_stops_on_shutdown(self):
        """Worker stops processing jobs when shutdown requested"""
        mock_db = Mock()

        # Create multiple jobs
        jobs = [Mock(id=f"job-{i}") for i in range(5)]
        query_mock = Mock()
        query_mock.filter.return_value.order_by.return_value.all.return_value = jobs
        mock_db.query.return_value = query_mock

        worker = VideoJobWorker(openai_api_key="test-key")

        # Mock _execute_job to set shutdown flag after 2 jobs
        execution_count = [0]

        def execute_with_shutdown(db, job):
            execution_count[0] += 1
            if execution_count[0] >= 2:
                worker.should_stop = True

        with patch.object(worker, '_execute_job', side_effect=execute_with_shutdown):
            with patch('workers.video_job_worker.get_db', return_value=iter([mock_db])):
                worker._process_pending_jobs()

                # Should only process 2 jobs before stopping
                assert execution_count[0] == 2


class TestWorkerIntegration:
    """Integration tests for worker"""

    def test_worker_configuration_from_env(self):
        """Worker loads all configuration from environment variables"""
        env_vars = {
            'WORKER_POLL_INTERVAL': '60',
            'WORKER_MAX_RETRIES': '5',
            'OUTPUT_DIRECTORY': '/app/output',
            'OPENAI_API_KEY': 'sk-test-key'
        }

        with patch.dict('os.environ', env_vars):
            worker = VideoJobWorker(
                poll_interval=int(env_vars['WORKER_POLL_INTERVAL']),
                max_retries=int(env_vars['WORKER_MAX_RETRIES'])
            )

            assert worker.poll_interval == 60
            assert worker.max_retries == 5
            assert worker.output_dir == '/app/output'
            assert worker.openai_api_key == 'sk-test-key'

    @patch('workers.video_job_worker.get_db')
    @patch('workers.video_job_worker.VideoPipelineService')
    def test_worker_full_cycle(self, mock_pipeline_class, mock_get_db):
        """Worker completes full cycle: poll → execute → complete"""
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = iter([mock_db])

        mock_job = Mock(spec=VideoJob)
        mock_job.id = "integration-job"
        mock_job.status = VideoJobStatus.PLANNED
        mock_job.channel = Mock(name="Test Channel", brand_niche="Test")
        mock_job.target_duration_minutes = 70

        query_mock = Mock()
        query_mock.filter.return_value.order_by.return_value.all.return_value = [mock_job]
        mock_db.query.return_value = query_mock

        mock_pipeline = Mock()
        mock_pipeline.execute_pipeline.return_value = {
            'job_id': 'integration-job',
            'status': 'completed',
            'output_directory': '/output',
            'video_path': '/output/video.mp4',
            'completed': True
        }
        mock_pipeline_class.return_value = mock_pipeline

        # Run worker cycle
        worker = VideoJobWorker(openai_api_key="test-key")
        worker._process_pending_jobs()

        # Verify complete workflow
        mock_db.query.assert_called()
        mock_pipeline_class.assert_called_once()
        mock_pipeline.execute_pipeline.assert_called_once_with("integration-job")
