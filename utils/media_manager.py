"""
Media Directory Management Utilities

Handles creation and management of media directories for video generation projects.
Ensures proper file organization and provides utilities for file operations.
"""

import os
import re
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime


# Base media directory (relative to project root)
MEDIA_ROOT = Path(__file__).parent.parent / "media"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a string to be filesystem-safe.

    Args:
        filename: Original filename or title

    Returns:
        Sanitized filename safe for all filesystems

    Examples:
        >>> sanitize_filename("My Video: Amazing Content!")
        'my-video-amazing-content'
        >>> sanitize_filename("2024/01/15 - Test")
        '2024-01-15-test'
    """
    # Convert to lowercase
    filename = filename.lower()

    # Replace spaces and special characters with hyphens
    filename = re.sub(r'[^\w\s-]', '', filename)
    filename = re.sub(r'[-\s]+', '-', filename)

    # Remove leading/trailing hyphens
    filename = filename.strip('-')

    # Limit length to 100 characters
    if len(filename) > 100:
        filename = filename[:100].rstrip('-')

    return filename or 'untitled'


def create_video_job_directory(video_job_title: str, video_job_id: str) -> Dict[str, Path]:
    """
    Create directory structure for a video job.

    Args:
        video_job_title: Title of the video job (will be sanitized)
        video_job_id: Unique ID of the video job (for uniqueness)

    Returns:
        Dictionary with paths:
        {
            'root': Path to job directory,
            'music': Path to music subdirectory,
            'images': Path to images subdirectory,
            'output': Path to output subdirectory
        }

    Directory structure:
        media/{sanitized-title}-{job-id}/
        ├── music/
        ├── images/
        └── output/
    """
    # Sanitize title and create unique directory name
    safe_title = sanitize_filename(video_job_title)
    dir_name = f"{safe_title}-{video_job_id}"

    # Create directory structure
    job_dir = MEDIA_ROOT / dir_name
    music_dir = job_dir / "music"
    images_dir = job_dir / "images"
    output_dir = job_dir / "output"

    # Create all directories
    job_dir.mkdir(parents=True, exist_ok=True)
    music_dir.mkdir(exist_ok=True)
    images_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)

    return {
        'root': job_dir,
        'music': music_dir,
        'images': images_dir,
        'output': output_dir
    }


def get_video_job_directory(video_job_id: str) -> Optional[Dict[str, Path]]:
    """
    Get existing directory structure for a video job.

    Args:
        video_job_id: Unique ID of the video job

    Returns:
        Dictionary with paths if directory exists, None otherwise
    """
    # Find directory ending with job ID
    for item in MEDIA_ROOT.iterdir():
        if item.is_dir() and item.name.endswith(f"-{video_job_id}"):
            return {
                'root': item,
                'music': item / "music",
                'images': item / "images",
                'output': item / "output"
            }

    return None


def list_music_files(video_job_id: str) -> List[Path]:
    """
    List all music files for a video job.

    Args:
        video_job_id: Unique ID of the video job

    Returns:
        List of paths to music files, sorted by filename
    """
    job_dirs = get_video_job_directory(video_job_id)
    if not job_dirs:
        return []

    music_dir = job_dirs['music']
    if not music_dir.exists():
        return []

    # Get all audio files
    audio_extensions = {'.mp3', '.wav', '.m4a', '.aac', '.flac'}
    music_files = [
        f for f in music_dir.iterdir()
        if f.is_file() and f.suffix.lower() in audio_extensions
    ]

    return sorted(music_files)


def list_image_files(video_job_id: str) -> List[Path]:
    """
    List all image files for a video job.

    Args:
        video_job_id: Unique ID of the video job

    Returns:
        List of paths to image files, sorted by filename
    """
    job_dirs = get_video_job_directory(video_job_id)
    if not job_dirs:
        return []

    images_dir = job_dirs['images']
    if not images_dir.exists():
        return []

    # Get all image files
    image_extensions = {'.png', '.jpg', '.jpeg', '.webp', '.gif'}
    image_files = [
        f for f in images_dir.iterdir()
        if f.is_file() and f.suffix.lower() in image_extensions
    ]

    return sorted(image_files)


def get_next_track_number(video_job_id: str) -> int:
    """
    Get the next available track number for a video job.

    Args:
        video_job_id: Unique ID of the video job

    Returns:
        Next track number (1-based)
    """
    music_files = list_music_files(video_job_id)

    if not music_files:
        return 1

    # Extract track numbers from filenames
    track_numbers = []
    for file in music_files:
        # Match track_XX.ext pattern
        match = re.search(r'track_(\d+)', file.stem.lower())
        if match:
            track_numbers.append(int(match.group(1)))

    return max(track_numbers, default=0) + 1


def get_music_file_path(video_job_id: str, track_number: int, extension: str = 'mp3') -> Path:
    """
    Get standardized path for a music track file.

    Args:
        video_job_id: Unique ID of the video job
        track_number: Track number (1-based)
        extension: File extension (default: 'mp3')

    Returns:
        Path to music file
    """
    job_dirs = get_video_job_directory(video_job_id)
    if not job_dirs:
        raise ValueError(f"Video job directory not found for ID: {video_job_id}")

    filename = f"track_{track_number:02d}.{extension}"
    return job_dirs['music'] / filename


def get_image_file_path(video_job_id: str, image_number: int, extension: str = 'png') -> Path:
    """
    Get standardized path for a visual/image file.

    Args:
        video_job_id: Unique ID of the video job
        image_number: Image number (1-based)
        extension: File extension (default: 'png')

    Returns:
        Path to image file
    """
    job_dirs = get_video_job_directory(video_job_id)
    if not job_dirs:
        raise ValueError(f"Video job directory not found for ID: {video_job_id}")

    filename = f"visual_{image_number:02d}.{extension}"
    return job_dirs['images'] / filename


def get_output_video_path(video_job_id: str) -> Path:
    """
    Get path for final rendered video.

    Args:
        video_job_id: Unique ID of the video job

    Returns:
        Path to output video file
    """
    job_dirs = get_video_job_directory(video_job_id)
    if not job_dirs:
        raise ValueError(f"Video job directory not found for ID: {video_job_id}")

    return job_dirs['output'] / 'final_video.mp4'


def get_metadata_file_path(video_job_id: str) -> Path:
    """
    Get path for metadata file.

    Args:
        video_job_id: Unique ID of the video job

    Returns:
        Path to metadata file
    """
    job_dirs = get_video_job_directory(video_job_id)
    if not job_dirs:
        raise ValueError(f"Video job directory not found for ID: {video_job_id}")

    return job_dirs['output'] / 'metadata.txt'


def delete_video_job_directory(video_job_id: str) -> bool:
    """
    Delete all media files for a video job.

    Args:
        video_job_id: Unique ID of the video job

    Returns:
        True if deleted successfully, False if directory not found
    """
    import shutil

    job_dirs = get_video_job_directory(video_job_id)
    if not job_dirs:
        return False

    try:
        shutil.rmtree(job_dirs['root'])
        return True
    except Exception as e:
        print(f"Error deleting video job directory: {e}")
        return False


def get_directory_size(video_job_id: str) -> int:
    """
    Get total size of all media files for a video job.

    Args:
        video_job_id: Unique ID of the video job

    Returns:
        Total size in bytes, or 0 if directory not found
    """
    job_dirs = get_video_job_directory(video_job_id)
    if not job_dirs:
        return 0

    total_size = 0
    for dirpath, dirnames, filenames in os.walk(job_dirs['root']):
        for filename in filenames:
            filepath = Path(dirpath) / filename
            try:
                total_size += filepath.stat().st_size
            except:
                pass

    return total_size


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 GB", "250 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"
