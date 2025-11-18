"""FastAPI Application Entry Point"""
import threading
import time
import logging
import traceback
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.channels import router as channels_router
from api.video_jobs import router as video_jobs_router
from api.audio_tracks import router as audio_tracks_router
from api.images import router as images_router
from api.videos import router as videos_router
from api.genres import router as genres_router
from api.ideas import router as ideas_router
from api.youtube_scraper import router as youtube_scraper_router
from api.settings import router as settings_router
from api.uploads import router as uploads_router

# Configure logging with detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Background scheduler for channel updates
scheduler_thread = None
should_stop = threading.Event()


def run_hourly_channel_refresh():
    """
    Background thread that checks for new videos every hour.
    Runs continuously while the application is running.
    """
    from models import get_db
    from services.channel_update_scheduler import channel_scheduler

    logger.info("Hourly channel refresh thread started")

    while not should_stop.is_set():
        try:
            # Wait for 1 hour (3600 seconds), but check every second if we should stop
            for _ in range(3600):
                if should_stop.is_set():
                    logger.info("Stopping hourly refresh thread")
                    return
                time.sleep(1)

            # Run the refresh
            logger.info("Running scheduled hourly channel refresh...")
            db_gen = get_db()
            db = next(db_gen)
            try:
                result = channel_scheduler.rescrape_all_channels(db, video_limit=50)
                logger.info(f"Hourly refresh completed: {result['channels_updated']} channels updated, "
                           f"{result['new_videos_found']} new videos found")
            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error in hourly refresh: {e}", exc_info=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    global scheduler_thread

    # Startup: Check for new videos on application start
    logger.info("Application starting up - checking for new videos...")
    try:
        from models import get_db
        from services.channel_update_scheduler import channel_scheduler

        db_gen = get_db()
        db = next(db_gen)
        try:
            result = channel_scheduler.rescrape_all_channels(db, video_limit=50)
            logger.info(f"Startup refresh completed: {result['channels_updated']} channels updated, "
                       f"{result['new_videos_found']} new videos found")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error during startup channel refresh: {e}", exc_info=True)

    # Start the hourly refresh thread
    scheduler_thread = threading.Thread(target=run_hourly_channel_refresh, daemon=True)
    scheduler_thread.start()
    logger.info("Hourly channel refresh thread started")

    yield  # Application runs here

    # Shutdown: Stop the background thread
    logger.info("Application shutting down...")
    should_stop.set()
    if scheduler_thread and scheduler_thread.is_alive():
        scheduler_thread.join(timeout=5)
    logger.info("Background threads stopped")


app = FastAPI(
    title="AI Background Channel Studio API",
    description="API for automated YouTube background video generation",
    version="1.0.0",
    lifespan=lifespan
)

# Global exception handler to log all errors with full stack traces
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch all unhandled exceptions and log them with full stack traces
    """
    logger.error(
        f"Unhandled exception on {request.method} {request.url.path}: {exc}",
        exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error": str(exc),
            "path": str(request.url.path)
        }
    )

# CORS - Allow both common dev ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(channels_router, prefix="/api/channels", tags=["channels"])
app.include_router(video_jobs_router, prefix="/api/video-jobs", tags=["video-jobs"])
app.include_router(audio_tracks_router, prefix="/api/audio-tracks", tags=["audio-tracks"])
app.include_router(images_router, prefix="/api/images", tags=["images"])
app.include_router(videos_router)  # Already has prefix in router definition
app.include_router(genres_router, prefix="/api/genres", tags=["genres"])
app.include_router(ideas_router, prefix="/api/ideas", tags=["ideas"])
app.include_router(youtube_scraper_router, prefix="/api/youtube-scraper", tags=["youtube-scraper"])
app.include_router(settings_router, prefix="/api/settings", tags=["settings"])
app.include_router(uploads_router, prefix="/api/uploads", tags=["uploads"])

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
