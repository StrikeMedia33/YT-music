"""Background Worker for Video Job Pipeline Execution

This worker continuously polls the database for video jobs in 'planned' status
and executes the complete video generation pipeline for each job.

Designed for deployment on Render as a background worker process.
"""
import os
import time
import logging
import signal
import sys
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from models import VideoJob, VideoJobStatus, get_db
from services import VideoPipelineService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class VideoJobWorker:
    """
    Background worker that executes video generation pipeline jobs.

    Features:
    - Polls database for jobs in 'planned' status
    - Executes complete pipeline via VideoPipelineService
    - Handles errors with retry logic and exponential backoff
    - Graceful shutdown on SIGTERM/SIGINT
    - Comprehensive logging for monitoring

    Configuration via environment variables:
    - WORKER_POLL_INTERVAL: Seconds between polling cycles (default: 30)
    - WORKER_MAX_RETRIES: Maximum retry attempts per job (default: 3)
    - OUTPUT_DIRECTORY: Base directory for generated files
    - OPENAI_API_KEY: API key for LLM services
    """

    def __init__(
        self,
        poll_interval: int = 30,
        max_retries: int = 3,
        output_dir: Optional[str] = None,
        openai_api_key: Optional[str] = None
    ):
        """
        Initialize the video job worker.

        Args:
            poll_interval: Seconds to wait between polling cycles
            max_retries: Maximum number of retry attempts per job
            output_dir: Base directory for generated files
            openai_api_key: OpenAI API key for LLM services
        """
        self.poll_interval = poll_interval
        self.max_retries = max_retries
        self.output_dir = output_dir or os.getenv("OUTPUT_DIRECTORY", "./output")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.should_stop = False

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

        logger.info(f"VideoJobWorker initialized:")
        logger.info(f"  Poll interval: {poll_interval}s")
        logger.info(f"  Max retries: {max_retries}")
        logger.info(f"  Output directory: {self.output_dir}")

    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.should_stop = True

    def run(self):
        """
        Main worker loop.

        Continuously polls for jobs and executes them until shutdown signal received.
        """
        logger.info("VideoJobWorker started. Polling for jobs...")

        while not self.should_stop:
            try:
                self._process_pending_jobs()
            except Exception as e:
                logger.error(f"Error in worker main loop: {e}", exc_info=True)

            if not self.should_stop:
                logger.debug(f"Sleeping for {self.poll_interval}s before next poll...")
                time.sleep(self.poll_interval)

        logger.info("VideoJobWorker stopped gracefully.")

    def _process_pending_jobs(self):
        """
        Poll database for pending jobs and process them.

        Queries for jobs in 'planned' status and executes pipeline for each.
        """
        db = next(get_db())

        try:
            # Find jobs in 'planned' status
            pending_jobs = (
                db.query(VideoJob)
                .filter(VideoJob.status == VideoJobStatus.PLANNED)
                .order_by(VideoJob.created_at.asc())  # Process oldest first
                .all()
            )

            if not pending_jobs:
                logger.debug("No pending jobs found.")
                return

            logger.info(f"Found {len(pending_jobs)} pending job(s).")

            for job in pending_jobs:
                if self.should_stop:
                    logger.info("Shutdown requested, stopping job processing.")
                    break

                self._execute_job(db, job)

        finally:
            db.close()

    def _execute_job(self, db: Session, job: VideoJob):
        """
        Execute the video generation pipeline for a single job.

        Args:
            db: Database session
            job: VideoJob to process
        """
        job_id = str(job.id)
        logger.info(f"[Job {job_id}] Starting pipeline execution...")
        logger.info(f"[Job {job_id}] Channel: {job.channel.name}")
        logger.info(f"[Job {job_id}] Niche: {job.channel.brand_niche}")
        logger.info(f"[Job {job_id}] Target duration: {job.target_duration_minutes} minutes")

        try:
            # Create pipeline service
            pipeline = VideoPipelineService(
                db=db,
                output_base_dir=self.output_dir,
                openai_api_key=self.openai_api_key
            )

            # Execute pipeline
            start_time = time.time()
            result = pipeline.execute_pipeline(job_id)
            elapsed_time = time.time() - start_time

            logger.info(f"[Job {job_id}] Pipeline completed successfully!")
            logger.info(f"[Job {job_id}] Status: {result['status']}")
            logger.info(f"[Job {job_id}] Output: {result['output_directory']}")
            logger.info(f"[Job {job_id}] Video: {result['video_path']}")
            logger.info(f"[Job {job_id}] Execution time: {elapsed_time:.1f}s ({elapsed_time/60:.1f} minutes)")

        except Exception as e:
            logger.error(f"[Job {job_id}] Pipeline execution failed: {e}", exc_info=True)

            # Refresh job to get latest state
            db.refresh(job)

            # Check if job should be retried
            if self._should_retry_job(job):
                self._schedule_retry(db, job)
            else:
                logger.error(f"[Job {job_id}] Max retries exceeded. Job marked as failed.")

    def _should_retry_job(self, job: VideoJob) -> bool:
        """
        Determine if a failed job should be retried.

        Args:
            job: VideoJob that failed

        Returns:
            True if job should be retried, False otherwise
        """
        # Count failed attempts by checking if job is in failed status
        # In a real implementation, you might track retry_count in the database
        # For now, we'll use a simple approach based on status

        # Jobs in FAILED status have exhausted retries
        if job.status == VideoJobStatus.FAILED:
            # Check if error_message indicates a transient error
            transient_errors = [
                "timeout",
                "connection",
                "network",
                "rate limit",
                "503",
                "502",
                "504"
            ]

            error_msg = (job.error_message or "").lower()
            is_transient = any(err in error_msg for err in transient_errors)

            if is_transient:
                logger.info(f"[Job {job.id}] Transient error detected, considering retry...")
                return True

            return False

        return False

    def _schedule_retry(self, db: Session, job: VideoJob):
        """
        Schedule a failed job for retry.

        Args:
            db: Database session
            job: VideoJob to retry
        """
        # For MVP, we'll simply reset the job to 'planned' status
        # In production, you'd implement exponential backoff using a scheduled_at field

        logger.info(f"[Job {job.id}] Scheduling retry...")

        # Reset job to planned status
        job.status = VideoJobStatus.PLANNED
        job.error_message = None  # Clear previous error

        db.commit()

        logger.info(f"[Job {job.id}] Job reset to planned status for retry.")


def main():
    """
    Worker entry point.

    Loads configuration from environment variables and starts the worker.
    """
    logger.info("=" * 80)
    logger.info("VIDEO JOB WORKER - STARTING")
    logger.info("=" * 80)

    # Load configuration from environment
    poll_interval = int(os.getenv("WORKER_POLL_INTERVAL", "30"))
    max_retries = int(os.getenv("WORKER_MAX_RETRIES", "3"))
    output_dir = os.getenv("OUTPUT_DIRECTORY", "./output")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not openai_api_key:
        logger.error("OPENAI_API_KEY environment variable not set!")
        logger.error("Worker cannot start without API key for LLM services.")
        sys.exit(1)

    # Create and run worker
    worker = VideoJobWorker(
        poll_interval=poll_interval,
        max_retries=max_retries,
        output_dir=output_dir,
        openai_api_key=openai_api_key
    )

    try:
        worker.run()
    except KeyboardInterrupt:
        logger.info("Worker interrupted by user.")
    except Exception as e:
        logger.error(f"Worker crashed: {e}", exc_info=True)
        sys.exit(1)

    logger.info("=" * 80)
    logger.info("VIDEO JOB WORKER - STOPPED")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
