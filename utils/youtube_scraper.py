"""
YouTube Scraper Utilities

Fast YouTube channel and video scraping using RSS feeds with fallback to yt-dlp.
Optimized for speed with multi-tier channel ID extraction.

Adapted from ScaleGrow project for YT-Music content research.
"""

import re
from typing import Optional, Dict, List
from datetime import datetime, timezone
import feedparser


def extract_video_id(url: str) -> Optional[str]:
    """
    Extract video ID from various YouTube URL formats

    Args:
        url: YouTube video URL

    Returns:
        Video ID or None

    Examples:
        >>> extract_video_id('https://youtube.com/watch?v=dQw4w9WgXcQ')
        'dQw4w9WgXcQ'
        >>> extract_video_id('https://youtu.be/dQw4w9WgXcQ')
        'dQw4w9WgXcQ'
    """
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/v\/([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})',  # YouTube Shorts
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def extract_channel_id(url: str) -> Optional[str]:
    """
    Extract channel ID from various YouTube channel URL formats.
    Uses multi-tier approach for speed:
    1. Direct URL pattern matching (instant)
    2. HEAD request to follow redirects (< 1 second)
    3. HTML parsing for embedded IDs (2-3 seconds)
    4. yt-dlp fallback (5-10 seconds, only if all else fails)

    Args:
        url: YouTube channel URL

    Returns:
        Channel ID or None

    Examples:
        >>> extract_channel_id('https://youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw')
        'UCuAXFkgsw1L7xaCfnd5JJOw'
        >>> extract_channel_id('https://youtube.com/@MrBeast')
        'UCX6OQ3DkcsbYNE6H8uQQuVA'
    """
    # Tier 1: Direct channel ID URL - instant
    channel_id_match = re.search(r'youtube\.com\/channel\/([a-zA-Z0-9_-]+)', url)
    if channel_id_match:
        return channel_id_match.group(1)

    # Tier 2: FAST - HEAD request to follow redirects (< 1 second)
    try:
        import httpx

        # Ensure URL is properly formatted
        if not url.startswith('http'):
            url = f'https://www.youtube.com/{url}'

        # HEAD request doesn't download body, just gets headers
        response = httpx.head(url, timeout=5.0, follow_redirects=True)

        # Check if redirected to channel URL
        final_url = str(response.url)
        channel_id_match = re.search(r'youtube\.com/channel/([A-Za-z0-9_-]+)', final_url)
        if channel_id_match:
            return channel_id_match.group(1)

    except Exception:
        pass  # Silent fail, try next method

    # Tier 3: MEDIUM - Fetch HTML and parse (2-3 seconds)
    try:
        import httpx

        response = httpx.get(url, timeout=8.0, follow_redirects=True)
        response.raise_for_status()

        html = response.text

        # Try multiple extraction patterns from YouTube's HTML
        # Pattern 1: Channel URL in HTML
        channel_url_match = re.search(r'youtube\.com/channel/([A-Za-z0-9_-]+)', html)
        if channel_url_match:
            return channel_url_match.group(1)

        # Pattern 2: channelId in embedded JSON
        channel_id_match = re.search(r'"channelId":"([A-Za-z0-9_-]+)"', html)
        if channel_id_match:
            return channel_id_match.group(1)

        # Pattern 3: externalId field
        external_id_match = re.search(r'"externalId":"([A-Za-z0-9_-]+)"', html)
        if external_id_match:
            return external_id_match.group(1)

    except Exception:
        pass  # Silent fail, try yt-dlp fallback

    # Tier 4: SLOW FALLBACK - Use yt-dlp only if all else fails (5-10 seconds)
    try:
        import yt_dlp

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get('channel_id')
    except:
        return None


def get_channel_rss_url(channel_id: str) -> str:
    """
    Generate RSS feed URL for a YouTube channel

    Args:
        channel_id: YouTube channel ID

    Returns:
        RSS feed URL

    Example:
        >>> get_channel_rss_url('UCuAXFkgsw1L7xaCfnd5JJOw')
        'https://www.youtube.com/feeds/videos.xml?channel_id=UCuAXFkgsw1L7xaCfnd5JJOw'
    """
    return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"


def get_channel_info(channel_id: str) -> Optional[Dict]:
    """
    Get basic metadata about a YouTube channel.
    Uses fast RSS feed approach instead of slow yt-dlp.

    Args:
        channel_id: YouTube channel ID

    Returns:
        Dictionary with channel metadata:
        {
            'channel_id': str,
            'channel_name': str,
            'channel_url': str,
            'description': str,
            'subscriber_count': int  # Always 0 (not available in RSS)
        }
        Returns None if channel not found
    """
    try:
        rss_url = get_channel_rss_url(channel_id)
        feed = feedparser.parse(rss_url)

        if not hasattr(feed, 'feed') or not hasattr(feed, 'entries'):
            return None

        # Extract channel name from feed (remove ' - YouTube' suffix if present)
        channel_name = feed.feed.get('title', '').replace(' - YouTube', '')
        if not channel_name and feed.entries:
            # Fallback: get author from first entry
            channel_name = feed.entries[0].get('author', f'Channel {channel_id}')

        channel_url = f"https://www.youtube.com/channel/{channel_id}"

        return {
            'channel_id': channel_id,
            'channel_name': channel_name,
            'channel_url': channel_url,
            'description': feed.feed.get('subtitle', ''),
            'subscriber_count': 0,  # Not available in RSS feed
        }
    except Exception as e:
        print(f"Error getting channel info for {channel_id}: {e}")
        return None


def validate_youtube_channel(url: str) -> bool:
    """
    Validate if a YouTube channel URL is accessible and has content

    Args:
        url: YouTube channel URL

    Returns:
        True if valid and has at least one video
    """
    try:
        channel_id = extract_channel_id(url)
        if not channel_id:
            return False

        # Try to fetch RSS feed
        rss_url = get_channel_rss_url(channel_id)
        feed = feedparser.parse(rss_url)

        return hasattr(feed, 'entries') and len(feed.entries) > 0

    except Exception:
        return False


def get_channel_videos_from_rss(channel_id: str, limit: int = 50) -> List[Dict]:
    """
    Get latest videos from a channel using RSS feed (fast, no API key needed).
    RSS feeds return approximately 15 videos max, so this is best for recent content.

    Args:
        channel_id: YouTube channel ID
        limit: Maximum number of videos to return (default: 50, but RSS typically has ~15)

    Returns:
        List of video dictionaries with basic metadata:
        {
            'video_id': str,
            'title': str,
            'video_url': str,
            'published_at': datetime,
            'author': str,
            'thumbnail_url': str (optional)
        }
    """
    try:
        rss_url = get_channel_rss_url(channel_id)
        feed = feedparser.parse(rss_url)

        videos = []
        for entry in feed.entries[:limit]:
            video_id = extract_video_id(entry.link)
            if not video_id:
                continue

            # Parse published date
            published_at = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                try:
                    published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                except:
                    pass

            # Extract thumbnail URL if available
            thumbnail_url = None
            if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
                thumbnail_url = entry.media_thumbnail[0].get('url')

            videos.append({
                'video_id': video_id,
                'title': entry.title,
                'video_url': entry.link,
                'published_at': published_at,
                'author': entry.get('author', ''),
                'thumbnail_url': thumbnail_url
            })

        return videos

    except Exception as e:
        print(f"Error getting channel videos from RSS: {e}")
        return []


def get_video_metadata(video_url: str) -> Optional[Dict]:
    """
    Get detailed metadata for a YouTube video using yt-dlp.
    This is slower but provides comprehensive data including views, likes, etc.

    Args:
        video_url: YouTube video URL

    Returns:
        Dictionary with video metadata:
        {
            'video_id': str,
            'title': str,
            'description': str,
            'video_url': str,
            'thumbnail_url': str,
            'published_at': datetime,
            'duration_seconds': int,
            'view_count': int,
            'like_count': int,
            'comment_count': int,
            'tags': List[str],
            'channel_id': str,
            'channel_url': str,
            'author': str
        }
        Returns None if video not found or error occurs
    """
    try:
        import yt_dlp

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'skip_download': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

            # Parse upload date (make it timezone-aware UTC)
            upload_date = info.get('upload_date')
            published_at = None
            if upload_date:
                try:
                    naive_date = datetime.strptime(upload_date, '%Y%m%d')
                    published_at = naive_date.replace(tzinfo=timezone.utc)
                except:
                    pass

            return {
                'video_id': extract_video_id(video_url),
                'title': info.get('title'),
                'description': info.get('description', ''),
                'video_url': video_url,
                'thumbnail_url': info.get('thumbnail'),
                'published_at': published_at,
                'duration_seconds': info.get('duration', 0),
                'view_count': info.get('view_count', 0),
                'like_count': info.get('like_count', 0),
                'comment_count': info.get('comment_count', 0),
                'tags': info.get('tags', []),
                'channel_id': info.get('channel_id'),
                'channel_url': info.get('channel_url'),
                'author': info.get('uploader') or info.get('channel')
            }
    except Exception as e:
        print(f"Error getting video metadata for {video_url}: {e}")
        return None


def get_channel_videos_batch(channel_id: str, limit: int = 50, include_metadata: bool = False) -> List[Dict]:
    """
    Get channel videos with optional detailed metadata.

    If include_metadata=False (default): Fast RSS-only approach (~1 second)
    If include_metadata=True: Fetches detailed data for each video using yt-dlp (~1-2 seconds per video)

    Args:
        channel_id: YouTube channel ID
        limit: Maximum number of videos (default: 50, RSS returns ~15)
        include_metadata: Whether to fetch detailed metadata for each video (slow)

    Returns:
        List of video dictionaries
    """
    # Get basic videos from RSS first (fast)
    videos = get_channel_videos_from_rss(channel_id, limit)

    if not include_metadata:
        return videos

    # Enrich with detailed metadata (slow)
    enriched_videos = []
    for video in videos:
        detailed_metadata = get_video_metadata(video['video_url'])
        if detailed_metadata:
            enriched_videos.append(detailed_metadata)
        else:
            # Fallback to RSS data if yt-dlp fails
            enriched_videos.append(video)

    return enriched_videos
