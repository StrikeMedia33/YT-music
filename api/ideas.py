"""Video Ideas API Routes"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from typing import List
from models import VideoIdea, IdeaPrompt, Genre, get_db
from schemas import (
    VideoIdeaCreate,
    VideoIdeaUpdate,
    VideoIdeaResponse,
    VideoIdeaDetail,
    VideoIdeaCloneRequest,
    IdeaPromptCreate,
    IdeaPromptUpdate,
)

router = APIRouter()


@router.post("/", response_model=VideoIdeaResponse, status_code=201)
def create_idea(idea: VideoIdeaCreate, db: Session = Depends(get_db)):
    """Create a new video idea"""
    # Verify genre exists
    genre = db.query(Genre).filter(Genre.id == idea.genre_id).first()
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")

    db_idea = VideoIdea(**idea.model_dump())
    db.add(db_idea)
    db.commit()
    db.refresh(db_idea)
    return db_idea


@router.get("/", response_model=List[VideoIdeaResponse])
def list_ideas(
    genre_id: str = Query(None, description="Filter by genre ID"),
    search: str = Query(None, description="Search in title and description"),
    mood_tags: List[str] = Query(None, description="Filter by mood tags"),
    is_template: bool = Query(None, description="Filter by template status"),
    is_archived: bool = Query(False, description="Include archived ideas"),
    sort_by: str = Query('created_at', description="Sort field: created_at, title, times_used"),
    sort_order: str = Query('desc', description="Sort order: asc or desc"),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """List video ideas with filtering and search"""
    query = db.query(VideoIdea).options(joinedload(VideoIdea.genre))

    # Apply filters
    if genre_id:
        query = query.filter(VideoIdea.genre_id == genre_id)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                VideoIdea.title.ilike(search_term),
                VideoIdea.description.ilike(search_term),
                VideoIdea.niche_label.ilike(search_term)
            )
        )

    if mood_tags:
        # Filter by mood tags (JSONB contains)
        for tag in mood_tags:
            query = query.filter(VideoIdea.mood_tags.contains([tag]))

    if is_template is not None:
        query = query.filter(VideoIdea.is_template == is_template)

    if not is_archived:
        query = query.filter(VideoIdea.is_archived == False)

    # Sorting
    if sort_by == 'title':
        order_col = VideoIdea.title
    elif sort_by == 'times_used':
        order_col = VideoIdea.times_used
    else:
        order_col = VideoIdea.created_at

    if sort_order == 'asc':
        query = query.order_by(order_col.asc())
    else:
        query = query.order_by(order_col.desc())

    ideas = query.offset(skip).limit(limit).all()
    return ideas


@router.get("/{idea_id}", response_model=VideoIdeaDetail)
def get_idea(idea_id: str, db: Session = Depends(get_db)):
    """Get a specific idea with full details including prompts"""
    idea = db.query(VideoIdea).options(
        joinedload(VideoIdea.genre),
        joinedload(VideoIdea.prompts)
    ).filter(VideoIdea.id == idea_id).first()

    if not idea:
        raise HTTPException(status_code=404, detail="Video idea not found")

    return idea


@router.put("/{idea_id}", response_model=VideoIdeaResponse)
def update_idea(
    idea_id: str,
    idea_update: VideoIdeaUpdate,
    db: Session = Depends(get_db)
):
    """Update a video idea"""
    idea = db.query(VideoIdea).filter(VideoIdea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Video idea not found")

    update_data = idea_update.model_dump(exclude_unset=True)

    # Verify genre if being updated
    if 'genre_id' in update_data:
        genre = db.query(Genre).filter(Genre.id == update_data['genre_id']).first()
        if not genre:
            raise HTTPException(status_code=404, detail="Genre not found")

    for key, value in update_data.items():
        setattr(idea, key, value)

    db.commit()
    db.refresh(idea)
    return idea


@router.delete("/{idea_id}", status_code=204)
def delete_idea(idea_id: str, db: Session = Depends(get_db)):
    """
    Delete an idea (soft delete by setting is_archived=True)
    Hard delete only if never used
    """
    idea = db.query(VideoIdea).filter(VideoIdea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Video idea not found")

    if idea.times_used > 0:
        # Soft delete - has been used
        idea.is_archived = True
        db.commit()
    else:
        # Hard delete - never used
        db.delete(idea)
        db.commit()


@router.post("/{idea_id}/clone", response_model=VideoIdeaResponse, status_code=201)
def clone_idea(
    idea_id: str,
    clone_request: VideoIdeaCloneRequest,
    db: Session = Depends(get_db)
):
    """Clone an existing idea with optional modifications"""
    original = db.query(VideoIdea).filter(VideoIdea.id == idea_id).first()
    if not original:
        raise HTTPException(status_code=404, detail="Video idea not found")

    # Create clone
    clone_data = {
        'title': clone_request.new_title or f"{original.title} (Copy)",
        'description': original.description,
        'genre_id': original.genre_id,
        'niche_label': original.niche_label,
        'mood_tags': original.mood_tags,
        'target_duration_minutes': original.target_duration_minutes,
        'num_tracks': original.num_tracks,
        'is_template': True,
        'times_used': 0,
    }

    # Apply modifications if provided
    if clone_request.modifications:
        clone_data.update(clone_request.modifications)

    cloned_idea = VideoIdea(**clone_data)
    db.add(cloned_idea)
    db.commit()
    db.refresh(cloned_idea)

    # Clone prompts if they exist
    if original.prompts:
        cloned_prompts = IdeaPrompt(
            idea_id=cloned_idea.id,
            music_prompts=original.prompts.music_prompts,
            visual_prompts=original.prompts.visual_prompts,
            metadata_title=original.prompts.metadata_title,
            metadata_description=original.prompts.metadata_description,
            metadata_tags=original.prompts.metadata_tags,
            generation_params=original.prompts.generation_params,
        )
        db.add(cloned_prompts)
        db.commit()

    return cloned_idea


# Prompts sub-routes

@router.post("/{idea_id}/prompts", response_model=dict, status_code=201)
def create_or_update_prompts(
    idea_id: str,
    prompts: IdeaPromptCreate,
    db: Session = Depends(get_db)
):
    """Create or update prompts for an idea"""
    idea = db.query(VideoIdea).filter(VideoIdea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Video idea not found")

    # Check if prompts already exist
    existing_prompts = db.query(IdeaPrompt).filter(IdeaPrompt.idea_id == idea_id).first()

    if existing_prompts:
        # Update existing
        for key, value in prompts.model_dump(exclude={'idea_id'}).items():
            setattr(existing_prompts, key, value)
        db.commit()
        db.refresh(existing_prompts)
        return {"message": "Prompts updated", "prompts": existing_prompts.to_dict()}
    else:
        # Create new
        db_prompts = IdeaPrompt(idea_id=idea_id, **prompts.model_dump(exclude={'idea_id'}))
        db.add(db_prompts)
        db.commit()
        db.refresh(db_prompts)
        return {"message": "Prompts created", "prompts": db_prompts.to_dict()}


@router.get("/{idea_id}/prompts")
def get_idea_prompts(idea_id: str, db: Session = Depends(get_db)):
    """Get prompts for a specific idea"""
    idea = db.query(VideoIdea).filter(VideoIdea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Video idea not found")

    prompts = db.query(IdeaPrompt).filter(IdeaPrompt.idea_id == idea_id).first()
    if not prompts:
        raise HTTPException(status_code=404, detail="Prompts not found for this idea")

    return prompts.to_dict()


@router.put("/{idea_id}/prompts")
def update_idea_prompts(
    idea_id: str,
    prompts_update: IdeaPromptUpdate,
    db: Session = Depends(get_db)
):
    """Update prompts for an idea"""
    prompts = db.query(IdeaPrompt).filter(IdeaPrompt.idea_id == idea_id).first()
    if not prompts:
        raise HTTPException(status_code=404, detail="Prompts not found for this idea")

    for key, value in prompts_update.model_dump(exclude_unset=True).items():
        setattr(prompts, key, value)

    db.commit()
    db.refresh(prompts)
    return prompts.to_dict()


@router.post("/{idea_id}/use", status_code=200)
def mark_idea_used(idea_id: str, db: Session = Depends(get_db)):
    """Increment the times_used counter for an idea"""
    idea = db.query(VideoIdea).filter(VideoIdea.id == idea_id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Video idea not found")

    idea.times_used += 1
    db.commit()
    db.refresh(idea)

    return {"message": "Idea usage tracked", "times_used": idea.times_used}
