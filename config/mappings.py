"""
Cat attribute mappings for code quality visualization.

This module contains configuration dictionaries that map repository
characteristics to cat attributes for image generation.

Mappings:
- LANGUAGE_BACKGROUNDS: Programming language -> cat background theme
- QUALITY_INDICATORS: Code quality markers (spaghetti vs legit)
- CAT_SIZE_MAPPING: Repository size (KB) -> cat size
- CAT_AGE_MAPPING: Language age + history -> cat age
- CAT_EXPRESSION_MAPPING: Test coverage + health -> cat expression
"""

from typing import Dict, Any


# ============================================================================
# LANGUAGE BACKGROUNDS - 28 Languages
# ============================================================================

LANGUAGE_BACKGROUNDS: Dict[str, str] = {
    # Popular languages (13)
    "Python": "snakes and code snippets in a cozy den",
    "JavaScript": "coffee cups and scattered npm packages on a laptop desk",
    "TypeScript": "organized coffee cups with a blue bow tie and type annotations",
    "Java": "coffee beans and enterprise office buildings with glass windows",
    "C#": ".NET framework symbols and Windows logos on a modern workspace",
    "C++": "circuit boards and low-level hardware with pointers and wires",
    "C": "memory chips and pointer diagrams on vintage computer hardware",
    "Go": "gophers running playfully through scenic mountains",
    "Rust": "gears, a friendly orange crab named Ferris, and metal safety equipment",
    "PHP": "purple elephants and web servers with code scrolls",
    "Ruby": "sparkling red gems scattered on polished railway tracks",
    "Swift": "elegant bird feathers and sleek iOS devices in a modern studio",
    "Kotlin": "friendly Android robots climbing colorful mountains",

    # Less popular but still used (15)
    "Perl": "wise camels carrying ancient scrolls through desert landscapes",
    "Scala": "elegant marble staircases ascending toward JVM clouds",
    "Haskell": "lambda symbols and complex mathematical equations on chalkboards",
    "Elixir": "mystical potion bottles and alchemy symbols in a magical workshop",
    "Clojure": "colorful nested parentheses forming beautiful fractal patterns",
    "Lua": "crescent moon and glowing stars in a peaceful night sky",
    "R": "statistical graphs and colorful data charts on scientific displays",
    "Dart": "delicate Flutter butterflies around vibrant mobile app screens",
    "Shell": "terminal windows with green text on black screens",
    "Bash": "command prompts and cascading shell scripts in a terminal",
    "Objective-C": "classic Apple logos and legacy code blueprints from the past",
    "F#": "functional programming pipes and .NET symbols in harmony",
    "Erlang": "telephone switches and distributed network diagrams",
    "Groovy": "musical notes and Gradle build scripts dancing together",
    "Crystal": "sparkling crystal shards and high-performance gemstones",
}

# Default background for unknown languages
DEFAULT_BACKGROUND = "a generic code editor with colorful syntax highlighting and binary matrix"


# ============================================================================
# QUALITY INDICATORS
# ============================================================================

QUALITY_INDICATORS: Dict[str, Dict[str, Any]] = {
    "spaghetti": {
        # Poor code quality markers
        "line_length": ">200",
        "function_length": ">100",
        "nesting_depth": ">4",
        "no_comments": True,
        "no_tests": True,
        "inconsistent_formatting": True,
        "no_type_hints": True,
    },
    "legit": {
        # High code quality markers
        "consistent_formatting": True,
        "type_hints": True,
        "tests_exist": True,
        "documentation": True,
        "modular_structure": True,
        "reasonable_line_length": True,
        "good_naming": True,
    },
}


# ============================================================================
# CAT SIZE MAPPING - Repository size to cat size
# ============================================================================

CAT_SIZE_MAPPING: Dict[str, Dict[str, Any]] = {
    "small": {
        "range": [0, 1000],  # 0-1000 KB
        "description": "tiny kitten",
        "prompt_modifier": "small, adorable kitten",
    },
    "medium": {
        "range": [1001, 5000],  # 1-5 MB
        "description": "regular cat",
        "prompt_modifier": "medium-sized, well-proportioned cat",
    },
    "large": {
        "range": [5001, 10000],  # 5-10 MB
        "description": "chonky cat",
        "prompt_modifier": "large, fluffy, chonky cat",
    },
    "very_large": {
        "range": [10001, 999999],  # 10+ MB
        "description": "absolute unit chonker",
        "prompt_modifier": "absolutely massive, legendary chonker cat",
    },
}


# ============================================================================
# CAT AGE MAPPING - Language age + commit history to cat age
# ============================================================================

CAT_AGE_MAPPING: Dict[str, Dict[str, Any]] = {
    "kitten": {
        "description": "baby kitten (0-3 months old)",
        "language_age_range": [0, 3],  # Years since language creation
        "commit_frequency": "high",  # Active development
        "prompt_modifier": "tiny baby kitten with bright curious eyes",
    },
    "young": {
        "description": "young cat (3-12 months old)",
        "language_age_range": [3, 10],  # Years
        "commit_frequency": "medium-high",
        "prompt_modifier": "young energetic cat with playful demeanor",
    },
    "adult": {
        "description": "adult cat (1-7 years old)",
        "language_age_range": [10, 20],  # Years
        "commit_frequency": "medium",
        "prompt_modifier": "mature adult cat with confident posture",
    },
    "senior": {
        "description": "senior cat (7+ years old)",
        "language_age_range": [20, 999],  # Years
        "commit_frequency": "low",
        "prompt_modifier": "wise senior cat with distinguished grey whiskers",
    },
}


# ============================================================================
# CAT EXPRESSION MAPPING - Test coverage + code health to expression
# ============================================================================

CAT_EXPRESSION_MAPPING: Dict[str, Dict[str, Any]] = {
    "happy": {
        "test_coverage_range": [80, 100],  # Percentage
        "code_health": "excellent",
        "description": "purring happily with contentment",
        "prompt_modifier": "happy, smiling, content expression with bright eyes",
    },
    "neutral": {
        "test_coverage_range": [50, 79],  # Percentage
        "code_health": "good",
        "description": "calm and relaxed",
        "prompt_modifier": "neutral, peaceful expression with calm demeanor",
    },
    "concerned": {
        "test_coverage_range": [20, 49],  # Percentage
        "code_health": "needs improvement",
        "description": "slightly worried",
        "prompt_modifier": "concerned, slightly worried expression with furrowed brow",
    },
    "grumpy": {
        "test_coverage_range": [0, 19],  # Percentage
        "code_health": "poor",
        "description": "very grumpy and displeased",
        "prompt_modifier": "grumpy, scowling, displeased expression like Grumpy Cat",
    },
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_language_background(language: str) -> str:
    """
    Get the background theme for a programming language.

    Performs case-insensitive lookup and returns a default background
    for unknown languages.

    Args:
        language: Programming language name (e.g., "Python", "javascript")

    Returns:
        Background description string

    Examples:
        >>> get_language_background("Python")
        'snakes and code snippets in a cozy den'
        >>> get_language_background("PYTHON")
        'snakes and code snippets in a cozy den'
        >>> get_language_background("UnknownLang")
        'a generic code editor with colorful syntax highlighting and binary matrix'
    """
    # Handle None or empty language
    if not language:
        return DEFAULT_BACKGROUND

    # Case-insensitive lookup
    language_normalized = language.strip()

    # Try exact match first
    if language_normalized in LANGUAGE_BACKGROUNDS:
        return LANGUAGE_BACKGROUNDS[language_normalized]

    # Try case-insensitive match
    for lang_key, background in LANGUAGE_BACKGROUNDS.items():
        if lang_key.lower() == language_normalized.lower():
            return background

    # Return default for unknown languages
    return DEFAULT_BACKGROUND


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    "LANGUAGE_BACKGROUNDS",
    "QUALITY_INDICATORS",
    "CAT_SIZE_MAPPING",
    "CAT_AGE_MAPPING",
    "CAT_EXPRESSION_MAPPING",
    "get_language_background",
    "DEFAULT_BACKGROUND",
]
