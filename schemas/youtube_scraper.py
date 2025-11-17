"""YouTube Scraper Pydantic Schemas"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime


class ChannelDiscoverRequest(BaseModel):
    """Request to discover a YouTube channel"""
    channel_url: str = Field(
        ...,
        description="YouTube channel URL in any format",
        min_length=1
    )


class ChannelDiscoverResponse(BaseModel):
    """Response from channel discovery"""
    success: bool
    channel_id: Optional[str] = None
    channel_name: Optional[str] = None
    channel_url: Optional[str] = None
    description: Optional[str] = None
    rss_feed_url: Optional[str] = None
    error: Optional[str] = None


class ChannelScrapeRequest(BaseModel):
    """Request to scrape a YouTube channel"""
    channel_url: str = Field(
        ...,
        description="YouTube channel URL in any format",
        min_length=1
    )
    video_limit: int = Field(
        default=50,
        ge=1,
        le=50,
        description="Number of videos to scrape (1-50)"
    )
    include_detailed_metadata: bool = Field(
        default=False,
        description="Whether to fetch detailed metadata (slower, includes views/likes)"
    )
    user_id: Optional[str] = Field(
        None,
        description="Optional user ID for multi-user support"
    )
    linked_channel_id: Optional[str] = Field(
        None,
        description="Optional UUID to link to existing channel in channels table"
    )


class ChannelScrapeResponse(BaseModel):
    """Response from channel scraping"""
    success: bool
    scraped_channel_id: Optional[int] = None
    channel_name: Optional[str] = None
    videos_scraped: Optional[int] = None
    videos_failed: Optional[int] = None
    error: Optional[str] = None


class ScrapedVideoResponse(BaseModel):
    """Response model for scraped video"""
    id: int
    scraped_channel_id: int
    youtube_video_id: str
    title: str
    description: Optional[str]
    video_url: str
    thumbnail_url: Optional[str]
    published_at: Optional[datetime]
    duration_seconds: Optional[int]
    view_count: Optional[int]
    like_count: Optional[int]
    comment_count: Optional[int]
    tags: List[str] = []
    created_at: datetime
    title_length: Optional[int]
    description_length: Optional[int]
    title_keywords: List[str] = []

    class Config:
        from_attributes = True


class ScrapedChannelResponse(BaseModel):
    """Response model for scraped channel"""
    id: int
    youtube_channel_id: str
    channel_name: str
    channel_url: str
    rss_feed_url: str
    description: Optional[str]
    subscriber_count: int
    video_count: int
    last_scraped_at: Optional[datetime]
    scrape_status: str
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    user_id: Optional[str]
    linked_channel_id: Optional[str]
    video_count_scraped: int = 0

    class Config:
        from_attributes = True


class VideoAnalysisStatsResponse(BaseModel):
    """Statistics for channel's scraped videos"""
    total_videos: int
    avg_view_count: float
    avg_like_count: float
    avg_duration_seconds: float
    most_common_keywords: List[str]
    avg_title_length: float
