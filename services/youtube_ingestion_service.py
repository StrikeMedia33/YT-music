"""
YouTube Channel Ingestion Service

Service for scraping YouTube channels and videos for content research and analysis.
Stores scraped data in database for prompt generation and genre analysis.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models import ScrapedChannel, ScrapedVideo
from utils.youtube_scraper import (
    extract_channel_id,
    get_channel_info,
    get_channel_rss_url,
    get_channel_videos_from_rss,
    get_video_metadata,
    validate_youtube_channel
)


class YouTubeIngestionService:
    """
    Service for ingesting YouTube channel and video data.

    Workflow:
    1. User provides YouTube channel URL
    2. Extract channel ID using multi-tier approach
    3. Validate channel exists and has content
    4. Create/update ScrapedChannel record
    5. Scrape last N videos (default: 50, max: 50)
    6. Store ScrapedVideo records with metadata
    7. Update channel scrape_status and timestamps
    """

    def __init__(self, db: Session):
        """
        Initialize the YouTube ingestion service.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def discover_channel(self, channel_url: str) -> Dict[str, Any]:
        """
        Discover and validate a YouTube channel without storing it.
        Use this to preview channel info before committing to scrape.

        Args:
            channel_url: YouTube channel URL (any format)

        Returns:
            Dict containing:
            {
                'success': bool,
                'channel_id': str,
                'channel_name': str,
                'channel_url': str,
                'description': str,
                'rss_feed_url': str,
                'error': str (if success=False)
            }

        Raises:
            ValueError: If channel URL is invalid or channel not found
        """
        # Extract channel ID
        channel_id = extract_channel_id(channel_url)
        if not channel_id:
            return {
                'success': False,
                'error': 'Could not extract channel ID from URL. Please verify the URL is correct.'
            }

        # Validate channel exists
        if not validate_youtube_channel(channel_url):
            return {
                'success': False,
                'error': 'Channel not found or has no videos. Please check the URL.'
            }

        # Get channel info
        channel_info = get_channel_info(channel_id)
        if not channel_info:
            return {
                'success': False,
                'error': 'Could not retrieve channel information. Channel may be private or deleted.'
            }

        return {
            'success': True,
            'channel_id': channel_id,
            'channel_name': channel_info['channel_name'],
            'channel_url': channel_info['channel_url'],
            'description': channel_info['description'],
            'rss_feed_url': get_channel_rss_url(channel_id)
        }

    def scrape_channel(
        self,
        channel_url: str,
        video_limit: int = 50,
        include_detailed_metadata: bool = False,
        user_id: Optional[str] = None,
        linked_channel_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Scrape a YouTube channel and store all data in the database.

        Args:
            channel_url: YouTube channel URL
            video_limit: Number of videos to scrape (1-50, default: 50)
            include_detailed_metadata: Whether to fetch detailed metadata with yt-dlp (slow)
            user_id: Optional user ID for multi-user support
            linked_channel_id: Optional UUID to link to existing channel in channels table

        Returns:
            Dict containing:
            {
                'success': bool,
                'scraped_channel_id': int,
                'channel_name': str,
                'videos_scraped': int,
                'videos_failed': int,
                'error': str (if success=False)
            }

        Raises:
            ValueError: If video_limit is out of range
        """
        # Validate inputs
        if not (1 <= video_limit <= 50):
            raise ValueError("video_limit must be between 1 and 50")

        # Discover channel first
        discovery = self.discover_channel(channel_url)
        if not discovery['success']:
            return discovery

        channel_id = discovery['channel_id']
        channel_name = discovery['channel_name']

        try:
            # Check if channel already exists
            existing_channel = self.db.query(ScrapedChannel).filter_by(
                youtube_channel_id=channel_id
            ).first()

            if existing_channel:
                # Update existing channel
                scraped_channel = existing_channel
                scraped_channel.channel_name = channel_name
                scraped_channel.channel_url = discovery['channel_url']
                scraped_channel.description = discovery['description']
                scraped_channel.rss_feed_url = discovery['rss_feed_url']
                scraped_channel.scrape_status = 'scraping'
                scraped_channel.error_message = None
                scraped_channel.user_id = user_id
                scraped_channel.linked_channel_id = linked_channel_id
            else:
                # Create new channel record
                scraped_channel = ScrapedChannel(
                    youtube_channel_id=channel_id,
                    channel_name=channel_name,
                    channel_url=discovery['channel_url'],
                    rss_feed_url=discovery['rss_feed_url'],
                    description=discovery['description'],
                    scrape_status='scraping',
                    user_id=user_id,
                    linked_channel_id=linked_channel_id
                )
                self.db.add(scraped_channel)
                self.db.flush()  # Get the ID

            # Scrape videos from RSS feed (fast)
            rss_videos = get_channel_videos_from_rss(channel_id, limit=video_limit)

            videos_scraped = 0
            videos_failed = 0

            for video_data in rss_videos:
                try:
                    # Check if video already exists
                    existing_video = self.db.query(ScrapedVideo).filter_by(
                        youtube_video_id=video_data['video_id']
                    ).first()

                    # Get detailed metadata if requested
                    if include_detailed_metadata:
                        detailed_metadata = get_video_metadata(video_data['video_url'])
                        if detailed_metadata:
                            video_data = detailed_metadata

                    # Calculate derived fields
                    title_length = len(video_data['title']) if video_data.get('title') else 0
                    description_length = len(video_data['description']) if video_data.get('description') else 0

                    # Extract simple title keywords
                    title_keywords = []
                    if video_data.get('title'):
                        words = video_data['title'].split()
                        title_keywords = [
                            word.strip('.,!?;:()[]{}')
                            for word in words
                            if len(word) > 3 and (word[0].isupper() or word.isupper())
                        ][:10]

                    if existing_video:
                        # Update existing video
                        existing_video.title = video_data.get('title', '')
                        existing_video.description = video_data.get('description', '')
                        existing_video.video_url = video_data['video_url']
                        existing_video.thumbnail_url = video_data.get('thumbnail_url')
                        existing_video.published_at = video_data.get('published_at')
                        existing_video.duration_seconds = video_data.get('duration_seconds')
                        existing_video.view_count = video_data.get('view_count')
                        existing_video.like_count = video_data.get('like_count')
                        existing_video.comment_count = video_data.get('comment_count')
                        existing_video.tags = video_data.get('tags', [])
                        existing_video.title_length = title_length
                        existing_video.description_length = description_length
                        existing_video.title_keywords = title_keywords
                    else:
                        # Create new video record
                        scraped_video = ScrapedVideo(
                            scraped_channel_id=scraped_channel.id,
                            youtube_video_id=video_data['video_id'],
                            title=video_data.get('title', ''),
                            description=video_data.get('description', ''),
                            video_url=video_data['video_url'],
                            thumbnail_url=video_data.get('thumbnail_url'),
                            published_at=video_data.get('published_at'),
                            duration_seconds=video_data.get('duration_seconds'),
                            view_count=video_data.get('view_count'),
                            like_count=video_data.get('like_count'),
                            comment_count=video_data.get('comment_count'),
                            tags=video_data.get('tags', []),
                            title_length=title_length,
                            description_length=description_length,
                            title_keywords=title_keywords
                        )
                        self.db.add(scraped_video)

                    videos_scraped += 1

                except Exception as e:
                    print(f"Error scraping video {video_data.get('video_id', 'unknown')}: {e}")
                    videos_failed += 1
                    continue

            # Update channel status
            scraped_channel.video_count = videos_scraped
            scraped_channel.last_scraped_at = datetime.now(timezone.utc)
            scraped_channel.scrape_status = 'completed'

            self.db.commit()

            return {
                'success': True,
                'scraped_channel_id': scraped_channel.id,
                'channel_name': channel_name,
                'videos_scraped': videos_scraped,
                'videos_failed': videos_failed
            }

        except Exception as e:
            self.db.rollback()

            # Update channel status to failed if we created it
            if 'scraped_channel' in locals():
                scraped_channel.scrape_status = 'failed'
                scraped_channel.error_message = str(e)
                try:
                    self.db.commit()
                except:
                    pass

            return {
                'success': False,
                'error': f'Failed to scrape channel: {str(e)}'
            }

    def get_scraped_channels(
        self,
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None
    ) -> List[ScrapedChannel]:
        """
        Get list of scraped channels with optional filtering.

        Args:
            limit: Maximum number of channels to return
            offset: Number of channels to skip
            status: Optional filter by scrape_status

        Returns:
            List of ScrapedChannel objects
        """
        query = self.db.query(ScrapedChannel)

        if status:
            query = query.filter_by(scrape_status=status)

        return query.order_by(ScrapedChannel.created_at.desc()).limit(limit).offset(offset).all()

    def get_scraped_channel(self, channel_id: int) -> Optional[ScrapedChannel]:
        """
        Get a single scraped channel by ID.

        Args:
            channel_id: ScrapedChannel ID (not YouTube channel ID)

        Returns:
            ScrapedChannel object or None
        """
        return self.db.query(ScrapedChannel).filter_by(id=channel_id).first()

    def get_channel_videos(
        self,
        scraped_channel_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[ScrapedVideo]:
        """
        Get videos for a specific scraped channel.

        Args:
            scraped_channel_id: ScrapedChannel ID
            limit: Maximum number of videos to return
            offset: Number of videos to skip

        Returns:
            List of ScrapedVideo objects ordered by publish date (newest first)
        """
        return (
            self.db.query(ScrapedVideo)
            .filter_by(scraped_channel_id=scraped_channel_id)
            .order_by(ScrapedVideo.published_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def delete_scraped_channel(self, channel_id: int) -> bool:
        """
        Delete a scraped channel and all its videos (CASCADE).

        Args:
            channel_id: ScrapedChannel ID

        Returns:
            True if deleted, False if not found
        """
        channel = self.get_scraped_channel(channel_id)
        if not channel:
            return False

        self.db.delete(channel)
        self.db.commit()
        return True

    def get_video_analysis_stats(self, scraped_channel_id: int) -> Dict[str, Any]:
        """
        Get analysis statistics for a scraped channel's videos.
        Useful for understanding content patterns and generating prompts.

        Args:
            scraped_channel_id: ScrapedChannel ID

        Returns:
            Dict with statistics:
            {
                'total_videos': int,
                'avg_view_count': float,
                'avg_like_count': float,
                'avg_duration_seconds': float,
                'most_common_keywords': List[str],
                'avg_title_length': float
            }
        """
        from sqlalchemy import func

        videos = self.get_channel_videos(scraped_channel_id, limit=1000)

        if not videos:
            return {
                'total_videos': 0,
                'avg_view_count': 0,
                'avg_like_count': 0,
                'avg_duration_seconds': 0,
                'most_common_keywords': [],
                'avg_title_length': 0
            }

        # Calculate averages
        total_videos = len(videos)
        avg_view_count = sum(v.view_count or 0 for v in videos) / total_videos
        avg_like_count = sum(v.like_count or 0 for v in videos) / total_videos
        avg_duration_seconds = sum(v.duration_seconds or 0 for v in videos) / total_videos
        avg_title_length = sum(v.title_length or 0 for v in videos) / total_videos

        # Get most common keywords
        all_keywords = []
        for v in videos:
            if v.title_keywords:
                all_keywords.extend(v.title_keywords)

        keyword_counts = {}
        for keyword in all_keywords:
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1

        most_common_keywords = sorted(
            keyword_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:20]
        most_common_keywords = [k[0] for k in most_common_keywords]

        return {
            'total_videos': total_videos,
            'avg_view_count': round(avg_view_count, 2),
            'avg_like_count': round(avg_like_count, 2),
            'avg_duration_seconds': round(avg_duration_seconds, 2),
            'most_common_keywords': most_common_keywords,
            'avg_title_length': round(avg_title_length, 2)
        }
