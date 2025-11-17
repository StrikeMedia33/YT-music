"""
Genre Model
Represents music/video genres for categorizing ideas
"""

from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from .database import Base


class Genre(Base):
    """
    Genre model for categorizing video ideas

    Attributes:
        id: Unique genre identifier (UUID)
        name: Display name (e.g., "Classical", "Lo-fi Hip Hop")
        slug: URL-friendly identifier (e.g., "classical", "lo-fi-hip-hop")
        description: Detailed genre description
        color: Hex color code for UI display (e.g., "#3B82F6")
        icon_name: Icon identifier for UI (e.g., "violin", "headphones")
        default_duration_minutes: Default video duration for this genre
        is_active: Whether genre is currently active
        sort_order: Custom ordering for UI display
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "genres"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Genre Information
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    # UI Display
    color = Column(String(7), nullable=True)  # Hex color #RRGGBB
    icon_name = Column(String(50), nullable=True)

    # Configuration
    default_duration_minutes = Column(Integer, default=70, nullable=False)

    # Status and Ordering
    is_active = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    video_ideas = relationship(
        "VideoIdea",
        back_populates="genre",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self):
        return f"<Genre(id={self.id}, name='{self.name}', slug='{self.slug}')>"

    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            "id": str(self.id),
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "color": self.color,
            "icon_name": self.icon_name,
            "default_duration_minutes": self.default_duration_minutes,
            "is_active": self.is_active,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
