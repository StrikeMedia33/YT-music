"""Video Idea Pydantic Schemas"""
from pydantic import BaseModel, Field, field_serializer
from typing import Optional, List, Union
from datetime import datetime
from uuid import UUID
from .idea_prompt import IdeaPromptResponse
from .genre import GenreResponse


class VideoIdeaBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    genre_id: Union[str, UUID]
    niche_label: str = Field(..., min_length=1, max_length=255)
    mood_tags: List[str] = Field(default_factory=list)
    target_duration_minutes: int = Field(70, ge=60, le=120)
    num_tracks: int = Field(20, ge=10, le=30)

    @field_serializer('genre_id')
    def serialize_genre_id(self, value: Union[str, UUID], _info) -> str:
        """Convert UUID to string"""
        return str(value)


class VideoIdeaCreate(VideoIdeaBase):
    """Schema for creating a new video idea"""
    is_template: bool = True


class VideoIdeaUpdate(BaseModel):
    """Schema for updating a video idea"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    genre_id: Optional[Union[str, UUID]] = None
    niche_label: Optional[str] = Field(None, min_length=1, max_length=255)
    mood_tags: Optional[List[str]] = None
    target_duration_minutes: Optional[int] = Field(None, ge=60, le=120)
    num_tracks: Optional[int] = Field(None, ge=10, le=30)
    is_template: Optional[bool] = None
    is_archived: Optional[bool] = None

    @field_serializer('genre_id')
    def serialize_genre_id(self, value: Optional[Union[str, UUID]], _info) -> Optional[str]:
        """Convert UUID to string"""
        return str(value) if value else None


class VideoIdeaResponse(VideoIdeaBase):
    """Basic video idea response (for list views)"""
    id: Union[str, UUID]
    is_template: bool
    is_archived: bool
    times_used: int
    created_at: datetime
    updated_at: datetime

    @field_serializer('id')
    def serialize_id(self, value: Union[str, UUID], _info) -> str:
        """Convert UUID to string"""
        return str(value)

    class Config:
        from_attributes = True


class VideoIdeaDetail(VideoIdeaResponse):
    """Detailed video idea response (includes prompts and genre)"""
    genre: Optional[GenreResponse] = None
    prompts: Optional[IdeaPromptResponse] = None


class VideoIdeaWithGenre(VideoIdeaResponse):
    """Video idea with nested genre information"""
    genre: GenreResponse

    class Config:
        from_attributes = True


class VideoIdeaCloneRequest(BaseModel):
    """Request schema for cloning an idea"""
    new_title: Optional[str] = Field(None, min_length=1, max_length=255)
    modifications: Optional[dict] = None


class VideoIdeaSearchParams(BaseModel):
    """Search/filter parameters for video ideas"""
    genre_id: Optional[Union[str, UUID]] = None
    search: Optional[str] = None  # Search in title/description
    mood_tags: Optional[List[str]] = None
    is_template: Optional[bool] = None
    is_archived: Optional[bool] = False
    sort_by: str = Field('created_at', pattern='^(created_at|title|times_used)$')
    sort_order: str = Field('desc', pattern='^(asc|desc)$')
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)

    @field_serializer('genre_id')
    def serialize_genre_id(self, value: Optional[Union[str, UUID]], _info) -> Optional[str]:
        """Convert UUID to string"""
        return str(value) if value else None
