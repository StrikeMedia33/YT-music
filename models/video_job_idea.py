"""
Video Job Idea Link Model
Links video jobs to the ideas they were created from
"""

from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from .database import Base


class VideoJobIdea(Base):
    """
    Link table between VideoJob and VideoIdea

    Tracks which ideas were used to create which video jobs,
    and stores any customizations made from the template.

    Attributes:
        id: Unique link identifier (UUID)
        video_job_id: Foreign key to video_jobs
        video_idea_id: Foreign key to video_ideas
        customizations_json: JSONB storing what was changed from template
        created_at: Creation timestamp
    """

    __tablename__ = "video_job_ideas"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    video_job_id = Column(
        UUID(as_uuid=True),
        ForeignKey("video_jobs.id", ondelete="CASCADE"),
        nullable=False,
    )

    video_idea_id = Column(
        UUID(as_uuid=True),
        ForeignKey("video_ideas.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Customizations tracking
    customizations_json = Column(
        JSONB,
        default={},
        nullable=False,
        comment="Tracks modifications from original idea template",
    )

    # Timestamp
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    video_job = relationship("VideoJob", back_populates="idea_link")
    video_idea = relationship("VideoIdea", back_populates="video_job_links")

    def __repr__(self):
        return f"<VideoJobIdea(id={self.id}, job_id={self.video_job_id}, idea_id={self.video_idea_id})>"

    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            "id": str(self.id),
            "video_job_id": str(self.video_job_id),
            "video_idea_id": str(self.video_idea_id),
            "customizations_json": self.customizations_json,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
