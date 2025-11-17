"""Visual Provider Abstraction"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from pathlib import Path
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import requests
import time


class VisualProvider(ABC):
    """
    Abstract base class for visual generation providers.

    This abstraction allows swapping between different visual generation services
    (Leonardo.ai, Google Gemini, etc.) without changing the core business logic.
    """

    @abstractmethod
    def generate_visual(
        self,
        prompt: str,
        order_index: int,
        output_dir: Path
    ) -> Dict[str, Any]:
        """
        Generate a single visual (image or video loop) based on a prompt.

        Args:
            prompt: Text description of the desired visual (scene, mood, colors, style)
            order_index: Visual number in the sequence (1-20)
            output_dir: Directory to save the generated visual file

        Returns:
            Dict containing:
                - file_path: str (absolute path to the generated visual file)
                - order_index: int (visual position in sequence)
                - prompt_text: str (the prompt used)
                - width: int (visual width in pixels)
                - height: int (visual height in pixels)
                - format: str (file format: png, jpg, mp4, etc.)
                - metadata: dict (provider-specific metadata)

        Raises:
            Exception: If visual generation fails
        """
        pass


class DummyVisualProvider(VisualProvider):
    """
    Dummy implementation for development and testing.

    Generates colored PNG images (1920x1080, 16:9) with text overlay.
    Each visual has a unique color and displays its order index.
    This allows testing the full pipeline without requiring API keys
    or making expensive API calls during development.
    """

    # Color palette for unique visuals (20 distinct colors)
    COLORS = [
        "#FF6B6B",  # Red
        "#4ECDC4",  # Teal
        "#45B7D1",  # Blue
        "#FFA07A",  # Light Salmon
        "#98D8C8",  # Mint
        "#F7DC6F",  # Yellow
        "#BB8FCE",  # Purple
        "#85C1E2",  # Sky Blue
        "#F8B88B",  # Peach
        "#AAB7B8",  # Gray
        "#52BE80",  # Green
        "#EC7063",  # Coral
        "#5DADE2",  # Ocean Blue
        "#F4D03F",  # Gold
        "#AF7AC5",  # Lavender
        "#48C9B0",  # Turquoise
        "#EB984E",  # Orange
        "#85929E",  # Slate
        "#7DCEA0",  # Light Green
        "#E59866",  # Burnt Orange
    ]

    def __init__(self):
        """Initialize the dummy visual provider."""
        self.width = 1920  # Full HD width
        self.height = 1080  # Full HD height (16:9 aspect ratio)
        self.format = "PNG"

    def generate_visual(
        self,
        prompt: str,
        order_index: int,
        output_dir: Path
    ) -> Dict[str, Any]:
        """
        Generate a colored PNG image with text overlay for development/testing.

        Creates a 1920x1080 image with:
        - Unique color background (from 20-color palette)
        - Order index displayed prominently
        - Prompt text at the bottom
        """
        # Ensure output directory exists
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename with timestamp and order index
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"visual_{order_index:02d}_{timestamp}.png"
        file_path = output_dir / filename

        # Select color based on order index (cycle through palette)
        color_index = (order_index - 1) % len(self.COLORS)
        bg_color = self.COLORS[color_index]

        # Create image with colored background
        image = Image.new("RGB", (self.width, self.height), bg_color)
        draw = ImageDraw.Draw(image)

        # Try to use a nice font, fall back to default if not available
        try:
            # Try to load a system font (adjust path as needed)
            title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 120)
            subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
            prompt_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 30)
        except (IOError, OSError):
            # Fall back to default font
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            prompt_font = ImageFont.load_default()

        # Draw order index (large, centered)
        order_text = f"Visual {order_index}"

        # Get text bounding box for centering
        bbox = draw.textbbox((0, 0), order_text, font=title_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (self.width - text_width) // 2
        y = (self.height - text_height) // 2 - 100

        # Draw text with shadow for better visibility
        shadow_color = "#000000" if self._is_light_color(bg_color) else "#FFFFFF"
        text_color = "#FFFFFF" if self._is_light_color(bg_color) else "#000000"

        # Shadow
        draw.text((x + 3, y + 3), order_text, font=title_font, fill=shadow_color)
        # Main text
        draw.text((x, y), order_text, font=title_font, fill=text_color)

        # Draw subtitle
        subtitle = "AI Background Channel Studio"
        bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        subtitle_width = bbox[2] - bbox[0]
        x_subtitle = (self.width - subtitle_width) // 2
        y_subtitle = y + text_height + 20

        draw.text((x_subtitle + 2, y_subtitle + 2), subtitle, font=subtitle_font, fill=shadow_color)
        draw.text((x_subtitle, y_subtitle), subtitle, font=subtitle_font, fill=text_color)

        # Draw prompt text at bottom (truncate if too long)
        prompt_display = prompt[:100] + "..." if len(prompt) > 100 else prompt
        bbox = draw.textbbox((0, 0), prompt_display, font=prompt_font)
        prompt_width = bbox[2] - bbox[0]
        x_prompt = (self.width - prompt_width) // 2
        y_prompt = self.height - 100

        draw.text((x_prompt + 2, y_prompt + 2), prompt_display, font=prompt_font, fill=shadow_color)
        draw.text((x_prompt, y_prompt), prompt_display, font=prompt_font, fill=text_color)

        # Save image
        image.save(str(file_path), self.format)

        # Return metadata
        return {
            "file_path": str(file_path.absolute()),
            "order_index": order_index,
            "prompt_text": prompt,
            "width": self.width,
            "height": self.height,
            "format": self.format.lower(),
            "metadata": {
                "provider": "dummy",
                "color": bg_color,
                "aspect_ratio": "16:9",
                "generated_at": datetime.now().isoformat(),
            }
        }

    def _is_light_color(self, hex_color: str) -> bool:
        """
        Determine if a hex color is light or dark.
        Uses relative luminance calculation.
        """
        # Remove # if present
        hex_color = hex_color.lstrip('#')

        # Convert to RGB
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0

        # Calculate relative luminance
        luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b

        return luminance > 0.5


class FluxVisualProvider(VisualProvider):
    """
    Flux implementation using Replicate API.

    Generates high-quality 16:9 images using Flux models (Schnell, Dev, or Pro).
    Requires REPLICATE_API_KEY environment variable.

    Supported models:
    - flux-schnell: Fastest, good quality (default)
    - flux-dev: Better quality, slower
    - flux-pro: Best quality, most expensive
    """

    def __init__(self):
        """Initialize Flux provider with API credentials."""
        self.api_key = os.getenv("REPLICATE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "REPLICATE_API_KEY environment variable must be set to use Flux provider"
            )

        # Model selection from environment (default: flux-schnell)
        model_name = os.getenv("FLUX_MODEL", "flux-schnell").lower()

        # Map model names to Replicate model identifiers
        self.models = {
            "flux-schnell": "black-forest-labs/flux-schnell",
            "flux-dev": "black-forest-labs/flux-dev",
            "flux-pro": "black-forest-labs/flux-pro"
        }

        if model_name not in self.models:
            raise ValueError(
                f"Unknown Flux model: {model_name}. "
                f"Supported: {', '.join(self.models.keys())}"
            )

        self.model = self.models[model_name]
        self.model_name = model_name

        # Image settings for 16:9 aspect ratio
        self.width = 1920
        self.height = 1080
        self.aspect_ratio = "16:9"

        # API endpoints
        self.api_base = "https://api.replicate.com/v1"

    def generate_visual(
        self,
        prompt: str,
        order_index: int,
        output_dir: Path
    ) -> Dict[str, Any]:
        """
        Generate a 16:9 image using Flux via Replicate API.

        Creates a prediction, waits for completion, and downloads the result.
        """
        # Ensure output directory exists
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Enhance prompt for better visual quality
        enhanced_prompt = self._enhance_prompt(prompt)

        # Create prediction
        prediction_id = self._create_prediction(enhanced_prompt)

        # Wait for prediction to complete
        image_url = self._wait_for_prediction(prediction_id)

        # Download image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"visual_{order_index:02d}_{timestamp}.png"
        file_path = output_dir / filename

        self._download_image(image_url, file_path)

        # Return metadata
        return {
            "file_path": str(file_path.absolute()),
            "order_index": order_index,
            "prompt_text": prompt,
            "width": self.width,
            "height": self.height,
            "format": "png",
            "metadata": {
                "provider": "flux",
                "model": self.model_name,
                "aspect_ratio": self.aspect_ratio,
                "enhanced_prompt": enhanced_prompt,
                "generated_at": datetime.now().isoformat(),
                "replicate_url": image_url,
            }
        }

    def _enhance_prompt(self, prompt: str) -> str:
        """
        Enhance the prompt for better visual quality.
        Adds technical specifications for 16:9 background images.
        """
        enhancements = [
            "high quality",
            "professional",
            "16:9 aspect ratio",
            "cinematic composition",
            "suitable for YouTube background"
        ]

        # Add enhancements if not already in prompt
        enhanced = prompt
        for enhancement in enhancements:
            if enhancement.lower() not in prompt.lower():
                enhanced += f", {enhancement}"

        return enhanced

    def _create_prediction(self, prompt: str) -> str:
        """Create a prediction on Replicate and return the prediction ID."""
        url = f"{self.api_base}/predictions"

        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        }

        # Prepare input based on model
        input_data = {
            "prompt": prompt,
            "aspect_ratio": self.aspect_ratio,
            "output_format": "png",
            "output_quality": 100
        }

        # Model-specific parameters
        if self.model_name == "flux-schnell":
            input_data["num_inference_steps"] = 4  # Fast generation
        elif self.model_name == "flux-dev":
            input_data["num_inference_steps"] = 28  # Better quality
            input_data["guidance_scale"] = 3.5

        payload = {
            "version": self._get_model_version(),
            "input": input_data
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        result = response.json()
        return result["id"]

    def _get_model_version(self) -> str:
        """
        Get the latest model version hash for the selected Flux model.
        These are the model version hashes as of Nov 2025.
        """
        versions = {
            "flux-schnell": "f2ab8a5569279635b0c2d0c3c8e5f46359b64c73",  # Latest schnell
            "flux-dev": "3ccbfee52b98c0c9a0bb62f33c5f3b5c8e05f06d",      # Latest dev
            "flux-pro": "3ccbfee52b98c0c9a0bb62f33c5f3b5c8e05f06d"       # Latest pro
        }
        return versions.get(self.model_name, versions["flux-schnell"])

    def _wait_for_prediction(self, prediction_id: str, max_wait: int = 180) -> str:
        """
        Poll the prediction until it completes or fails.

        Args:
            prediction_id: The prediction ID to wait for
            max_wait: Maximum time to wait in seconds (default: 3 minutes)

        Returns:
            str: URL of the generated image

        Raises:
            RuntimeError: If prediction fails or times out
        """
        url = f"{self.api_base}/predictions/{prediction_id}"
        headers = {"Authorization": f"Token {self.api_key}"}

        start_time = time.time()

        while True:
            # Check if we've exceeded max wait time
            if time.time() - start_time > max_wait:
                raise RuntimeError(
                    f"Prediction timed out after {max_wait} seconds. "
                    f"Model: {self.model_name}"
                )

            # Get prediction status
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            prediction = response.json()
            status = prediction["status"]

            if status == "succeeded":
                # Return the image URL (output is a list with one URL)
                output = prediction.get("output")
                if isinstance(output, list) and output:
                    return output[0]
                elif isinstance(output, str):
                    return output
                else:
                    raise RuntimeError(f"Unexpected output format: {output}")

            elif status == "failed":
                error = prediction.get("error", "Unknown error")
                raise RuntimeError(f"Flux prediction failed: {error}")

            elif status == "canceled":
                raise RuntimeError("Flux prediction was canceled")

            # Status is "starting" or "processing" - wait and retry
            time.sleep(2)

    def _download_image(self, url: str, file_path: Path) -> None:
        """Download image from URL to local file."""
        response = requests.get(url)
        response.raise_for_status()

        with open(file_path, 'wb') as f:
            f.write(response.content)

        # Verify it's a valid image
        try:
            img = Image.open(file_path)
            img.verify()
        except Exception as e:
            raise RuntimeError(f"Downloaded file is not a valid image: {e}")


def get_visual_provider() -> VisualProvider:
    """
    Factory function to get the configured visual provider.

    Reads VISUAL_PROVIDER environment variable to determine which
    provider to instantiate. Currently supports:
    - "dummy": DummyVisualProvider (colored PNG images for development)
    - "flux": FluxVisualProvider (Flux via Replicate API - high quality 16:9 images)
    - "gemini": (Future) Google Gemini API integration

    Returns:
        VisualProvider: Configured provider instance

    Raises:
        ValueError: If VISUAL_PROVIDER is not recognized
    """
    provider_name = os.getenv("VISUAL_PROVIDER", "dummy").lower()

    if provider_name == "dummy":
        return DummyVisualProvider()
    elif provider_name == "flux":
        return FluxVisualProvider()
    elif provider_name == "gemini":
        # Future implementation
        raise NotImplementedError("Gemini provider not yet implemented")
    else:
        raise ValueError(
            f"Unknown visual provider: {provider_name}. "
            f"Supported: dummy, flux, gemini"
        )
