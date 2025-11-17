"""
Create YouTube Scraping Tables

This migration creates tables for storing scraped YouTube channel and video data
to enable content analysis and research for video generation.
"""

from models.database import engine
from sqlalchemy import text


def upgrade():
    """Create scraped_channels and scraped_videos tables"""

    with engine.connect() as conn:
        # Create scraped_channels table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS scraped_channels (
                id SERIAL PRIMARY KEY,
                youtube_channel_id VARCHAR(50) UNIQUE NOT NULL,
                channel_name VARCHAR(255) NOT NULL,
                channel_url TEXT NOT NULL,
                rss_feed_url TEXT NOT NULL,
                description TEXT,
                subscriber_count INTEGER DEFAULT 0,
                video_count INTEGER DEFAULT 0,
                last_scraped_at TIMESTAMP WITH TIME ZONE,
                scrape_status VARCHAR(50) DEFAULT 'pending',
                error_message TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

                -- For future multi-user support
                user_id VARCHAR(255),

                -- Optional: Link to our channels table
                linked_channel_id UUID REFERENCES channels(id) ON DELETE SET NULL
            );
        """))

        # Create scraped_videos table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS scraped_videos (
                id SERIAL PRIMARY KEY,
                scraped_channel_id INTEGER NOT NULL REFERENCES scraped_channels(id) ON DELETE CASCADE,
                youtube_video_id VARCHAR(20) UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                video_url TEXT NOT NULL,
                thumbnail_url TEXT,
                published_at TIMESTAMP WITH TIME ZONE,
                duration_seconds INTEGER,
                view_count BIGINT,
                like_count INTEGER,
                comment_count INTEGER,
                tags TEXT[],
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

                -- Derived fields for analysis
                title_length INTEGER,
                description_length INTEGER,
                title_keywords TEXT[]
            );
        """))

        # Create indexes for better query performance
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_scraped_channels_youtube_id
            ON scraped_channels(youtube_channel_id);
        """))

        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_scraped_channels_status
            ON scraped_channels(scrape_status);
        """))

        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_scraped_videos_channel_id
            ON scraped_videos(scraped_channel_id);
        """))

        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_scraped_videos_youtube_id
            ON scraped_videos(youtube_video_id);
        """))

        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_scraped_videos_published_at
            ON scraped_videos(published_at DESC);
        """))

        conn.commit()
        print("✅ Created scraped_channels and scraped_videos tables")


def downgrade():
    """Drop scraped_channels and scraped_videos tables"""

    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS scraped_videos CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS scraped_channels CASCADE;"))
        conn.commit()
        print("✅ Dropped scraped_channels and scraped_videos tables")


if __name__ == "__main__":
    print("Running migration: Create YouTube Scraping Tables")
    upgrade()
    print("Migration completed successfully!")
