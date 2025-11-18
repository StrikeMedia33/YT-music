"""
VideoJob Model
Represents video generation jobs and tracks pipeline progress
"""

from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Enum, CheckConstraint, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
import uuid
from datetime import datetime

from .database import Base


class VideoJobStatus(str, enum.Enum):
    """Video job pipeline status"""

    PLANNED = "planned"
    GENERATING_MUSIC = "generating_music"
    GENERATING_IMAGE = "generating_image"
    RENDERING = "rendering"
    READY_FOR_EXPORT = "ready_for_export"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class VideoStatusDisplay(str, enum.Enum):
    """Display status for completed videos (used in Videos page)"""

    PRODUCTION = "production"  # ready_for_export, not draft, not published
    DRAFT = "draft"  # is_draft=true
    SCHEDULED = "scheduled"  # scheduled_publish_date set, not published
    PUBLISHED = "published"  # youtube_video_id set


class VideoJob(Base):
    """
    Video generation job model

    Tracks a video through the complete generation pipeline:
    planned → generating_music → generating_image → rendering → ready_for_export → completed

    Attributes:
        id: Unique job identifier (UUID)
        channel_id: Foreign key to channels table
        status: Current pipeline status
        niche_label: Video niche/theme
        mood_keywords: Comma-separated mood descriptors
        target_duration_minutes: Target video length (60-90 minutes)
        prompts_json: Generated prompts for music and visuals
        local_video_path: Path to final rendered video
        output_directory: Directory for all job assets
        error_message: Error details if status is 'failed'
        created_at: Job creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "video_jobs"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    channel_id = Column(
        UUID(as_uuid=True), ForeignKey("channels.id", ondelete="CASCADE"), nullable=False
    )

    # Job Configuration
    status = Column(
        Enum(VideoJobStatus, native_enum=False, values_callable=lambda obj: [e.value for e in obj]),
        default=VideoJobStatus.PLANNED,
        nullable=False,
    )
    niche_label = Column(String(255), nullable=False)
    mood_keywords = Column(Text, nullable=False)
    target_duration_minutes = Column(Integer, nullable=False)

    # Generated Data
    prompts_json = Column(JSONB, nullable=True)  # Stores music and visual prompts

    # File Paths
    local_video_path = Column(Text, nullable=True)
    output_directory = Column(Text, nullable=False)

    # Error Tracking
    error_message = Column(Text, nullable=True)

    # YouTube Publishing Fields
    youtube_video_id = Column(String(255), nullable=True)  # YouTube video ID
    youtube_url = Column(Text, nullable=True)  # Full YouTube URL
    scheduled_publish_date = Column(DateTime(timezone=True), nullable=True)  # Scheduled publish date
    is_draft = Column(Boolean, default=False, nullable=False)  # Draft flag
    published_at = Column(DateTime(timezone=True), nullable=True)  # Actual publish timestamp
    video_title = Column(Text, nullable=True)  # Generated title for YouTube
    video_description = Column(Text, nullable=True)  # Generated description

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "target_duration_minutes BETWEEN 60 AND 90",
            name="check_target_duration_range",
        ),
    )

    # Relationships
    channel = relationship("Channel", back_populates="video_jobs")
    audio_tracks = relationship(
        "AudioTrack",
        back_populates="video_job",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="AudioTrack.order_index",
    )
    images = relationship(
        "Image",
        back_populates="video_job",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Image.order_index",
    )
    render_tasks = relationship(
        "RenderTask",
        back_populates="video_job",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    idea_link = relationship(
        "VideoJobIdea",
        back_populates="video_job",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,  # One-to-one relationship
    )

    @property
    def video_status(self) -> VideoStatusDisplay:
        """
        Compute the display status for the Videos page based on job state.

        Logic:
        - Published: Has youtube_video_id
        - Draft: is_draft=true
        - Scheduled: Has scheduled_publish_date and not published
        - Production: ready_for_export, not draft, not scheduled, not published
        """
        if self.youtube_video_id:
            return VideoStatusDisplay.PUBLISHED
        elif self.is_draft:
            return VideoStatusDisplay.DRAFT
        elif self.scheduled_publish_date:
            return VideoStatusDisplay.SCHEDULED
        else:
            return VideoStatusDisplay.PRODUCTION

    def mark_as_draft(self, is_draft: bool = True):
        """Toggle draft status"""
        self.is_draft = is_draft

    def schedule(self, publish_date: datetime):
        """Schedule video for future publish"""
        self.scheduled_publish_date = publish_date
        self.is_draft = False  # Remove draft status when scheduling

    def mark_as_published(self, youtube_video_id: str, youtube_url: str, published_at: datetime = None):
        """Mark video as published to YouTube"""
        self.youtube_video_id = youtube_video_id
        self.youtube_url = youtube_url
        self.published_at = published_at or datetime.now()
        self.is_draft = False
        self.status = VideoJobStatus.COMPLETED  # Move to completed status

    def __repr__(self):
        return f"<VideoJob(id={self.id}, status='{self.status.value}', niche='{self.niche_label}')>"

    def to_dict(self, include_relations=False):
        """Convert model to dictionary for API responses"""
        data = {
            "id": str(self.id),
            "channel_id": str(self.channel_id),
            "status": self.status.value,
            "niche_label": self.niche_label,
            "mood_keywords": self.mood_keywords,
            "target_duration_minutes": self.target_duration_minutes,
            "prompts_json": self.prompts_json,
            "local_video_path": self.local_video_path,
            "output_directory": self.output_directory,
            "error_message": self.error_message,
            "youtube_video_id": self.youtube_video_id,
            "youtube_url": self.youtube_url,
            "scheduled_publish_date": self.scheduled_publish_date.isoformat() if self.scheduled_publish_date else None,
            "is_draft": self.is_draft,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "video_title": self.video_title,
            "video_description": self.video_description,
            "video_status": self.video_status.value if self.status in [VideoJobStatus.READY_FOR_EXPORT, VideoJobStatus.COMPLETED] else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_relations:
            # Include channel information
            if self.channel:
                data["channel"] = {
                    "id": str(self.channel.id),
                    "name": self.channel.name,
                    "brand_niche": self.channel.brand_niche,
                    "youtube_channel_id": self.channel.youtube_channel_id,
                    "is_active": self.channel.is_active,
                }

            data["audio_tracks"] = [track.to_dict() for track in self.audio_tracks]
            data["images"] = [img.to_dict() for img in self.images]
            data["render_tasks"] = [task.to_dict() for task in self.render_tasks]

        return data
