#!/usr/bin/env python
"""
Worker Startup Script

Starts the video job background worker. This script is designed to be run
as a long-running process on Render or other deployment platforms.

Usage:
    python run_worker.py

Environment Variables:
    DATABASE_URL: Postgres connection string (required)
    OPENAI_API_KEY: OpenAI API key for LLM services (required)
    OUTPUT_DIRECTORY: Base directory for generated files (default: ./output)
    WORKER_POLL_INTERVAL: Seconds between polling cycles (default: 30)
    WORKER_MAX_RETRIES: Maximum retry attempts per job (default: 3)

Example:
    export DATABASE_URL="postgresql://user:pass@localhost:5432/ytmusic"
    export OPENAI_API_KEY="sk-..."
    export OUTPUT_DIRECTORY="/app/output"
    python run_worker.py
"""
import sys
import os

# Ensure workers module can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workers.video_job_worker import main

if __name__ == "__main__":
    main()
