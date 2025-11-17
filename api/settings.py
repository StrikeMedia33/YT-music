"""
Settings API Routes

Handles provider configuration and connection status checks.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal, Optional
import os

router = APIRouter()


class ProviderStatus(BaseModel):
    """Provider connection status"""
    provider: str
    connected: bool
    name: str
    description: str


class ProviderSettings(BaseModel):
    """Provider settings configuration"""
    music_provider: Optional[Literal["mubert", "beatoven", "suno"]] = None
    visual_provider: Optional[Literal["leonardo", "gemini", "replicate"]] = None


class SettingsResponse(BaseModel):
    """Complete settings response"""
    music_providers: list[ProviderStatus]
    visual_providers: list[ProviderStatus]
    selected_music_provider: Optional[str]
    selected_visual_provider: Optional[str]


# Provider definitions
MUSIC_PROVIDERS = {
    "mubert": {
        "name": "Mubert",
        "description": "AI music generation with royalty-free licensing",
        "env_key": "MUBERT_API_KEY"
    },
    "beatoven": {
        "name": "Beatoven.ai",
        "description": "Mood-based AI music generation",
        "env_key": "BEATOVEN_API_KEY"
    },
    "suno": {
        "name": "Suno",
        "description": "Text-to-music AI generation",
        "env_key": "SUNO_API_KEY"
    }
}

VISUAL_PROVIDERS = {
    "leonardo": {
        "name": "Leonardo.ai",
        "description": "AI image and video generation platform",
        "env_key": "LEONARDO_API_KEY"
    },
    "gemini": {
        "name": "Google Gemini",
        "description": "Google's multimodal AI for image generation",
        "env_key": "GEMINI_API_KEY"
    },
    "replicate": {
        "name": "Replicate",
        "description": "Run AI models via API (supports various image models)",
        "env_key": "REPLICATE_API_KEY"
    }
}


def check_provider_connection(env_key: str) -> bool:
    """Check if provider has API key configured"""
    api_key = os.getenv(env_key)
    return api_key is not None and api_key.strip() != ""


def get_selected_provider(provider_type: Literal["music", "visual"]) -> Optional[str]:
    """Get currently selected provider from environment"""
    if provider_type == "music":
        return os.getenv("MUSIC_PROVIDER")
    else:
        return os.getenv("VISUAL_PROVIDER")


@router.get("/status", response_model=SettingsResponse)
async def get_settings_status():
    """
    Get provider connection status and current selections.

    Returns:
        SettingsResponse with all provider statuses and current selections
    """
    # Check music providers
    music_providers = []
    for provider_id, provider_info in MUSIC_PROVIDERS.items():
        music_providers.append(ProviderStatus(
            provider=provider_id,
            connected=check_provider_connection(provider_info["env_key"]),
            name=provider_info["name"],
            description=provider_info["description"]
        ))

    # Check visual providers
    visual_providers = []
    for provider_id, provider_info in VISUAL_PROVIDERS.items():
        visual_providers.append(ProviderStatus(
            provider=provider_id,
            connected=check_provider_connection(provider_info["env_key"]),
            name=provider_info["name"],
            description=provider_info["description"]
        ))

    return SettingsResponse(
        music_providers=music_providers,
        visual_providers=visual_providers,
        selected_music_provider=get_selected_provider("music"),
        selected_visual_provider=get_selected_provider("visual")
    )


@router.post("/providers", response_model=dict)
async def update_provider_settings(settings: ProviderSettings):
    """
    Update selected providers.

    Note: This updates environment variables for the current session only.
    For persistent configuration, update the .env file.

    Args:
        settings: Provider settings with music and visual provider selections

    Returns:
        Success message with updated selections
    """
    updated = {}

    if settings.music_provider:
        # Verify provider exists and is connected
        if settings.music_provider not in MUSIC_PROVIDERS:
            raise HTTPException(status_code=400, detail=f"Invalid music provider: {settings.music_provider}")

        provider_info = MUSIC_PROVIDERS[settings.music_provider]
        if not check_provider_connection(provider_info["env_key"]):
            raise HTTPException(
                status_code=400,
                detail=f"{provider_info['name']} is not connected. Please add {provider_info['env_key']} to your .env file"
            )

        os.environ["MUSIC_PROVIDER"] = settings.music_provider
        updated["music_provider"] = settings.music_provider

    if settings.visual_provider:
        # Verify provider exists and is connected
        if settings.visual_provider not in VISUAL_PROVIDERS:
            raise HTTPException(status_code=400, detail=f"Invalid visual provider: {settings.visual_provider}")

        provider_info = VISUAL_PROVIDERS[settings.visual_provider]
        if not check_provider_connection(provider_info["env_key"]):
            raise HTTPException(
                status_code=400,
                detail=f"{provider_info['name']} is not connected. Please add {provider_info['env_key']} to your .env file"
            )

        os.environ["VISUAL_PROVIDER"] = settings.visual_provider
        updated["visual_provider"] = settings.visual_provider

    return {
        "success": True,
        "message": "Provider settings updated successfully",
        "updated": updated
    }
