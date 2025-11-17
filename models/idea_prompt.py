"""
Idea Prompt Model
Stores generated prompts and metadata for video ideas
"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from .database import Base


class IdeaPrompt(Base):
    """
    Idea prompt model for storing generated prompts and metadata

    Attributes:
        id: Unique prompt identifier (UUID)
        idea_id: Foreign key to video_idea (one-to-one)
        music_prompts: Array of 20 music generation prompts (JSONB)
        visual_prompts: Array of 20 visual generation prompts (JSONB)
        metadata_title: Pre-generated YouTube title
        metadata_description: Pre-generated YouTube description
        metadata_tags: Array of pre-generated tags (JSONB)
        generation_params: LLM parameters used for generation (JSONB)
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "idea_prompts"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    idea_id = Column(
        UUID(as_uuid=True),
        ForeignKey("video_ideas.id", ondelete="CASCADE"),
        unique=True,  # One-to-one relationship
        nullable=False,
    )

    # Prompts (stored as JSON arrays)
    music_prompts = Column(JSONB, default=[], nullable=False)
    visual_prompts = Column(JSONB, default=[], nullable=False)

    # Generated Metadata
    metadata_title = Column(String(255), nullable=True)
    metadata_description = Column(Text, nullable=True)
    metadata_tags = Column(JSONB, default=[], nullable=False)

    # Generation Information
    generation_params = Column(
        JSONB,
        default={},
        nullable=False,
        comment="LLM provider, model, temperature, etc.",
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    video_idea = relationship("VideoIdea", back_populates="prompts")

    def __repr__(self):
        music_count = len(self.music_prompts) if self.music_prompts else 0
        visual_count = len(self.visual_prompts) if self.visual_prompts else 0
        return f"<IdeaPrompt(id={self.id}, idea_id={self.idea_id}, music={music_count}, visual={visual_count})>"

    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            "id": str(self.id),
            "idea_id": str(self.idea_id),
            "music_prompts": self.music_prompts,
            "visual_prompts": self.visual_prompts,
            "metadata_title": self.metadata_title,
            "metadata_description": self.metadata_description,
            "metadata_tags": self.metadata_tags,
            "generation_params": self.generation_params,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def validate_prompts(self):
        """Validate that we have the correct number of prompts"""
        music_count = len(self.music_prompts) if self.music_prompts else 0
        visual_count = len(self.visual_prompts) if self.visual_prompts else 0

        errors = []
        if music_count != 20:
            errors.append(f"Expected 20 music prompts, got {music_count}")
        if visual_count != 20:
            errors.append(f"Expected 20 visual prompts, got {visual_count}")

        return errors if errors else None
