"""
ScrapedChannel Model

Represents a YouTube channel that has been scraped for research and analysis.
Used to store channel metadata and track scraping status.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.database import Base
from datetime import datetime
from typing import Optional, Dict, Any


class ScrapedChannel(Base):
    """Model for scraped YouTube channels"""

    __tablename__ = "scraped_channels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    youtube_channel_id = Column(String(50), unique=True, nullable=False, index=True)
    channel_name = Column(String(255), nullable=False)
    channel_url = Column(Text, nullable=False)
    rss_feed_url = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    subscriber_count = Column(Integer, default=0)
    video_count = Column(Integer, default=0)
    last_scraped_at = Column(DateTime(timezone=True), nullable=True)
    scrape_status = Column(String(50), default='pending', index=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # For future multi-user support
    user_id = Column(String(255), nullable=True)

    # Optional: Link to our channels table
    linked_channel_id = Column(UUID(as_uuid=True), ForeignKey('channels.id', ondelete='SET NULL'), nullable=True)

    # Relationships
    scraped_videos = relationship(
        "ScrapedVideo",
        back_populates="scraped_channel",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    linked_channel = relationship("Channel", foreign_keys=[linked_channel_id])

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for API responses"""
        return {
            'id': self.id,
            'youtube_channel_id': self.youtube_channel_id,
            'channel_name': self.channel_name,
            'channel_url': self.channel_url,
            'rss_feed_url': self.rss_feed_url,
            'description': self.description,
            'subscriber_count': self.subscriber_count,
            'video_count': self.video_count,
            'last_scraped_at': self.last_scraped_at.isoformat() if self.last_scraped_at else None,
            'scrape_status': self.scrape_status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_id': self.user_id,
            'linked_channel_id': self.linked_channel_id,
            'video_count_scraped': self.scraped_videos.count() if hasattr(self, 'scraped_videos') else 0
        }

    def __repr__(self) -> str:
        return f"<ScrapedChannel(id={self.id}, channel_name='{self.channel_name}', status='{self.scrape_status}')>"
