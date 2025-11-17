"""
Database Migration Script - Ideas Management System
Creates tables for genres, video ideas, prompts, and job-idea links

Run with: python migrations/003_create_ideas_system.py
"""

import os
import sys
import psycopg2
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


def create_genres_table(conn):
    """Create genres table"""
    print("\n📋 Creating 'genres' table...")

    cursor = conn.cursor()

    sql_script = """
    CREATE TABLE IF NOT EXISTS genres (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        name VARCHAR(100) UNIQUE NOT NULL,
        slug VARCHAR(100) UNIQUE NOT NULL,
        description TEXT,
        color VARCHAR(7),
        icon_name VARCHAR(50),
        default_duration_minutes INTEGER DEFAULT 70 NOT NULL,
        is_active BOOLEAN DEFAULT TRUE NOT NULL,
        sort_order INTEGER DEFAULT 0 NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
    );

    -- Indexes
    CREATE INDEX IF NOT EXISTS idx_genres_slug ON genres(slug);
    CREATE INDEX IF NOT EXISTS idx_genres_is_active ON genres(is_active);
    CREATE INDEX IF NOT EXISTS idx_genres_sort_order ON genres(sort_order);
    CREATE INDEX IF NOT EXISTS idx_genres_created_at ON genres(created_at DESC);
    """

    try:
        cursor.execute(sql_script)
        conn.commit()
        print("  ✅ 'genres' table created")
    except Exception as e:
        print(f"  ❌ Error creating 'genres' table: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()


def create_video_ideas_table(conn):
    """Create video_ideas table"""
    print("\n📋 Creating 'video_ideas' table...")

    cursor = conn.cursor()

    sql_script = """
    CREATE TABLE IF NOT EXISTS video_ideas (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        genre_id UUID NOT NULL REFERENCES genres(id) ON DELETE CASCADE,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        niche_label VARCHAR(255) NOT NULL,
        mood_tags JSONB DEFAULT '[]'::jsonb NOT NULL,
        target_duration_minutes INTEGER DEFAULT 70 NOT NULL,
        num_tracks INTEGER DEFAULT 20 NOT NULL,
        is_template BOOLEAN DEFAULT TRUE NOT NULL,
        is_archived BOOLEAN DEFAULT FALSE NOT NULL,
        times_used INTEGER DEFAULT 0 NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
    );

    -- Indexes
    CREATE INDEX IF NOT EXISTS idx_video_ideas_genre_id ON video_ideas(genre_id);
    CREATE INDEX IF NOT EXISTS idx_video_ideas_title ON video_ideas(title);
    CREATE INDEX IF NOT EXISTS idx_video_ideas_is_template ON video_ideas(is_template);
    CREATE INDEX IF NOT EXISTS idx_video_ideas_is_archived ON video_ideas(is_archived);
    CREATE INDEX IF NOT EXISTS idx_video_ideas_created_at ON video_ideas(created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_video_ideas_times_used ON video_ideas(times_used DESC);
    CREATE INDEX IF NOT EXISTS idx_video_ideas_mood_tags ON video_ideas USING GIN (mood_tags);
    """

    try:
        cursor.execute(sql_script)
        conn.commit()
        print("  ✅ 'video_ideas' table created")
    except Exception as e:
        print(f"  ❌ Error creating 'video_ideas' table: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()


def create_idea_prompts_table(conn):
    """Create idea_prompts table"""
    print("\n📋 Creating 'idea_prompts' table...")

    cursor = conn.cursor()

    sql_script = """
    CREATE TABLE IF NOT EXISTS idea_prompts (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        idea_id UUID UNIQUE NOT NULL REFERENCES video_ideas(id) ON DELETE CASCADE,
        music_prompts JSONB DEFAULT '[]'::jsonb NOT NULL,
        visual_prompts JSONB DEFAULT '[]'::jsonb NOT NULL,
        metadata_title VARCHAR(255),
        metadata_description TEXT,
        metadata_tags JSONB DEFAULT '[]'::jsonb NOT NULL,
        generation_params JSONB DEFAULT '{}'::jsonb NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
    );

    -- Indexes
    CREATE INDEX IF NOT EXISTS idx_idea_prompts_idea_id ON idea_prompts(idea_id);
    CREATE INDEX IF NOT EXISTS idx_idea_prompts_created_at ON idea_prompts(created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_idea_prompts_music ON idea_prompts USING GIN (music_prompts);
    CREATE INDEX IF NOT EXISTS idx_idea_prompts_visual ON idea_prompts USING GIN (visual_prompts);
    """

    try:
        cursor.execute(sql_script)
        conn.commit()
        print("  ✅ 'idea_prompts' table created")
    except Exception as e:
        print(f"  ❌ Error creating 'idea_prompts' table: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()


def create_video_job_ideas_table(conn):
    """Create video_job_ideas link table"""
    print("\n📋 Creating 'video_job_ideas' table...")

    cursor = conn.cursor()

    sql_script = """
    CREATE TABLE IF NOT EXISTS video_job_ideas (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        video_job_id UUID NOT NULL REFERENCES video_jobs(id) ON DELETE CASCADE,
        video_idea_id UUID NOT NULL REFERENCES video_ideas(id) ON DELETE CASCADE,
        customizations_json JSONB DEFAULT '{}'::jsonb NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
    );

    -- Indexes
    CREATE INDEX IF NOT EXISTS idx_video_job_ideas_job_id ON video_job_ideas(video_job_id);
    CREATE INDEX IF NOT EXISTS idx_video_job_ideas_idea_id ON video_job_ideas(video_idea_id);
    CREATE INDEX IF NOT EXISTS idx_video_job_ideas_created_at ON video_job_ideas(created_at DESC);
    """

    try:
        cursor.execute(sql_script)
        conn.commit()
        print("  ✅ 'video_job_ideas' table created")
    except Exception as e:
        print(f"  ❌ Error creating 'video_job_ideas' table: {e}")
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

    expected_tables = ['genres', 'video_ideas', 'idea_prompts', 'video_job_ideas']
    found_tables = [t[0] for t in tables if t[0] in expected_tables]

    print(f"\n  Found {len(found_tables)}/{len(expected_tables)} new tables:")
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
    print("DATABASE MIGRATION: Ideas Management System")
    print("=" * 60)

    # Connect to database
    conn = get_database_connection()

    try:
        # Create tables in order (respecting foreign keys)
        create_genres_table(conn)
        create_video_ideas_table(conn)
        create_idea_prompts_table(conn)
        create_video_job_ideas_table(conn)

        # Verify
        if verify_tables(conn):
            print("\n" + "=" * 60)
            print("✅ MIGRATION COMPLETE!")
            print("=" * 60)
            print("\n📊 Ideas Management System tables created")
            print("🚀 Next step: Create Pydantic schemas and API routes\n")
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
