"""Video Job API Routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models import VideoJob, get_db
from schemas import VideoJobCreate, VideoJobUpdate, VideoJobResponse, VideoJobDetail

router = APIRouter()

@router.post("/", response_model=VideoJobResponse, status_code=201)
def create_video_job(job: VideoJobCreate, db: Session = Depends(get_db)):
    db_job = VideoJob(**job.model_dump())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

@router.get("/", response_model=List[VideoJobResponse])
def list_video_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    jobs = db.query(VideoJob).offset(skip).limit(limit).all()
    return jobs

@router.get("/{job_id}", response_model=VideoJobDetail)
def get_video_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(VideoJob).filter(VideoJob.id == job_id).first()
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
