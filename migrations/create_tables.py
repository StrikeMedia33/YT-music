"""
Database Migration Script
Creates all tables for AI Background Channel Studio

Run with: python migrations/create_tables.py
"""

import os
import sys
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_database_connection():
    """Get database connection from environment variable"""
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set!")
        print("\nPlease add to your .env file:")
        print("DATABASE_URL=postgresql://user:password@host:5432/yt_music")
        sys.exit(1)

    try:
        conn = psycopg2.connect(database_url)
        print(f"✅ Connected to database")
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        sys.exit(1)


def create_enums(conn):
    """Create ENUM types"""
    print("\n📋 Creating ENUM types...")

    cursor = conn.cursor()

    enums = [
        # Video job status enum
        """
        DO $$ BEGIN
            CREATE TYPE video_job_status AS ENUM (
                'planned',
                'generating_music',
                'generating_image',
                'rendering',
                'ready_for_export',
                'completed',
                'failed'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        """,

        # Music provider enum
        """
        DO $$ BEGIN
            CREATE TYPE music_provider AS ENUM (
                'dummy',
                'mubert',
                'beatoven'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        """,

        # Visual provider enum
        """
        DO $$ BEGIN
            CREATE TYPE visual_provider AS ENUM (
                'dummy',
                'leonardo',
                'gemini'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        """,

        # Render status enum
        """
        DO $$ BEGIN
            CREATE TYPE render_status AS ENUM (
                'pending',
                'in_progress',
                'completed',
                'failed'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
        """
    ]

    for enum_sql in enums:
        try:
            cursor.execute(enum_sql)
            conn.commit()
        except Exception as e:
            print(f"  ⚠️  ENUM creation warning: {e}")
            conn.rollback()

    cursor.close()
    print("  ✅ ENUM types created (or already exist)")


def create_channels_table(conn):
    """Create channels table"""
    print("\n📋 Creating 'channels' table...")

    cursor = conn.cursor()

    sql_script = """
    CREATE TABLE IF NOT EXISTS channels (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        name VARCHAR(255) NOT NULL,
        youtube_channel_id VARCHAR(100) UNIQUE,
        brand_niche VARCHAR(255) NOT NULL,
        is_active BOOLEAN DEFAULT TRUE NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
    );

    -- Indexes
    CREATE INDEX IF NOT EXISTS idx_channels_is_active ON channels(is_active);
    CREATE INDEX IF NOT EXISTS idx_channels_created_at ON channels(created_at DESC);
    """

    try:
        cursor.execute(sql_script)
        conn.commit()
        print("  ✅ 'channels' table created")
    except Exception as e:
        print(f"  ❌ Error creating 'channels' table: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()


def create_video_jobs_table(conn):
    """Create video_jobs table"""
    print("\n📋 Creating 'video_jobs' table...")

    cursor = conn.cursor()

    sql_script = """
    CREATE TABLE IF NOT EXISTS video_jobs (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        channel_id UUID NOT NULL REFERENCES channels(id) ON DELETE CASCADE,
        status video_job_status DEFAULT 'planned' NOT NULL,
        niche_label VARCHAR(255) NOT NULL,
        mood_keywords TEXT NOT NULL,
        target_duration_minutes INTEGER NOT NULL CHECK (target_duration_minutes BETWEEN 60 AND 90),
        prompts_json JSONB,
        local_video_path TEXT,
        output_directory TEXT NOT NULL,
        error_message TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
    );

    -- Indexes
    CREATE INDEX IF NOT EXISTS idx_video_jobs_channel_id ON video_jobs(channel_id);
    CREATE INDEX IF NOT EXISTS idx_video_jobs_status ON video_jobs(status);
    CREATE INDEX IF NOT EXISTS idx_video_jobs_created_at ON video_jobs(created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_video_jobs_prompts ON video_jobs USING GIN (prompts_json);
    """

    try:
        cursor.execute(sql_script)
        conn.commit()
        print("  ✅ 'video_jobs' table created")
    except Exception as e:
        print(f"  ❌ Error creating 'video_jobs' table: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()


def create_audio_tracks_table(conn):
    """Create audio_tracks table"""
    print("\n📋 Creating 'audio_tracks' table...")

    cursor = conn.cursor()

    sql_script = """
    CREATE TABLE IF NOT EXISTS audio_tracks (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        video_job_id UUID NOT NULL REFERENCES video_jobs(id) ON DELETE CASCADE,
        provider music_provider NOT NULL,
        provider_track_id VARCHAR(255),
        order_index INTEGER NOT NULL CHECK (order_index BETWEEN 1 AND 20),
        duration_seconds NUMERIC(6, 2) NOT NULL CHECK (duration_seconds > 0),
        local_file_path TEXT NOT NULL,
        license_document_url TEXT,
        prompt_text TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,

        UNIQUE (video_job_id, order_index)
    );

    -- Indexes
    CREATE INDEX IF NOT EXISTS idx_audio_tracks_video_job_id ON audio_tracks(video_job_id);
    CREATE INDEX IF NOT EXISTS idx_audio_tracks_order ON audio_tracks(video_job_id, order_index);
    """

    try:
        cursor.execute(sql_script)
        conn.commit()
        print("  ✅ 'audio_tracks' table created")
    except Exception as e:
        print(f"  ❌ Error creating 'audio_tracks' table: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()


def create_images_table(conn):
    """Create images table"""
    print("\n📋 Creating 'images' table...")

    cursor = conn.cursor()

    sql_script = """
    CREATE TABLE IF NOT EXISTS images (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        video_job_id UUID REFERENCES video_jobs(id) ON DELETE CASCADE,
        provider visual_provider NOT NULL,
        provider_image_id VARCHAR(255),
        order_index INTEGER CHECK (order_index BETWEEN 1 AND 20),
        local_file_path TEXT NOT NULL,
        prompt_text TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,

        UNIQUE (video_job_id, order_index)
    );

    -- Indexes
    CREATE INDEX IF NOT EXISTS idx_images_video_job_id ON images(video_job_id);
    CREATE INDEX IF NOT EXISTS idx_images_order ON images(video_job_id, order_index);
    """

    try:
        cursor.execute(sql_script)
        conn.commit()
        print("  ✅ 'images' table created")
    except Exception as e:
        print(f"  ❌ Error creating 'images' table: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()


def create_render_tasks_table(conn):
    """Create render_tasks table"""
    print("\n📋 Creating 'render_tasks' table...")

    cursor = conn.cursor()

    sql_script = """
    CREATE TABLE IF NOT EXISTS render_tasks (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        video_job_id UUID NOT NULL REFERENCES video_jobs(id) ON DELETE CASCADE,
        ffmpeg_command TEXT NOT NULL,
        local_video_path TEXT,
        resolution VARCHAR(20) DEFAULT '1920x1080' NOT NULL,
        duration_seconds NUMERIC(10, 2),
        status render_status DEFAULT 'pending' NOT NULL,
        error_message TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        completed_at TIMESTAMP WITH TIME ZONE
    );

    -- Indexes
    CREATE INDEX IF NOT EXISTS idx_render_tasks_video_job_id ON render_tasks(video_job_id);
    CREATE INDEX IF NOT EXISTS idx_render_tasks_status ON render_tasks(status);
    CREATE INDEX IF NOT EXISTS idx_render_tasks_created_at ON render_tasks(created_at DESC);
    """

    try:
        cursor.execute(sql_script)
        conn.commit()
        print("  ✅ 'render_tasks' table created")
    except Exception as e:
        print(f"  ❌ Error creating 'render_tasks' table: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()


def verify_tables(conn):
    """Verify all tables were created"""
    print("\n📋 Verifying table creation...")

    cursor = conn.cursor()

    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)

    tables = cursor.fetchall()
    cursor.close()

    expected_tables = ['audio_tracks', 'channels', 'images', 'render_tasks', 'video_jobs']
    found_tables = [t[0] for t in tables if t[0] in expected_tables]

    print(f"\n  Found {len(found_tables)}/{len(expected_tables)} tables:")
    for table in found_tables:
        print(f"    ✅ {table}")

    missing = set(expected_tables) - set(found_tables)
    if missing:
        print(f"\n  ❌ Missing tables: {', '.join(missing)}")
        return False

    return True


def main():
    """Run all migrations"""
    print("=" * 60)
    print("DATABASE MIGRATION: AI Background Channel Studio")
    print("=" * 60)

    # Connect to database
    conn = get_database_connection()

    try:
        # Create ENUM types
        create_enums(conn)

        # Create tables in order (respecting foreign keys)
        create_channels_table(conn)
        create_video_jobs_table(conn)
        create_audio_tracks_table(conn)
        create_images_table(conn)
        create_render_tasks_table(conn)

        # Verify
        if verify_tables(conn):
            print("\n" + "=" * 60)
            print("✅ MIGRATION COMPLETE!")
            print("=" * 60)
            print("\n📊 Database is ready for use")
            print("🚀 Next step: Create API models and routes\n")
        else:
            print("\n❌ Migration completed with warnings")

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)

    finally:
        conn.close()
        print("🔒 Database connection closed\n")


if __name__ == "__main__":
    main()
