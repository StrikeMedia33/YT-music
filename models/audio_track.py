"""
AudioTrack Model
Represents individual generated audio tracks (20 per video)
"""

from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Enum, CheckConstraint, Numeric, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
import uuid

from .database import Base


class MusicProvider(str, enum.Enum):
    """Music generation provider"""

    DUMMY = "dummy"
    MUBERT = "mubert"
    BEATOVEN = "beatoven"


class AudioTrack(Base):
    """
    Audio track model

    Represents one of 20 unique music tracks in a video
    Tracks are ordered 1-20 and paired with corresponding visuals

    Supports alternative versions: multiple tracks can share the same order_index,
    but only one is selected for the final video.

    Attributes:
        id: Unique track identifier (UUID)
        video_job_id: Foreign key to video_jobs table
        provider: Music generation provider
        provider_track_id: External API track ID (if applicable)
        order_index: Track position in video (1-20)
        duration_seconds: Exact track duration
        local_file_path: Path to audio file
        license_document_url: URL to licensing documentation
        prompt_text: LLM prompt used to generate this track
        is_alternative: True if this is an alternative version (not the first generation)
        is_selected: True if this version is selected for the final video
        display_order: Custom order for final video (nullable until arranged by user)
        created_at: Creation timestamp
    """

    __tablename__ = "audio_tracks"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    video_job_id = Column(
        UUID(as_uuid=True), ForeignKey("video_jobs.id", ondelete="CASCADE"), nullable=False
    )

    # Provider Information
    provider = Column(Enum(MusicProvider, native_enum=False), nullable=False)
    provider_track_id = Column(String(255), nullable=True)

    # Track Details
    order_index = Column(Integer, nullable=False)
    duration_seconds = Column(Numeric(6, 2), nullable=False)
    local_file_path = Column(Text, nullable=False)
    license_document_url = Column(Text, nullable=True)
    prompt_text = Column(Text, nullable=False)

    # Alternative Assets & Arrangement
    is_alternative = Column(Boolean, default=False, nullable=False)
    is_selected = Column(Boolean, default=True, nullable=False)
    display_order = Column(Integer, nullable=True)

    # Timestamp
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Constraints
    __table_args__ = (
        CheckConstraint("order_index BETWEEN 1 AND 20", name="check_order_index_range"),
        CheckConstraint("duration_seconds > 0", name="check_duration_positive"),
    )

    # Relationships
    video_job = relationship("VideoJob", back_populates="audio_tracks")

    def __repr__(self):
        return f"<AudioTrack(id={self.id}, order={self.order_index}, duration={self.duration_seconds}s)>"

    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            "id": str(self.id),
            "video_job_id": str(self.video_job_id),
            "provider": self.provider.value,
            "provider_track_id": self.provider_track_id,
            "order_index": self.order_index,
            "duration_seconds": float(self.duration_seconds),
            "local_file_path": self.local_file_path,
            "license_document_url": self.license_document_url,
            "prompt_text": self.prompt_text,
            "is_alternative": self.is_alternative,
            "is_selected": self.is_selected,
            "display_order": self.display_order,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
