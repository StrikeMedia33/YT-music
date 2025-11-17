"""Genre Pydantic Schemas"""
from pydantic import BaseModel, Field, field_serializer
from typing import Optional, Union
from datetime import datetime
from uuid import UUID


class GenreBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')  # Hex color validation
    icon_name: Optional[str] = Field(None, max_length=50)
    default_duration_minutes: int = Field(70, ge=60, le=120)
    sort_order: int = Field(0, ge=0)


class GenreCreate(GenreBase):
    pass


class GenreUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    icon_name: Optional[str] = Field(None, max_length=50)
    default_duration_minutes: Optional[int] = Field(None, ge=60, le=120)
    is_active: Optional[bool] = None
    sort_order: Optional[int] = Field(None, ge=0)


class GenreResponse(GenreBase):
    id: Union[str, UUID]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @field_serializer('id')
    def serialize_id(self, value: Union[str, UUID], _info) -> str:
        """Convert UUID to string"""
        return str(value)

    class Config:
        from_attributes = True


class GenreWithStats(GenreResponse):
    """Genre with additional statistics"""
    idea_count: int = 0
    active_idea_count: int = 0
