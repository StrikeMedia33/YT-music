# Generated Assets Output Directory

This directory stores all generated assets during video production.

## Structure

```
output/
├── video_job_{id}/
│   ├── audio/
│   │   ├── track_01.wav (3-4 minutes)
│   │   ├── track_02.wav
│   │   └── ... (20 total tracks)
│   ├── visuals/
│   │   ├── visual_01.png (1920x1080)
│   │   ├── visual_02.png
│   │   └── ... (20 total visuals)
│   ├── final_video.mp4 (60-80 minutes, 1080p)
│   ├── metadata.txt (title, description with timestamps, tags)
│   └── prompts.json (generated prompts for all assets)
```

## File Naming Convention

- **Audio**: `track_{order_index:02d}.wav` (e.g., `track_01.wav`, `track_02.wav`)
- **Visuals**: `visual_{order_index:02d}.png` (e.g., `visual_01.png`, `visual_02.png`)
- **Video**: `final_video.mp4`
- **Metadata**: `metadata.txt`
- **Prompts**: `prompts.json`

## Storage Strategy

- **Development**: Local file system (this directory)
- **Production**: Consider cloud storage (S3/R2) for larger scale
- **Retention**: Keep generated assets until video is successfully uploaded

## .gitignore

This directory should be excluded from git due to large file sizes:
```
output/*
!output/README.md
```

## Compliance Notes

All generated content must follow YouTube's "Curated Album" strategy:
- 20 unique songs (NO looping)
- 20 unique visuals (one per track)
- Visual-audio pairing (Visual 1 with Track 1, etc.)
- Timestamps in metadata for all 20 tracks
