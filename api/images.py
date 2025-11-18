"""Image API Routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pathlib import Path
import os
from models import Image, VideoJob, get_db
from providers import get_visual_provider

router = APIRouter()


@router.post("/{image_id}/regenerate", status_code=201)
def regenerate_image(image_id: str, db: Session = Depends(get_db)):
    """
    Regenerate an image by creating an alternative version.

    Uses the existing prompt_text to generate a new image with the same specifications.
    The new image will have is_alternative=True and is_selected=False.
    """
    # Get the original image
    original_image = db.query(Image).filter(Image.id == image_id).first()
    if not original_image:
        raise HTTPException(status_code=404, detail="Image not found")

    # Get the video job to check status
    video_job = db.query(VideoJob).filter(VideoJob.id == original_image.video_job_id).first()
    if not video_job:
        raise HTTPException(status_code=404, detail="Video job not found")

    try:
        # Get the visual provider
        visual_provider = get_visual_provider()

        # Get output directory for this video job
        output_base_dir = Path(os.getenv("OUTPUT_DIRECTORY", "./output"))
        job_output_dir = output_base_dir / video_job.output_directory / "images"

        # Generate new image using the same prompt
        image_metadata = visual_provider.generate_visual(
            prompt=original_image.prompt_text,
            order_index=original_image.order_index,
            output_dir=job_output_dir
        )

        # Create new image record as alternative
        new_image = Image(
            video_job_id=original_image.video_job_id,
            order_index=original_image.order_index,  # Same order_index for alternatives
            prompt_text=original_image.prompt_text,
            local_file_path=image_metadata['file_path'],
            provider=original_image.provider,  # Use same provider as original
            provider_image_id=image_metadata.get('provider_image_id'),
            is_alternative=True,  # Mark as alternative
            is_selected=False,  # Not selected by default
            display_order=None,  # No display order until arranged
            original_resolution=image_metadata.get('resolution'),
            upscaled=False  # Initial generation is not upscaled
        )

        db.add(new_image)
        db.commit()
        db.refresh(new_image)

        return new_image.to_dict()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to regenerate image: {str(e)}"
        )


@router.patch("/{image_id}/select")
def select_image(image_id: str, db: Session = Depends(get_db)):
    """
    Mark an image as selected for the final video.

    Deselects all other images with the same video_job_id and order_index.
    """
    # Get the image to select
    image_to_select = db.query(Image).filter(Image.id == image_id).first()
    if not image_to_select:
        raise HTTPException(status_code=404, detail="Image not found")

    # Get all images with the same video_job_id and order_index
    all_images_at_position = db.query(Image).filter(
        Image.video_job_id == image_to_select.video_job_id,
        Image.order_index == image_to_select.order_index
    ).all()

    # Deselect all images at this position
    deselected_ids = []
    for image in all_images_at_position:
        if image.id != image_to_select.id and image.is_selected:
            image.is_selected = False
            deselected_ids.append(str(image.id))

    # Select the chosen image
    image_to_select.is_selected = True

    db.commit()
    db.refresh(image_to_select)

    return {
        "success": True,
        "selected_id": str(image_to_select.id),
        "deselected_ids": deselected_ids
    }
