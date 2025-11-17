# Database Schema Design

This document defines the complete database schema for the AI Background Channel Studio.

## Database: PostgreSQL (Neon)

### Connection String Format
```
postgresql://user:password@host:5432/yt_music
```

---

## Table Definitions

### 1. `channels` Table

Stores YouTube channel information and configuration.

```sql
CREATE TABLE channels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    youtube_channel_id VARCHAR(100) UNIQUE,
    brand_niche VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Indexes
CREATE INDEX idx_channels_is_active ON channels(is_active);
CREATE INDEX idx_channels_created_at ON channels(created_at DESC);
```

**Columns:**
- `id`: Unique channel identifier (UUID)
- `name`: Display name for the channel
- `youtube_channel_id`: YouTube channel ID (nullable for development/testing)
- `brand_niche`: Target niche/genre (e.g., "Medieval Fantasy Ambience", "Lo-Fi Study Beats")
- `is_active`: Whether channel is currently active
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

---

### 2. `video_jobs` Table

Stores video generation jobs and tracks their progress through the pipeline.

```sql
CREATE TYPE video_job_status AS ENUM (
    'planned',
    'generating_music',
    'generating_image',
    'rendering',
    'ready_for_export',
    'completed',
    'failed'
);

CREATE TABLE video_jobs (
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
CREATE INDEX idx_video_jobs_channel_id ON video_jobs(channel_id);
CREATE INDEX idx_video_jobs_status ON video_jobs(status);
CREATE INDEX idx_video_jobs_created_at ON video_jobs(created_at DESC);

-- GIN index for JSONB queries
CREATE INDEX idx_video_jobs_prompts ON video_jobs USING GIN (prompts_json);
```

**Columns:**
- `id`: Unique job identifier (UUID)
- `channel_id`: Foreign key to channels table
- `status`: Current pipeline status (enum)
- `niche_label`: Video niche/theme (e.g., "Royal Court Ambience")
- `mood_keywords`: Comma-separated mood descriptors (e.g., "elegant, classical, serene")
- `target_duration_minutes`: Target video length (60-90 minutes)
- `prompts_json`: Generated prompts for music and visuals (JSONB structure below)
- `local_video_path`: Path to final rendered video
- `output_directory`: Directory for all job assets
- `error_message`: Error details if status is 'failed'
- `created_at`: Job creation timestamp
- `updated_at`: Last update timestamp

**prompts_json Structure:**
```json
{
  "music_prompts": [
    {
      "order_index": 1,
      "prompt": "Elegant waltz with strings, piano, light percussion. Tempo: 120 BPM. Duration: 3-4 minutes.",
      "duration_minutes": 3.5
    },
    // ... 19 more unique prompts
  ],
  "visual_prompts": [
    {
      "order_index": 1,
      "prompt": "16:9 background of a grand ballroom with chandeliers, golden accents, warm lighting"
    },
    // ... 19 more unique prompts
  ]
}
```

---

### 3. `audio_tracks` Table

Stores information about individual generated audio tracks (20 per video).

```sql
CREATE TYPE music_provider AS ENUM (
    'dummy',
    'mubert',
    'beatoven'
);

CREATE TABLE audio_tracks (
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

    -- Ensure unique order per job
    UNIQUE (video_job_id, order_index)
);

-- Indexes
CREATE INDEX idx_audio_tracks_video_job_id ON audio_tracks(video_job_id);
CREATE INDEX idx_audio_tracks_order ON audio_tracks(video_job_id, order_index);
```

**Columns:**
- `id`: Unique track identifier (UUID)
- `video_job_id`: Foreign key to video_jobs table
- `provider`: Music generation provider (enum)
- `provider_track_id`: External API track ID (if applicable)
- `order_index`: Track position in video (1-20)
- `duration_seconds`: Exact track duration
- `local_file_path`: Path to audio file
- `license_document_url`: URL to licensing documentation
- `prompt_text`: LLM prompt used to generate this track
- `created_at`: Creation timestamp

---

### 4. `images` Table

Stores information about generated background visuals (20 per video).

```sql
CREATE TYPE visual_provider AS ENUM (
    'dummy',
    'leonardo',
    'gemini'
);

CREATE TABLE images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_job_id UUID REFERENCES video_jobs(id) ON DELETE CASCADE,
    provider visual_provider NOT NULL,
    provider_image_id VARCHAR(255),
    order_index INTEGER CHECK (order_index BETWEEN 1 AND 20),
    local_file_path TEXT NOT NULL,
    prompt_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,

    -- Ensure unique order per job (if linked to a job)
    UNIQUE (video_job_id, order_index)
);

-- Indexes
CREATE INDEX idx_images_video_job_id ON images(video_job_id);
CREATE INDEX idx_images_order ON images(video_job_id, order_index);
```

**Columns:**
- `id`: Unique image identifier (UUID)
- `video_job_id`: Foreign key to video_jobs table (nullable for standalone images)
- `provider`: Visual generation provider (enum)
- `provider_image_id`: External API image ID (if applicable)
- `order_index`: Visual position in video (1-20, matches corresponding audio track)
- `local_file_path`: Path to image file
- `prompt_text`: LLM prompt used to generate this visual
- `created_at`: Creation timestamp

---

### 5. `render_tasks` Table

Stores FFmpeg rendering task information and results.

```sql
CREATE TYPE render_status AS ENUM (
    'pending',
    'in_progress',
    'completed',
    'failed'
);

CREATE TABLE render_tasks (
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
CREATE INDEX idx_render_tasks_video_job_id ON render_tasks(video_job_id);
CREATE INDEX idx_render_tasks_status ON render_tasks(status);
CREATE INDEX idx_render_tasks_created_at ON render_tasks(created_at DESC);
```

**Columns:**
- `id`: Unique render task identifier (UUID)
- `video_job_id`: Foreign key to video_jobs table
- `ffmpeg_command`: Complete FFmpeg command executed
- `local_video_path`: Path to rendered video file
- `resolution`: Video resolution (default: 1920x1080)
- `duration_seconds`: Final video duration
- `status`: Rendering status (enum)
- `error_message`: Error details if status is 'failed'
- `created_at`: Task creation timestamp
- `completed_at`: Task completion timestamp

---

## Relationships

```
channels (1) ─────< (many) video_jobs
                        │
                        ├─────< (many) audio_tracks
                        ├─────< (many) images
                        └─────< (many) render_tasks
```

### Cascade Behavior

- **ON DELETE CASCADE**: When a channel is deleted, all associated video_jobs and their related records are deleted
- **ON DELETE CASCADE**: When a video_job is deleted, all associated audio_tracks, images, and render_tasks are deleted

---

## Constraints & Business Rules

### Video Jobs
- Target duration must be 60-90 minutes (YouTube "curated album" strategy)
- Exactly 20 audio tracks per video (order_index 1-20)
- Exactly 20 visuals per video (order_index 1-20)
- Visual-audio pairing: `images.order_index` matches `audio_tracks.order_index`

### Pipeline Status Flow
```
planned → generating_music → generating_image → rendering → ready_for_export → completed
                                                                ↓
                                                              failed
```

---

## Sample Queries

### Get all active channels with job counts
```sql
SELECT
    c.id,
    c.name,
    c.brand_niche,
    COUNT(vj.id) as total_jobs,
    COUNT(CASE WHEN vj.status = 'completed' THEN 1 END) as completed_jobs
FROM channels c
LEFT JOIN video_jobs vj ON c.id = vj.channel_id
WHERE c.is_active = TRUE
GROUP BY c.id, c.name, c.brand_niche
ORDER BY c.created_at DESC;
```

### Get video job with all related assets
```sql
SELECT
    vj.*,
    json_agg(DISTINCT jsonb_build_object(
        'id', at.id,
        'order_index', at.order_index,
        'duration_seconds', at.duration_seconds,
        'local_file_path', at.local_file_path
    ) ORDER BY at.order_index) as audio_tracks,
    json_agg(DISTINCT jsonb_build_object(
        'id', i.id,
        'order_index', i.order_index,
        'local_file_path', i.local_file_path
    ) ORDER BY i.order_index) as images
FROM video_jobs vj
LEFT JOIN audio_tracks at ON vj.id = at.video_job_id
LEFT JOIN images i ON vj.id = i.video_job_id
WHERE vj.id = '<job_id>'
GROUP BY vj.id;
```

### Get jobs ready for next pipeline step
```sql
SELECT * FROM video_jobs
WHERE status = 'planned'
ORDER BY created_at ASC
LIMIT 1;
```

---

## Indexes Strategy

**Primary Indexes:**
- All primary keys (UUID) are automatically indexed
- Foreign keys have explicit indexes for join performance

**Query Optimization:**
- Status fields indexed for filtering by pipeline stage
- Timestamps indexed DESC for recent-first queries
- JSONB field (prompts_json) has GIN index for JSON queries
- Composite indexes on (video_job_id, order_index) for ordered asset retrieval

**Performance Considerations:**
- UUIDs chosen over SERIAL for distributed system compatibility
- JSONB for flexible prompt storage (avoids separate tables)
- Cascade deletes prevent orphaned records
- Check constraints enforce business rules at database level

---

## Future Enhancements

### YouTube Integration (Future)
When implementing YouTube upload functionality, add to `video_jobs` table:
```sql
ALTER TABLE video_jobs
ADD COLUMN upload_strategy VARCHAR(50),
ADD COLUMN scheduled_time TIMESTAMP WITH TIME ZONE,
ADD COLUMN youtube_video_id VARCHAR(100);
```

Add to `channels` table:
```sql
ALTER TABLE channels
ADD COLUMN youtube_refresh_token TEXT;
```

### Analytics (Future)
Create separate `video_analytics` table:
```sql
CREATE TABLE video_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_job_id UUID NOT NULL REFERENCES video_jobs(id),
    youtube_video_id VARCHAR(100) NOT NULL,
    views INTEGER DEFAULT 0,
    watch_time_hours NUMERIC(10, 2),
    revenue_usd NUMERIC(10, 2),
    snapshot_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```
