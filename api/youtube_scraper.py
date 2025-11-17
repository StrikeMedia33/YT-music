"""YouTube Scraper API Routes"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from models import get_db
from schemas import (
    ChannelDiscoverRequest,
    ChannelDiscoverResponse,
    ChannelScrapeRequest,
    ChannelScrapeResponse,
    ScrapedChannelResponse,
    ScrapedVideoResponse,
    VideoAnalysisStatsResponse,
)
from services.youtube_ingestion_service import YouTubeIngestionService


router = APIRouter()


@router.post("/discover", response_model=ChannelDiscoverResponse)
def discover_channel(
    request: ChannelDiscoverRequest,
    db: Session = Depends(get_db)
):
    """
    Discover and validate a YouTube channel without storing it.

    This endpoint:
    - Extracts channel ID from URL (multi-tier approach)
    - Validates channel exists and has content
    - Returns channel metadata
    - Does NOT store anything in database

    Use this endpoint to preview channel info before scraping.
    """
    service = YouTubeIngestionService(db)
    result = service.discover_channel(request.channel_url)
    return result


@router.post("/scrape", response_model=ChannelScrapeResponse)
def scrape_channel(
    request: ChannelScrapeRequest,
    db: Session = Depends(get_db)
):
    """
    Scrape a YouTube channel and store all data in the database.

    This endpoint:
    - Extracts channel ID from URL
    - Creates/updates ScrapedChannel record
    - Scrapes last N videos (default: 50, max: 50)
    - Stores ScrapedVideo records
    - Updates scrape_status and timestamps

    Set include_detailed_metadata=true to fetch views/likes (slower, ~1-2s per video).
    Default (false) uses fast RSS-only approach (~1s total for ~15 videos).
    """
    service = YouTubeIngestionService(db)
    result = service.scrape_channel(
        channel_url=request.channel_url,
        video_limit=request.video_limit,
        include_detailed_metadata=request.include_detailed_metadata,
        user_id=request.user_id,
        linked_channel_id=request.linked_channel_id
    )

    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error', 'Scraping failed'))

    return result


@router.get("/channels", response_model=List[ScrapedChannelResponse])
def list_scraped_channels(
    skip: int = 0,
    limit: int = 50,
    status: str = None,
    db: Session = Depends(get_db)
):
    """
    Get list of scraped channels with optional filtering.

    Query parameters:
    - skip: Number of channels to skip (pagination)
    - limit: Maximum number of channels to return
    - status: Filter by scrape_status (pending, scraping, completed, failed)
    """
    service = YouTubeIngestionService(db)
    channels = service.get_scraped_channels(limit=limit, offset=skip, status=status)

    # Convert to dict and add video_count_scraped
    return [
        ScrapedChannelResponse(
            **channel.to_dict(),
            video_count_scraped=channel.scraped_videos.count()
        )
        for channel in channels
    ]


@router.get("/channels/{channel_id}", response_model=ScrapedChannelResponse)
def get_scraped_channel(
    channel_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a single scraped channel by ID.
    """
    service = YouTubeIngestionService(db)
    channel = service.get_scraped_channel(channel_id)

    if not channel:
        raise HTTPException(status_code=404, detail="Scraped channel not found")

    return ScrapedChannelResponse(
        **channel.to_dict(),
        video_count_scraped=channel.scraped_videos.count()
    )


@router.delete("/channels/{channel_id}", status_code=204)
def delete_scraped_channel(
    channel_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a scraped channel and all its videos (CASCADE).
    """
    service = YouTubeIngestionService(db)
    deleted = service.delete_scraped_channel(channel_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Scraped channel not found")


@router.get("/channels/{channel_id}/videos", response_model=List[ScrapedVideoResponse])
def get_channel_videos(
    channel_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get videos for a specific scraped channel.

    Returns videos ordered by publish date (newest first).
    """
    service = YouTubeIngestionService(db)

    # Verify channel exists
    channel = service.get_scraped_channel(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Scraped channel not found")

    videos = service.get_channel_videos(
        scraped_channel_id=channel_id,
        limit=limit,
        offset=skip
    )

    return [ScrapedVideoResponse.model_validate(video) for video in videos]


@router.get("/channels/{channel_id}/analysis", response_model=VideoAnalysisStatsResponse)
def get_channel_analysis(
    channel_id: int,
    db: Session = Depends(get_db)
):
    """
    Get analysis statistics for a scraped channel's videos.

    Returns:
    - Total videos count
    - Average view/like counts
    - Average duration
    - Most common keywords (useful for prompt generation)
    - Average title length
    """
    service = YouTubeIngestionService(db)

    # Verify channel exists
    channel = service.get_scraped_channel(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Scraped channel not found")

    stats = service.get_video_analysis_stats(channel_id)
    return VideoAnalysisStatsResponse(**stats)
