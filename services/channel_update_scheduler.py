"""
Channel Update Scheduler Service

Handles automatic re-scraping of YouTube channels to keep video data up-to-date.
Runs on application startup and periodically while the application is running.
"""

import logging
from datetime import datetime, timezone
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from models import ScrapedChannel
from services.youtube_ingestion_service import YouTubeIngestionService

logger = logging.getLogger(__name__)


class ChannelUpdateScheduler:
    """
    Service for scheduling and executing channel re-scrapes.

    Features:
    - Re-scrapes all channels on startup
    - Runs periodic updates (default: hourly)
    - Updates existing videos with new metadata
    - Adds newly published videos
    - Handles errors gracefully
    """

    def __init__(self):
        """Initialize the scheduler service."""
        self.is_running = False
        self.last_run = None

    def rescrape_all_channels(self, db: Session, video_limit: int = 50) -> Dict[str, Any]:
        """
        Re-scrape all channels to check for new videos and update metadata.

        Args:
            db: Database session
            video_limit: Number of videos to fetch per channel (default: 50)

        Returns:
            Dict with summary of the re-scrape operation:
            {
                'success': bool,
                'channels_processed': int,
                'channels_updated': int,
                'channels_failed': int,
                'new_videos_found': int,
                'videos_updated': int,
                'errors': List[str]
            }
        """
        self.is_running = True
        logger.info("Starting channel re-scrape for all channels...")

        summary = {
            'success': True,
            'channels_processed': 0,
            'channels_updated': 0,
            'channels_failed': 0,
            'new_videos_found': 0,
            'videos_updated': 0,
            'errors': [],
            'started_at': datetime.now(timezone.utc).isoformat()
        }

        try:
            # Get all scraped channels
            channels = db.query(ScrapedChannel).all()

            if not channels:
                logger.info("No channels to re-scrape")
                summary['completed_at'] = datetime.now(timezone.utc).isoformat()
                self.is_running = False
                self.last_run = datetime.now(timezone.utc)
                return summary

            logger.info(f"Found {len(channels)} channels to re-scrape")

            service = YouTubeIngestionService(db)

            for channel in channels:
                summary['channels_processed'] += 1

                try:
                    logger.info(f"Re-scraping channel: {channel.channel_name} ({channel.youtube_channel_id})")

                    # Get video count before re-scrape
                    videos_before = channel.scraped_videos.count()

                    # Re-scrape the channel
                    result = service.scrape_channel(
                        channel_url=channel.channel_url,
                        video_limit=video_limit,
                        include_detailed_metadata=False,  # Fast mode
                        user_id=channel.user_id,
                        linked_channel_id=channel.linked_channel_id
                    )

                    if result['success']:
                        summary['channels_updated'] += 1

                        # Calculate new videos found
                        videos_after = channel.scraped_videos.count()
                        new_videos = videos_after - videos_before

                        if new_videos > 0:
                            summary['new_videos_found'] += new_videos
                            logger.info(f"  ✓ Found {new_videos} new video(s)")
                        else:
                            summary['videos_updated'] += result['videos_scraped']
                            logger.info(f"  ✓ Updated {result['videos_scraped']} video(s)")
                    else:
                        summary['channels_failed'] += 1
                        error_msg = f"Channel {channel.channel_name}: {result.get('error', 'Unknown error')}"
                        summary['errors'].append(error_msg)
                        logger.error(f"  ✗ {error_msg}")

                except Exception as e:
                    summary['channels_failed'] += 1
                    error_msg = f"Channel {channel.channel_name}: {str(e)}"
                    summary['errors'].append(error_msg)
                    logger.error(f"  ✗ Error re-scraping channel: {error_msg}")
                    continue

            # Update summary
            summary['completed_at'] = datetime.now(timezone.utc).isoformat()
            summary['success'] = summary['channels_failed'] == 0

            logger.info(f"Re-scrape completed: {summary['channels_updated']}/{summary['channels_processed']} channels updated, "
                       f"{summary['new_videos_found']} new videos found")

            self.last_run = datetime.now(timezone.utc)

        except Exception as e:
            summary['success'] = False
            summary['errors'].append(f"Fatal error: {str(e)}")
            logger.error(f"Fatal error during re-scrape: {e}")

        finally:
            self.is_running = False

        return summary

    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the scheduler.

        Returns:
            Dict with status information
        """
        return {
            'is_running': self.is_running,
            'last_run': self.last_run.isoformat() if self.last_run else None
        }


# Global scheduler instance
channel_scheduler = ChannelUpdateScheduler()
