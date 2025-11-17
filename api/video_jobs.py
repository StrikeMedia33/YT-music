"""Video Job API Routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from models import VideoJob, VideoIdea, VideoJobIdea, get_db
from schemas import VideoJobCreate, VideoJobUpdate, VideoJobResponse, VideoJobDetail
from utils.media_manager import create_video_job_directory

router = APIRouter()

@router.post("/", response_model=VideoJobResponse, status_code=201)
def create_video_job(job: VideoJobCreate, db: Session = Depends(get_db)):
    """Create a new video job, optionally from an idea template"""
    idea_id = job.idea_id

    # Create the video job (exclude idea_id as it's not a VideoJob field)
    job_data = job.model_dump(exclude={'idea_id'})
    db_job = VideoJob(**job_data)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)

    # Create media directory structure for this job
    try:
        # Use niche_label as title if available, otherwise use job ID
        title = db_job.niche_label or f"video-job-{db_job.id}"
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
