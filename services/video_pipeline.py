"""Video Pipeline Service - Orchestrates complete video generation workflow"""
import json
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session

from models import VideoJob, AudioTrack, Image, RenderTask, VideoJobStatus, get_db
from providers import get_music_provider, get_visual_provider, FFmpegRenderer
from .prompt_generator import PromptGeneratorService
from .metadata_generator import MetadataGeneratorService


class VideoPipelineService:
    """
    Orchestrates the complete video generation pipeline.

    5-step process:
    1. Generate prompts (20 music + 20 visual)
    2. Generate 20 music tracks (3-4 minutes each)
    3. Generate 20 visuals (matched to tracks)
    4. Render video (concatenate audio with crossfades, pair visuals)
    5. Generate metadata (title, description with timestamps, tags)

    Each step updates database and job status. Pipeline is idempotent.
    """

    def __init__(
        self,
        db: Session,
        output_base_dir: Path,
        openai_api_key: Optional[str] = None
    ):
        """
        Initialize the video pipeline service.

        Args:
            db: SQLAlchemy database session
            output_base_dir: Base directory for all generated files
            openai_api_key: OpenAI API key for LLM services
        """
        self.db = db
        self.output_base_dir = Path(output_base_dir)
        self.output_base_dir.mkdir(parents=True, exist_ok=True)

        # Initialize services
        self.prompt_service = PromptGeneratorService(api_key=openai_api_key)
        self.metadata_service = MetadataGeneratorService(api_key=openai_api_key)
        self.music_provider = get_music_provider()
        self.visual_provider = get_visual_provider()
        self.renderer = FFmpegRenderer()

    def execute_pipeline(self, job_id: str) -> Dict[str, Any]:
        """
        Execute the complete video generation pipeline for a job.

        Args:
            job_id: UUID of the video job to process

        Returns:
            Dict with pipeline execution summary

        Raises:
            ValueError: If job not found or in invalid state
            RuntimeError: If pipeline step fails
        """
        # Get job from database
        job = self.db.query(VideoJob).filter(VideoJob.id == job_id).first()
        if not job:
            raise ValueError(f"Job {job_id} not found")

        # Create job-specific output directory
        job_output_dir = self.output_base_dir / str(job.id)
        job_output_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Execute pipeline steps
            if job.status == VideoJobStatus.PLANNED:
                self._step_1_generate_prompts(job, job_output_dir)

            if job.status == VideoJobStatus.GENERATING_MUSIC:
                self._step_2_generate_music(job, job_output_dir)

            if job.status == VideoJobStatus.GENERATING_IMAGE:
                self._step_3_generate_visuals(job, job_output_dir)

            if job.status == VideoJobStatus.RENDERING:
                self._step_4_render_video(job, job_output_dir)

            if job.status == VideoJobStatus.READY_FOR_EXPORT:
                self._step_5_generate_metadata(job, job_output_dir)

            # Job should now be completed
            self.db.commit()

            return {
                "job_id": str(job.id),
                "status": job.status.value,
                "output_directory": str(job_output_dir),
                "video_path": job.local_video_path,
                "completed": job.status == VideoJobStatus.COMPLETED
            }

        except Exception as e:
            # Mark job as failed
            job.status = VideoJobStatus.FAILED
            job.error_message = str(e)
            self.db.commit()
            raise RuntimeError(f"Pipeline failed for job {job_id}: {e}")

    def _step_1_generate_prompts(self, job: VideoJob, output_dir: Path):
        """
        Step 1: Generate 20 music prompts and 20 visual prompts.

        Updates:
        - video_jobs.prompts_json
        - video_jobs.status → generating_music
        """
        print(f"[Step 1] Generating prompts for job {job.id}...")

        # Generate prompts
        prompts = self.prompt_service.generate_prompts(
            niche_label=job.channel.brand_niche,
            mood_keywords=["ambient", "calm", "focused"],  # TODO: Make configurable
            target_duration_minutes=job.target_duration_minutes
        )

        # Store in database
        job.prompts_json = prompts
        job.status = VideoJobStatus.GENERATING_MUSIC
        self.db.commit()

        print(f"[Step 1] Generated {len(prompts['music_prompts'])} music prompts and {len(prompts['visual_prompts'])} visual prompts")

    def _step_2_generate_music(self, job: VideoJob, output_dir: Path):
        """
        Step 2: Generate 20 unique music tracks (3-4 minutes each).

        Creates:
        - 20 audio files in output_dir/audio/
        - 20 audio_tracks database records

        Updates:
        - video_jobs.status → generating_image
        """
        print(f"[Step 2] Generating 20 music tracks for job {job.id}...")

        # Create audio output directory
        audio_dir = output_dir / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)

        # Get music prompts from stored JSON
        music_prompts = job.prompts_json["music_prompts"]
        if len(music_prompts) != 20:
            raise ValueError(f"Expected 20 music prompts, got {len(music_prompts)}")

        # Calculate duration per track
        total_duration = job.target_duration_minutes
        duration_per_track = total_duration / 20.0  # 3-4 minutes typical

        # Generate each track
        for i, prompt in enumerate(music_prompts, 1):
            print(f"  Generating track {i}/20...")

            # Generate track
            track_result = self.music_provider.generate_track(
                prompt=prompt,
                duration_minutes=duration_per_track,
                order_index=i,
                output_dir=audio_dir
            )

            # Create database record
            from models import MusicProvider as MusicProviderEnum
            audio_track = AudioTrack(
                video_job_id=job.id,
                order_index=i,
                local_file_path=track_result["file_path"],
                duration_seconds=track_result["duration_seconds"],
                prompt_text=prompt,
                provider=MusicProviderEnum(track_result["metadata"]["provider"])
            )
            self.db.add(audio_track)

        # Update job status
        job.status = VideoJobStatus.GENERATING_IMAGE
        self.db.commit()

        print(f"[Step 2] Generated 20 music tracks")

    def _step_3_generate_visuals(self, job: VideoJob, output_dir: Path):
        """
        Step 3: Generate 20 unique visuals matched to music tracks.

        Creates:
        - 20 visual files in output_dir/visuals/
        - 20 images database records

        Updates:
        - video_jobs.status → rendering
        """
        print(f"[Step 3] Generating 20 visuals for job {job.id}...")

        # Create visuals output directory
        visual_dir = output_dir / "visuals"
        visual_dir.mkdir(parents=True, exist_ok=True)

        # Get visual prompts from stored JSON
        visual_prompts = job.prompts_json["visual_prompts"]
        if len(visual_prompts) != 20:
            raise ValueError(f"Expected 20 visual prompts, got {len(visual_prompts)}")

        # Generate each visual
        for i, prompt in enumerate(visual_prompts, 1):
            print(f"  Generating visual {i}/20...")

            # Generate visual
            visual_result = self.visual_provider.generate_visual(
                prompt=prompt,
                order_index=i,
                output_dir=visual_dir
            )

            # Create database record
            from models import VisualProvider as VisualProviderEnum
            image = Image(
                video_job_id=job.id,
                order_index=i,  # Matches corresponding audio track
                local_file_path=visual_result["file_path"],
                prompt_text=prompt,
                provider=VisualProviderEnum(visual_result["metadata"]["provider"])
            )
            self.db.add(image)

        # Update job status
        job.status = VideoJobStatus.RENDERING
        self.db.commit()

        print(f"[Step 3] Generated 20 visuals")

    def _step_4_render_video(self, job: VideoJob, output_dir: Path):
        """
        Step 4: Render final video with visual-audio pairing.

        Creates:
        - Final MP4 video in output_dir/
        - render_tasks database record

        Updates:
        - video_jobs.local_video_path
        - video_jobs.status → ready_for_export
        """
        print(f"[Step 4] Rendering video for job {job.id}...")

        # Get all audio tracks in order
        audio_tracks = (
            self.db.query(AudioTrack)
            .filter(AudioTrack.video_job_id == job.id)
            .order_by(AudioTrack.order_index)
            .all()
        )

        if len(audio_tracks) != 20:
            raise ValueError(f"Expected 20 audio tracks, got {len(audio_tracks)}")

        # Get all visuals in order
        visuals = (
            self.db.query(Image)
            .filter(Image.video_job_id == job.id)
            .order_by(Image.order_index)
            .all()
        )

        if len(visuals) != 20:
            raise ValueError(f"Expected 20 visuals, got {len(visuals)}")

        # Prepare data for renderer
        audio_tracks_data = [
            {
                "file_path": track.local_file_path,
                "duration_seconds": float(track.duration_seconds),
                "order_index": track.order_index
            }
            for track in audio_tracks
        ]

        visuals_data = [
            {
                "file_path": visual.local_file_path,
                "order_index": visual.order_index
            }
            for visual in visuals
        ]

        # Define output path
        output_video_path = output_dir / f"video_{job.id}.mp4"

        # Render video
        print(f"  Rendering {len(audio_tracks)} tracks with {len(visuals)} visuals...")

        def progress_callback(progress: float):
            print(f"  Rendering progress: {progress*100:.1f}%")

        render_result = self.renderer.render_video(
            audio_tracks=audio_tracks_data,
            visuals=visuals_data,
            output_path=output_video_path,
            crossfade_duration=2.0,
            progress_callback=progress_callback
        )

        # Create render_tasks record
        render_task = RenderTask(
            video_job_id=job.id,
            local_video_path=render_result["output_path"],
            resolution="1920x1080",
            duration_seconds=render_result["duration_seconds"],
            status="completed"
        )
        self.db.add(render_task)

        # Update job
        job.local_video_path = render_result["output_path"]
        job.status = VideoJobStatus.READY_FOR_EXPORT
        self.db.commit()

        print(f"[Step 4] Video rendered: {render_result['output_path']}")
        print(f"  Duration: {render_result['duration_seconds']/60:.1f} minutes")
        print(f"  Size: {render_result['file_size_mb']:.1f} MB")

    def _step_5_generate_metadata(self, job: VideoJob, output_dir: Path):
        """
        Step 5: Generate YouTube metadata (title, description, tags).

        Creates:
        - Metadata text file in output_dir/

        Updates:
        - video_jobs.status → completed
        """
        print(f"[Step 5] Generating metadata for job {job.id}...")

        # Get all audio tracks for metadata
        audio_tracks = (
            self.db.query(AudioTrack)
            .filter(AudioTrack.video_job_id == job.id)
            .order_by(AudioTrack.order_index)
            .all()
        )

        # Prepare track data
        track_titles = [track.prompt_text for track in audio_tracks]
        track_durations = [float(track.duration_seconds) for track in audio_tracks]

        # Generate metadata
        metadata = self.metadata_service.generate_metadata(
            niche_label=job.channel.brand_niche,
            mood_keywords=["ambient", "calm", "focused"],  # TODO: Make configurable
            track_titles=track_titles,
            track_durations=track_durations
        )

        # Save metadata to file
        metadata_path = output_dir / "youtube_metadata.txt"
        self.metadata_service.save_metadata_to_file(metadata, metadata_path)

        # Update job status to completed
        job.status = VideoJobStatus.COMPLETED
        self.db.commit()

        print(f"[Step 5] Metadata generated and saved to {metadata_path}")
        print(f"  Title: {metadata['title']}")
        print(f"  Tags: {len(metadata['tags'])} tags")
        print(f"\n✅ Pipeline completed for job {job.id}!")
