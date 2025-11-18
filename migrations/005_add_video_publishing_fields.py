"""
Database Migration: Add video publishing fields to video_jobs table

This migration adds fields to track YouTube publishing workflow:
- youtube_video_id: YouTube video ID after upload
- youtube_url: Full YouTube URL
- scheduled_publish_date: When to publish
- is_draft: Draft flag
- published_at: Actual publish timestamp
- video_title: Generated title for YouTube
- video_description: Generated description
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Add video publishing fields to video_jobs table"""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")

    # Connect to database
    conn = psycopg2.connect(database_url)
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        print("Starting migration: Add video publishing fields...")

        # Check if columns already exist
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'video_jobs'
            AND column_name IN (
                'youtube_video_id',
                'youtube_url',
                'scheduled_publish_date',
                'is_draft',
                'published_at',
                'video_title',
                'video_description'
            );
        """)

        existing_columns = {row[0] for row in cursor.fetchall()}
        columns_to_add = {
            'youtube_video_id': "VARCHAR(255)",
            'youtube_url': "TEXT",
            'scheduled_publish_date': "TIMESTAMP WITH TIME ZONE",
            'is_draft': "BOOLEAN DEFAULT false NOT NULL",
            'published_at': "TIMESTAMP WITH TIME ZONE",
            'video_title': "TEXT",
            'video_description': "TEXT"
        }

        added_count = 0
        for column_name, column_type in columns_to_add.items():
            if column_name in existing_columns:
                print(f"  ✓ Column '{column_name}' already exists")
            else:
                cursor.execute(f"""
                    ALTER TABLE video_jobs
                    ADD COLUMN {column_name} {column_type};
                """)
                print(f"  ✓ Added column '{column_name}' ({column_type})")
                added_count += 1

        if added_count == 0:
            print("\n✓ All columns already exist - no changes needed")
        else:
            print(f"\n✓ Migration completed successfully! Added {added_count} columns")

    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        raise

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    run_migration()
