"""Metadata Generation Service for YouTube Videos"""
import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from openai import OpenAI


class MetadataGeneratorService:
    """
    Service for generating YouTube video metadata using LLM.

    Generates:
    - Engaging titles using "Album", "Mix", or "Anthology" terminology (NOT "Loop")
    - SEO-optimized descriptions with timestamps for all 20 tracks
    - Relevant tags for YouTube search
    - Metadata text files for manual upload workflow

    Includes reminders about "Altered or synthetic content" checkbox.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-4"
    ):
        """
        Initialize the metadata generator service.

        Args:
            api_key: OpenAI API key (or compatible). Defaults to OPENAI_API_KEY env var.
            base_url: Base URL for API (for OpenAI-compatible services).
            model: Model to use for generation
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )

        client_kwargs = {"api_key": self.api_key}
        if base_url:
            client_kwargs["base_url"] = base_url

        self.client = OpenAI(**client_kwargs)
        self.model = model

    def generate_metadata(
        self,
        niche_label: str,
        mood_keywords: List[str],
        track_titles: List[str],
        track_durations: List[float]
    ) -> Dict[str, Any]:
        """
        Generate complete YouTube metadata.

        Args:
            niche_label: Content niche
            mood_keywords: Mood/atmosphere keywords
            track_titles: List of 20 track titles/prompts
            track_durations: List of 20 track durations in seconds

        Returns:
            Dict containing:
                - title: str (YouTube video title)
                - description: str (Description with timestamps)
                - tags: List[str] (YouTube tags)
                - metadata: Dict (generation info)

        Raises:
            ValueError: If parameters are invalid
        """
        if len(track_titles) != len(track_durations):
            raise ValueError("track_titles and track_durations must have same length")

        if len(track_titles) != 20:
            raise ValueError("Must have exactly 20 tracks")

        # Generate title
        title = self.generate_title(niche_label, mood_keywords)

        # Generate description with timestamps
        description = self.generate_description(
            niche_label, mood_keywords, track_titles, track_durations
        )

        # Generate tags
        tags = self.generate_tags(niche_label, mood_keywords)

        return {
            "title": title,
            "description": description,
            "tags": tags,
            "metadata": {
                "niche_label": niche_label,
                "mood_keywords": mood_keywords,
                "num_tracks": len(track_titles),
                "total_duration_seconds": sum(track_durations),
                "generated_at": datetime.now().isoformat(),
            }
        }

    def generate_title(
        self,
        niche_label: str,
        mood_keywords: List[str]
    ) -> str:
        """
        Generate engaging YouTube video title.

        Uses "Album", "Mix", or "Anthology" terminology (NOT "Loop").
        Example: "Royal Court Ambience: A 1-Hour Regency Classical Mix"

        Args:
            niche_label: Content niche
            mood_keywords: Mood keywords

        Returns:
            Engaging YouTube title string

        Raises:
            RuntimeError: If LLM API call fails
        """
        mood_str = ", ".join(mood_keywords)

        system_prompt = """You are an expert YouTube content strategist specializing in background music videos.

Your task is to create an engaging, SEO-optimized YouTube video title.

Key requirements:
- Use "Album", "Mix", or "Anthology" terminology (NEVER use "Loop")
- Title should be 60-80 characters for optimal YouTube display
- Include niche/genre and mood descriptors
- Be engaging and clickable while maintaining professionalism
- Format: Return ONLY the title text, no quotes or extra formatting"""

        user_prompt = f"""Create a YouTube video title for this content:

Niche: {niche_label}
Mood: {mood_str}
Duration: Approximately 1 hour

Example formats:
- "Royal Court Ambience: A 1-Hour Regency Classical Mix"
- "Ethereal Soundscapes: Ambient Electronic Album for Focus"
- "Coffeehouse Jazz Anthology: 70 Minutes of Smooth Piano"

Generate the title now (60-80 characters):"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=100
            )

            title = response.choices[0].message.content.strip()

            # Remove quotes if present
            if title.startswith('"') and title.endswith('"'):
                title = title[1:-1]

            return title

        except Exception as e:
            raise RuntimeError(f"Title generation failed: {e}")

    def generate_description(
        self,
        niche_label: str,
        mood_keywords: List[str],
        track_titles: List[str],
        track_durations: List[float]
    ) -> str:
        """
        Generate SEO-optimized YouTube description with timestamps.

        Includes:
        - Brief introduction to the album/mix
        - Timestamps for all 20 tracks
        - Reminder about "Altered or synthetic content" checkbox

        Args:
            niche_label: Content niche
            mood_keywords: Mood keywords
            track_titles: List of 20 track titles
            track_durations: List of 20 durations in seconds

        Returns:
            Complete YouTube description with timestamps

        Raises:
            RuntimeError: If LLM API call fails
        """
        # Calculate timestamps
        timestamps = self._calculate_timestamps(track_titles, track_durations)

        mood_str = ", ".join(mood_keywords)

        system_prompt = """You are an expert YouTube content strategist.

Your task is to write an engaging, SEO-optimized video description.

Key requirements:
- Write 2-3 paragraph introduction about the album/mix
- Describe the mood, atmosphere, and ideal use cases
- Be engaging and informative
- Use natural language (avoid overly promotional tone)
- Format: Return ONLY the introduction text, no extra formatting"""

        user_prompt = f"""Write a YouTube description introduction for this music album/mix:

Niche: {niche_label}
Mood: {mood_str}
Duration: {sum(track_durations) / 60:.0f} minutes
Number of tracks: 20

Requirements:
- 2-3 paragraphs
- Describe the mood and atmosphere
- Mention ideal listening scenarios (study, relaxation, work, etc.)
- Emphasize the curated nature and track variety

Generate the introduction now:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            intro = response.choices[0].message.content.strip()

            # Build complete description
            description_parts = [
                intro,
                "",
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                "📋 TRACKLIST & TIMESTAMPS",
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                ""
            ]

            # Add timestamps
            description_parts.extend(timestamps)

            description_parts.extend([
                "",
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                "",
                "⚠️ IMPORTANT: This content contains AI-generated music and visuals.",
                "Please ensure the 'Altered or synthetic content' checkbox is enabled in YouTube Studio.",
                "",
                f"🎵 Genre: {niche_label}",
                f"🎭 Mood: {mood_str}",
                f"⏱️ Duration: {sum(track_durations) / 60:.0f} minutes",
                f"🎼 Tracks: 20 unique compositions",
                "",
                "🤖 Generated with Claude Code",
                "https://claude.com/claude-code"
            ])

            return "\n".join(description_parts)

        except Exception as e:
            raise RuntimeError(f"Description generation failed: {e}")

    def generate_tags(
        self,
        niche_label: str,
        mood_keywords: List[str]
    ) -> List[str]:
        """
        Generate relevant YouTube tags for SEO.

        Args:
            niche_label: Content niche
            mood_keywords: Mood keywords

        Returns:
            List of YouTube tags (15-20 tags)

        Raises:
            RuntimeError: If LLM API call fails
        """
        mood_str = ", ".join(mood_keywords)

        system_prompt = """You are a YouTube SEO expert.

Your task is to generate relevant tags for a music video.

Key requirements:
- Generate 15-20 relevant tags
- Include genre, mood, use case tags
- Use both specific and broad tags
- Follow YouTube tag best practices
- Format: Return tags as a JSON array of strings"""

        user_prompt = f"""Generate YouTube tags for this music video:

Niche: {niche_label}
Mood: {mood_str}

Requirements:
- 15-20 tags total
- Include genre tags ({niche_label.lower()})
- Include mood tags ({mood_str.lower()})
- Include use case tags (study music, focus music, relaxation, background music, etc.)
- Include format tags (album, mix, compilation)
- Mix specific and broad tags for better reach

Output format: JSON array of strings
Example: ["ambient music", "study music", "focus music", ...]

Generate the tags now:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )

            content = response.choices[0].message.content.strip()

            # Parse JSON response
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            tags = json.loads(content)

            if not isinstance(tags, list):
                raise ValueError("Tags response is not a list")

            # Limit to 20 tags
            return tags[:20]

        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse tags as JSON: {e}")
        except Exception as e:
            raise RuntimeError(f"Tags generation failed: {e}")

    def save_metadata_to_file(
        self,
        metadata: Dict[str, Any],
        output_path: Path
    ) -> Path:
        """
        Save generated metadata to a text file.

        Args:
            metadata: Metadata dict from generate_metadata()
            output_path: Path to save metadata file

        Returns:
            Path to saved file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("YOUTUBE VIDEO METADATA\n")
            f.write("=" * 80 + "\n\n")

            f.write("TITLE:\n")
            f.write("-" * 80 + "\n")
            f.write(metadata["title"] + "\n\n")

            f.write("DESCRIPTION:\n")
            f.write("-" * 80 + "\n")
            f.write(metadata["description"] + "\n\n")

            f.write("TAGS:\n")
            f.write("-" * 80 + "\n")
            tags_str = ", ".join(metadata["tags"])
            f.write(tags_str + "\n\n")

            f.write("=" * 80 + "\n")
            f.write("UPLOAD CHECKLIST:\n")
            f.write("=" * 80 + "\n")
            f.write("☐ Copy title to YouTube\n")
            f.write("☐ Copy description to YouTube\n")
            f.write("☐ Copy tags to YouTube\n")
            f.write("☐ Enable 'Altered or synthetic content' checkbox\n")
            f.write("☐ Set appropriate category (Music)\n")
            f.write("☐ Add custom thumbnail (optional)\n")
            f.write("☐ Schedule or publish\n\n")

            f.write("Generated: " + datetime.now().isoformat() + "\n")

        return output_path

    def _calculate_timestamps(
        self,
        track_titles: List[str],
        track_durations: List[float]
    ) -> List[str]:
        """
        Calculate timestamps for all tracks.

        Args:
            track_titles: List of track titles
            track_durations: List of durations in seconds

        Returns:
            List of formatted timestamp strings
        """
        timestamps = []
        current_time = 0.0

        for i, (title, duration) in enumerate(zip(track_titles, track_durations), 1):
            # Format time as MM:SS or HH:MM:SS
            minutes = int(current_time // 60)
            seconds = int(current_time % 60)

            if minutes >= 60:
                hours = minutes // 60
                minutes = minutes % 60
                time_str = f"{hours:01d}:{minutes:02d}:{seconds:02d}"
            else:
                time_str = f"{minutes:02d}:{seconds:02d}"

            # Truncate long titles
            display_title = title[:80] + "..." if len(title) > 80 else title

            timestamps.append(f"{time_str} - {display_title}")

            current_time += duration

        return timestamps
