"""Channel Pydantic Schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ChannelBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    youtube_channel_id: Optional[str] = Field(None, max_length=100)
    brand_niche: str = Field(..., min_length=1, max_length=255)

class ChannelCreate(ChannelBase):
    pass

class ChannelUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    youtube_channel_id: Optional[str] = Field(None, max_length=100)
    brand_niche: Optional[str] = Field(None, min_length=1, max_length=255)
    is_active: Optional[bool] = None

class ChannelResponse(ChannelBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
