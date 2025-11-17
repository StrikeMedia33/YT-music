"""VideoJob Pydantic Schemas"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from models import VideoJobStatus

class VideoJobBase(BaseModel):
    niche_label: str = Field(..., min_length=1, max_length=255)
    mood_keywords: str = Field(..., min_length=1)
    target_duration_minutes: int = Field(..., ge=60, le=90)
    output_directory: str = Field(..., min_length=1)

class VideoJobCreate(VideoJobBase):
    channel_id: str

class VideoJobUpdate(BaseModel):
    status: Optional[VideoJobStatus] = None
    prompts_json: Optional[Dict[str, Any]] = None
    local_video_path: Optional[str] = None
    error_message: Optional[str] = None

class VideoJobResponse(VideoJobBase):
    id: str
    channel_id: str
    status: str
    prompts_json: Optional[Dict[str, Any]] = None
    local_video_path: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class VideoJobDetail(VideoJobResponse):
    audio_tracks: List[Dict[str, Any]] = []
    images: List[Dict[str, Any]] = []
    render_tasks: List[Dict[str, Any]] = []
