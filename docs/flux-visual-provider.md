# Flux Visual Provider - Setup Guide

## Overview

The Flux Visual Provider generates high-quality 16:9 images for YouTube background videos using Flux models via Replicate's API.

## Features

- ✅ Native 16:9 aspect ratio (1920x1080)
- ✅ Three quality tiers: Schnell (fast), Dev (balanced), Pro (best)
- ✅ Automatic prompt enhancement for better visuals
- ✅ Commercial usage allowed
- ✅ Cost-effective (~$0.30-0.50 for 20 images)

## Setup

### 1. Get Replicate API Key

1. Sign up at https://replicate.com
2. Go to Account Settings → API Tokens
3. Copy your API token

### 2. Configure Environment Variables

Add to your `.env` file:

```bash
# Visual Provider Configuration
VISUAL_PROVIDER=flux
REPLICATE_API_KEY=r8_your_api_key_here

# Optional: Choose Flux model (default: flux-schnell)
FLUX_MODEL=flux-schnell  # Options: flux-schnell, flux-dev, flux-pro
```

### 3. Model Selection

Choose based on your needs:

| Model | Speed | Quality | Cost per Image | Best For |
|-------|-------|---------|----------------|----------|
| **flux-schnell** | ⚡ Very Fast (4s) | Good | ~$0.002 | Development, tight budget |
| **flux-dev** | 🐢 Slow (20s) | Better | ~$0.015 | Production, balanced |
| **flux-pro** | 🐢 Slow (25s) | Best | ~$0.025 | Premium content |

**Recommendation**: Start with `flux-schnell` for testing, use `flux-dev` for production.

## Usage

The provider is automatically used when generating visuals through the video job pipeline:

```python
from providers.visual_provider import get_visual_provider

# Get configured provider
provider = get_visual_provider()

# Generate a visual
result = provider.generate_visual(
    prompt="Serene forest at sunset with golden light filtering through trees",
    order_index=1,
    output_dir=Path("./output/visuals")
)

# Result contains:
# - file_path: Path to generated PNG
# - width: 1920
# - height: 1080
# - metadata: Provider info, model used, enhanced prompt
```

## Prompt Enhancement

The provider automatically enhances prompts for better quality:

**Original Prompt:**
```
Peaceful ocean waves at sunset
```

**Enhanced Prompt:**
```
Peaceful ocean waves at sunset, high quality, professional,
16:9 aspect ratio, cinematic composition, suitable for YouTube background
```

## Cost Estimation

For a typical 20-image video:

- **flux-schnell**: ~$0.04-0.10 (20 images × $0.002-0.005)
- **flux-dev**: ~$0.30-0.40 (20 images × $0.015-0.020)
- **flux-pro**: ~$0.50-0.60 (20 images × $0.025-0.030)

**Monthly costs** (assuming 10 videos/month):
- flux-schnell: ~$1-2/month
- flux-dev: ~$3-4/month
- flux-pro: ~$5-6/month

## Error Handling

The provider handles common errors:

- **Timeout**: Max wait time of 3 minutes per image
- **API Errors**: Raises RuntimeError with detailed message
- **Invalid Images**: Verifies downloaded files are valid
- **Rate Limits**: Replicate handles queueing automatically

## Testing

Test the provider before full production use:

```bash
# Set environment variables
export VISUAL_PROVIDER=flux
export REPLICATE_API_KEY=your_key
export FLUX_MODEL=flux-schnell  # Fast for testing

# Run test (if available)
pytest tests/providers/test_visual_provider.py -v
```

## Comparison with Other Providers

| Feature | Flux (Replicate) | DALL-E 3 | Gemini |
|---------|------------------|----------|--------|
| 16:9 Native | ✅ Yes | ⚠️ 1792x1024 | ✅ Yes |
| Cost/Image | $0.002-0.025 | $0.040-0.080 | Varies |
| Speed | 4-25s | 10-30s | 5-15s |
| Quality | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| API Access | ✅ Public | ✅ Public | ✅ Public |
| Commercial Use | ✅ Yes | ✅ Yes | ⚠️ Check terms |

## Troubleshooting

### "REPLICATE_API_KEY not set"
- Add `REPLICATE_API_KEY` to your `.env` file
- Restart your application

### "Prediction timed out"
- Switch to faster model: `FLUX_MODEL=flux-schnell`
- Increase timeout (edit `max_wait` in code)
- Check Replicate status page

### "Unknown Flux model"
- Valid options: `flux-schnell`, `flux-dev`, `flux-pro`
- Check for typos in `FLUX_MODEL` environment variable

### Poor image quality
- Try `flux-dev` or `flux-pro` for better quality
- Improve your prompts with more details
- Ensure prompts describe visual scenes, not just concepts

## Advanced Configuration

### Custom Model Versions

Model versions are auto-managed, but you can update them in `providers/visual_provider.py`:

```python
def _get_model_version(self) -> str:
    versions = {
        "flux-schnell": "latest_version_hash",
        # ...
    }
```

### Timeout Adjustment

Modify timeout in `visual_provider.py`:

```python
image_url = self._wait_for_prediction(
    prediction_id,
    max_wait=300  # 5 minutes instead of 3
)
```

## Support

- **Replicate Docs**: https://replicate.com/docs
- **Flux Model Pages**:
  - Schnell: https://replicate.com/black-forest-labs/flux-schnell
  - Dev: https://replicate.com/black-forest-labs/flux-dev
  - Pro: https://replicate.com/black-forest-labs/flux-pro
- **API Status**: https://status.replicate.com

## Next Steps

1. ✅ Set up environment variables
2. ✅ Choose your Flux model
3. ✅ Test with a single image generation
4. ✅ Run a full 20-image video generation
5. ✅ Monitor costs in Replicate dashboard
6. ✅ Optimize prompts based on results
