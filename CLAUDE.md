# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an internal "AI Background Channel Studio" that automates the creation of high-quality background music videos for YouTube using the **"Curated Album" strategy**. The system generates 60-80 minute music videos by combining 20 unique AI-generated music tracks with 20 unique AI-generated visuals (one per track), designed to comply with YouTube's July 2025 "Inauthentic Content" policies.

**Key Goals:**
- Strategy: "Curated Album" approach - fewer but higher quality videos
- Audio: 20 unique songs (3-4 minutes each) with NO looping
- Visuals: 20 unique video loops/images synced to each track
- Metadata: Timestamps for all tracks, using "Album"/"Mix"/"Anthology" terminology
- Focus on high-quality, monetizable content that avoids "Repetitious Content" triggers
- Use only APIs with clear commercial-usage terms suitable for YouTube monetization

## Technology Stack

**Backend:**
- Python with FastAPI
- Deployed on Render with background workers for long-running jobs
- FFmpeg for media processing (audio concatenation, video rendering)

**Database:**
- Neon Postgres with the following core tables:
  - `channels`: YouTube channel metadata for tracking purposes
  - `video_jobs`: Video generation jobs with status tracking (statuses: planned, generating_music, generating_image, rendering, ready_for_export, completed, failed)
  - `audio_tracks`: Generated music tracks with local file paths
  - `images`: Generated background images with local file paths
  - `render_tasks`: FFmpeg rendering job records with local output paths

**Frontend:**
- Next.js (App Router) with React and Tailwind CSS
- Pages: Channels list, Video jobs list, Video job detail

**External Services:**
- Music providers: Mubert or Beatoven.ai (royalty-free AI music, 20 unique tracks per video)
- Visual providers: Leonardo.ai (video loops or dynamic images, with pluggable architecture for future Google Gemini/Nano Banana, 20 unique visuals per video)
- Local file storage: Audio files, visual files, and rendered MP4s stored in local output directory
- YouTube Data API: Planned for future implementation; v1 uses manual upload workflow with generated metadata

## Core Architecture Principles

**Provider Abstraction Pattern:**
The system uses clean provider abstractions to allow swapping implementations:

1. **MusicProvider**: Interface for generating music tracks
   - Method: `generate_track(prompt: str, duration_minutes: int)` → track metadata + file path
   - Generates 20 unique tracks of 3-4 minutes each (NO looping)
   - Start with dummy provider (generates silent WAV files) for development
   - Later wire to Mubert or Beatoven API

2. **VisualProvider**: Interface for generating visuals (video loops or dynamic images)
   - Method: `generate_visual(prompt: str)` → visual metadata + file path
   - Generates 20 unique visuals (one per track) for visual-audio pairing
   - Start with dummy provider (colored PNG 1920x1080 with text) for development
   - Later wire to Leonardo.ai or Google Gemini for video loops/dynamic images

3. **YouTubeClient**: Interface for YouTube operations (future implementation)
   - Method: `upload_video(channel, file_url, title, description, tags, privacy_status, scheduled_time)` → youtube_video_id
   - Not implemented in v1; manual upload workflow used instead
   - Will be wired to YouTube Data API with OAuth in future version

4. **FFmpegRenderer**: Video rendering abstraction
   - Concatenates 20 audio tracks with crossfades
   - Creates video that switches visuals per track (Visual 1 with Track 1, Visual 2 with Track 2, etc.)
   - This visual-audio pairing proves "human editing effort" to YouTube
   - Exports 1080p MP4 (H.264 + AAC, ~8 Mbps video, ~192 kbps audio)

**Code Organization:**
Keep the codebase production-friendly with separate modules:
- `api/`: FastAPI routes and endpoints
- `models/`: Database models (SQLAlchemy/Pydantic)
- `services/`: Business logic and orchestration
- `providers/`: Provider implementations (music, image, YouTube)
- `workers/`: Background job processing
- `schemas/`: API request/response schemas

## Video Generation Pipeline

The end-to-end pipeline for generating one video:

1. **Prompt Generation** (`status: planned`)
   - Use LLM (OpenAI-compatible API) to generate:
     - **20 music prompts** describing unique tracks (style, instruments, mood, tempo, target 3-4 minutes each)
     - **20 visual prompts** for 16:9 background artwork (one per track, matched to track's mood/theme)
   - Store in `video_jobs.prompts_json` (JSONB field)

2. **Music Generation** (`status: generating_music`)
   - Call MusicProvider for each of the 20 tracks based on prompts
   - Generate 20 unique tracks of 3-4 minutes each (total: 60-80 minutes)
   - NO tracks are repeated or looped (complies with YouTube "Repetitious Content" policy)
   - Save audio files to local output directory
   - Create `audio_tracks` records with local file paths and order_index

3. **Visual Generation** (`status: generating_image`)
   - Call VisualProvider for each of the 20 visuals based on prompts
   - Generate 20 unique visuals (16:9 format, 1920x1080)
   - Each visual is matched to its corresponding track
   - Save to local output directory
   - Create `images` records with local file paths and order_index for pairing

4. **Video Rendering** (`status: rendering`)
   - Read all 20 audio tracks in order from local file paths
   - Use FFmpeg to concatenate with crossfades
   - **Create video stream that switches visuals per track:**
     - Visual 1 displays during Track 1 (3-4 mins)
     - Visual 2 displays during Track 2 (3-4 mins)
     - Continue for all 20 tracks
   - This visual-audio pairing demonstrates "human editing effort"
   - Export final MP4 (1080p, H.264 + AAC)
   - Save to local output directory
   - Create `render_tasks` record
   - Update `video_jobs.local_video_path` and set status to `ready_for_export`

5. **Metadata Generation** (`status: ready_for_export` → `completed`)
   - Generate title using LLM with "Album", "Mix", or "Anthology" terminology (NOT "Loop")
     - Example: "Royal Court Ambience: A 1-Hour Regency Classical Mix"
   - Generate description with:
     - Brief introduction to the album/mix
     - **Timestamps for all 20 tracks** (e.g., "04:12 - Elegant Waltz in the Ballroom")
     - Timestamps signal to YouTube that content is structured and distinct
   - Generate suggested tags for YouTube
   - Add reminder to enable **"Altered or synthetic content"** checkbox in YouTube Studio
   - Save metadata to text file in output directory
   - Set status to `completed`
   - User manually edits and uploads to YouTube
   - Note: Automated YouTube upload via API planned for future implementation

**Job Orchestration:**
- Background worker periodically scans for jobs in "planned" status
- Executes pipeline steps sequentially
- Updates status and error_message fields appropriately
- Steps should be idempotent (can re-run without breaking data)

## Environment Configuration

All configuration via environment variables (twelve-factor friendly):

- `DATABASE_URL`: Neon Postgres connection string
- `OUTPUT_DIRECTORY`: Local directory path for generated assets (default: ./output)
- `OPENAI_API_KEY`: For LLM prompt generation
- `MUSIC_PROVIDER`: Provider choice (mubert/beatoven)
- `MUSIC_API_KEY`: Music provider API key
- `IMAGE_PROVIDER`: Provider choice (leonardo/gemini)
- `IMAGE_API_KEY`: Image provider API key

**Future environment variables (for YouTube API integration):**
- `YOUTUBE_CLIENT_ID`: OAuth credentials
- `YOUTUBE_CLIENT_SECRET`: OAuth credentials

## Development Workflow

**Backend Development:**
- Use dummy providers initially for music and image generation
- Test pipeline steps independently before integration
- Ensure FFmpeg is available in development environment

**Frontend Development:**
- Backend API assumed at `/api` prefix
- Use loading and error states for all async operations
- Tables for list views, forms for creation/editing

**Database Migrations:**
- Use Python to run all database SQL migrations (per user preferences)

## API Endpoints

**Channels Management:**
- Create, list, view, enable/disable channels
- Store YouTube channel metadata for tracking purposes

**Video Jobs:**
- Create video job (select channel, set niche/mood/duration, specify output directory)
- List jobs with status
- View job detail (prompts, tracks, images, status, logs, output directory path)
- Manually trigger pipeline steps (regenerate music/image, re-render)
- Display generated metadata (title, description, tags) for manual upload

## Authentication

Initial implementation: Simple single-admin setup or no auth (internal tool)
Architecture should make it easy to add auth later

## Task Management (Trello Integration)

The project uses Trello for task management with an intelligent Claude Code agent that processes voice notes and organizes work.

**Board Structure:**
- **Voice Notes** → Mobile dictation inbox (auto-processed at session start)
- **Video Ideas** → Content planning and brainstorming
- **Backlog** → Future videos not yet scheduled
- **Planned** → Videos scoped for upcoming production
- **Next Up** → High-priority videos ready to start
- **Music Generation** → Active music generation (20 tracks)
- **Visual Generation** → Active visual generation (20 visuals)
- **Rendering** → FFmpeg rendering phase
- **Ready for Export** → Videos awaiting manual editing/upload
- **To Review** → Work awaiting manual approval
- **Completed** → Approved videos (user-only)
- **Archive** → Historical completed work

**Trello Project Manager Agent:**
- Automatically checks Voice Notes at session start
- Intelligently parses urgency, categories, and keywords
- Creates structured tasks from natural language
- Maintains audit trail via 🤖 comments
- Never auto-approves (To Review → Completed requires manual approval)

**Setup:** See `trello-manager/README.md` for complete setup instructions (~15 minutes)

**Usage:** Simply ask the agent:
- "Check the Trello board"
- "Process my voice notes"
- "Add this to Next Up: [task description]"
- "What's in Music Generation?"

## Reference Documentation

See `/Users/tim/Library/CloudStorage/Dropbox/PyDev/YT-Music/docs/PRD.md` for complete product requirements and detailed specifications.
