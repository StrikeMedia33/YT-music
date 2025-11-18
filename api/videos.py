"""
Videos API Endpoints
Manages completed videos and publishing workflow
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from uuid import UUID

from models import get_db, VideoJob, VideoJobStatus, VideoStatusDisplay
from schemas.video_job import (
    VideoJobResponse,
    VideoJobDetail,
    MarkAsDraftRequest,
    ScheduleVideoRequest,
    MarkAsPublishedRequest,
    VideoMetadataResponse,
)

router = APIRouter(prefix="/api/videos", tags=["videos"])


@router.get("/", response_model=List[VideoJobResponse])
def list_videos(
    channel_id: Optional[str] = Query(None, description="Filter by channel ID"),
    video_status: Optional[str] = Query(None, description="Filter by video status (production, draft, scheduled, published)"),
    search: Optional[str] = Query(None, description="Search by title or niche"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    List all completed videos (ready_for_export or completed status).

    Query params:
    - channel_id: Filter by specific channel
    - video_status: Filter by display status (production, draft, scheduled, published)
    - search: Search in video_title or niche_label
    - limit: Max results to return
    - offset: Pagination offset
    """
    # Base query: only show videos that are ready or completed
    query = db.query(VideoJob).filter(
        or_(
            VideoJob.status == VideoJobStatus.READY_FOR_EXPORT,
            VideoJob.status == VideoJobStatus.COMPLETED,
        )
    )

    # Filter by channel
    if channel_id:
        try:
            query = query.filter(VideoJob.channel_id == UUID(channel_id))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid channel_id format")

    # Filter by video status (computed status)
    if video_status:
        try:
            status_filter = VideoStatusDisplay(video_status)
            if status_filter == VideoStatusDisplay.PUBLISHED:
                query = query.filter(VideoJob.youtube_video_id.isnot(None))
            elif status_filter == VideoStatusDisplay.DRAFT:
                query = query.filter(VideoJob.is_draft == True)
            elif status_filter == VideoStatusDisplay.SCHEDULED:
                query = query.filter(
                    VideoJob.scheduled_publish_date.isnot(None),
                    VideoJob.youtube_video_id.is_(None)
                )
            elif status_filter == VideoStatusDisplay.PRODUCTION:
                query = query.filter(
                    VideoJob.status == VideoJobStatus.READY_FOR_EXPORT,
                    VideoJob.is_draft == False,
                    VideoJob.youtube_video_id.is_(None),
                    VideoJob.scheduled_publish_date.is_(None)
                )
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid video_status. Must be one of: production, draft, scheduled, published"
            )

    # Search by title or niche
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                VideoJob.video_title.ilike(search_term),
                VideoJob.niche_label.ilike(search_term)
            )
        )

    # Order by created_at descending (newest first)
    query = query.order_by(VideoJob.created_at.desc())

    # Apply pagination
    jobs = query.offset(offset).limit(limit).all()

    # Convert to dictionaries with video_status
    return [VideoJobResponse(**job.to_dict()) for job in jobs]


@router.get("/{video_id}", response_model=VideoJobDetail)
def get_video(video_id: str, db: Session = Depends(get_db)):
    """Get details for a specific video"""
    try:
        job_uuid = UUID(video_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid video ID format")

    job = db.query(VideoJob).filter(VideoJob.id == job_uuid).first()
    if not job:
        raise HTTPException(status_code=404, detail="Video not found")

    # Only allow access to ready/completed videos
    if job.status not in [VideoJobStatus.READY_FOR_EXPORT, VideoJobStatus.COMPLETED]:
        raise HTTPException(
            status_code=400,
            detail="Video is not ready yet. Check video jobs page for status."
        )

    return VideoJobDetail(**job.to_dict(include_relations=True))


@router.put("/{video_id}/draft", response_model=VideoJobResponse)
def mark_as_draft(
    video_id: str,
    request: MarkAsDraftRequest,
    db: Session = Depends(get_db),
):
    """Mark video as draft or remove draft status"""
    try:
        job_uuid = UUID(video_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid video ID format")

    job = db.query(VideoJob).filter(VideoJob.id == job_uuid).first()
    if not job:
        raise HTTPException(status_code=404, detail="Video not found")

    # Update draft status
    job.mark_as_draft(request.is_draft)
    db.commit()
    db.refresh(job)

    return VideoJobResponse(**job.to_dict())


@router.put("/{video_id}/schedule", response_model=VideoJobResponse)
def schedule_video(
    video_id: str,
    request: ScheduleVideoRequest,
    db: Session = Depends(get_db),
):
    """Schedule video for future publish"""
    try:
        job_uuid = UUID(video_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid video ID format")

    job = db.query(VideoJob).filter(VideoJob.id == job_uuid).first()
    if not job:
        raise HTTPException(status_code=404, detail="Video not found")

    # Schedule the video
    job.schedule(request.scheduled_publish_date)
    db.commit()
    db.refresh(job)

    return VideoJobResponse(**job.to_dict())


@router.put("/{video_id}/publish", response_model=VideoJobResponse)
def mark_as_published(
    video_id: str,
    request: MarkAsPublishedRequest,
    db: Session = Depends(get_db),
):
    """Mark video as published to YouTube"""
    try:
        job_uuid = UUID(video_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid video ID format")

    job = db.query(VideoJob).filter(VideoJob.id == job_uuid).first()
    if not job:
        raise HTTPException(status_code=404, detail="Video not found")

    # Mark as published
    job.mark_as_published(
        youtube_video_id=request.youtube_video_id,
        youtube_url=request.youtube_url,
        published_at=request.published_at,
    )
    db.commit()
    db.refresh(job)

    return VideoJobResponse(**job.to_dict())


@router.get("/{video_id}/metadata", response_model=VideoMetadataResponse)
def get_video_metadata(video_id: str, db: Session = Depends(get_db)):
    """
    Get generated YouTube metadata for manual upload.
    Returns title, description, and tags.
    """
    try:
        job_uuid = UUID(video_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid video ID format")

    job = db.query(VideoJob).filter(VideoJob.id == job_uuid).first()
    if not job:
        raise HTTPException(status_code=404, detail="Video not found")

    # Generate metadata if not already generated
    if not job.video_title:
        # Use niche_label as fallback title
        job.video_title = f"{job.niche_label} | {job.target_duration_minutes} Minute Music Mix"

    if not job.video_description:
        # Generate basic description
        mood_list = job.mood_keywords.replace(',', '\n-')
        job.video_description = f"""Enjoy this {job.target_duration_minutes}-minute {job.niche_label} music mix.

Perfect for:
- {mood_list}

🎵 This video features 20 unique AI-generated tracks, each with custom visuals.

⚠️ IMPORTANT: When uploading to YouTube, enable the "Altered or synthetic content" checkbox in YouTube Studio under Video Details > Advanced Settings.

#music #{job.niche_label.replace(' ', '')}"""

        db.commit()
        db.refresh(job)

    # Generate tags from mood keywords and niche
    tags = [job.niche_label]
    tags.extend([keyword.strip() for keyword in job.mood_keywords.split(',')])
    tags.append("AI Generated Music")
    tags.append("Background Music")

    return VideoMetadataResponse(
        video_title=job.video_title,
        video_description=job.video_description,
        tags=tags[:15],  # YouTube allows max 15 tags
        niche_label=job.niche_label,
        mood_keywords=job.mood_keywords,
    )
