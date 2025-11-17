# Providers

This directory contains provider abstractions for external services used in the AI Background Channel Studio.

## Overview

The provider pattern allows swapping implementations of external services without changing core business logic. Each provider has:
- An abstract base class defining the interface
- A dummy implementation for development/testing
- Configuration via environment variables
- Future integration points for real APIs

## Music Provider

**Purpose**: Generate audio tracks for videos

**Base Class**: `MusicProvider`

**Interface**:
```python
def generate_track(
    prompt: str,           # Text description (style, mood, instruments, tempo)
    duration_minutes: float,  # Target duration (3-4 minutes typical)
    order_index: int,      # Track position (1-20)
    output_dir: Path       # Where to save the file
) -> Dict[str, Any]        # Returns metadata + file path
```

**Implementations**:
- **DummyMusicProvider** (available now): Generates silent WAV files
  - CD quality: 44.1kHz, 16-bit, stereo
  - Useful for testing pipeline without API costs
  - Fast generation for development

- **MubertProvider** (planned): Mubert AI music generation
  - Royalty-free AI-generated music
  - Commercial usage suitable for YouTube
  - Requires API key

- **BeatovenProvider** (planned): Beatoven.ai integration
  - Royalty-free AI-generated music
  - Commercial usage suitable for YouTube
  - Requires API key

**Configuration**:
```bash
# In .env file
MUSIC_PROVIDER=dummy     # Options: dummy, mubert, beatoven
MUSIC_API_KEY=your-key   # Required for mubert/beatoven
```

**Usage**:
```python
from providers import get_music_provider

# Get configured provider
provider = get_music_provider()

# Generate a track
result = provider.generate_track(
    prompt="Energetic electronic dance music with synthesizers",
    duration_minutes=3.5,
    order_index=1,
    output_dir=Path("./output/audio")
)

# Result contains:
# - file_path: Absolute path to generated WAV file
# - duration_seconds: Actual duration
# - order_index: Track position
# - prompt_text: The prompt used
# - metadata: Provider-specific details
```

**Testing**:
Run tests with:
```bash
pytest tests/providers/test_music_provider.py -v
```

## Visual Provider

**Purpose**: Generate background visuals for videos (coming in Phase 4.2)

**Base Class**: `VisualProvider` (planned)

**Interface** (planned):
```python
def generate_visual(
    prompt: str,      # Text description for 16:9 artwork
    order_index: int, # Visual position (1-20)
    output_dir: Path  # Where to save the file
) -> Dict[str, Any]   # Returns metadata + file path
```

**Implementations** (planned):
- **DummyVisualProvider**: Colored PNG with text (1920x1080, 16:9)
- **LeonardoProvider**: Leonardo.ai video loops or dynamic images
- **GeminiProvider**: Google Gemini for video/image generation

**Configuration** (planned):
```bash
VISUAL_PROVIDER=dummy      # Options: dummy, leonardo, gemini
VISUAL_API_KEY=your-key    # Required for leonardo/gemini
```

## FFmpeg Renderer

**Purpose**: Render final videos with visual-audio pairing (coming in Phase 4.3)

**Class**: `FFmpegRenderer` (planned)

**Key Features** (planned):
- Concatenate 20 audio tracks with crossfades
- Switch visuals at track boundaries (Visual 1 → Track 1, Visual 2 → Track 2, etc.)
- Export 1080p MP4 (H.264 + AAC)
- Progress tracking for 60-80 minute renders

## Architecture Benefits

**Why Provider Abstraction?**

1. **Development Speed**: Test pipeline with dummy providers (no API keys, instant generation)
2. **Flexibility**: Swap APIs without changing business logic
3. **Cost Control**: Avoid expensive API calls during development
4. **Testing**: Unit test with dummy providers, integration test with real APIs
5. **Future-Proof**: Easy to add new providers (Suno, Stable Audio, etc.)

**Pattern**:
```
Application Code
       ↓
get_provider() factory
       ↓
Provider Interface (abstract class)
       ↓
   ┌────┴────┬─────────┬──────────┐
   ↓         ↓         ↓          ↓
Dummy   Mubert    Beatoven    Future
```

## Adding a New Provider

To add a new music provider:

1. Create a new class inheriting from `MusicProvider`
2. Implement the `generate_track()` method
3. Add provider name to `get_music_provider()` factory
4. Add configuration to `.env.template`
5. Write unit tests in `tests/providers/`
6. Document in this README

Example:
```python
class MubertMusicProvider(MusicProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = MubertClient(api_key)

    def generate_track(self, prompt, duration_minutes, order_index, output_dir):
        # Call Mubert API
        response = self.client.generate(
            prompt=prompt,
            duration=int(duration_minutes * 60)
        )

        # Download and save audio
        file_path = output_dir / f"track_{order_index:02d}_mubert.mp3"
        self.client.download(response.url, file_path)

        # Return metadata
        return {
            "file_path": str(file_path),
            "duration_seconds": duration_minutes * 60,
            "order_index": order_index,
            "prompt_text": prompt,
            "metadata": {
                "provider": "mubert",
                "track_id": response.id,
                "format": "mp3",
            }
        }
```

## Environment Variables

All providers are configured via environment variables:

```bash
# Music Provider
MUSIC_PROVIDER=dummy          # Which provider to use
MUSIC_API_KEY=                # API key (for non-dummy providers)

# Visual Provider (future)
VISUAL_PROVIDER=dummy         # Which provider to use
VISUAL_API_KEY=               # API key (for non-dummy providers)

# Output
OUTPUT_DIRECTORY=./output     # Where to save generated files
```

## File Structure

```
providers/
├── __init__.py              # Exports for easy importing
├── music_provider.py        # Music provider abstraction + implementations
├── visual_provider.py       # (Phase 4.2) Visual provider abstraction
├── ffmpeg_renderer.py       # (Phase 4.3) Video rendering
└── README.md               # This file

tests/providers/
├── __init__.py
├── test_music_provider.py  # Music provider tests (18 tests)
├── test_visual_provider.py # (Phase 4.2)
└── test_ffmpeg_renderer.py # (Phase 4.3)
```

## Related Documentation

- `/docs/PRD.md` - Product requirements with provider strategy
- `/CLAUDE.md` - Project instructions including provider pattern
- `/docs/database-schema.md` - Database tables for tracking generated assets
- `/.env.template` - Environment variable reference

## Next Steps

- **Phase 4.2**: Implement Visual Provider abstraction
- **Phase 4.3**: Implement FFmpeg Renderer
- **Future**: Add real API integrations (Mubert, Beatoven, Leonardo, Gemini)
