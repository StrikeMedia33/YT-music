You are an expert senior engineer acting as my AI pair programmer. We are going to build an internal “AI Background Channel Studio” that automates the creation of high-quality background music videos for YouTube.

Context and goals

1) This is a side-hustle support tool, not a spam farm. The goal is to create high-quality, long-form background music videos (60–80 minutes) using the "Curated Album" approach that can be uploaded to a small set of YouTube channels. This strategy prioritizes quality over quantity to avoid YouTube's July 2025 "Inauthentic Content" demonetization policies.

2) We will aim for fewer but higher quality videos per channel. The system must make it easy to orchestrate the creation of these curated albums without manually touching every step.

3) **The "Curated Album" Strategy:**
   - **Audio:** 20 unique AI-generated songs (3-4 minutes each) = 60-80 minute video with NO looping
   - **Visuals:** 20 unique video loops or dynamic images (one per track), synced to each song
   - **Metadata:** Includes timestamps for all 20 tracks in description, uses "Album", "Mix", or "Anthology" terminology (NOT "Loop")
   - **Compliance:** "Altered or synthetic content" checkbox enabled in YouTube Studio
   - **Advantage:** Eliminates "Repetitious Content" trigger and proves human curation effort

4) We will only use APIs that are relatively safe for YouTube monetization and have clear commercial-usage terms. For music, we will start with a provider such as Mubert (Render / Generate Track API) or Beatoven.ai, which offer royalty-free AI-generated background music with licenses suitable for YouTube monetization. For visuals, we will start with Leonardo.ai (and keep the visual engine pluggable so we could also use Google Gemini / Nano Banana later).

5) The stack:
   - Backend: Python (FastAPI) running on Render, with background worker(s) for long jobs.
   - Database: Neon Postgres.
   - Frontend: Next.js (App Router) with React and Tailwind CSS.
   - Media processing: FFmpeg inside the backend container for concatenating audio and generating the MP4 video.
   - Storage: Local file storage for audio, images, and rendered MP4s.
   - YouTube: Manual upload workflow for v1 (YouTube Data API integration planned for future).

High-level architecture

I want you to:
1) Propose and then implement a minimal but practical architecture with:
   - A FastAPI backend exposing a REST API under /api for:
     - Managing channels (YouTube channel metadata for tracking purposes).
     - Creating and viewing "video jobs" (planned videos to be generated).
     - Triggering generation steps (music, images, rendering), although background workers should also be able to run these automatically.
   - A simple background job mechanism. Start with a basic internal job queue (for example using Redis + RQ or just a DB-backed job queue) and keep it simple for v1.
   - A Neon Postgres schema that models:
     - channels: id, name, youtube_channel_id, brand_niche, created_at, updated_at, is_active boolean
     - video_jobs: id, channel_id (fk), status (enum: planned, generating_music, generating_image, rendering, ready_for_export, completed, failed), niche_label, mood_keywords, target_duration_minutes, prompts_json (JSONB), local_video_path, output_directory, created_at, updated_at, error_message
     - audio_tracks: id, video_job_id (fk), provider (enum), provider_track_id, order_index, duration_seconds, local_file_path, license_document_url, prompt_text, created_at
     - images: id, video_job_id (fk, nullable), provider (enum), provider_image_id, local_file_path, prompt_text, created_at
     - render_tasks: id, video_job_id (fk), ffmpeg_command, local_video_path, resolution, duration_seconds, status, created_at, completed_at, error_message
   - A Next.js frontend that:
     - Shows a list of channels and lets me create, view, or disable them.
     - Shows a list of video jobs with status and created_at.
     - Provides a simple "Create video job" form that lets me:
       - Select a channel.
       - Enter a niche label and mood keywords.
       - Set target duration (e.g. 70 minutes).
       - Specify an output directory for the generated assets.
     - Shows a detail page for a video job, including:
       - Generated prompts (music and image).
       - Links/paths to any generated tracks and images.
       - Current status and logs.
       - Buttons to manually re-run a step (regenerate music, regenerate image, re-render).
       - Display the final output directory path for manual editing and upload.

2) Implement the end-to-end pipeline for one video job:
   - Step 1: Prompt generation
     - Given a video_jobs row with niche_label, mood_keywords, and target_duration_minutes, call an LLM (you can assume an OpenAI-compatible API; implement a placeholder that reads an OPENAI_API_KEY env var).
     - Generate:
       - A set of **20 music prompts**, each describing one unique track (style, instruments, mood, tempo, target length of 3-4 minutes).
       - A set of **20 visual prompts** for background artwork (16:9 composition, coherent with the niche, one unique visual per track).
       - Each visual should be distinct and matched to its corresponding track's mood/theme.
     - Store these prompts in prompts_json on video_jobs.

   - Step 2: Music generation (integrate with a "music provider" abstraction, but stub out actual API calls at first)
     - Create a MusicProvider interface that can:
       - generate_track(prompt: str, duration_minutes: int) -> track metadata + local file path.
     - Implement a dummy provider first (for development) that just generates a silent WAV file of the right length and stores it locally.
     - Later, this will be wired to Mubert or Beatoven's API, but design the abstraction and configuration now.
     - Generate **20 unique tracks** of 3-4 minutes each (total: 60-80 minutes) based on the prompts.
     - Ensure NO track is repeated or looped to comply with YouTube's "Repetitious Content" policy.
     - Save the generated audio files to the local output directory and create audio_tracks rows with local file paths.

   - Step 3: Visual generation (integrate with a "visual provider" abstraction, again starting with a dummy)
     - Create a VisualProvider interface that can:
       - generate_visual(prompt: str) -> visual metadata + local file path.
     - Implement a dummy provider that creates a simple colored PNG (1920x1080, 16:9) with overlaid text for development.
     - Later, this will be wired to Leonardo or Gemini API to generate video loops or dynamic images.
     - Generate **20 unique visuals** (one per track), save them to the local output directory, and create images rows with local file paths.
     - Each visual should be linked to its corresponding audio track via order_index to enable visual-audio pairing during rendering.

   - Step 4: Video rendering
     - Implement an FFmpeg-based renderer that:
       - Reads all 20 audio_tracks for the job in order from local file paths.
       - Concatenates them with simple crossfades between tracks (use standard FFmpeg filters).
       - **Creates a video stream that switches visuals per track:**
         - Visual 1 plays during Track 1 (3-4 mins)
         - Visual 2 plays during Track 2 (3-4 mins)
         - ... and so on for all 20 tracks
       - This visual-audio pairing proves "human editing effort" and avoids static/low-effort visuals.
       - Exports a final MP4 (1080p, H.264 + AAC) with a reasonable bitrate (e.g. ~8 Mbps video, ~192 kbps audio).
     - Save the MP4 to the local output directory, create a render_tasks row, and update video_jobs with local_video_path and status "ready_for_export".

   - Step 5: Metadata generation for manual upload
     - Generate a title using "Album", "Mix", or "Anthology" terminology (NOT "Loop") from the niche_label and mood_keywords using the LLM.
       - Example: "Royal Court Ambience: A 1-Hour Regency Classical Mix"
     - Generate a description that includes:
       - Brief introduction to the album/mix
       - **Timestamps for all 20 tracks** (e.g., "04:12 - Elegant Waltz in the Ballroom")
       - Timestamps are a trust signal to YouTube that content is structured and distinct
     - Generate suggested tags based on the content.
     - Add reminder to enable **"Altered or synthetic content"** checkbox in YouTube Studio.
     - Save this metadata to a text file in the output directory for easy reference during manual upload.
     - Set status to "completed".
     - Note: YouTube Data API integration for automated uploads is planned for a future version.

3) Job orchestration and state transitions
   - Implement a simple job orchestrator that:
     - Periodically scans for video_jobs in "planned" and starts the pipeline (prompt -> music -> image -> render -> metadata generation) in order.
     - Updates status and error_message fields appropriately.
     - Makes sure steps are idempotent enough that you can re-run parts of the pipeline without breaking data (for example: if audio_tracks already exist and we're re-running, either delete and regenerate, or skip, depending on the requested mode).
     - Final status is "ready_for_export" or "completed" indicating assets are ready for manual editing and YouTube upload.

4) Frontend implementation details
   - Implement the Next.js frontend to talk to the FastAPI backend.
   - Use a clean, minimal UI with Tailwind: simple tables for lists and straightforward forms.
   - Add basic loading and error states so I can clearly see what the system is doing.

5) Configuration and deployment
   - Provide a clear configuration scheme using environment variables for:
     - Neon connection string.
     - Local output directory path for generated assets (default: ./output).
     - OpenAI-compatible API key for the LLM.
     - Music and image provider configuration (API keys, base URLs) even if they are not yet wired.
   - Assume we'll deploy the backend and worker(s) on Render in Docker containers and the frontend on Vercel, but you don't need to write deployment manifests yet. Focus on making the code environment-variable-driven and twelve-factor-friendly.
   - Note: YouTube OAuth credentials will be added when YouTube Data API integration is implemented in a future version.

Important constraints
- Prioritize clean abstractions: MusicProvider, ImageProvider, FFmpegRenderer. They should be small, testable classes or modules so we can swap implementations later.
- Keep YouTubeClient abstraction in mind for future implementation, but it's not needed for v1.
- Keep the code base organized and production-friendly: separate modules for api, models, services, providers, workers.
- This is an internal tool used only by me, so authentication can be a simple single-admin setup or even no auth for the very first iteration, but keep it easy to add auth later.

Now:
1) Design the folder structure for the backend and frontend.
2) Generate the initial FastAPI backend code, including models, schemas, and routes for channels and video_jobs, plus stubs for the providers.
3) Generate the initial Next.js app (App Router) with pages for:
   - Channels list.
   - Video jobs list.
   - Video job detail.
4) Then we will iterate on wiring the pipeline steps one by one.