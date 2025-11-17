"""
Image Model
Represents generated background visuals (20 per video)
"""

from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Enum, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
import uuid

from .database import Base


class VisualProvider(str, enum.Enum):
    """Visual generation provider"""

    DUMMY = "dummy"
    LEONARDO = "leonardo"
    GEMINI = "gemini"


class Image(Base):
    """
    Image/visual model

    Represents one of 20 unique background visuals in a video
    Each visual is paired with a corresponding audio track (matching order_index)

    Attributes:
        id: Unique image identifier (UUID)
        video_job_id: Foreign key to video_jobs table
        provider: Visual generation provider
        provider_image_id: External API image ID (if applicable)
        order_index: Visual position in video (1-20, matches audio track)
        local_file_path: Path to image file
        prompt_text: LLM prompt used to generate this visual
        created_at: Creation timestamp
    """

    __tablename__ = "images"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys (nullable for standalone images)
    video_job_id = Column(
        UUID(as_uuid=True), ForeignKey("video_jobs.id", ondelete="CASCADE"), nullable=True
    )

    # Provider Information
    provider = Column(Enum(VisualProvider, native_enum=False), nullable=False)
    provider_image_id = Column(String(255), nullable=True)

    # Image Details
    order_index = Column(Integer, nullable=True)  # Nullable for standalone images
    local_file_path = Column(Text, nullable=False)
    prompt_text = Column(Text, nullable=False)

    # Timestamp
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Constraints
    __table_args__ = (
        CheckConstraint("order_index BETWEEN 1 AND 20", name="check_image_order_range"),
        UniqueConstraint("video_job_id", "order_index", name="unique_video_job_image_order"),
    )

    # Relationships
    video_job = relationship("VideoJob", back_populates="images")

    def __repr__(self):
        return f"<Image(id={self.id}, order={self.order_index}, provider='{self.provider.value}')>"

    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            "id": str(self.id),
            "video_job_id": str(self.video_job_id) if self.video_job_id else None,
            "provider": self.provider.value,
            "provider_image_id": self.provider_image_id,
            "order_index": self.order_index,
            "local_file_path": self.local_file_path,
            "prompt_text": self.prompt_text,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
