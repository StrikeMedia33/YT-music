"""Genre API Routes"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from models import Genre, VideoIdea, get_db
from schemas import GenreCreate, GenreUpdate, GenreResponse, GenreWithStats

router = APIRouter()


@router.post("/", response_model=GenreResponse, status_code=201)
def create_genre(genre: GenreCreate, db: Session = Depends(get_db)):
    """Create a new genre"""
    # Check if genre with same name or slug already exists
    existing = db.query(Genre).filter(
        (Genre.name == genre.name) | (Genre.slug == genre.slug)
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Genre with name '{genre.name}' or slug '{genre.slug}' already exists"
        )

    db_genre = Genre(**genre.model_dump())
    db.add(db_genre)
    db.commit()
    db.refresh(db_genre)
    return db_genre


@router.get("/", response_model=List[GenreWithStats])
def list_genres(
    include_inactive: bool = Query(False, description="Include inactive genres"),
    with_stats: bool = Query(True, description="Include idea counts"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all genres with optional statistics"""
    query = db.query(Genre)

    if not include_inactive:
        query = query.filter(Genre.is_active == True)

    query = query.order_by(Genre.sort_order, Genre.name)
    genres = query.offset(skip).limit(limit).all()

    if with_stats:
        # Add statistics to each genre
        result = []
        for genre in genres:
            genre_dict = genre.to_dict()
            # Count ideas for this genre
            total_ideas = db.query(func.count(VideoIdea.id)).filter(
                VideoIdea.genre_id == genre.id
            ).scalar()
            active_ideas = db.query(func.count(VideoIdea.id)).filter(
                VideoIdea.genre_id == genre.id,
                VideoIdea.is_archived == False
            ).scalar()

            genre_dict['idea_count'] = total_ideas or 0
            genre_dict['active_idea_count'] = active_ideas or 0
            result.append(genre_dict)
        return result
    else:
        return genres


@router.get("/{genre_id}", response_model=GenreWithStats)
def get_genre(genre_id: str, db: Session = Depends(get_db)):
    """Get a specific genre by ID"""
    genre = db.query(Genre).filter(Genre.id == genre_id).first()
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")

    # Add statistics
    genre_dict = genre.to_dict()
    total_ideas = db.query(func.count(VideoIdea.id)).filter(
        VideoIdea.genre_id == genre.id
    ).scalar()
    active_ideas = db.query(func.count(VideoIdea.id)).filter(
        VideoIdea.genre_id == genre.id,
        VideoIdea.is_archived == False
    ).scalar()

    genre_dict['idea_count'] = total_ideas or 0
    genre_dict['active_idea_count'] = active_ideas or 0

    return genre_dict


@router.get("/slug/{slug}", response_model=GenreResponse)
def get_genre_by_slug(slug: str, db: Session = Depends(get_db)):
    """Get a specific genre by slug"""
    genre = db.query(Genre).filter(Genre.slug == slug).first()
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    return genre


@router.put("/{genre_id}", response_model=GenreResponse)
def update_genre(
    genre_id: str,
    genre_update: GenreUpdate,
    db: Session = Depends(get_db)
):
    """Update a genre"""
    genre = db.query(Genre).filter(Genre.id == genre_id).first()
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")

    # Check for duplicate name/slug if being updated
    update_data = genre_update.model_dump(exclude_unset=True)
    if 'name' in update_data or 'slug' in update_data:
        existing = db.query(Genre).filter(
            Genre.id != genre_id,
            (Genre.name == update_data.get('name', genre.name)) |
            (Genre.slug == update_data.get('slug', genre.slug))
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Genre with this name or slug already exists"
            )

    for key, value in update_data.items():
        setattr(genre, key, value)

    db.commit()
    db.refresh(genre)
    return genre


@router.delete("/{genre_id}", status_code=204)
def delete_genre(genre_id: str, db: Session = Depends(get_db)):
    """
    Delete a genre (soft delete by setting is_active=False)
    Hard delete only if no ideas exist for this genre
    """
    genre = db.query(Genre).filter(Genre.id == genre_id).first()
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")

    # Check if genre has ideas
    idea_count = db.query(func.count(VideoIdea.id)).filter(
        VideoIdea.genre_id == genre.id
    ).scalar()

    if idea_count > 0:
        # Soft delete - just mark as inactive
        genre.is_active = False
        db.commit()
    else:
        # Hard delete - no ideas exist
        db.delete(genre)
        db.commit()
