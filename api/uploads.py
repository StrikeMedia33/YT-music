"""
File Upload API Routes

Handles uploading music tracks and other media files for video jobs.
Supports manual upload workflow (e.g., for Suno-generated music).
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path
import shutil

from models import VideoJob, get_db
from utils.media_manager import (
    get_video_job_directory,
    get_next_track_number,
    get_music_file_path,
    list_music_files,
    format_file_size,
    get_directory_size
)

router = APIRouter()

# Maximum file size: 50MB per file
MAX_FILE_SIZE = 50 * 1024 * 1024

# Allowed audio formats
ALLOWED_AUDIO_FORMATS = {'.mp3', '.wav', '.m4a', '.aac', '.flac'}


@router.post("/video-jobs/{job_id}/music")
async def upload_music_track(
    job_id: str,
    file: UploadFile = File(...),
    track_number: int = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload a music track for a video job.

    Args:
        job_id: Video job ID
        file: Audio file to upload
        track_number: Optional track number (auto-assigned if not provided)
        db: Database session

    Returns:
        Upload status with file details
    """
    # Verify video job exists
    video_job = db.query(VideoJob).filter_by(id=job_id).first()
    if not video_job:
        raise HTTPException(status_code=404, detail="Video job not found")

    # Check if video job directory exists
    job_dirs = get_video_job_directory(job_id)
    if not job_dirs:
        raise HTTPException(
            status_code=400,
            detail="Video job media directory not initialized. Please create the video job first."
        )

    # Validate file format
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_AUDIO_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format. Allowed formats: {', '.join(ALLOWED_AUDIO_FORMATS)}"
        )

    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {format_file_size(MAX_FILE_SIZE)}"
        )

    # Determine track number
    if track_number is None:
        track_number = get_next_track_number(job_id)

    # Validate track number
    if not (1 <= track_number <= 20):
        raise HTTPException(
            status_code=400,
            detail="Track number must be between 1 and 20"
        )

    # Get file path
    file_path = get_music_file_path(job_id, track_number, file_ext.lstrip('.'))

    # Check if file already exists
    if file_path.exists():
        raise HTTPException(
            status_code=409,
            detail=f"Track {track_number} already exists. Delete it first or use a different track number."
        )

    # Save file
    try:
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {str(e)}"
        )
    finally:
        file.file.close()

    return {
        "success": True,
        "message": f"Track {track_number} uploaded successfully",
        "file": {
            "track_number": track_number,
            "filename": file_path.name,
            "path": str(file_path),
            "size": format_file_size(file_size),
            "format": file_ext.lstrip('.')
        }
    }


@router.get("/video-jobs/{job_id}/music")
async def list_uploaded_music(
    job_id: str,
    db: Session = Depends(get_db)
):
    """
    List all uploaded music tracks for a video job.

    Args:
        job_id: Video job ID
        db: Database session

    Returns:
        List of uploaded music files with details
    """
    # Verify video job exists
    video_job = db.query(VideoJob).filter_by(id=job_id).first()
    if not video_job:
        raise HTTPException(status_code=404, detail="Video job not found")

    # Get music files
    music_files = list_music_files(job_id)

    files = []
    for file_path in music_files:
        # Extract track number from filename
        import re
        match = re.search(r'track_(\d+)', file_path.stem.lower())
        track_number = int(match.group(1)) if match else None

        files.append({
            "track_number": track_number,
            "filename": file_path.name,
            "path": str(file_path),
            "size": format_file_size(file_path.stat().st_size),
            "format": file_path.suffix.lstrip('.'),
            "created_at": file_path.stat().st_mtime
        })

    # Sort by track number
    files.sort(key=lambda x: x['track_number'] or 999)

    return {
        "success": True,
        "job_id": job_id,
        "total_tracks": len(files),
        "total_size": format_file_size(get_directory_size(job_id)),
        "files": files
    }


@router.delete("/video-jobs/{job_id}/music/{track_number}")
async def delete_music_track(
    job_id: str,
    track_number: int,
    db: Session = Depends(get_db)
):
    """
    Delete an uploaded music track.

    Args:
        job_id: Video job ID
        track_number: Track number to delete
        db: Database session

    Returns:
        Deletion status
    """
    # Verify video job exists
    video_job = db.query(VideoJob).filter_by(id=job_id).first()
    if not video_job:
        raise HTTPException(status_code=404, detail="Video job not found")

    # Find the file
    music_files = list_music_files(job_id)
    target_file = None

    for file_path in music_files:
        import re
        match = re.search(r'track_(\d+)', file_path.stem.lower())
        if match and int(match.group(1)) == track_number:
            target_file = file_path
            break

    if not target_file:
        raise HTTPException(
            status_code=404,
            detail=f"Track {track_number} not found"
        )

    # Delete file
    try:
        target_file.unlink()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete file: {str(e)}"
        )

    return {
        "success": True,
        "message": f"Track {track_number} deleted successfully"
    }


@router.post("/video-jobs/{job_id}/music/batch")
async def upload_multiple_tracks(
    job_id: str,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload multiple music tracks at once.

    Args:
        job_id: Video job ID
        files: List of audio files to upload
        db: Database session

    Returns:
        Batch upload status with individual file results
    """
    # Verify video job exists
    video_job = db.query(VideoJob).filter_by(id=job_id).first()
    if not video_job:
        raise HTTPException(status_code=404, detail="Video job not found")

    # Check if video job directory exists
    job_dirs = get_video_job_directory(job_id)
    if not job_dirs:
        raise HTTPException(
            status_code=400,
            detail="Video job media directory not initialized"
        )

    # Limit number of files
    if len(files) > 20:
        raise HTTPException(
            status_code=400,
            detail="Maximum 20 files allowed per batch upload"
        )

    results = []
    success_count = 0
    failed_count = 0

    for idx, file in enumerate(files, start=1):
        try:
            # Validate file format
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in ALLOWED_AUDIO_FORMATS:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": f"Invalid format: {file_ext}"
                })
                failed_count += 1
                continue

            # Check file size
            file.file.seek(0, 2)
            file_size = file.file.tell()
            file.file.seek(0)

            if file_size > MAX_FILE_SIZE:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": "File too large"
                })
                failed_count += 1
                continue

            # Auto-assign track number
            track_number = get_next_track_number(job_id)

            # Get file path
            file_path = get_music_file_path(job_id, track_number, file_ext.lstrip('.'))

            # Save file
            with open(file_path, 'wb') as f:
                shutil.copyfileobj(file.file, f)

            results.append({
                "filename": file.filename,
                "success": True,
                "track_number": track_number,
                "size": format_file_size(file_size)
            })
            success_count += 1

        except Exception as e:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": str(e)
            })
            failed_count += 1
        finally:
            file.file.close()

    return {
        "success": failed_count == 0,
        "message": f"Uploaded {success_count}/{len(files)} files successfully",
        "total": len(files),
        "success_count": success_count,
        "failed_count": failed_count,
        "results": results
    }
