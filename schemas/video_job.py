"""VideoJob Pydantic Schemas"""
from pydantic import BaseModel, Field, field_serializer
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from models import VideoJobStatus, VideoStatusDisplay

class VideoJobBase(BaseModel):
    niche_label: str = Field(..., min_length=1, max_length=255)
    mood_keywords: str = Field(..., min_length=1)
    target_duration_minutes: int = Field(..., ge=60, le=90)
    output_directory: str = Field(..., min_length=1)

class VideoJobCreate(VideoJobBase):
    channel_id: str
    idea_id: Optional[str] = None  # Optional link to video idea template

class VideoJobUpdate(BaseModel):
    status: Optional[VideoJobStatus] = None
    prompts_json: Optional[Dict[str, Any]] = None
    local_video_path: Optional[str] = None
    error_message: Optional[str] = None

class VideoJobResponse(VideoJobBase):
    id: UUID
    channel_id: UUID
    status: str
    prompts_json: Optional[Dict[str, Any]] = None
    local_video_path: Optional[str] = None
    error_message: Optional[str] = None
    youtube_video_id: Optional[str] = None
    youtube_url: Optional[str] = None
    scheduled_publish_date: Optional[datetime] = None
    is_draft: bool = False
    published_at: Optional[datetime] = None
    video_title: Optional[str] = None
    video_description: Optional[str] = None
    video_status: Optional[str] = None  # Computed VideoStatusDisplay value
    created_at: datetime
    updated_at: datetime

    @field_serializer('id', 'channel_id')
    def serialize_uuid(self, value: UUID) -> str:
        return str(value)

    class Config:
        from_attributes = True

class VideoJobDetail(VideoJobResponse):
    channel: Optional[Dict[str, Any]] = None
    audio_tracks: List[Dict[str, Any]] = []
    images: List[Dict[str, Any]] = []
    render_tasks: List[Dict[str, Any]] = []


# Video Publishing Schemas

class MarkAsDraftRequest(BaseModel):
    """Request to mark video as draft or remove draft status"""
    is_draft: bool


class ScheduleVideoRequest(BaseModel):
    """Request to schedule video for future publish"""
    scheduled_publish_date: datetime


class MarkAsPublishedRequest(BaseModel):
    """Request to mark video as published to YouTube"""
    youtube_video_id: str = Field(..., min_length=1)
    youtube_url: str = Field(..., min_length=1)
    published_at: Optional[datetime] = None


class VideoMetadataResponse(BaseModel):
    """Response containing generated YouTube metadata"""
    video_title: str
    video_description: str
    tags: List[str]
    niche_label: str
    mood_keywords: str
