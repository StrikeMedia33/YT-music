"""
Database Migration: Add 'cancelled' status to video_job_status enum

This migration adds the 'cancelled' value to the video_job_status enum type
in the PostgreSQL database.
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Add 'cancelled' status to video_job_status enum"""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")

    # Connect to database
    conn = psycopg2.connect(database_url)
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        # Check if 'cancelled' already exists in the enum
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM pg_enum
                WHERE enumlabel = 'cancelled'
                AND enumtypid = (
                    SELECT oid FROM pg_type WHERE typname = 'video_job_status'
                )
            );
        """)

        exists = cursor.fetchone()[0]

        if exists:
            print("✓ 'cancelled' status already exists in video_job_status enum")
        else:
            # Add 'cancelled' to the enum
            cursor.execute("""
                ALTER TYPE video_job_status ADD VALUE 'cancelled';
            """)
            print("✓ Added 'cancelled' status to video_job_status enum")

        print("\n✓ Migration completed successfully!")

    except Exception as e:
        print(f"✗ Migration failed: {e}")
        raise

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    run_migration()
