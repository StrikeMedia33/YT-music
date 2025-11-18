"""
Database Migration: Add alternative assets and arrangement fields

This migration adds support for alternative asset versions and custom arrangement:

AudioTrack changes:
- is_alternative: Boolean flag for alternative track versions
- is_selected: Boolean flag indicating which version is used in video
- display_order: Custom order for final video arrangement (nullable until arranged)

Image changes:
- is_alternative: Boolean flag for alternative image versions
- is_selected: Boolean flag indicating which version is used in video
- display_order: Custom order for final video arrangement (nullable until arranged)
- original_resolution: Store original resolution before upscaling (e.g., "1024x768")
- upscaled: Boolean flag indicating if image was upscaled

Constraint changes:
- Drop unique constraints on (video_job_id, order_index) to allow alternatives
- Both tables can now have multiple rows with same video_job_id + order_index
  (e.g., Track 1 primary + Track 1 alternative 1 + Track 1 alternative 2)
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Add alternative assets and arrangement fields"""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")

    # Connect to database
    conn = psycopg2.connect(database_url)
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        print("Starting migration: Add alternative assets and arrangement fields...")

        # ===== AudioTrack Changes =====
        print("\n[AudioTrack Table]")

        # Check existing columns for audio_tracks
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'audio_tracks'
            AND column_name IN ('is_alternative', 'is_selected', 'display_order');
        """)
        existing_audio_columns = {row[0] for row in cursor.fetchall()}

        audio_columns_to_add = {
            'is_alternative': "BOOLEAN DEFAULT false NOT NULL",
            'is_selected': "BOOLEAN DEFAULT true NOT NULL",
            'display_order': "INTEGER"
        }

        audio_added_count = 0
        for column_name, column_type in audio_columns_to_add.items():
            if column_name in existing_audio_columns:
                print(f"  ✓ Column '{column_name}' already exists")
            else:
                cursor.execute(f"""
                    ALTER TABLE audio_tracks
                    ADD COLUMN {column_name} {column_type};
                """)
                print(f"  ✓ Added column '{column_name}' ({column_type})")
                audio_added_count += 1

        # Drop unique constraint on (video_job_id, order_index) if it exists
        cursor.execute("""
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_name = 'audio_tracks'
            AND constraint_name = 'unique_video_job_order';
        """)

        if cursor.fetchone():
            cursor.execute("""
                ALTER TABLE audio_tracks
                DROP CONSTRAINT IF EXISTS unique_video_job_order;
            """)
            print("  ✓ Dropped unique constraint 'unique_video_job_order' to allow alternatives")
        else:
            print("  ✓ Constraint 'unique_video_job_order' does not exist (already dropped)")

        # ===== Image Changes =====
        print("\n[Image Table]")

        # Check existing columns for images
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'images'
            AND column_name IN ('is_alternative', 'is_selected', 'display_order', 'original_resolution', 'upscaled');
        """)
        existing_image_columns = {row[0] for row in cursor.fetchall()}

        image_columns_to_add = {
            'is_alternative': "BOOLEAN DEFAULT false NOT NULL",
            'is_selected': "BOOLEAN DEFAULT true NOT NULL",
            'display_order': "INTEGER",
            'original_resolution': "VARCHAR(50)",
            'upscaled': "BOOLEAN DEFAULT false NOT NULL"
        }

        image_added_count = 0
        for column_name, column_type in image_columns_to_add.items():
            if column_name in existing_image_columns:
                print(f"  ✓ Column '{column_name}' already exists")
            else:
                cursor.execute(f"""
                    ALTER TABLE images
                    ADD COLUMN {column_name} {column_type};
                """)
                print(f"  ✓ Added column '{column_name}' ({column_type})")
                image_added_count += 1

        # Drop unique constraint on (video_job_id, order_index) if it exists
        cursor.execute("""
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_name = 'images'
            AND constraint_name = 'unique_video_job_image_order';
        """)

        if cursor.fetchone():
            cursor.execute("""
                ALTER TABLE images
                DROP CONSTRAINT IF EXISTS unique_video_job_image_order;
            """)
            print("  ✓ Dropped unique constraint 'unique_video_job_image_order' to allow alternatives")
        else:
            print("  ✓ Constraint 'unique_video_job_image_order' does not exist (already dropped)")

        total_added = audio_added_count + image_added_count
        if total_added == 0:
            print("\n✓ All columns and constraints already updated - no changes needed")
        else:
            print(f"\n✓ Migration completed successfully! Added {total_added} columns and updated constraints")

        print("\nNote: Primary versions (first generation) have is_alternative=false, is_selected=true")
        print("      Alternative versions have is_alternative=true, is_selected=true/false based on user selection")
        print("      display_order remains NULL until user arranges assets in Step 6")

    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        raise

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    run_migration()
