"""Music Provider Abstraction"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from pathlib import Path
import os
from datetime import datetime
import wave
import struct


class MusicProvider(ABC):
    """
    Abstract base class for music generation providers.

    This abstraction allows swapping between different music generation services
    (Mubert, Beatoven, etc.) without changing the core business logic.
    """

    @abstractmethod
    def generate_track(
        self,
        prompt: str,
        duration_minutes: float,
        order_index: int,
        output_dir: Path
    ) -> Dict[str, Any]:
        """
        Generate a single music track based on a prompt.

        Args:
            prompt: Text description of the desired music (style, mood, instruments, tempo)
            duration_minutes: Target duration in minutes (3-4 minutes typical)
            order_index: Track number in the sequence (1-20)
            output_dir: Directory to save the generated audio file

        Returns:
            Dict containing:
                - file_path: str (absolute path to the generated audio file)
                - duration_seconds: float (actual duration of the track)
                - order_index: int (track position in sequence)
                - prompt_text: str (the prompt used)
                - metadata: dict (provider-specific metadata)

        Raises:
            Exception: If track generation fails
        """
        pass


class DummyMusicProvider(MusicProvider):
    """
    Dummy implementation for development and testing.

    Generates silent WAV files of the specified duration.
    This allows testing the full pipeline without requiring API keys
    or making expensive API calls during development.
    """

    def __init__(self):
        """Initialize the dummy music provider."""
        self.sample_rate = 44100  # CD quality
        self.channels = 2  # Stereo
        self.sample_width = 2  # 16-bit

    def generate_track(
        self,
        prompt: str,
        duration_minutes: float,
        order_index: int,
        output_dir: Path
    ) -> Dict[str, Any]:
        """
        Generate a silent WAV file for development/testing.

        Creates a silent audio file of the specified duration with proper
        WAV headers and CD-quality settings (44.1kHz, 16-bit, stereo).
        """
        # Ensure output directory exists
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename with timestamp and order index
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"track_{order_index:02d}_{timestamp}.wav"
        file_path = output_dir / filename

        # Calculate number of frames for the duration
        duration_seconds = duration_minutes * 60
        num_frames = int(duration_seconds * self.sample_rate)

        # Create silent WAV file
        with wave.open(str(file_path), 'wb') as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(self.sample_width)
            wav_file.setframerate(self.sample_rate)

            # Write silent frames (zeros)
            silent_frame = struct.pack('<h', 0) * self.channels
            for _ in range(num_frames):
                wav_file.writeframes(silent_frame)

        # Return metadata
        return {
            "file_path": str(file_path.absolute()),
            "duration_seconds": duration_seconds,
            "order_index": order_index,
            "prompt_text": prompt,
            "metadata": {
                "provider": "dummy",
                "sample_rate": self.sample_rate,
                "channels": self.channels,
                "bit_depth": self.sample_width * 8,
                "generated_at": datetime.now().isoformat(),
            }
        }


def get_music_provider() -> MusicProvider:
    """
    Factory function to get the configured music provider.

    Reads MUSIC_PROVIDER environment variable to determine which
    provider to instantiate. Currently supports:
    - "dummy": DummyMusicProvider (silent WAV files)
    - "mubert": (Future) Mubert API integration
    - "beatoven": (Future) Beatoven.ai API integration

    Returns:
        MusicProvider: Configured provider instance

    Raises:
        ValueError: If MUSIC_PROVIDER is not recognized
    """
    provider_name = os.getenv("MUSIC_PROVIDER", "dummy").lower()

    if provider_name == "dummy":
        return DummyMusicProvider()
    elif provider_name == "mubert":
        # Future implementation
        raise NotImplementedError("Mubert provider not yet implemented")
    elif provider_name == "beatoven":
        # Future implementation
        raise NotImplementedError("Beatoven provider not yet implemented")
    else:
        raise ValueError(
            f"Unknown music provider: {provider_name}. "
            f"Supported: dummy, mubert, beatoven"
        )
