"""
Video Idea Model
Represents reusable video concept templates
"""

from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from .database import Base


class VideoIdea(Base):
    """
    Video idea/template model for reusable video concepts

    Attributes:
        id: Unique idea identifier (UUID)
        genre_id: Foreign key to genre
        title: Descriptive title (e.g., "Regency Era Ballroom Ambience")
        description: Detailed concept description
        niche_label: Specific niche for this idea
        mood_tags: Array of mood keywords (JSONB: ["calm", "elegant", "atmospheric"])
        target_duration_minutes: Target video duration
        num_tracks: Number of music tracks (default 20)
        is_template: Whether this can be used as a template
        is_archived: Soft delete flag
        times_used: Counter for how many video jobs created from this idea
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "video_ideas"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    genre_id = Column(
        UUID(as_uuid=True),
        ForeignKey("genres.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Idea Information
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    niche_label = Column(String(255), nullable=False)

    # Configuration
    mood_tags = Column(JSONB, default=[], nullable=False)
    target_duration_minutes = Column(Integer, default=70, nullable=False)
    num_tracks = Column(Integer, default=20, nullable=False)

    # Status
    is_template = Column(Boolean, default=True, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)
    times_used = Column(Integer, default=0, nullable=False)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    genre = relationship("Genre", back_populates="video_ideas")

    prompts = relationship(
        "IdeaPrompt",
        back_populates="video_idea",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,  # One-to-one relationship
    )

    video_job_links = relationship(
        "VideoJobIdea",
        back_populates="video_idea",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self):
        return f"<VideoIdea(id={self.id}, title='{self.title}', genre_id={self.genre_id})>"

    def to_dict(self, include_prompts=False):
        """Convert model to dictionary for API responses"""
        data = {
            "id": str(self.id),
            "genre_id": str(self.genre_id),
            "title": self.title,
            "description": self.description,
            "niche_label": self.niche_label,
            "mood_tags": self.mood_tags,
            "target_duration_minutes": self.target_duration_minutes,
            "num_tracks": self.num_tracks,
            "is_template": self.is_template,
            "is_archived": self.is_archived,
            "times_used": self.times_used,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        # Optionally include prompts (for detail views)
        if include_prompts and self.prompts:
            data["prompts"] = self.prompts.to_dict()

        return data
