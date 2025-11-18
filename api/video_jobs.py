"""Video Job API Routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from models import VideoJob, VideoIdea, VideoJobIdea, Channel, AudioTrack, Image, get_db
from schemas import (
    VideoJobCreate, VideoJobUpdate, VideoJobResponse, VideoJobDetail,
    GenerateTitleRequest, GenerateTitleResponse,
    UpdatePromptsRequest, RegeneratePromptRequest, RegeneratePromptResponse,
    SaveArrangementRequest, SaveArrangementResponse
)
from utils.media_manager import create_video_job_directory, sanitize_filename
from services.metadata_generator import MetadataGeneratorService
from services.prompt_generator import PromptGeneratorService

router = APIRouter()

@router.post("/", response_model=VideoJobResponse, status_code=201)
def create_video_job(job: VideoJobCreate, db: Session = Depends(get_db)):
    """Create a new video job, optionally from an idea template"""
    idea_id = job.idea_id
    video_title = job.video_title

    # Get channel information for directory naming
    channel = db.query(Channel).filter(Channel.id == job.channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    # Create the video job (exclude idea_id and video_title temporarily)
    job_data = job.model_dump(exclude={'idea_id', 'video_title'})
    db_job = VideoJob(**job_data)

    # Set video_title if provided
    if video_title:
        db_job.video_title = video_title

    db.add(db_job)
    db.commit()
    db.refresh(db_job)

    # Create media directory structure for this job
    try:
        # Use video_title if available, otherwise use niche_label or job ID
        title = video_title or db_job.niche_label or f"video-job-{db_job.id}"

        # Create structured directory: {channel_name}/{sanitized_title}/
        sanitized_channel = sanitize_filename(channel.name)
        sanitized_title = sanitize_filename(title)

        # Update output_directory to include channel hierarchy
        structured_path = f"{sanitized_channel}/{sanitized_title}"
        db_job.output_directory = structured_path

        # Create the directory structure
        create_video_job_directory(title, str(db_job.id))
    except Exception as e:
        # Log error but don't fail job creation
        print(f"Warning: Failed to create media directory for job {db_job.id}: {e}")

    # If idea_id was provided, create the link and increment usage
    if idea_id:
        idea = db.query(VideoIdea).filter(VideoIdea.id == idea_id).first()
        if idea:
            # Create link record
            link = VideoJobIdea(
                video_job_id=db_job.id,
                video_idea_id=idea_id,
                customizations_json={}
            )
            db.add(link)

            # Increment times_used counter
            idea.times_used += 1

            db.commit()

    return db_job

@router.get("/", response_model=List[VideoJobResponse])
def list_video_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    jobs = db.query(VideoJob).offset(skip).limit(limit).all()
    return jobs

@router.get("/{job_id}", response_model=VideoJobDetail)
def get_video_job(job_id: str, db: Session = Depends(get_db)):
    job = (
        db.query(VideoJob)
        .options(
            joinedload(VideoJob.channel),
            joinedload(VideoJob.audio_tracks),
            joinedload(VideoJob.images),
            joinedload(VideoJob.render_tasks)
        )
        .filter(VideoJob.id == job_id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Video job not found")
    return VideoJobDetail(
        **job.to_dict(include_relations=True)
    )

@router.put("/{job_id}", response_model=VideoJobResponse)
def update_video_job(job_id: str, job_update: VideoJobUpdate, db: Session = Depends(get_db)):
    job = db.query(VideoJob).filter(VideoJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Video job not found")
    for key, value in job_update.model_dump(exclude_unset=True).items():
        setattr(job, key, value)
    db.commit()
    db.refresh(job)
    return job

@router.post("/{job_id}/cancel", response_model=VideoJobResponse)
def cancel_video_job(job_id: str, db: Session = Depends(get_db)):
    """Cancel a video job by setting its status to CANCELLED"""
    from models import VideoJobStatus

    job = db.query(VideoJob).filter(VideoJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Video job not found")

    # Don't allow canceling already completed or failed jobs
    if job.status in [VideoJobStatus.COMPLETED, VideoJobStatus.FAILED, VideoJobStatus.CANCELLED]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel job with status '{job.status.value}'"
        )

    # Set status to cancelled
    job.status = VideoJobStatus.CANCELLED
    job.error_message = "Job cancelled by user"
    db.commit()
    db.refresh(job)
    return job


# New Workflow Endpoints for Enhanced Video Job Creation

@router.post("/generate-title", response_model=GenerateTitleResponse)
def generate_title(request: GenerateTitleRequest, db: Session = Depends(get_db)):
    """
    Generate a video title from channel, niche, and mood using LLM.

    Also suggests an output directory based on channel name and generated title.
    """
    # Get channel to extract name for directory path
    channel = db.query(Channel).filter(Channel.id == request.channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    # Determine niche and mood for title generation
    niche = request.niche_label or channel.brand_niche or "Background Music"
    mood = request.mood_keywords or "relaxing, ambient"

    # Parse mood keywords (handle comma-separated string)
    mood_list = [m.strip() for m in mood.split(",") if m.strip()]

    try:
        # Initialize metadata generator
        metadata_service = MetadataGeneratorService()

        # Generate title
        title = metadata_service.generate_title(niche, mood_list)

        # Generate suggested output directory
        # Format: {channel_name}/{sanitized_title}
        sanitized_channel = sanitize_filename(channel.name)
        sanitized_title = sanitize_filename(title)
        output_directory = f"{sanitized_channel}/{sanitized_title}"

        return GenerateTitleResponse(
            title=title,
            output_directory=output_directory
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Title generation failed: {str(e)}"
        )


@router.patch("/{job_id}/prompts", response_model=VideoJobResponse)
def update_prompts(job_id: str, request: UpdatePromptsRequest, db: Session = Depends(get_db)):
    """
    Update music and/or visual prompts for a video job.

    Allows editing individual prompts before asset generation begins.
    """
    job = db.query(VideoJob).filter(VideoJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Video job not found")

    # Get current prompts
    prompts_json = job.prompts_json or {}

    # Update music prompts if provided
    if request.music_prompts is not None:
        if len(request.music_prompts) != 20:
            raise HTTPException(
                status_code=400,
                detail="music_prompts must contain exactly 20 prompts"
            )
        prompts_json["music_prompts"] = request.music_prompts

    # Update visual prompts if provided
    if request.visual_prompts is not None:
        if len(request.visual_prompts) != 20:
            raise HTTPException(
                status_code=400,
                detail="visual_prompts must contain exactly 20 prompts"
            )
        prompts_json["visual_prompts"] = request.visual_prompts

    # Save updated prompts
    job.prompts_json = prompts_json
    db.commit()
    db.refresh(job)

    return job


@router.post("/{job_id}/regenerate-prompt", response_model=RegeneratePromptResponse)
def regenerate_prompt(
    job_id: str,
    request: RegeneratePromptRequest,
    db: Session = Depends(get_db)
):
    """
    Regenerate a specific prompt (music or visual) using LLM.

    Useful when user wants to refresh a single prompt without regenerating all 20.
    """
    job = db.query(VideoJob).filter(VideoJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Video job not found")

    # Validate prompt index
    if not (0 <= request.prompt_index < 20):
        raise HTTPException(
            status_code=400,
            detail="prompt_index must be between 0 and 19"
        )

    try:
        # Initialize prompt generator
        prompt_service = PromptGeneratorService()

        # Parse mood keywords
        mood_list = [m.strip() for m in job.mood_keywords.split(",") if m.strip()]

        if request.prompt_type == "music":
            # Generate a single music prompt
            # For now, generate all 20 and return the requested index
            # (Ideally we'd have a method to generate just one)
            all_prompts = prompt_service.generate_music_prompts(
                niche_label=job.niche_label,
                mood_keywords=mood_list,
                target_duration_minutes=job.target_duration_minutes
            )
            new_prompt = all_prompts[request.prompt_index]

            # Update the specific prompt in the job
            prompts_json = job.prompts_json or {}
            music_prompts = prompts_json.get("music_prompts", [])
            if len(music_prompts) > request.prompt_index:
                music_prompts[request.prompt_index] = new_prompt
                prompts_json["music_prompts"] = music_prompts
                job.prompts_json = prompts_json
                db.commit()

        elif request.prompt_type == "visual":
            # Generate a single visual prompt
            # Get current music prompts for context
            prompts_json = job.prompts_json or {}
            music_prompts = prompts_json.get("music_prompts", [])

            all_visual_prompts = prompt_service.generate_visual_prompts(
                niche_label=job.niche_label,
                mood_keywords=mood_list,
                music_prompts=music_prompts
            )
            new_prompt = all_visual_prompts[request.prompt_index]

            # Update the specific prompt
            visual_prompts = prompts_json.get("visual_prompts", [])
            if len(visual_prompts) > request.prompt_index:
                visual_prompts[request.prompt_index] = new_prompt
                prompts_json["visual_prompts"] = visual_prompts
                job.prompts_json = prompts_json
                db.commit()

        else:
            raise HTTPException(
                status_code=400,
                detail="prompt_type must be 'music' or 'visual'"
            )

        return RegeneratePromptResponse(
            new_prompt=new_prompt,
            prompt_index=request.prompt_index,
            prompt_type=request.prompt_type
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prompt regeneration failed: {str(e)}"
        )


@router.patch("/{job_id}/arrangement", response_model=SaveArrangementResponse)
def save_arrangement(
    job_id: str,
    request: SaveArrangementRequest,
    db: Session = Depends(get_db)
):
    """
    Save the asset arrangement for a video job.

    Updates the display_order field for all audio tracks and images based on
    the user's custom arrangement. This determines the final order in the rendered video.
    """
    # Get the video job
    job = db.query(VideoJob).filter(VideoJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Video job not found")

    # Validate that we have exactly 20 pairs
    if len(request.pairs) != 20:
        raise HTTPException(
            status_code=400,
            detail="Must provide exactly 20 asset pairs"
        )

    # Validate positions are unique and complete (1-20)
    positions = [pair.position for pair in request.pairs]
    if sorted(positions) != list(range(1, 21)):
        raise HTTPException(
            status_code=400,
            detail="Positions must be unique and cover 1-20"
        )

    try:
        total_duration = 0.0

        # Update each audio track and image with display_order
        for pair in request.pairs:
            # Update audio track
            audio_track = db.query(AudioTrack).filter(AudioTrack.id == pair.audio_track_id).first()
            if not audio_track:
                raise HTTPException(
                    status_code=404,
                    detail=f"Audio track {pair.audio_track_id} not found"
                )
            if audio_track.video_job_id != job.id:
                raise HTTPException(
                    status_code=400,
                    detail=f"Audio track {pair.audio_track_id} does not belong to this job"
                )
            audio_track.display_order = pair.position

            # Add to total duration
            total_duration += float(audio_track.duration_seconds)

            # Update image
            image = db.query(Image).filter(Image.id == pair.image_id).first()
            if not image:
                raise HTTPException(
                    status_code=404,
                    detail=f"Image {pair.image_id} not found"
                )
            if image.video_job_id != job.id:
                raise HTTPException(
                    status_code=400,
                    detail=f"Image {pair.image_id} does not belong to this job"
                )
            image.display_order = pair.position

        db.commit()

        return SaveArrangementResponse(
            success=True,
            total_duration_seconds=total_duration
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save arrangement: {str(e)}"
        )
