"""Idea Prompt Pydantic Schemas"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class IdeaPromptBase(BaseModel):
    music_prompts: List[str] = Field(default_factory=list)
    visual_prompts: List[str] = Field(default_factory=list)
    metadata_title: Optional[str] = Field(None, max_length=255)
    metadata_description: Optional[str] = None
    metadata_tags: List[str] = Field(default_factory=list)
    generation_params: Dict[str, Any] = Field(default_factory=dict)

    @field_validator('music_prompts')
    @classmethod
    def validate_music_prompts_count(cls, v):
        if v and len(v) not in [0, 20]:
            raise ValueError('Must have exactly 20 music prompts or none')
        return v

    @field_validator('visual_prompts')
    @classmethod
    def validate_visual_prompts_count(cls, v):
        if v and len(v) not in [0, 20]:
            raise ValueError('Must have exactly 20 visual prompts or none')
        return v


class IdeaPromptCreate(IdeaPromptBase):
    idea_id: str


class IdeaPromptUpdate(BaseModel):
    music_prompts: Optional[List[str]] = None
    visual_prompts: Optional[List[str]] = None
    metadata_title: Optional[str] = Field(None, max_length=255)
    metadata_description: Optional[str] = None
    metadata_tags: Optional[List[str]] = None
    generation_params: Optional[Dict[str, Any]] = None

    @field_validator('music_prompts')
    @classmethod
    def validate_music_prompts_count(cls, v):
        if v is not None and len(v) != 20:
            raise ValueError('Must have exactly 20 music prompts')
        return v

    @field_validator('visual_prompts')
    @classmethod
    def validate_visual_prompts_count(cls, v):
        if v is not None and len(v) != 20:
            raise ValueError('Must have exactly 20 visual prompts')
        return v


class IdeaPromptResponse(IdeaPromptBase):
    id: str
    idea_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
