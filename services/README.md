# Business Logic Services

This directory contains service classes that orchestrate business logic and coordinate between different components.

## Services

- `prompt_generator.py` - LLM-powered prompt generation for music and visuals (20 unique prompts each)
- `metadata_generator.py` - YouTube metadata generation (title, description with timestamps, tags)
- `video_pipeline.py` - Complete video generation pipeline orchestration
- `job_scheduler.py` - Background job scheduling and management

## Design Pattern

Services should:
- Be stateless and testable
- Coordinate between models, providers, and external APIs
- Handle error conditions gracefully
- Log important operations
