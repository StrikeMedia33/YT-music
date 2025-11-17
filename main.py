"""FastAPI Application Entry Point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.channels import router as channels_router
from api.video_jobs import router as video_jobs_router
from api.genres import router as genres_router
from api.ideas import router as ideas_router

app = FastAPI(
    title="AI Background Channel Studio API",
    description="API for automated YouTube background video generation",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(channels_router, prefix="/api/channels", tags=["channels"])
app.include_router(video_jobs_router, prefix="/api/video-jobs", tags=["video-jobs"])
app.include_router(genres_router, prefix="/api/genres", tags=["genres"])
app.include_router(ideas_router, prefix="/api/ideas", tags=["ideas"])

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
