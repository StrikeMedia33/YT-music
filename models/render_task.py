"""
RenderTask Model
Represents FFmpeg rendering tasks and results
"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
import uuid

from .database import Base


class RenderStatus(str, enum.Enum):
    """Rendering task status"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class RenderTask(Base):
    """
    Render task model

    Stores FFmpeg rendering information for video jobs
    Tracks the rendering process from pending to completed/failed

    Attributes:
        id: Unique render task identifier (UUID)
        video_job_id: Foreign key to video_jobs table
        ffmpeg_command: Complete FFmpeg command executed
        local_video_path: Path to rendered video file
        resolution: Video resolution (default: 1920x1080)
        duration_seconds: Final video duration
        status: Rendering status
        error_message: Error details if status is 'failed'
        created_at: Task creation timestamp
        completed_at: Task completion timestamp
    """

    __tablename__ = "render_tasks"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    video_job_id = Column(
        UUID(as_uuid=True), ForeignKey("video_jobs.id", ondelete="CASCADE"), nullable=False
    )

    # Rendering Details
    ffmpeg_command = Column(Text, nullable=False)
    local_video_path = Column(Text, nullable=True)
    resolution = Column(String(20), default="1920x1080", nullable=False)
    duration_seconds = Column(Numeric(10, 2), nullable=True)

    # Status
    status = Column(
        Enum(RenderStatus, native_enum=False),
        default=RenderStatus.PENDING,
        nullable=False,
    )
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    video_job = relationship("VideoJob", back_populates="render_tasks")

    def __repr__(self):
        return f"<RenderTask(id={self.id}, status='{self.status.value}', resolution='{self.resolution}')>"

    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            "id": str(self.id),
            "video_job_id": str(self.video_job_id),
            "ffmpeg_command": self.ffmpeg_command,
            "local_video_path": self.local_video_path,
            "resolution": self.resolution,
            "duration_seconds": float(self.duration_seconds) if self.duration_seconds else None,
            "status": self.status.value,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
