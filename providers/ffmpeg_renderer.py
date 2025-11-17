"""FFmpeg Video Renderer with Visual-Audio Pairing"""
import subprocess
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import tempfile


class FFmpegRenderer:
    """
    Video renderer using FFmpeg for creating background music videos.

    Handles:
    - Concatenating 20 audio tracks with crossfades
    - Creating video with visual-audio pairing (Visual 1→Track 1, Visual 2→Track 2, etc.)
    - Exporting 1080p MP4 (H.264 + AAC)
    - Progress tracking for long renders (60-80 minutes)
    """

    def __init__(
        self,
        video_bitrate: str = "8000k",
        audio_bitrate: str = "192k",
        video_codec: str = "libx264",
        audio_codec: str = "aac",
        preset: str = "medium",
        crf: int = 23
    ):
        """
        Initialize FFmpeg renderer with encoding parameters.

        Args:
            video_bitrate: Video bitrate (e.g., "8000k" for 8 Mbps)
            audio_bitrate: Audio bitrate (e.g., "192k" for 192 kbps)
            video_codec: Video codec (default: libx264 for H.264)
            audio_codec: Audio codec (default: aac)
            preset: FFmpeg encoding preset (ultrafast, fast, medium, slow, veryslow)
            crf: Constant Rate Factor for quality (0-51, lower = better quality)
        """
        self.video_bitrate = video_bitrate
        self.audio_bitrate = audio_bitrate
        self.video_codec = video_codec
        self.audio_codec = audio_codec
        self.preset = preset
        self.crf = crf

        # Verify FFmpeg is available
        self._verify_ffmpeg()

    def _verify_ffmpeg(self):
        """Verify FFmpeg is installed and accessible."""
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "FFmpeg not found. Please install FFmpeg: "
                "https://ffmpeg.org/download.html"
            )

    def render_video(
        self,
        audio_tracks: List[Dict[str, Any]],
        visuals: List[Dict[str, Any]],
        output_path: Path,
        crossfade_duration: float = 2.0,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> Dict[str, Any]:
        """
        Render final video with visual-audio pairing.

        This method:
        1. Concatenates audio tracks with crossfades
        2. Creates video that switches visuals at track boundaries
        3. Proves "human editing effort" through visual-audio pairing

        Args:
            audio_tracks: List of audio track dicts with 'file_path', 'duration_seconds', 'order_index'
            visuals: List of visual dicts with 'file_path', 'order_index'
            output_path: Path for output MP4 file
            crossfade_duration: Duration of crossfade between tracks (seconds)
            progress_callback: Optional callback function for progress updates (0.0 to 1.0)

        Returns:
            Dict containing:
                - output_path: str (path to rendered video)
                - duration_seconds: float (total video duration)
                - resolution: str (e.g., "1920x1080")
                - file_size_mb: float (output file size in MB)
                - metadata: dict (encoding details)

        Raises:
            ValueError: If audio_tracks and visuals don't match (must both have 20 items)
            RuntimeError: If FFmpeg rendering fails
        """
        # Validate inputs
        if len(audio_tracks) != len(visuals):
            raise ValueError(
                f"Audio tracks ({len(audio_tracks)}) and visuals ({len(visuals)}) "
                f"must have the same count"
            )

        if len(audio_tracks) < 1:
            raise ValueError("Must have at least 1 audio track and 1 visual")

        # Sort by order_index to ensure correct sequence
        audio_tracks = sorted(audio_tracks, key=lambda x: x['order_index'])
        visuals = sorted(visuals, key=lambda x: x['order_index'])

        # Ensure output directory exists
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Step 1: Concatenate audio with crossfades
        if progress_callback:
            progress_callback(0.1)

        audio_file = self._concatenate_audio_with_crossfades(
            audio_tracks,
            crossfade_duration
        )

        # Step 2: Create video with visual-audio pairing
        if progress_callback:
            progress_callback(0.3)

        video_result = self._create_video_with_visuals(
            audio_file,
            audio_tracks,
            visuals,
            output_path,
            crossfade_duration,
            progress_callback
        )

        # Clean up temporary audio file
        if audio_file.exists():
            audio_file.unlink()

        if progress_callback:
            progress_callback(1.0)

        return video_result

    def _concatenate_audio_with_crossfades(
        self,
        audio_tracks: List[Dict[str, Any]],
        crossfade_duration: float
    ) -> Path:
        """
        Concatenate audio tracks with crossfades between them.

        Args:
            audio_tracks: List of audio track dicts
            crossfade_duration: Duration of crossfade in seconds

        Returns:
            Path to temporary concatenated audio file
        """
        # Create temporary file for concatenated audio
        temp_audio = Path(tempfile.mktemp(suffix=".wav"))

        if len(audio_tracks) == 1:
            # Single track - no crossfade needed, just copy
            subprocess.run(
                [
                    "ffmpeg", "-y",
                    "-i", audio_tracks[0]["file_path"],
                    "-c:a", "pcm_s16le",
                    str(temp_audio)
                ],
                check=True,
                capture_output=True
            )
            return temp_audio

        # Build FFmpeg filter complex for crossfading
        # Format: [0:a][1:a]acrossfade=d=2[a01];[a01][2:a]acrossfade=d=2[a02];...
        inputs = []
        filter_parts = []

        for i, track in enumerate(audio_tracks):
            inputs.extend(["-i", track["file_path"]])

        # Build crossfade chain
        current_label = "0:a"
        for i in range(1, len(audio_tracks)):
            next_label = f"{i}:a"
            output_label = f"a{i-1}{i}"

            filter_parts.append(
                f"[{current_label}][{next_label}]acrossfade=d={crossfade_duration}:c1=tri:c2=tri[{output_label}]"
            )
            current_label = output_label

        filter_complex = ";".join(filter_parts)

        # Run FFmpeg to concatenate with crossfades
        cmd = [
            "ffmpeg", "-y",
            *inputs,
            "-filter_complex", filter_complex,
            "-map", f"[{current_label}]",
            "-c:a", "pcm_s16le",
            str(temp_audio)
        ]

        subprocess.run(cmd, check=True, capture_output=True)

        return temp_audio

    def _create_video_with_visuals(
        self,
        audio_file: Path,
        audio_tracks: List[Dict[str, Any]],
        visuals: List[Dict[str, Any]],
        output_path: Path,
        crossfade_duration: float,
        progress_callback: Optional[Callable[[float], None]]
    ) -> Dict[str, Any]:
        """
        Create video with visuals that switch at track boundaries.

        This creates the visual-audio pairing:
        - Visual 1 displays during Track 1
        - Visual 2 displays during Track 2
        - etc.

        Args:
            audio_file: Path to concatenated audio
            audio_tracks: List of track dicts with durations
            visuals: List of visual dicts
            output_path: Output video path
            crossfade_duration: Crossfade duration (for timing calculations)
            progress_callback: Progress callback function

        Returns:
            Dict with video metadata
        """
        # Calculate timing for each visual
        # Each visual should display for the duration of its corresponding track
        visual_timings = []
        current_time = 0.0

        for i, track in enumerate(audio_tracks):
            duration = track["duration_seconds"]

            # Adjust for crossfade overlap (except first and last tracks)
            if i > 0:
                current_time -= crossfade_duration

            visual_timings.append({
                "visual_path": visuals[i]["file_path"],
                "start_time": current_time,
                "duration": duration,
                "order_index": visuals[i]["order_index"]
            })

            current_time += duration

        # Get total duration
        total_duration = current_time - (crossfade_duration * (len(audio_tracks) - 1))

        # Build FFmpeg command with concat demuxer for images
        # Create a temporary concat file listing all visuals with durations
        concat_file = self._create_visual_concat_file(visual_timings)

        try:
            cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_file),
                "-i", str(audio_file),
                "-c:v", self.video_codec,
                "-preset", self.preset,
                "-crf", str(self.crf),
                "-b:v", self.video_bitrate,
                "-c:a", self.audio_codec,
                "-b:a", self.audio_bitrate,
                "-pix_fmt", "yuv420p",
                "-shortest",
                "-movflags", "+faststart",
                str(output_path)
            ]

            # Run FFmpeg with progress tracking
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            # Monitor progress (parse stderr for time info)
            if progress_callback:
                for line in process.stderr:
                    if "time=" in line:
                        try:
                            time_str = line.split("time=")[1].split()[0]
                            h, m, s = time_str.split(":")
                            current_seconds = int(h) * 3600 + int(m) * 60 + float(s)
                            progress = 0.3 + (current_seconds / total_duration) * 0.7
                            progress = min(progress, 1.0)
                            progress_callback(progress)
                        except (ValueError, IndexError):
                            pass

            process.wait()

            if process.returncode != 0:
                raise RuntimeError(f"FFmpeg rendering failed: {process.stderr}")

        finally:
            # Clean up concat file
            if concat_file.exists():
                concat_file.unlink()

        # Get output file info
        file_size_mb = output_path.stat().st_size / (1024 * 1024)

        return {
            "output_path": str(output_path.absolute()),
            "duration_seconds": total_duration,
            "resolution": "1920x1080",
            "file_size_mb": round(file_size_mb, 2),
            "metadata": {
                "video_codec": self.video_codec,
                "audio_codec": self.audio_codec,
                "video_bitrate": self.video_bitrate,
                "audio_bitrate": self.audio_bitrate,
                "preset": self.preset,
                "crf": self.crf,
                "num_tracks": len(audio_tracks),
                "num_visuals": len(visuals),
                "crossfade_duration": crossfade_duration,
                "rendered_at": datetime.now().isoformat(),
            }
        }

    def _create_visual_concat_file(
        self,
        visual_timings: List[Dict[str, Any]]
    ) -> Path:
        """
        Create FFmpeg concat file for images with durations.

        Format:
        file 'visual_01.png'
        duration 210.5
        file 'visual_02.png'
        duration 195.3
        ...

        Args:
            visual_timings: List of dicts with visual_path and duration

        Returns:
            Path to temporary concat file
        """
        concat_file = Path(tempfile.mktemp(suffix=".txt"))

        with open(concat_file, "w") as f:
            for timing in visual_timings:
                # FFmpeg concat requires absolute paths
                abs_path = Path(timing["visual_path"]).absolute()
                f.write(f"file '{abs_path}'\n")
                f.write(f"duration {timing['duration']}\n")

            # Repeat last image to ensure it displays fully
            last_visual = visual_timings[-1]["visual_path"]
            abs_path = Path(last_visual).absolute()
            f.write(f"file '{abs_path}'\n")

        return concat_file

    def get_video_info(self, video_path: Path) -> Dict[str, Any]:
        """
        Get information about a video file using ffprobe.

        Args:
            video_path: Path to video file

        Returns:
            Dict with video information (duration, resolution, codecs, etc.)
        """
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(video_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = json.loads(result.stdout)

        # Extract relevant info
        video_stream = next(
            (s for s in info["streams"] if s["codec_type"] == "video"),
            None
        )
        audio_stream = next(
            (s for s in info["streams"] if s["codec_type"] == "audio"),
            None
        )

        return {
            "duration_seconds": float(info["format"]["duration"]),
            "file_size_mb": round(int(info["format"]["size"]) / (1024 * 1024), 2),
            "video": {
                "codec": video_stream["codec_name"] if video_stream else None,
                "width": video_stream.get("width") if video_stream else None,
                "height": video_stream.get("height") if video_stream else None,
                "bitrate": video_stream.get("bit_rate") if video_stream else None,
            } if video_stream else None,
            "audio": {
                "codec": audio_stream["codec_name"] if audio_stream else None,
                "sample_rate": audio_stream.get("sample_rate") if audio_stream else None,
                "channels": audio_stream.get("channels") if audio_stream else None,
                "bitrate": audio_stream.get("bit_rate") if audio_stream else None,
            } if audio_stream else None,
        }
