"""Unit tests for Visual Provider"""
import pytest
import os
from pathlib import Path
from PIL import Image
from providers import VisualProvider, DummyVisualProvider, get_visual_provider


class TestVisualProviderInterface:
    """Test the VisualProvider abstract interface"""

    def test_cannot_instantiate_abstract_class(self):
        """VisualProvider is abstract and cannot be instantiated directly"""
        with pytest.raises(TypeError):
            VisualProvider()

    def test_subclass_must_implement_generate_visual(self):
        """Subclasses must implement generate_visual method"""

        class IncompleteProvider(VisualProvider):
            pass

        with pytest.raises(TypeError):
            IncompleteProvider()


class TestDummyVisualProvider:
    """Test the DummyVisualProvider implementation"""

    @pytest.fixture
    def provider(self):
        """Create a DummyVisualProvider instance"""
        return DummyVisualProvider()

    @pytest.fixture
    def temp_output_dir(self, tmp_path):
        """Create a temporary output directory"""
        output_dir = tmp_path / "test_visuals"
        output_dir.mkdir()
        return output_dir

    def test_provider_initialization(self, provider):
        """Provider initializes with correct image settings"""
        assert provider.width == 1920  # Full HD width
        assert provider.height == 1080  # Full HD height (16:9)
        assert provider.format == "PNG"

    def test_generate_visual_creates_file(self, provider, temp_output_dir):
        """generate_visual creates a PNG file in the output directory"""
        result = provider.generate_visual(
            prompt="Ambient forest scene with soft lighting",
            order_index=1,
            output_dir=temp_output_dir
        )

        assert "file_path" in result
        file_path = Path(result["file_path"])
        assert file_path.exists()
        assert file_path.suffix == ".png"
        assert file_path.parent == temp_output_dir

    def test_generate_visual_correct_dimensions(self, provider, temp_output_dir):
        """Generated visual has correct dimensions (1920x1080, 16:9)"""
        result = provider.generate_visual(
            prompt="Test visual",
            order_index=1,
            output_dir=temp_output_dir
        )

        # Check returned dimensions
        assert result["width"] == 1920
        assert result["height"] == 1080

        # Verify actual image dimensions
        with Image.open(result["file_path"]) as img:
            assert img.width == 1920
            assert img.height == 1080
            assert img.format == "PNG"

    def test_generate_visual_correct_aspect_ratio(self, provider, temp_output_dir):
        """Generated visual has 16:9 aspect ratio"""
        result = provider.generate_visual(
            prompt="Test visual",
            order_index=1,
            output_dir=temp_output_dir
        )

        aspect_ratio = result["width"] / result["height"]
        assert aspect_ratio == pytest.approx(16/9, rel=0.01)

    def test_generate_visual_metadata(self, provider, temp_output_dir):
        """Generated visual returns correct metadata"""
        prompt = "Serene ocean waves at sunset"
        order_index = 5

        result = provider.generate_visual(
            prompt=prompt,
            order_index=order_index,
            output_dir=temp_output_dir
        )

        assert result["order_index"] == order_index
        assert result["prompt_text"] == prompt
        assert result["format"] == "png"

        # Check metadata dict
        assert "metadata" in result
        assert result["metadata"]["provider"] == "dummy"
        assert result["metadata"]["aspect_ratio"] == "16:9"
        assert "color" in result["metadata"]
        assert "generated_at" in result["metadata"]

    def test_generate_visual_creates_output_dir(self, provider, tmp_path):
        """generate_visual creates output directory if it doesn't exist"""
        non_existent_dir = tmp_path / "nested" / "visuals" / "output"
        assert not non_existent_dir.exists()

        result = provider.generate_visual(
            prompt="Test",
            order_index=1,
            output_dir=non_existent_dir
        )

        assert non_existent_dir.exists()
        assert Path(result["file_path"]).exists()

    def test_generate_multiple_visuals(self, provider, temp_output_dir):
        """Can generate multiple unique visuals with different order indices"""
        results = []
        for i in range(1, 4):
            result = provider.generate_visual(
                prompt=f"Visual {i}: Unique scene",
                order_index=i,
                output_dir=temp_output_dir
            )
            results.append(result)

        # All files should exist and be unique
        file_paths = [r["file_path"] for r in results]
        assert len(file_paths) == len(set(file_paths))  # All unique
        for file_path in file_paths:
            assert Path(file_path).exists()

        # Order indices should be correct
        assert [r["order_index"] for r in results] == [1, 2, 3]

    def test_visuals_have_unique_colors(self, provider, temp_output_dir):
        """Each visual has a unique background color"""
        results = []
        for i in range(1, 6):
            result = provider.generate_visual(
                prompt=f"Visual {i}",
                order_index=i,
                output_dir=temp_output_dir
            )
            results.append(result)

        # Extract colors from metadata
        colors = [r["metadata"]["color"] for r in results]

        # All colors should be unique (for first 6 visuals)
        assert len(colors) == len(set(colors))

    def test_visual_color_palette_cycles(self, provider, temp_output_dir):
        """Color palette cycles correctly after 20 visuals"""
        # Generate visuals 1 and 21 (should have same color)
        result_1 = provider.generate_visual(
            prompt="Visual 1",
            order_index=1,
            output_dir=temp_output_dir
        )

        result_21 = provider.generate_visual(
            prompt="Visual 21",
            order_index=21,
            output_dir=temp_output_dir
        )

        # Color should repeat after 20 visuals
        assert result_1["metadata"]["color"] == result_21["metadata"]["color"]

    def test_visual_is_valid_image(self, provider, temp_output_dir):
        """Generated visual is a valid, viewable image"""
        result = provider.generate_visual(
            prompt="Test image",
            order_index=1,
            output_dir=temp_output_dir
        )

        # Open and verify image
        with Image.open(result["file_path"]) as img:
            # Should be RGB mode
            assert img.mode == "RGB"

            # Should have pixels (not empty)
            pixels = list(img.getdata())
            assert len(pixels) == 1920 * 1080

            # Should not be all one color (has text/graphics)
            unique_colors = set(pixels)
            assert len(unique_colors) > 1

    def test_long_prompt_truncation(self, provider, temp_output_dir):
        """Very long prompts are truncated for display"""
        long_prompt = "A" * 200  # 200 character prompt

        result = provider.generate_visual(
            prompt=long_prompt,
            order_index=1,
            output_dir=temp_output_dir
        )

        # Prompt should be stored in full
        assert result["prompt_text"] == long_prompt
        assert len(result["prompt_text"]) == 200

        # Image should still be created successfully
        assert Path(result["file_path"]).exists()


class TestVisualProviderFactory:
    """Test the get_visual_provider factory function"""

    def test_default_provider_is_dummy(self, monkeypatch):
        """Default provider is DummyVisualProvider when no env var set"""
        monkeypatch.delenv("VISUAL_PROVIDER", raising=False)
        provider = get_visual_provider()
        assert isinstance(provider, DummyVisualProvider)

    def test_explicit_dummy_provider(self, monkeypatch):
        """Can explicitly request dummy provider"""
        monkeypatch.setenv("VISUAL_PROVIDER", "dummy")
        provider = get_visual_provider()
        assert isinstance(provider, DummyVisualProvider)

    def test_case_insensitive_provider_name(self, monkeypatch):
        """Provider name is case-insensitive"""
        monkeypatch.setenv("VISUAL_PROVIDER", "DUMMY")
        provider = get_visual_provider()
        assert isinstance(provider, DummyVisualProvider)

    def test_leonardo_provider_not_implemented(self, monkeypatch):
        """Leonardo provider raises NotImplementedError"""
        monkeypatch.setenv("VISUAL_PROVIDER", "leonardo")
        with pytest.raises(NotImplementedError, match="Leonardo provider not yet implemented"):
            get_visual_provider()

    def test_gemini_provider_not_implemented(self, monkeypatch):
        """Gemini provider raises NotImplementedError"""
        monkeypatch.setenv("VISUAL_PROVIDER", "gemini")
        with pytest.raises(NotImplementedError, match="Gemini provider not yet implemented"):
            get_visual_provider()

    def test_unknown_provider_raises_error(self, monkeypatch):
        """Unknown provider name raises ValueError"""
        monkeypatch.setenv("VISUAL_PROVIDER", "unknown_provider")
        with pytest.raises(ValueError, match="Unknown visual provider: unknown_provider"):
            get_visual_provider()


class TestVisualProviderIntegration:
    """Integration tests for visual provider in realistic scenarios"""

    @pytest.fixture
    def provider(self):
        return DummyVisualProvider()

    @pytest.fixture
    def output_dir(self, tmp_path):
        return tmp_path / "output" / "visuals"

    def test_generate_20_unique_visuals(self, provider, output_dir):
        """Simulate generating 20 unique visuals for a full video"""
        visuals = []

        # Generate 20 visuals with unique prompts
        for i in range(1, 21):
            result = provider.generate_visual(
                prompt=f"Visual {i}: Ambient scene variation {i}",
                order_index=i,
                output_dir=output_dir
            )
            visuals.append(result)

        # Verify all 20 visuals generated successfully
        assert len(visuals) == 20

        # All should have unique file paths
        file_paths = [v["file_path"] for v in visuals]
        assert len(file_paths) == len(set(file_paths))

        # All should have correct order indices (1-20)
        order_indices = [v["order_index"] for v in visuals]
        assert order_indices == list(range(1, 21))

        # All files should exist and be valid images
        for visual in visuals:
            file_path = Path(visual["file_path"])
            assert file_path.exists()

            # Verify image can be opened
            with Image.open(file_path) as img:
                assert img.width == 1920
                assert img.height == 1080

        # All should have unique colors
        colors = [v["metadata"]["color"] for v in visuals]
        assert len(colors) == len(set(colors))  # All 20 colors unique

    def test_visuals_saved_to_correct_directory(self, provider, output_dir):
        """All visuals are saved to the specified output directory"""
        num_visuals = 5

        for i in range(1, num_visuals + 1):
            result = provider.generate_visual(
                prompt=f"Visual {i}",
                order_index=i,
                output_dir=output_dir
            )
            file_path = Path(result["file_path"])
            assert file_path.parent == output_dir

    def test_visual_audio_pairing(self, provider, output_dir):
        """Visuals can be paired with audio tracks via order_index"""
        # Simulate 5 track-visual pairs
        pairs = []

        for i in range(1, 6):
            visual = provider.generate_visual(
                prompt=f"Visual for track {i}",
                order_index=i,
                output_dir=output_dir
            )
            pairs.append({
                "track_index": i,
                "visual_index": visual["order_index"],
                "visual_path": visual["file_path"]
            })

        # Verify pairing matches
        for pair in pairs:
            assert pair["track_index"] == pair["visual_index"]
            assert Path(pair["visual_path"]).exists()

    def test_16_9_aspect_ratio_for_youtube(self, provider, output_dir):
        """All generated visuals have YouTube-compatible 16:9 aspect ratio"""
        for i in range(1, 6):
            result = provider.generate_visual(
                prompt=f"YouTube visual {i}",
                order_index=i,
                output_dir=output_dir
            )

            # Check metadata
            assert result["metadata"]["aspect_ratio"] == "16:9"

            # Verify actual image
            with Image.open(result["file_path"]) as img:
                aspect_ratio = img.width / img.height
                assert aspect_ratio == pytest.approx(16/9, rel=0.01)

    def test_full_hd_resolution(self, provider, output_dir):
        """All generated visuals are Full HD (1920x1080) for quality"""
        for i in range(1, 4):
            result = provider.generate_visual(
                prompt=f"HD visual {i}",
                order_index=i,
                output_dir=output_dir
            )

            with Image.open(result["file_path"]) as img:
                assert img.width == 1920
                assert img.height == 1080
                # Verify it's Full HD, not lower resolution
                assert img.width * img.height == 2073600  # 1920 * 1080
