"""Audio Track API Routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pathlib import Path
import os
from models import AudioTrack, VideoJob, get_db
from providers import get_music_provider

router = APIRouter()


@router.post("/{track_id}/regenerate", status_code=201)
def regenerate_audio_track(track_id: str, db: Session = Depends(get_db)):
    """
    Regenerate an audio track by creating an alternative version.

    Uses the existing prompt_text to generate a new track with the same specifications.
    The new track will have is_alternative=True and is_selected=False.
    """
    # Get the original track
    original_track = db.query(AudioTrack).filter(AudioTrack.id == track_id).first()
    if not original_track:
        raise HTTPException(status_code=404, detail="Audio track not found")

    # Get the video job to check status
    video_job = db.query(VideoJob).filter(VideoJob.id == original_track.video_job_id).first()
    if not video_job:
        raise HTTPException(status_code=404, detail="Video job not found")

    try:
        # Get the music provider
        music_provider = get_music_provider()

        # Get output directory for this video job
        output_base_dir = Path(os.getenv("OUTPUT_DIRECTORY", "./output"))
        job_output_dir = output_base_dir / video_job.output_directory / "audio"

        # Generate new track using the same prompt
        # Extract duration from original track (convert Decimal to float for API)
        duration_minutes = float(original_track.duration_seconds) / 60.0

        # Generate new track
        track_metadata = music_provider.generate_track(
            prompt=original_track.prompt_text,
            duration_minutes=duration_minutes,
            order_index=original_track.order_index,
            output_dir=job_output_dir
        )

        # Create new audio track record as alternative
        new_track = AudioTrack(
            video_job_id=original_track.video_job_id,
            order_index=original_track.order_index,  # Same order_index for alternatives
            prompt_text=original_track.prompt_text,
            duration_seconds=track_metadata['duration_seconds'],
            local_file_path=track_metadata['file_path'],
            provider=original_track.provider,  # Use same provider as original
            provider_track_id=track_metadata.get('provider_track_id'),
            license_document_url=track_metadata.get('license_document_url'),
            is_alternative=True,  # Mark as alternative
            is_selected=False,  # Not selected by default
            display_order=None  # No display order until arranged
        )

        db.add(new_track)
        db.commit()
        db.refresh(new_track)

        return new_track.to_dict()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to regenerate audio track: {str(e)}"
        )


@router.patch("/{track_id}/select")
def select_audio_track(track_id: str, db: Session = Depends(get_db)):
    """
    Mark an audio track as selected for the final video.

    Deselects all other tracks with the same video_job_id and order_index.
    """
    # Get the track to select
    track_to_select = db.query(AudioTrack).filter(AudioTrack.id == track_id).first()
    if not track_to_select:
        raise HTTPException(status_code=404, detail="Audio track not found")

    # Get all tracks with the same video_job_id and order_index
    all_tracks_at_position = db.query(AudioTrack).filter(
        AudioTrack.video_job_id == track_to_select.video_job_id,
        AudioTrack.order_index == track_to_select.order_index
    ).all()

    # Deselect all tracks at this position
    deselected_ids = []
    for track in all_tracks_at_position:
        if track.id != track_to_select.id and track.is_selected:
            track.is_selected = False
            deselected_ids.append(str(track.id))

    # Select the chosen track
    track_to_select.is_selected = True

    db.commit()
    db.refresh(track_to_select)

    return {
        "success": True,
        "selected_id": str(track_to_select.id),
        "deselected_ids": deselected_ids
    }
