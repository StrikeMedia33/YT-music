"""Prompt Generation Service using LLM"""
import os
import json
from typing import Dict, List, Any, Optional
from openai import OpenAI


class PromptGeneratorService:
    """
    Service for generating music and visual prompts using LLM.

    Uses OpenAI-compatible API to generate:
    - 20 unique music prompts (style, instruments, mood, tempo, duration)
    - 20 unique visual prompts (16:9 artwork matched to track mood/theme)

    Ensures content diversity to comply with YouTube's "Inauthentic Content" policies.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-4"
    ):
        """
        Initialize the prompt generator service.

        Args:
            api_key: OpenAI API key (or compatible API key). Defaults to OPENAI_API_KEY env var.
            base_url: Base URL for API (for OpenAI-compatible services). Defaults to OpenAI.
            model: Model to use for generation (e.g., "gpt-4", "gpt-3.5-turbo")
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )

        # Initialize OpenAI client (compatible with other providers via base_url)
        client_kwargs = {"api_key": self.api_key}
        if base_url:
            client_kwargs["base_url"] = base_url

        self.client = OpenAI(**client_kwargs)
        self.model = model

    def generate_prompts(
        self,
        niche_label: str,
        mood_keywords: List[str],
        target_duration_minutes: int = 70
    ) -> Dict[str, Any]:
        """
        Generate both music and visual prompts for a video.

        Args:
            niche_label: The content niche (e.g., "Regency Era Classical", "Lo-fi Study Beats")
            mood_keywords: List of mood/atmosphere keywords
            target_duration_minutes: Target video duration (60-90 minutes)

        Returns:
            Dict containing:
                - music_prompts: List[str] (20 unique music prompts)
                - visual_prompts: List[str] (20 unique visual prompts)
                - metadata: Dict (generation info)

        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If LLM API call fails
        """
        # Validate inputs
        if not niche_label or not niche_label.strip():
            raise ValueError("niche_label cannot be empty")

        if not mood_keywords or len(mood_keywords) == 0:
            raise ValueError("mood_keywords must contain at least one keyword")

        if not (60 <= target_duration_minutes <= 90):
            raise ValueError("target_duration_minutes must be between 60 and 90")

        # Generate music prompts
        music_prompts = self.generate_music_prompts(
            niche_label=niche_label,
            mood_keywords=mood_keywords,
            target_duration_minutes=target_duration_minutes
        )

        # Generate visual prompts (matched to music prompts)
        visual_prompts = self.generate_visual_prompts(
            niche_label=niche_label,
            mood_keywords=mood_keywords,
            music_prompts=music_prompts
        )

        return {
            "music_prompts": music_prompts,
            "visual_prompts": visual_prompts,
            "metadata": {
                "niche_label": niche_label,
                "mood_keywords": mood_keywords,
                "target_duration_minutes": target_duration_minutes,
                "num_tracks": len(music_prompts),
                "num_visuals": len(visual_prompts),
            }
        }

    def generate_music_prompts(
        self,
        niche_label: str,
        mood_keywords: List[str],
        target_duration_minutes: int = 70
    ) -> List[str]:
        """
        Generate 20 unique music track prompts.

        Each prompt describes a distinct track with:
        - Musical style and genre
        - Instrumentation
        - Mood and atmosphere
        - Tempo and rhythm
        - Target duration (3-4 minutes)

        Args:
            niche_label: Content niche
            mood_keywords: Mood/atmosphere keywords
            target_duration_minutes: Target total duration

        Returns:
            List of 20 unique music prompts

        Raises:
            RuntimeError: If LLM API call fails
        """
        # Calculate average track duration
        avg_duration_minutes = target_duration_minutes / 20

        # Build system prompt
        system_prompt = """You are an expert music curator and composer. Your task is to create diverse, unique music track descriptions for an album.

Key requirements:
- Generate exactly 20 UNIQUE and DISTINCT music track prompts
- Each track must be different from all others (varied instruments, tempo, mood, style)
- Each track should be 3-4 minutes long
- Use rich, descriptive language for instruments, mood, tempo, and style
- Ensure variety to avoid repetitious content (critical for YouTube compliance)
- Format: Return ONLY a JSON array of strings, no other text"""

        # Build user prompt
        mood_str = ", ".join(mood_keywords)
        user_prompt = f"""Create 20 unique music track prompts for a "{niche_label}" album.

Mood/Atmosphere: {mood_str}
Average track duration: {avg_duration_minutes:.1f} minutes (3-4 minutes typical)

Requirements:
1. Each prompt must describe a DISTINCT track (different instruments, tempo, style, mood variations)
2. Vary instrumentation across tracks (piano, strings, woodwinds, percussion, etc.)
3. Vary tempo (slow, moderate, upbeat, etc.)
4. Vary mood within the theme (peaceful, energetic, contemplative, joyful, etc.)
5. Include specific musical elements (key, time signature, dynamics, etc.)

Output format: JSON array of 20 strings
Example: ["Track 1: Gentle piano with soft strings...", "Track 2: Energetic acoustic guitar with...", ...]

Generate the 20 prompts now:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.9,  # Higher temperature for more diversity
                max_tokens=2000
            )

            content = response.choices[0].message.content.strip()

            # Parse JSON response
            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            prompts = json.loads(content)

            if not isinstance(prompts, list):
                raise ValueError("LLM response is not a list")

            if len(prompts) != 20:
                raise ValueError(f"Expected 20 prompts, got {len(prompts)}")

            return prompts

        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse LLM response as JSON: {e}")
        except Exception as e:
            raise RuntimeError(f"LLM API call failed: {e}")

    def generate_visual_prompts(
        self,
        niche_label: str,
        mood_keywords: List[str],
        music_prompts: List[str]
    ) -> List[str]:
        """
        Generate 20 unique visual prompts matched to music tracks.

        Each prompt describes a 16:9 background visual that complements
        its corresponding music track.

        Args:
            niche_label: Content niche
            mood_keywords: Mood/atmosphere keywords
            music_prompts: List of 20 music prompts to match visuals to

        Returns:
            List of 20 unique visual prompts (one per music track)

        Raises:
            RuntimeError: If LLM API call fails
        """
        # Build system prompt
        system_prompt = """You are an expert visual designer specializing in YouTube background visuals. Your task is to create visual descriptions that complement music tracks.

Key requirements:
- Generate exactly 20 UNIQUE and DISTINCT visual prompts
- Each visual must complement its corresponding music track
- Each visual should be different from all others (varied scenes, colors, composition)
- Use rich, descriptive language for scenes, lighting, atmosphere, colors
- All visuals must be 16:9 aspect ratio (YouTube standard)
- Ensure variety to avoid repetitious content
- Format: Return ONLY a JSON array of strings, no other text"""

        # Build user prompt with music track context
        mood_str = ", ".join(mood_keywords)

        # Create a summary of music tracks to help with visual matching
        track_summaries = []
        for i, prompt in enumerate(music_prompts[:5], 1):  # Include first 5 as examples
            # Truncate long prompts
            summary = prompt[:100] + "..." if len(prompt) > 100 else prompt
            track_summaries.append(f"Track {i}: {summary}")

        tracks_context = "\n".join(track_summaries)

        user_prompt = f"""Create 20 unique visual prompts for a "{niche_label}" video.

Mood/Atmosphere: {mood_str}

Music track examples (you'll create visuals for all 20):
{tracks_context}
... (15 more tracks follow similar pattern)

Requirements:
1. Create ONE visual prompt for EACH of the 20 music tracks
2. Each visual must COMPLEMENT its track's mood and style
3. Each visual must be DISTINCT and UNIQUE (different scenes, compositions, lighting, colors)
4. All visuals are 16:9 aspect ratio for YouTube
5. Vary visual elements: indoor/outdoor, time of day, weather, colors, composition
6. Include specific details: lighting, atmosphere, colors, focal points

Output format: JSON array of 20 strings
Example: ["Visual 1: Soft morning light streaming through...", "Visual 2: Dynamic sunset over rolling hills with...", ...]

Generate the 20 visual prompts now:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.9,  # Higher temperature for more diversity
                max_tokens=2000
            )

            content = response.choices[0].message.content.strip()

            # Parse JSON response
            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            prompts = json.loads(content)

            if not isinstance(prompts, list):
                raise ValueError("LLM response is not a list")

            if len(prompts) != 20:
                raise ValueError(f"Expected 20 prompts, got {len(prompts)}")

            return prompts

        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse LLM response as JSON: {e}")
        except Exception as e:
            raise RuntimeError(f"LLM API call failed: {e}")
