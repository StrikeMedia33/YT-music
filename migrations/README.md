# Database Migrations

This directory contains Python scripts for managing database schema migrations.

## Prerequisites

1. **Neon Postgres Database**: Create a database at [neon.tech](https://neon.tech)
2. **DATABASE_URL**: Add your connection string to `.env` file

## Usage

### Initial Setup

1. Create your Neon Postgres database
2. Copy the connection string
3. Add to `.env` file:
   ```
   DATABASE_URL=postgresql://user:password@host:5432/yt_music
   ```

### Run Migrations

```bash
# Activate virtual environment
source venv/bin/activate

# Run migration script
python migrations/create_tables.py
```

This will:
- Create 4 ENUM types (video_job_status, music_provider, visual_provider, render_status)
- Create 5 tables (channels, video_jobs, audio_tracks, images, render_tasks)
- Create all indexes
- Verify table creation

### Drop All Tables (Development Only)

**WARNING**: This will delete ALL data!

```bash
python migrations/drop_tables.py
```

## Migration Scripts

- `create_tables.py` - Creates all tables, ENUMs, and indexes
- `drop_tables.py` - Drops all tables and ENUMs (for development reset)

## Table Creation Order

Tables are created in this order to respect foreign key constraints:

1. `channels` (no dependencies)
2. `video_jobs` (depends on channels)
3. `audio_tracks` (depends on video_jobs)
4. `images` (depends on video_jobs)
5. `render_tasks` (depends on video_jobs)

## Schema Documentation

See `docs/database-schema.md` for complete schema documentation including:
- Table definitions
- Column descriptions
- Relationships
- Indexes
- Sample queries
