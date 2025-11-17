"""
Channel Model
Represents YouTube channels for video distribution
"""

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from .database import Base


class Channel(Base):
    """
    YouTube channel model

    Attributes:
        id: Unique channel identifier (UUID)
        name: Display name for the channel
        youtube_channel_id: YouTube channel ID (nullable for dev/testing)
        brand_niche: Target niche/genre (e.g., "Medieval Fantasy Ambience")
        is_active: Whether channel is currently active
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "channels"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Channel Information
    name = Column(String(255), nullable=False)
    youtube_channel_id = Column(String(100), unique=True, nullable=True)
    brand_niche = Column(String(255), nullable=False)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    video_jobs = relationship(
        "VideoJob",
        back_populates="channel",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self):
        return f"<Channel(id={self.id}, name='{self.name}', niche='{self.brand_niche}')>"

    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            "id": str(self.id),
            "name": self.name,
            "youtube_channel_id": self.youtube_channel_id,
            "brand_niche": self.brand_niche,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
