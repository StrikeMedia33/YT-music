"""Pydantic Schemas for API validation"""
from .channel import ChannelCreate, ChannelUpdate, ChannelResponse
from .video_job import VideoJobCreate, VideoJobUpdate, VideoJobResponse, VideoJobDetail
from .genre import GenreCreate, GenreUpdate, GenreResponse, GenreWithStats
from .idea import (
    VideoIdeaCreate,
    VideoIdeaUpdate,
    VideoIdeaResponse,
    VideoIdeaDetail,
    VideoIdeaWithGenre,
    VideoIdeaCloneRequest,
    VideoIdeaSearchParams,
)
from .idea_prompt import IdeaPromptCreate, IdeaPromptUpdate, IdeaPromptResponse
from .youtube_scraper import (
    ChannelDiscoverRequest,
    ChannelDiscoverResponse,
    ChannelScrapeRequest,
    ChannelScrapeResponse,
    ScrapedVideoResponse,
    ScrapedChannelResponse,
    VideoAnalysisStatsResponse,
)

__all__ = [
    # Channel schemas
    "ChannelCreate",
    "ChannelUpdate",
    "ChannelResponse",
    # Video Job schemas
    "VideoJobCreate",
    "VideoJobUpdate",
    "VideoJobResponse",
    "VideoJobDetail",
    # Genre schemas
    "GenreCreate",
    "GenreUpdate",
    "GenreResponse",
    "GenreWithStats",
    # Video Idea schemas
    "VideoIdeaCreate",
    "VideoIdeaUpdate",
    "VideoIdeaResponse",
    "VideoIdeaDetail",
    "VideoIdeaWithGenre",
    "VideoIdeaCloneRequest",
    "VideoIdeaSearchParams",
    # Idea Prompt schemas
    "IdeaPromptCreate",
    "IdeaPromptUpdate",
    "IdeaPromptResponse",
    # YouTube Scraper schemas
    "ChannelDiscoverRequest",
    "ChannelDiscoverResponse",
    "ChannelScrapeRequest",
    "ChannelScrapeResponse",
    "ScrapedVideoResponse",
    "ScrapedChannelResponse",
    "VideoAnalysisStatsResponse",
]
