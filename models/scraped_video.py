"""
ScrapedVideo Model

Represents a YouTube video that has been scraped from a channel.
Stores video metadata, analytics, and derived fields for analysis.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.database import Base
from datetime import datetime
from typing import Optional, Dict, Any, List


class ScrapedVideo(Base):
    """Model for scraped YouTube videos"""

    __tablename__ = "scraped_videos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scraped_channel_id = Column(
        Integer,
        ForeignKey('scraped_channels.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    youtube_video_id = Column(String(20), unique=True, nullable=False, index=True)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    video_url = Column(Text, nullable=False)
    thumbnail_url = Column(Text, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True, index=True)
    duration_seconds = Column(Integer, nullable=True)
    view_count = Column(BigInteger, nullable=True)
    like_count = Column(Integer, nullable=True)
    comment_count = Column(Integer, nullable=True)
    tags = Column(ARRAY(Text), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Derived fields for analysis
    title_length = Column(Integer, nullable=True)
    description_length = Column(Integer, nullable=True)
    title_keywords = Column(ARRAY(Text), nullable=True)

    # Relationships
    scraped_channel = relationship("ScrapedChannel", back_populates="scraped_videos")

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for API responses"""
        return {
            'id': self.id,
            'scraped_channel_id': self.scraped_channel_id,
            'youtube_video_id': self.youtube_video_id,
            'title': self.title,
            'description': self.description,
            'video_url': self.video_url,
            'thumbnail_url': self.thumbnail_url,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'duration_seconds': self.duration_seconds,
            'view_count': self.view_count,
            'like_count': self.like_count,
            'comment_count': self.comment_count,
            'tags': self.tags if self.tags else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'title_length': self.title_length,
            'description_length': self.description_length,
            'title_keywords': self.title_keywords if self.title_keywords else []
        }

    def calculate_derived_fields(self):
        """Calculate derived fields from existing data"""
        if self.title:
            self.title_length = len(self.title)
            # Extract simple keywords (words longer than 3 chars, capitalized)
            words = self.title.split()
            self.title_keywords = [
                word.strip('.,!?;:()[]{}')
                for word in words
                if len(word) > 3 and (word[0].isupper() or word.isupper())
            ][:10]  # Limit to 10 keywords

        if self.description:
            self.description_length = len(self.description)

    def __repr__(self) -> str:
        return f"<ScrapedVideo(id={self.id}, youtube_video_id='{self.youtube_video_id}', title='{self.title[:50]}...')>"
