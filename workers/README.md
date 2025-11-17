# Background Workers

This directory contains background job processing logic for long-running tasks.

## Workers

- `video_pipeline_worker.py` - Executes video generation pipeline steps
- `job_queue.py` - Job queue management (Redis or DB-backed)
- `scheduler.py` - Periodic task scheduling

## Pipeline Steps

1. **Prompt Generation** - Generate 20 music + 20 visual prompts
2. **Music Generation** - Generate 20 unique 3-4 minute tracks
3. **Visual Generation** - Generate 20 unique 16:9 visuals
4. **Video Rendering** - Concatenate audio with visual-audio pairing
5. **Metadata Generation** - Create YouTube metadata with timestamps

## Error Handling

Workers should:
- Update job status in database
- Log errors with full context
- Support retries for transient failures
- Make operations idempotent
