# Project Tasks - AI Background Channel Studio

This document outlines all tasks required to build the AI Background Channel Studio from scratch, organized in implementation order.

## Project Strategy: "Curated Album" Approach

This project uses a quality-over-quantity strategy to avoid YouTube's July 2025 "Inauthentic Content" demonetization policies:
- **20 unique songs** (3-4 minutes each) = 60-80 minute videos with NO looping
- **20 unique visuals** (one per track) synced to each song
- **Timestamps** for all tracks in video description
- **"Album", "Mix", or "Anthology"** terminology (NOT "Loop")
- **Visual-audio pairing** to prove "human editing effort"
- **"Altered or synthetic content"** checkbox compliance in YouTube Studio

## Phase 1: Project Setup & Infrastructure

### 1.1 Project Structure
- [ ] Create backend directory structure
  - [ ] `/api` - FastAPI routes and endpoints
  - [ ] `/models` - Database models (SQLAlchemy)
  - [ ] `/schemas` - Pydantic schemas for API requests/responses
  - [ ] `/services` - Business logic and orchestration
  - [ ] `/providers` - Provider implementations (music, visual)
  - [ ] `/workers` - Background job processing
  - [ ] `/utils` - Utility functions and helpers
- [ ] Create frontend directory structure (Next.js App Router)
  - [ ] `/app` - App Router pages
  - [ ] `/components` - React components
  - [ ] `/lib` - Utility functions and API clients
  - [ ] `/types` - TypeScript type definitions
- [ ] Create output directory for generated assets (`./output`)
- [ ] Set up `.env` file with environment variables
- [ ] Create `.gitignore` for Python and Next.js

### 1.2 Dependencies & Configuration
- [ ] Set up Python virtual environment
- [ ] Install backend dependencies
  - [ ] FastAPI
  - [ ] SQLAlchemy
  - [ ] Psycopg2 (PostgreSQL driver)
  - [ ] Pydantic
  - [ ] python-dotenv
  - [ ] OpenAI SDK (for LLM calls)
  - [ ] Requests (for API calls)
  - [ ] Pillow (for image generation)
  - [ ] Wave/pydub (for audio generation)
- [ ] Install frontend dependencies
  - [ ] Next.js 14+
  - [ ] React
  - [ ] TypeScript
  - [ ] Tailwind CSS
  - [ ] Axios or fetch for API calls
- [ ] Install FFmpeg on development machine
- [ ] Configure environment variables template

## Phase 2: Database Setup

### 2.1 Database Schema Design
- [ ] Design `channels` table
  - [ ] id (primary key)
  - [ ] name
  - [ ] youtube_channel_id
  - [ ] brand_niche
  - [ ] created_at
  - [ ] updated_at
  - [ ] is_active (boolean)

- [ ] Design `video_jobs` table
  - [ ] id (primary key)
  - [ ] channel_id (foreign key)
  - [ ] status (enum: planned, generating_music, generating_image, rendering, ready_for_export, completed, failed)
  - [ ] niche_label
  - [ ] mood_keywords
  - [ ] target_duration_minutes
  - [ ] prompts_json (JSONB)
  - [ ] local_video_path
  - [ ] output_directory
  - [ ] created_at
  - [ ] updated_at
  - [ ] error_message

- [ ] Design `audio_tracks` table
  - [ ] id (primary key)
  - [ ] video_job_id (foreign key)
  - [ ] provider (enum)
  - [ ] provider_track_id
  - [ ] order_index
  - [ ] duration_seconds
  - [ ] local_file_path
  - [ ] license_document_url
  - [ ] prompt_text
  - [ ] created_at

- [ ] Design `images` table
  - [ ] id (primary key)
  - [ ] video_job_id (foreign key, nullable)
  - [ ] provider (enum)
  - [ ] provider_image_id
  - [ ] local_file_path
  - [ ] prompt_text
  - [ ] created_at

- [ ] Design `render_tasks` table
  - [ ] id (primary key)
  - [ ] video_job_id (foreign key)
  - [ ] ffmpeg_command
  - [ ] local_video_path
  - [ ] resolution
  - [ ] duration_seconds
  - [ ] status
  - [ ] created_at
  - [ ] completed_at
  - [ ] error_message

### 2.2 Database Migrations
- [ ] Set up Neon Postgres database
- [ ] Create Python migration script for `channels` table
- [ ] Create Python migration script for `video_jobs` table
- [ ] Create Python migration script for `audio_tracks` table
- [ ] Create Python migration script for `images` table
- [ ] Create Python migration script for `render_tasks` table
- [ ] Run migrations on development database
- [ ] Verify schema creation

## Phase 3: Backend API Development

### 3.1 Database Models
- [ ] Create SQLAlchemy model for `channels`
- [ ] Create SQLAlchemy model for `video_jobs`
- [ ] Create SQLAlchemy model for `audio_tracks`
- [ ] Create SQLAlchemy model for `images`
- [ ] Create SQLAlchemy model for `render_tasks`
- [ ] Set up database connection and session management
- [ ] Create database initialization script

### 3.2 Pydantic Schemas
- [ ] Create request/response schemas for channels
  - [ ] ChannelCreate
  - [ ] ChannelResponse
  - [ ] ChannelUpdate
- [ ] Create request/response schemas for video jobs
  - [ ] VideoJobCreate
  - [ ] VideoJobResponse
  - [ ] VideoJobUpdate
  - [ ] VideoJobDetail (with related tracks, images, render tasks)
- [ ] Create schemas for audio tracks
- [ ] Create schemas for images
- [ ] Create schemas for render tasks

### 3.3 API Routes - Channels
- [ ] `POST /api/channels` - Create new channel
- [ ] `GET /api/channels` - List all channels
- [ ] `GET /api/channels/{id}` - Get channel by ID
- [ ] `PUT /api/channels/{id}` - Update channel
- [ ] `DELETE /api/channels/{id}` - Disable/delete channel

### 3.4 API Routes - Video Jobs
- [ ] `POST /api/video-jobs` - Create new video job
- [ ] `GET /api/video-jobs` - List all video jobs with filtering
- [ ] `GET /api/video-jobs/{id}` - Get video job detail
- [ ] `PUT /api/video-jobs/{id}` - Update video job
- [ ] `POST /api/video-jobs/{id}/regenerate-prompts` - Regenerate prompts
- [ ] `POST /api/video-jobs/{id}/regenerate-music` - Regenerate all 20 music tracks
- [ ] `POST /api/video-jobs/{id}/regenerate-visuals` - Regenerate all 20 visuals
- [ ] `POST /api/video-jobs/{id}/rerender` - Re-render video with visual-audio pairing
- [ ] `GET /api/video-jobs/{id}/metadata` - Get generated metadata file

### 3.5 FastAPI Application Setup
- [ ] Create main FastAPI app instance
- [ ] Configure CORS for frontend
- [ ] Set up error handling middleware
- [ ] Configure logging
- [ ] Create health check endpoint
- [ ] Set up API documentation (Swagger/OpenAPI)

## Phase 4: Provider Abstractions

### 4.1 Music Provider
- [ ] Create `MusicProvider` base class/interface
  - [ ] `generate_track(prompt: str, duration_minutes: int)` method
- [ ] Implement `DummyMusicProvider` for development
  - [ ] Generate silent WAV file of specified duration (3-4 minutes)
  - [ ] Save to local output directory
  - [ ] Return metadata with file path and order_index
- [ ] Create configuration system for provider selection
- [ ] Ensure system generates **20 unique tracks** with NO repetition/looping
- [ ] Add unit tests for dummy provider
- [ ] Design future integration points for Mubert/Beatoven APIs

### 4.2 Visual Provider
- [ ] Create `VisualProvider` base class/interface
  - [ ] `generate_visual(prompt: str)` method
- [ ] Implement `DummyVisualProvider` for development
  - [ ] Generate colored PNG (1920x1080, 16:9) with text overlay
  - [ ] Save to local output directory
  - [ ] Return metadata with file path and order_index
- [ ] Create configuration system for provider selection
- [ ] Ensure system generates **20 unique visuals** (one per track) for visual-audio pairing
- [ ] Add unit tests for dummy provider
- [ ] Design future integration points for Leonardo/Gemini APIs (video loops or dynamic images)

### 4.3 FFmpeg Renderer
- [ ] Create `FFmpegRenderer` class
  - [ ] Method to concatenate 20 audio files with crossfades
  - [ ] Method to create video with visual-audio pairing (Visual 1 with Track 1, Visual 2 with Track 2, etc.)
  - [ ] Method to switch visuals at track boundaries
  - [ ] Method to export final MP4 (1080p, H.264 + AAC)
- [ ] Implement crossfade logic between tracks
- [ ] Implement visual switching logic that proves "human editing effort"
- [ ] Configure video encoding parameters (bitrate ~8 Mbps video, ~192 kbps audio, resolution, codec)
- [ ] Add error handling for FFmpeg failures
- [ ] Add progress tracking for long renders (60-80 minutes total)
- [ ] Add unit tests with sample files

## Phase 5: LLM Integration

### 5.1 Prompt Generation Service
- [ ] Create `PromptGeneratorService` class
- [ ] Implement method to generate music prompts
  - [ ] Input: niche_label, mood_keywords, target_duration
  - [ ] Output: **20 unique track prompts** with style, instruments, mood, tempo, target length (3-4 minutes each)
  - [ ] Ensure each prompt is distinct to avoid repetitious content
- [ ] Implement method to generate visual prompts
  - [ ] Input: niche_label, mood_keywords
  - [ ] Output: **20 unique visual prompts** for 16:9 background artwork (one per track, matched to track's mood/theme)
  - [ ] Each visual should be distinct and complement its corresponding track
- [ ] Configure OpenAI-compatible API client
- [ ] Store prompts in `video_jobs.prompts_json`
- [ ] Add error handling for API failures
- [ ] Add unit tests with mocked LLM responses

### 5.2 Metadata Generation Service
- [ ] Create `MetadataGeneratorService` class
- [ ] Implement method to generate video title
  - [ ] Input: niche_label, mood_keywords, track list
  - [ ] Output: Engaging YouTube title using **"Album", "Mix", or "Anthology"** terminology (NOT "Loop")
  - [ ] Example: "Royal Court Ambience: A 1-Hour Regency Classical Mix"
- [ ] Implement method to generate video description
  - [ ] Input: niche_label, mood_keywords, track list with durations
  - [ ] Output: SEO-optimized description with:
    - [ ] Brief introduction to the album/mix
    - [ ] **Timestamps for all 20 tracks** (e.g., "00:00 - Opening Sunrise", "04:12 - Elegant Waltz in the Ballroom")
    - [ ] Timestamps are critical trust signals to YouTube
- [ ] Implement method to generate video tags
  - [ ] Input: niche_label, mood_keywords
  - [ ] Output: List of relevant tags
- [ ] Add reminder to enable **"Altered or synthetic content"** checkbox in YouTube Studio
- [ ] Save metadata to text file in output directory
- [ ] Add unit tests

## Phase 6: Pipeline Orchestration

### 6.1 Pipeline Service
- [ ] Create `VideoPipelineService` class
- [ ] Implement Step 1: Prompt generation
  - [ ] Call `PromptGeneratorService`
  - [ ] Update `video_jobs.prompts_json`
  - [ ] Update status to `generating_music`
- [ ] Implement Step 2: Music generation
  - [ ] Parse 20 music prompts from JSON
  - [ ] Call `MusicProvider` for each of the 20 tracks (3-4 minutes each)
  - [ ] Ensure NO tracks are repeated or looped
  - [ ] Create 20 `audio_tracks` records with order_index
  - [ ] Update status to `generating_image`
- [ ] Implement Step 3: Visual generation
  - [ ] Parse 20 visual prompts from JSON
  - [ ] Call `VisualProvider` for each of the 20 visuals
  - [ ] Create 20 `images` records with order_index matching corresponding tracks
  - [ ] Update status to `rendering`
- [ ] Implement Step 4: Video rendering
  - [ ] Collect all 20 audio track file paths in order
  - [ ] Collect all 20 visual file paths in order
  - [ ] Call `FFmpegRenderer` to create video with visual-audio pairing
  - [ ] Ensure Visual 1 displays during Track 1, Visual 2 during Track 2, etc.
  - [ ] Create `render_tasks` record
  - [ ] Update `video_jobs.local_video_path`
  - [ ] Update status to `ready_for_export`
- [ ] Implement Step 5: Metadata generation
  - [ ] Call `MetadataGeneratorService` with all 20 track names and durations
  - [ ] Generate title with "Album"/"Mix"/"Anthology" terminology
  - [ ] Generate description with timestamps for all 20 tracks
  - [ ] Generate tags and "Altered Content" reminder
  - [ ] Save metadata to output directory
  - [ ] Update status to `completed`
- [ ] Add error handling for each step
  - [ ] Update `error_message` field on failure
  - [ ] Set status to `failed`
- [ ] Make steps idempotent (can re-run without breaking data)

### 6.2 Background Worker
- [ ] Create background job queue system (Redis + RQ or DB-backed)
- [ ] Implement worker that scans for `planned` jobs
- [ ] Implement worker that executes pipeline steps sequentially
- [ ] Add job scheduling/retry logic
- [ ] Add logging for worker activity
- [ ] Create worker startup script
- [ ] Add unit tests for worker logic

## Phase 7: Frontend Development

### 7.1 API Client Library
- [ ] Create API client utility for backend communication
- [ ] Implement methods for all channel endpoints
- [ ] Implement methods for all video job endpoints
- [ ] Add error handling and loading states
- [ ] Configure base URL and authentication (if needed)

### 7.2 Channels Page
- [ ] Create `/channels` page
- [ ] Implement channels list table
  - [ ] Columns: name, youtube_channel_id, brand_niche, is_active, actions
  - [ ] Sort by created_at (newest first)
- [ ] Add "Create Channel" button and form
  - [ ] Fields: name, youtube_channel_id, brand_niche
- [ ] Add enable/disable channel toggle
- [ ] Add view channel detail button
- [ ] Add loading and error states
- [ ] Style with Tailwind CSS

### 7.3 Video Jobs List Page
- [ ] Create `/video-jobs` page
- [ ] Implement video jobs list table
  - [ ] Columns: id, channel, status, niche_label, target_duration, created_at, actions
  - [ ] Color-code status (planned, in-progress, completed, failed)
  - [ ] Sort by created_at (newest first)
- [ ] Add "Create Video Job" button and form
  - [ ] Fields: channel (dropdown), niche_label, mood_keywords, target_duration, output_directory
- [ ] Add view detail button for each job
- [ ] Add loading and error states
- [ ] Add pagination if needed
- [ ] Style with Tailwind CSS

### 7.4 Video Job Detail Page
- [ ] Create `/video-jobs/{id}` page
- [ ] Display job metadata
  - [ ] Channel, niche, mood, duration, status, created_at
- [ ] Display generated prompts (music and image)
- [ ] Display audio tracks list
  - [ ] Order, prompt, duration, file path
- [ ] Display generated images
  - [ ] Prompt, file path
- [ ] Display render task info
  - [ ] Resolution, duration, FFmpeg command, file path
- [ ] Display generated metadata (title, description, tags)
- [ ] Display output directory path prominently
- [ ] Add manual action buttons
  - [ ] Regenerate prompts
  - [ ] Regenerate music
  - [ ] Regenerate image
  - [ ] Re-render video
- [ ] Show logs/error messages if available
- [ ] Add loading and error states
- [ ] Style with Tailwind CSS

### 7.5 Shared Components
- [ ] Create reusable Table component
- [ ] Create reusable Form components
- [ ] Create reusable Button components
- [ ] Create reusable Status badge component
- [ ] Create reusable Loading spinner component
- [ ] Create reusable Error message component
- [ ] Create navigation menu/header
- [ ] Add responsive design for mobile

## Phase 8: Testing & Quality Assurance

### 8.1 Backend Testing
- [ ] Write unit tests for database models
- [ ] Write unit tests for API routes
- [ ] Write unit tests for provider abstractions
- [ ] Write unit tests for pipeline service
- [ ] Write integration tests for end-to-end pipeline
- [ ] Test error handling and edge cases
- [ ] Test idempotency of pipeline steps

### 8.2 Frontend Testing
- [ ] Test channels page (create, list, view, disable)
- [ ] Test video jobs list page (create, list, filter)
- [ ] Test video job detail page (view, manual actions)
- [ ] Test API client error handling
- [ ] Test loading and error states
- [ ] Test responsive design

### 8.3 End-to-End Testing
- [ ] Create a complete video job from start to finish
- [ ] Verify all pipeline steps execute correctly
- [ ] Verify all assets are saved to output directory
- [ ] Verify metadata file is generated correctly
- [ ] Test manual re-run of individual steps
- [ ] Test failure scenarios and recovery

## Phase 9: Deployment & Documentation

### 9.1 Backend Deployment
- [ ] Create Dockerfile for backend
- [ ] Configure Render deployment
  - [ ] Set up web service for FastAPI
  - [ ] Set up background worker service
  - [ ] Configure environment variables
  - [ ] Connect to Neon Postgres
- [ ] Test deployment on staging environment
- [ ] Set up logging and monitoring

### 9.2 Frontend Deployment
- [ ] Configure Next.js for production build
- [ ] Set up Vercel deployment
  - [ ] Configure environment variables
  - [ ] Set API base URL
- [ ] Test deployment on staging environment

### 9.3 Documentation
- [ ] Document environment variables and setup
- [ ] Document API endpoints (auto-generated via OpenAPI)
- [ ] Document provider abstraction system
- [ ] Document pipeline flow and status transitions
- [ ] Create user guide for creating video jobs
- [ ] Create developer guide for adding new providers
- [ ] Document deployment process

---

## Future Additions

### YouTube Data API Integration
- [ ] Set up YouTube OAuth 2.0 credentials
- [ ] Create `YouTubeClient` abstraction
  - [ ] Method: `upload_video(channel, file_url, title, description, tags, privacy_status, scheduled_time)`
  - [ ] Implement OAuth token refresh logic
- [ ] Add YouTube authentication flow to frontend
- [ ] Update `channels` table to include `youtube_refresh_token`
- [ ] Update `video_jobs` table to include:
  - [ ] `upload_strategy` (immediate or scheduled)
  - [ ] `scheduled_time`
  - [ ] `youtube_video_id`
- [ ] Update pipeline to include automated upload step
  - [ ] New status: `ready_to_upload`
  - [ ] New status: `uploaded`
- [ ] Add YouTube upload button to video job detail page
- [ ] Add scheduling UI for future uploads
- [ ] Test OAuth flow and video uploads
- [ ] Document YouTube API integration

### Real Music Provider Integration (Mubert/Beatoven)
- [ ] Research Mubert API documentation
- [ ] Research Beatoven.ai API documentation
- [ ] Implement `MubertMusicProvider`
  - [ ] API authentication
  - [ ] Track generation API call (20 unique tracks of 3-4 minutes each)
  - [ ] Download and save audio file
  - [ ] Handle rate limits and errors
  - [ ] Ensure NO track repetition or looping
- [ ] Implement `BeatovenMusicProvider` (alternative)
- [ ] Add provider selection configuration
- [ ] Test with real API keys (generate full 20-track album)
- [ ] Document API setup, costs, and track limits per request

### Real Visual Provider Integration (Leonardo/Gemini)
- [ ] Research Leonardo.ai API documentation (video loops and dynamic images)
- [ ] Research Google Gemini API documentation
- [ ] Implement `LeonardoVisualProvider`
  - [ ] API authentication
  - [ ] Visual generation API call (20 unique visuals, video loops or dynamic images)
  - [ ] Download and save visual file
  - [ ] Handle rate limits and errors
  - [ ] Each visual should be 16:9 format (1920x1080)
- [ ] Implement `GeminiVisualProvider` (alternative)
- [ ] Add provider selection configuration
- [ ] Test with real API keys (generate full 20-visual set)
- [ ] Document API setup, costs, and visual limits per request

### Advanced Features
- [ ] Add support for custom crossfade durations between tracks
- [ ] Add support for visual transition effects (fade, dissolve, wipe)
- [ ] Add video preview generation (thumbnail + short clip)
- [ ] Add batch job creation (multiple curated albums at once)
- [ ] Add job queue management UI
- [ ] Add analytics and reporting dashboard (track monetization status, views, revenue)
- [ ] Add webhook notifications for job completion
- [ ] Add cost estimation before job creation (API costs for 20 tracks + 20 visuals)
- [ ] Add automatic YouTube compliance checker (verify timestamps, no loops, etc.)
- [ ] Add support for generating individual track names using LLM
