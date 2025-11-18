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
    video_title: Optional[str] = None  # Optional title (can be auto-generated)

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


# New Workflow Schemas for Enhanced Video Job Creation

class GenerateTitleRequest(BaseModel):
    """Request to generate a video title from channel and niche/mood"""
    channel_id: str
    niche_label: Optional[str] = None
    mood_keywords: Optional[str] = None


class GenerateTitleResponse(BaseModel):
    """Response containing generated title and suggested output directory"""
    title: str
    output_directory: str


class UpdatePromptsRequest(BaseModel):
    """Request to update music and/or visual prompts"""
    music_prompts: Optional[List[str]] = None  # Array of 20 prompts
    visual_prompts: Optional[List[str]] = None  # Array of 20 prompts


class RegeneratePromptRequest(BaseModel):
    """Request to regenerate a specific prompt"""
    prompt_type: str = Field(..., pattern="^(music|visual)$")
    prompt_index: int = Field(..., ge=0, lt=20)


class RegeneratePromptResponse(BaseModel):
    """Response containing regenerated prompt"""
    new_prompt: str
    prompt_index: int
    prompt_type: str


# Asset Arrangement Schemas

class AssetPair(BaseModel):
    """Asset pair for arrangement"""
    position: int = Field(..., ge=1, le=20)
    audio_track_id: str
    image_id: str


class SaveArrangementRequest(BaseModel):
    """Request to save asset arrangement"""
    pairs: List[AssetPair] = Field(..., min_length=20, max_length=20)


class SaveArrangementResponse(BaseModel):
    """Response after saving arrangement"""
    success: bool
    total_duration_seconds: float
