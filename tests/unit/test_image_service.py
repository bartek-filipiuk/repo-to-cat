"""
Unit tests for app/services/image_service.py

Tests for image generation service functions:
- map_analysis_to_cat_attributes()
- create_image_prompt()
- save_image_locally()
"""
import os
import base64
import uuid
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
import pytest

from app.services.image_service import (
    map_analysis_to_cat_attributes,
    create_image_prompt,
    save_image_locally,
    ImageServiceError
)


# ============================================================================
# Test: map_analysis_to_cat_attributes()
# ============================================================================

class TestMapAnalysisToAttributes:
    """Test mapping analysis results to cat attributes."""

    def test_maps_small_repo_to_small_cat(self):
        """Test that small repository maps to small cat size."""
        metadata = {
            "size_kb": 500,  # 500 KB -> small
            "primary_language": "Python"
        }
        analysis = {
            "code_quality_score": 7.0,
            "metrics": {"has_tests": True}
        }

        result = map_analysis_to_cat_attributes(metadata, analysis)

        assert result["size"] == "small"

    def test_maps_medium_repo_to_medium_cat(self):
        """Test that medium repository maps to medium cat size."""
        metadata = {
            "size_kb": 3000,  # 3 MB -> medium
            "primary_language": "JavaScript"
        }
        analysis = {
            "code_quality_score": 6.0,
            "metrics": {"has_tests": False}
        }

        result = map_analysis_to_cat_attributes(metadata, analysis)

        assert result["size"] == "medium"

    def test_maps_large_repo_to_large_cat(self):
        """Test that large repository maps to large cat size."""
        metadata = {
            "size_kb": 7000,  # 7 MB -> large
            "primary_language": "Go"
        }
        analysis = {
            "code_quality_score": 8.0,
            "metrics": {"has_tests": True}
        }

        result = map_analysis_to_cat_attributes(metadata, analysis)

        assert result["size"] == "large"

    def test_maps_very_large_repo_to_chonker(self):
        """Test that very large repository maps to chonker cat."""
        metadata = {
            "size_kb": 15000,  # 15 MB -> very_large
            "primary_language": "Rust"
        }
        analysis = {
            "code_quality_score": 9.0,
            "metrics": {"has_tests": True}
        }

        result = map_analysis_to_cat_attributes(metadata, analysis)

        assert result["size"] == "very_large"

    def test_maps_excellent_quality_to_senior_age(self):
        """Test that excellent code quality maps to senior (wise) cat."""
        metadata = {
            "size_kb": 1000,
            "primary_language": "Python"
        }
        analysis = {
            "code_quality_score": 9.0,  # >= 8 -> senior
            "metrics": {"has_tests": True}
        }

        result = map_analysis_to_cat_attributes(metadata, analysis)

        assert result["age"] == "senior"

    def test_maps_good_quality_to_adult_age(self):
        """Test that good code quality maps to adult cat."""
        metadata = {
            "size_kb": 1000,
            "primary_language": "Python"
        }
        analysis = {
            "code_quality_score": 7.0,  # >= 6 -> adult
            "metrics": {"has_tests": True}
        }

        result = map_analysis_to_cat_attributes(metadata, analysis)

        assert result["age"] == "adult"

    def test_maps_average_quality_to_young_age(self):
        """Test that average code quality maps to young cat."""
        metadata = {
            "size_kb": 1000,
            "primary_language": "Python"
        }
        analysis = {
            "code_quality_score": 5.0,  # >= 4 -> young
            "metrics": {"has_tests": False}
        }

        result = map_analysis_to_cat_attributes(metadata, analysis)

        assert result["age"] == "young"

    def test_maps_poor_quality_to_kitten_age(self):
        """Test that poor code quality maps to kitten (inexperienced)."""
        metadata = {
            "size_kb": 1000,
            "primary_language": "Python"
        }
        analysis = {
            "code_quality_score": 3.0,  # < 4 -> kitten
            "metrics": {"has_tests": False}
        }

        result = map_analysis_to_cat_attributes(metadata, analysis)

        assert result["age"] == "kitten"

    def test_maps_high_quality_with_tests_to_happy_expression(self):
        """Test that high quality code with tests maps to happy expression."""
        metadata = {
            "size_kb": 1000,
            "primary_language": "Python"
        }
        analysis = {
            "code_quality_score": 8.5,  # >= 8 with tests -> happy
            "metrics": {"has_tests": True}
        }

        result = map_analysis_to_cat_attributes(metadata, analysis)

        assert result["expression"] == "happy"

    def test_maps_good_quality_to_neutral_expression(self):
        """Test that good quality code maps to neutral expression."""
        metadata = {
            "size_kb": 1000,
            "primary_language": "Python"
        }
        analysis = {
            "code_quality_score": 7.0,  # >= 6 -> neutral
            "metrics": {"has_tests": True}
        }

        result = map_analysis_to_cat_attributes(metadata, analysis)

        assert result["expression"] == "neutral"

    def test_maps_mediocre_quality_to_concerned_expression(self):
        """Test that mediocre quality code maps to concerned expression."""
        metadata = {
            "size_kb": 1000,
            "primary_language": "Python"
        }
        analysis = {
            "code_quality_score": 5.0,  # >= 4 -> concerned
            "metrics": {"has_tests": False}
        }

        result = map_analysis_to_cat_attributes(metadata, analysis)

        assert result["expression"] == "concerned"

    def test_maps_poor_quality_to_grumpy_expression(self):
        """Test that poor quality code maps to grumpy expression."""
        metadata = {
            "size_kb": 1000,
            "primary_language": "Python"
        }
        analysis = {
            "code_quality_score": 2.0,  # < 4 -> grumpy
            "metrics": {"has_tests": False}
        }

        result = map_analysis_to_cat_attributes(metadata, analysis)

        assert result["expression"] == "grumpy"

    def test_maps_python_to_snakes_background(self):
        """Test that Python language maps to snakes background."""
        metadata = {
            "size_kb": 1000,
            "primary_language": "Python"
        }
        analysis = {
            "code_quality_score": 7.0,
            "metrics": {"has_tests": True}
        }

        result = map_analysis_to_cat_attributes(metadata, analysis)

        assert "snakes" in result["background"].lower()

    def test_maps_javascript_to_coffee_background(self):
        """Test that JavaScript language maps to coffee background."""
        metadata = {
            "size_kb": 1000,
            "primary_language": "JavaScript"
        }
        analysis = {
            "code_quality_score": 7.0,
            "metrics": {"has_tests": True}
        }

        result = map_analysis_to_cat_attributes(metadata, analysis)

        assert "coffee" in result["background"].lower()

    def test_maps_unknown_language_to_default_background(self):
        """Test that unknown language maps to default background."""
        metadata = {
            "size_kb": 1000,
            "primary_language": "UnknownLang123"
        }
        analysis = {
            "code_quality_score": 7.0,
            "metrics": {"has_tests": True}
        }

        result = map_analysis_to_cat_attributes(metadata, analysis)

        assert "code editor" in result["background"].lower() or "binary" in result["background"].lower()

    def test_returns_beauty_score_matching_quality_score(self):
        """Test that beauty_score matches code_quality_score."""
        metadata = {
            "size_kb": 1000,
            "primary_language": "Python"
        }
        analysis = {
            "code_quality_score": 7.5,
            "metrics": {"has_tests": True}
        }

        result = map_analysis_to_cat_attributes(metadata, analysis)

        assert result["beauty_score"] == 7.5

    def test_includes_all_required_fields(self):
        """Test that result includes all required cat attribute fields."""
        metadata = {
            "size_kb": 1000,
            "primary_language": "Python"
        }
        analysis = {
            "code_quality_score": 7.0,
            "metrics": {"has_tests": True}
        }

        result = map_analysis_to_cat_attributes(metadata, analysis)

        assert "size" in result
        assert "age" in result
        assert "beauty_score" in result
        assert "expression" in result
        assert "background" in result
        assert "language" in result


# ============================================================================
# Test: create_image_prompt()
# ============================================================================

class TestCreateImagePrompt:
    """Test image prompt generation."""

    def test_creates_prompt_with_all_attributes(self, monkeypatch):
        """Test that prompt includes all cat attributes."""
        # Mock add_creative_spice to return base prompt unchanged
        def mock_spice(base_prompt, quality_score):
            return base_prompt

        monkeypatch.setattr("app.services.image_service.add_creative_spice", mock_spice)

        cat_attrs = {
            "size": "medium",
            "age": "adult",
            "beauty_score": 7.5,
            "expression": "happy",
            "background": "snakes and code snippets",
            "language": "Python"
        }

        prompt = create_image_prompt(cat_attrs)

        # Check for key elements
        assert "medium" in prompt.lower() or "cat" in prompt.lower()
        assert "adult" in prompt.lower()
        assert "happy" in prompt.lower() or "happily" in prompt.lower()
        assert "snakes" in prompt.lower()

    def test_prompt_includes_beauty_modifiers_for_high_score(self, monkeypatch):
        """Test that high beauty score includes positive modifiers."""
        # Mock add_creative_spice
        def mock_spice(base_prompt, quality_score):
            return base_prompt

        monkeypatch.setattr("app.services.image_service.add_creative_spice", mock_spice)

        cat_attrs = {
            "size": "medium",
            "age": "adult",
            "beauty_score": 9.0,  # High score
            "expression": "happy",
            "background": "snakes and code snippets",
            "language": "Python"
        }

        prompt = create_image_prompt(cat_attrs)

        # Should include positive descriptors
        assert any(word in prompt.lower() for word in ["beautiful", "well-groomed"])

    def test_prompt_includes_beauty_modifiers_for_low_score(self, monkeypatch):
        """Test that low beauty score includes appropriate modifiers."""
        # Mock add_creative_spice
        def mock_spice(base_prompt, quality_score):
            return base_prompt

        monkeypatch.setattr("app.services.image_service.add_creative_spice", mock_spice)

        cat_attrs = {
            "size": "small",
            "age": "kitten",
            "beauty_score": 3.0,  # Low score
            "expression": "grumpy",
            "background": "snakes and code snippets",
            "language": "Python"
        }

        prompt = create_image_prompt(cat_attrs)

        # Should include descriptors for lower quality
        assert any(word in prompt.lower() for word in ["scruffy", "disheveled", "ordinary"])

    def test_prompt_for_kitten_small_size(self, monkeypatch):
        """Test prompt generation for small kitten."""
        # Mock add_creative_spice
        def mock_spice(base_prompt, quality_score):
            return base_prompt

        monkeypatch.setattr("app.services.image_service.add_creative_spice", mock_spice)

        cat_attrs = {
            "size": "small",
            "age": "kitten",
            "beauty_score": 6.0,
            "expression": "concerned",
            "background": "coffee cups and laptops",
            "language": "JavaScript"
        }

        prompt = create_image_prompt(cat_attrs)

        assert "kitten" in prompt.lower() or "small" in prompt.lower()
        assert "coffee" in prompt.lower()

    def test_prompt_for_chonker_senior(self, monkeypatch):
        """Test prompt generation for large senior cat."""
        # Mock add_creative_spice
        def mock_spice(base_prompt, quality_score):
            return base_prompt

        monkeypatch.setattr("app.services.image_service.add_creative_spice", mock_spice)

        cat_attrs = {
            "size": "very_large",
            "age": "senior",
            "beauty_score": 9.5,
            "expression": "happy",
            "background": "gophers and mountains",
            "language": "Go"
        }

        prompt = create_image_prompt(cat_attrs)

        assert any(word in prompt.lower() for word in ["large", "chonk", "massive"])
        assert "senior" in prompt.lower() or "wise" in prompt.lower()
        assert "gophers" in prompt.lower() or "mountains" in prompt.lower()

    def test_prompt_includes_photorealistic_instruction(self, monkeypatch):
        """Test that prompt includes quality/realism instructions."""
        # Mock add_creative_spice
        def mock_spice(base_prompt, quality_score):
            return base_prompt

        monkeypatch.setattr("app.services.image_service.add_creative_spice", mock_spice)

        cat_attrs = {
            "size": "medium",
            "age": "adult",
            "beauty_score": 7.0,
            "expression": "neutral",
            "background": "snakes and code snippets",
            "language": "Python"
        }

        prompt = create_image_prompt(cat_attrs)

        # Should include quality instructions
        assert any(word in prompt.lower() for word in ["photorealistic", "detailed", "quality", "cinematic"])

    def test_prompt_is_non_empty_string(self, monkeypatch):
        """Test that prompt is a non-empty string."""
        # Mock add_creative_spice
        def mock_spice(base_prompt, quality_score):
            return base_prompt

        monkeypatch.setattr("app.services.image_service.add_creative_spice", mock_spice)

        cat_attrs = {
            "size": "medium",
            "age": "adult",
            "beauty_score": 7.0,
            "expression": "neutral",
            "background": "snakes and code snippets",
            "language": "Python"
        }

        prompt = create_image_prompt(cat_attrs)

        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_creative_spice_is_called(self, monkeypatch):
        """Test that add_creative_spice is called during prompt generation."""
        spice_called = []

        def mock_spice(base_prompt, quality_score):
            spice_called.append(True)
            return f"{base_prompt} (enhanced)"

        monkeypatch.setattr("app.services.image_service.add_creative_spice", mock_spice)

        cat_attrs = {
            "size": "medium",
            "age": "adult",
            "beauty_score": 7.0,
            "expression": "neutral",
            "background": "snakes and code snippets",
            "language": "Python"
        }

        prompt = create_image_prompt(cat_attrs)

        # Verify spice was called
        assert len(spice_called) == 1
        assert "(enhanced)" in prompt


# ============================================================================
# Test: Breed Variation
# ============================================================================

class TestBreedVariation:
    """Test cat breed variation based on programming language."""

    def test_python_produces_tabby_breed(self):
        """Test that Python language produces tabby cat breed."""
        cat_attrs = {
            "size": "medium",
            "age": "adult",
            "beauty_score": 7.0,
            "expression": "neutral",
            "background": "snakes and code snippets",
            "language": "Python"
        }

        prompt = create_image_prompt(cat_attrs)

        assert "tabby" in prompt.lower()
        assert "striped" in prompt.lower() or "stripe" in prompt.lower()

    def test_javascript_produces_siamese_breed(self):
        """Test that JavaScript language produces siamese cat breed."""
        cat_attrs = {
            "size": "medium",
            "age": "adult",
            "beauty_score": 7.0,
            "expression": "neutral",
            "background": "coffee cups and laptops",
            "language": "JavaScript"
        }

        prompt = create_image_prompt(cat_attrs)

        assert "siamese" in prompt.lower()
        assert "blue eyes" in prompt.lower()

    def test_java_produces_persian_breed(self):
        """Test that Java language produces persian cat breed."""
        cat_attrs = {
            "size": "large",
            "age": "adult",
            "beauty_score": 7.0,
            "expression": "neutral",
            "background": "coffee beans and enterprise buildings",
            "language": "Java"
        }

        prompt = create_image_prompt(cat_attrs)

        assert "persian" in prompt.lower()
        assert "long fur" in prompt.lower()

    def test_rust_produces_maine_coon_breed(self):
        """Test that Rust language produces maine coon cat breed."""
        cat_attrs = {
            "size": "large",
            "age": "adult",
            "beauty_score": 8.0,
            "expression": "neutral",
            "background": "gears and orange crab",
            "language": "Rust"
        }

        prompt = create_image_prompt(cat_attrs)

        assert "maine coon" in prompt.lower()
        assert "majestic" in prompt.lower() or "tufted ears" in prompt.lower()

    def test_go_produces_maine_coon_breed(self):
        """Test that Go language produces maine coon cat breed."""
        cat_attrs = {
            "size": "medium",
            "age": "adult",
            "beauty_score": 7.0,
            "expression": "neutral",
            "background": "gophers and mountains",
            "language": "Go"
        }

        prompt = create_image_prompt(cat_attrs)

        assert "maine coon" in prompt.lower()

    def test_haskell_produces_scottish_fold_breed(self):
        """Test that Haskell language produces scottish fold cat breed."""
        cat_attrs = {
            "size": "small",
            "age": "adult",
            "beauty_score": 7.0,
            "expression": "neutral",
            "background": "lambda symbols and equations",
            "language": "Haskell"
        }

        prompt = create_image_prompt(cat_attrs)

        assert "scottish fold" in prompt.lower()
        assert "folded ears" in prompt.lower()

    def test_swift_produces_british_shorthair_breed(self):
        """Test that Swift language produces british shorthair cat breed."""
        cat_attrs = {
            "size": "medium",
            "age": "adult",
            "beauty_score": 7.5,
            "expression": "neutral",
            "background": "bird feathers and iOS devices",
            "language": "Swift"
        }

        prompt = create_image_prompt(cat_attrs)

        assert "british shorthair" in prompt.lower()
        assert "round face" in prompt.lower() or "plush" in prompt.lower()

    def test_unknown_language_produces_domestic_shorthair_breed(self):
        """Test that unknown language produces domestic shorthair (default)."""
        cat_attrs = {
            "size": "medium",
            "age": "adult",
            "beauty_score": 7.0,
            "expression": "neutral",
            "background": "generic code editor",
            "language": "UnknownLang123"
        }

        prompt = create_image_prompt(cat_attrs)

        assert "domestic shorthair" in prompt.lower()

    def test_case_insensitive_language_matching(self):
        """Test that language matching is case-insensitive."""
        cat_attrs_upper = {
            "size": "medium",
            "age": "adult",
            "beauty_score": 7.0,
            "expression": "neutral",
            "background": "snakes and code",
            "language": "PYTHON"
        }

        cat_attrs_lower = {
            "size": "medium",
            "age": "adult",
            "beauty_score": 7.0,
            "expression": "neutral",
            "background": "snakes and code",
            "language": "python"
        }

        prompt_upper = create_image_prompt(cat_attrs_upper)
        prompt_lower = create_image_prompt(cat_attrs_lower)

        # Both should produce tabby
        assert "tabby" in prompt_upper.lower()
        assert "tabby" in prompt_lower.lower()

    def test_different_languages_produce_different_breeds(self):
        """Test that different language families produce distinct breeds."""
        python_attrs = {
            "size": "medium",
            "age": "adult",
            "beauty_score": 7.0,
            "expression": "neutral",
            "background": "snakes",
            "language": "Python"
        }

        javascript_attrs = {
            "size": "medium",
            "age": "adult",
            "beauty_score": 7.0,
            "expression": "neutral",
            "background": "coffee",
            "language": "JavaScript"
        }

        rust_attrs = {
            "size": "medium",
            "age": "adult",
            "beauty_score": 7.0,
            "expression": "neutral",
            "background": "gears",
            "language": "Rust"
        }

        python_prompt = create_image_prompt(python_attrs)
        javascript_prompt = create_image_prompt(javascript_attrs)
        rust_prompt = create_image_prompt(rust_attrs)

        # Verify each has its own breed
        assert "tabby" in python_prompt.lower()
        assert "siamese" in javascript_prompt.lower()
        assert "maine coon" in rust_prompt.lower()

        # Verify prompts are different
        assert python_prompt != javascript_prompt
        assert python_prompt != rust_prompt
        assert javascript_prompt != rust_prompt

    def test_breed_in_prompt_with_all_other_attributes(self):
        """Test that breed is properly integrated with size, age, and expression."""
        cat_attrs = {
            "size": "large",
            "age": "senior",
            "beauty_score": 9.0,
            "expression": "happy",
            "background": "coffee beans",
            "language": "Java"
        }

        prompt = create_image_prompt(cat_attrs)

        # Should include all elements
        assert "persian" in prompt.lower()  # breed
        assert any(word in prompt.lower() for word in ["large", "chonk"])  # size
        assert "senior" in prompt.lower() or "wise" in prompt.lower()  # age
        assert "happy" in prompt.lower() or "happily" in prompt.lower()  # expression
        assert "coffee" in prompt.lower()  # background


# ============================================================================
# Test: save_image_locally()
# ============================================================================

class TestSaveImageLocally:
    """Test local image saving."""

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_saves_image_with_uuid_filename(self, mock_mkdir, mock_file):
        """Test that image is saved with UUID-based filename."""
        base64_data = base64.b64encode(b"fake_image_data").decode("utf-8")
        generation_id = str(uuid.uuid4())

        result_path = save_image_locally(base64_data, generation_id)

        # Verify file was opened for writing
        mock_file.assert_called_once()

        # Verify mkdir was called to ensure directory exists
        mock_mkdir.assert_called_once()

        # Verify path is absolute URL (starts with /) and contains generation_id
        assert result_path.startswith("/")
        assert generation_id in result_path
        assert result_path.endswith(".png")

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_decodes_base64_before_saving(self, mock_mkdir, mock_file):
        """Test that base64 data is properly decoded before saving."""
        original_data = b"fake_image_binary_data"
        base64_data = base64.b64encode(original_data).decode("utf-8")
        generation_id = str(uuid.uuid4())

        save_image_locally(base64_data, generation_id)

        # Get the data that was written
        handle = mock_file()
        handle.write.assert_called_once_with(original_data)

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_creates_directory_if_not_exists(self, mock_mkdir, mock_file):
        """Test that generated_images directory is created if it doesn't exist."""
        base64_data = base64.b64encode(b"fake_image_data").decode("utf-8")
        generation_id = str(uuid.uuid4())

        save_image_locally(base64_data, generation_id)

        # Verify mkdir was called with parents=True, exist_ok=True
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @patch("builtins.open", side_effect=PermissionError("Permission denied"))
    @patch("pathlib.Path.mkdir")
    def test_raises_error_on_permission_denied(self, mock_mkdir, mock_file):
        """Test that PermissionError is handled gracefully."""
        base64_data = base64.b64encode(b"fake_image_data").decode("utf-8")
        generation_id = str(uuid.uuid4())

        with pytest.raises(ImageServiceError) as exc_info:
            save_image_locally(base64_data, generation_id)

        assert "permission" in str(exc_info.value).lower()

    def test_raises_error_on_invalid_base64(self):
        """Test that invalid base64 data raises error."""
        invalid_base64 = "not_valid_base64!@#$%"
        generation_id = str(uuid.uuid4())

        with pytest.raises(ImageServiceError) as exc_info:
            save_image_locally(invalid_base64, generation_id)

        assert "base64" in str(exc_info.value).lower() or "decode" in str(exc_info.value).lower()

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_returns_absolute_url_path_format(self, mock_mkdir, mock_file):
        """Test that returned path is absolute URL for API serving."""
        base64_data = base64.b64encode(b"fake_image_data").decode("utf-8")
        generation_id = str(uuid.uuid4())

        result_path = save_image_locally(base64_data, generation_id)

        # Path should be absolute URL starting with /
        assert result_path.startswith("/generated_images/")
        assert generation_id in result_path
        assert result_path.endswith(".png")
        assert result_path == f"/generated_images/{generation_id}.png"

    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_handles_empty_base64_data(self, mock_mkdir, mock_file):
        """Test that empty base64 data raises error."""
        base64_data = ""
        generation_id = str(uuid.uuid4())

        with pytest.raises(ImageServiceError) as exc_info:
            save_image_locally(base64_data, generation_id)

        assert "empty" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()
