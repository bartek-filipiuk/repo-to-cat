"""
Unit tests for configuration mappings.

Following TDD: Write tests FIRST, then implement config/mappings.py

Tests cover:
- LANGUAGE_BACKGROUNDS (25+ languages)
- QUALITY_INDICATORS (code quality markers)
- CAT_SIZE_MAPPING (repo size -> cat size)
- CAT_AGE_MAPPING (language age + history -> cat age)
- CAT_EXPRESSION_MAPPING (test coverage -> expression)
- Helper functions for safe lookups
"""
import pytest


def test_language_backgrounds_exists():
    """Test that LANGUAGE_BACKGROUNDS dictionary exists and is non-empty."""
    from config.mappings import LANGUAGE_BACKGROUNDS

    assert isinstance(LANGUAGE_BACKGROUNDS, dict)
    assert len(LANGUAGE_BACKGROUNDS) > 0


def test_language_backgrounds_has_popular_languages():
    """Test that popular languages are present in LANGUAGE_BACKGROUNDS."""
    from config.mappings import LANGUAGE_BACKGROUNDS

    # Popular languages that must be supported
    popular_languages = [
        "Python", "JavaScript", "TypeScript", "Java", "C#", "C++", "C",
        "Go", "Rust", "PHP", "Ruby", "Swift", "Kotlin"
    ]

    for language in popular_languages:
        assert language in LANGUAGE_BACKGROUNDS, f"{language} should be in LANGUAGE_BACKGROUNDS"
        assert isinstance(LANGUAGE_BACKGROUNDS[language], str), f"{language} background should be a string"
        assert len(LANGUAGE_BACKGROUNDS[language]) > 0, f"{language} background should not be empty"


def test_language_backgrounds_has_less_popular_languages():
    """Test that less popular but still used languages are present."""
    from config.mappings import LANGUAGE_BACKGROUNDS

    # Less popular languages that should be supported
    less_popular = [
        "Perl", "Scala", "Haskell", "Elixir", "Clojure", "Lua", "R",
        "Dart", "Shell", "Bash", "Objective-C", "F#", "Erlang"
    ]

    # At least 10 of these should be present
    present_count = sum(1 for lang in less_popular if lang in LANGUAGE_BACKGROUNDS)
    assert present_count >= 10, f"At least 10 less popular languages should be supported, found {present_count}"


def test_language_backgrounds_has_minimum_count():
    """Test that at least 25 languages are supported."""
    from config.mappings import LANGUAGE_BACKGROUNDS

    assert len(LANGUAGE_BACKGROUNDS) >= 25, f"Should have at least 25 languages, found {len(LANGUAGE_BACKGROUNDS)}"


def test_language_backgrounds_all_are_strings():
    """Test that all background values are non-empty strings."""
    from config.mappings import LANGUAGE_BACKGROUNDS

    for language, background in LANGUAGE_BACKGROUNDS.items():
        assert isinstance(language, str), f"Language key {language} should be a string"
        assert isinstance(background, str), f"Background for {language} should be a string"
        assert len(background) > 0, f"Background for {language} should not be empty"
        assert len(background) >= 10, f"Background for {language} should be descriptive (at least 10 chars)"


def test_get_language_background_function_exists():
    """Test that helper function for safe language lookup exists."""
    from config.mappings import get_language_background

    # Should return a background for known language
    python_bg = get_language_background("Python")
    assert isinstance(python_bg, str)
    assert len(python_bg) > 0


def test_get_language_background_returns_default_for_unknown():
    """Test that get_language_background returns default for unknown languages."""
    from config.mappings import get_language_background

    # Unknown language should return default
    unknown_bg = get_language_background("UnknownLanguage123")
    assert isinstance(unknown_bg, str)
    assert len(unknown_bg) > 0

    # Should be different from a real language
    python_bg = get_language_background("Python")
    assert unknown_bg != python_bg or "code" in unknown_bg.lower() or "editor" in unknown_bg.lower()


def test_get_language_background_case_insensitive():
    """Test that get_language_background handles case variations."""
    from config.mappings import get_language_background

    # Should handle different cases
    bg1 = get_language_background("Python")
    bg2 = get_language_background("python")
    bg3 = get_language_background("PYTHON")

    # All should return the same background
    assert bg1 == bg2 == bg3


def test_quality_indicators_exists():
    """Test that QUALITY_INDICATORS dictionary exists with required keys."""
    from config.mappings import QUALITY_INDICATORS

    assert isinstance(QUALITY_INDICATORS, dict)
    assert "spaghetti" in QUALITY_INDICATORS
    assert "legit" in QUALITY_INDICATORS


def test_quality_indicators_spaghetti_structure():
    """Test that spaghetti quality indicators have expected structure."""
    from config.mappings import QUALITY_INDICATORS

    spaghetti = QUALITY_INDICATORS["spaghetti"]
    assert isinstance(spaghetti, dict)

    # Should have indicators for poor code quality
    expected_keys = ["line_length", "function_length", "nesting_depth", "no_comments", "no_tests"]
    for key in expected_keys:
        assert key in spaghetti, f"spaghetti should have {key} indicator"


def test_quality_indicators_legit_structure():
    """Test that legit quality indicators have expected structure."""
    from config.mappings import QUALITY_INDICATORS

    legit = QUALITY_INDICATORS["legit"]
    assert isinstance(legit, dict)

    # Should have indicators for good code quality
    expected_keys = ["consistent_formatting", "type_hints", "tests_exist", "documentation", "modular_structure"]
    for key in expected_keys:
        assert key in legit, f"legit should have {key} indicator"


def test_cat_size_mapping_exists():
    """Test that CAT_SIZE_MAPPING dictionary exists with proper structure."""
    from config.mappings import CAT_SIZE_MAPPING

    assert isinstance(CAT_SIZE_MAPPING, dict)

    # Should have size categories
    assert "small" in CAT_SIZE_MAPPING
    assert "medium" in CAT_SIZE_MAPPING
    assert "large" in CAT_SIZE_MAPPING


def test_cat_size_mapping_has_ranges():
    """Test that CAT_SIZE_MAPPING has proper range definitions."""
    from config.mappings import CAT_SIZE_MAPPING

    # Each size should have a range
    for size in ["small", "medium", "large"]:
        size_value = CAT_SIZE_MAPPING[size]
        assert isinstance(size_value, dict), f"{size} should be a dict with range"
        assert "range" in size_value, f"{size} should have a range"
        assert "description" in size_value, f"{size} should have a description"


def test_cat_size_mapping_values_are_descriptive():
    """Test that cat size descriptions are meaningful."""
    from config.mappings import CAT_SIZE_MAPPING

    for size_key in ["small", "medium", "large"]:
        size_data = CAT_SIZE_MAPPING[size_key]
        description = size_data["description"]

        assert isinstance(description, str)
        assert len(description) > 0
        # Should contain cat-related terms
        assert "cat" in description.lower() or "kitten" in description.lower() or "chonk" in description.lower()


def test_cat_age_mapping_exists():
    """Test that CAT_AGE_MAPPING dictionary exists."""
    from config.mappings import CAT_AGE_MAPPING

    assert isinstance(CAT_AGE_MAPPING, dict)
    assert len(CAT_AGE_MAPPING) > 0


def test_cat_age_mapping_has_age_categories():
    """Test that CAT_AGE_MAPPING has expected age categories."""
    from config.mappings import CAT_AGE_MAPPING

    # Should have different age categories
    expected_ages = ["kitten", "young", "adult", "senior"]

    for age in expected_ages:
        assert age in CAT_AGE_MAPPING, f"Should have {age} category"
        assert isinstance(CAT_AGE_MAPPING[age], dict)
        assert "description" in CAT_AGE_MAPPING[age]


def test_cat_expression_mapping_exists():
    """Test that CAT_EXPRESSION_MAPPING dictionary exists."""
    from config.mappings import CAT_EXPRESSION_MAPPING

    assert isinstance(CAT_EXPRESSION_MAPPING, dict)
    assert len(CAT_EXPRESSION_MAPPING) > 0


def test_cat_expression_mapping_has_expressions():
    """Test that CAT_EXPRESSION_MAPPING has expected expressions."""
    from config.mappings import CAT_EXPRESSION_MAPPING

    # Should have different expressions
    expected_expressions = ["happy", "neutral", "grumpy", "concerned"]

    for expression in expected_expressions:
        assert expression in CAT_EXPRESSION_MAPPING, f"Should have {expression} expression"
        assert isinstance(CAT_EXPRESSION_MAPPING[expression], dict)
        assert "test_coverage_range" in CAT_EXPRESSION_MAPPING[expression]
        assert "description" in CAT_EXPRESSION_MAPPING[expression]


def test_mappings_module_has_all_exports():
    """Test that all required mappings are exported from the module."""
    from config import mappings

    # Check all required exports exist
    assert hasattr(mappings, "LANGUAGE_BACKGROUNDS")
    assert hasattr(mappings, "QUALITY_INDICATORS")
    assert hasattr(mappings, "CAT_SIZE_MAPPING")
    assert hasattr(mappings, "CAT_AGE_MAPPING")
    assert hasattr(mappings, "CAT_EXPRESSION_MAPPING")
    assert hasattr(mappings, "get_language_background")


def test_no_duplicate_backgrounds():
    """Test that language backgrounds are unique (no copy-paste duplicates)."""
    from config.mappings import LANGUAGE_BACKGROUNDS

    # Collect all background descriptions
    backgrounds = list(LANGUAGE_BACKGROUNDS.values())
    unique_backgrounds = set(backgrounds)

    # Most should be unique (allowing a few similar ones for related languages)
    uniqueness_ratio = len(unique_backgrounds) / len(backgrounds)
    assert uniqueness_ratio >= 0.9, f"Backgrounds should be mostly unique, found {uniqueness_ratio:.0%} unique"


def test_php_elephant_background():
    """Test that PHP specifically has elephant-related background as requested."""
    from config.mappings import LANGUAGE_BACKGROUNDS

    assert "PHP" in LANGUAGE_BACKGROUNDS
    php_background = LANGUAGE_BACKGROUNDS["PHP"]

    # Should mention elephants (PHP's mascot)
    assert "elephant" in php_background.lower(), "PHP background should mention elephants"
