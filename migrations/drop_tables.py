"""
Drop All Tables Script
WARNING: This will delete ALL data!

Run with: python migrations/drop_tables.py
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
        sys.exit(1)

    try:
        conn = psycopg2.connect(database_url)
        print(f"✅ Connected to database")
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        sys.exit(1)


def drop_all_tables(conn):
    """Drop all tables and ENUMs"""
    print("\n⚠️  WARNING: This will delete ALL tables and data!")
    print("=" * 60)

    # Ask for confirmation
    response = input("Type 'DELETE ALL' to confirm: ")

    if response != "DELETE ALL":
        print("❌ Aborted. No tables were dropped.")
        return False

    cursor = conn.cursor()

    # Drop tables in reverse order (respect foreign keys)
    tables = [
        'render_tasks',
        'images',
        'audio_tracks',
        'video_jobs',
        'channels'
    ]

    print("\n📋 Dropping tables...")
    for table in tables:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
            conn.commit()
            print(f"  ✅ Dropped table: {table}")
        except Exception as e:
            print(f"  ❌ Error dropping {table}: {e}")
            conn.rollback()

    # Drop ENUMs
    enums = [
        'video_job_status',
        'music_provider',
        'visual_provider',
        'render_status'
    ]

    print("\n📋 Dropping ENUM types...")
    for enum in enums:
        try:
            cursor.execute(f"DROP TYPE IF EXISTS {enum} CASCADE;")
            conn.commit()
            print(f"  ✅ Dropped ENUM: {enum}")
        except Exception as e:
            print(f"  ❌ Error dropping {enum}: {e}")
            conn.rollback()

    cursor.close()

    print("\n" + "=" * 60)
    print("✅ ALL TABLES AND ENUMS DROPPED!")
    print("=" * 60)
    print("\n💡 Run 'python migrations/create_tables.py' to recreate schema\n")

    return True


def main():
    """Main function"""
    print("=" * 60)
    print("DROP ALL TABLES - AI Background Channel Studio")
    print("=" * 60)

    conn = get_database_connection()

    try:
        drop_all_tables(conn)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    finally:
        conn.close()
        print("🔒 Database connection closed\n")


if __name__ == "__main__":
    main()
