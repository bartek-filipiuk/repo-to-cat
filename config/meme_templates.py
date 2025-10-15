"""
Meme text examples for LLM-based generation.

This module provides curated examples of high-quality meme text
to inspire the LLM's style and humor. These are NOT templates to be
randomly selected - they serve as reference examples in the prompt.

The LLM generates 100% of meme text, using these examples to understand:
- Desired tone and energy
- Programming humor style
- Internet slang usage
- Format and length
"""

from typing import List, Tuple


# ============================================================================
# BEST MEME EXAMPLES - For LLM Style Reference
# ============================================================================

MEME_EXAMPLES: List[Tuple[str, str, str]] = [
    # (top_text, bottom_text, context)

    # Python Examples (5)
    ("DEF SPAGHETTI", "RETURN MEATBALLS", "Python poor quality"),
    ("FROM IMPORT STAR", "FROM CHAOS IMPORT EVERYTHING", "Python poor imports"),
    ("ASYNC AWAIT MASTERY", "EVENT LOOP GO BRRRR", "Python excellent async code"),
    ("ZERO WARNINGS", "PYLINT GAVE UP LOOKING", "Python excellent quality"),
    ("GLOBAL VARIABLES", "GLOBAL PROBLEMS", "Python poor practices"),

    # JavaScript Examples (5)
    ("NODE MODULES", "500MB OF SOMEONE ELSES PROBLEM", "JavaScript dependency hell"),
    ("UNDEFINED IS NOT A FUNCTION", "STORY OF MY LIFE FR", "JavaScript runtime errors"),
    ("THIS DOT PROPS", "UNDEFINED DOT PROPS DOT BOOM", "JavaScript undefined chaos"),
    ("VAR EVERYWHERE", "LET CONST LEFT THE CHAT", "JavaScript old style"),
    ("PROMISE ALL SETTLED", "NO REJECTIONS ALLOWED", "JavaScript excellent async"),

    # Rust Examples (5)
    ("IF IT COMPILES", "IT WORKS TRUST ME BRO", "Rust excellent type safety"),
    ("UNWRAP EVERYWHERE", "PANIC IS MY FRIEND", "Rust poor error handling"),
    ("ZERO COST ABSTRACTIONS", "BLAZINGLY FAST GO BRRRR", "Rust performance"),
    ("MUT MUT MUT", "IMMUTABILITY LEFT THE CHAT", "Rust poor mutability"),
    ("LIFETIME ANNOTATIONS", "MORE LIKE LIFETIME ABOMINATIONS", "Rust complexity"),

    # Go Examples (5)
    ("UNDERSCORE ERR", "UNDERSCORE UNDERSCORE UNDERSCORE", "Go error ignoring"),
    ("IF ERR NIL YOLO", "PANIC EVERYWHERE OH NO", "Go poor error handling"),
    ("GO ROUTINES LEAK", "MEMORY LEAK SPEEDRUN ANY PERCENT", "Go concurrency bugs"),
    ("DEFER PANIC RECOVER", "THE HOLY TRINITY", "Go excellent patterns"),
    ("NO GENERICS", "WHO NEEDS EM ANYWAY", "Go simplicity"),

    # Java Examples (5)
    ("FACTORY FACTORY", "FACTORY FACTORY FACTORY", "Java design patterns"),
    ("NULL POINTER", "MY OLD FRIEND HELLO DARKNESS", "Java null exceptions"),
    ("INSTANCEOF EVERYWHERE", "POLYMORPHISM LEFT THE CHAT", "Java poor OOP"),
    ("ABSTRACT FACTORY", "FACTORY FACTORY FACTORY", "Java enterprise patterns"),
    ("EXCEPTION CATCH ALL", "CATCH EXCEPTION E DO NOTHING", "Java poor error handling"),

    # Generic Examples (5)
    ("WORKS ON MY MACHINE", "SHIP THE MACHINE", "Generic deployment humor"),
    ("TECHNICAL DEBT", "TECHNICAL BANKRUPTCY", "Generic code quality"),
    ("YOLO MODE", "ACTIVATED", "Generic no tests"),
    ("PRODUCTION IS TEST", "YOLO DEPLOYMENT ACTIVATED", "Generic testing humor"),
    ("NO TESTS", "NO MERCY NO REGRETS NO HOPE", "Generic no testing"),
]


def format_examples_for_prompt(language: str = None, limit: int = 15) -> str:
    """
    Format meme examples for inclusion in LLM prompt.

    Returns a formatted string of examples to show the LLM the desired style.
    If language is specified, prioritizes examples from that language family.

    Args:
        language: Programming language to prioritize (optional)
        limit: Maximum number of examples to include (default: 15)

    Returns:
        Formatted string of examples

    Example:
        >>> format_examples_for_prompt("Python", 5)
        'TOP: "DEF SPAGHETTI" / BOTTOM: "RETURN MEATBALLS"\\nTOP: "FROM IMPORT STAR" / ...'
    """
    # Map language to keywords for prioritization
    language_keywords = {
        "Python": ["Python", "python"],
        "JavaScript": ["JavaScript", "JS", "javascript"],
        "TypeScript": ["JavaScript", "JS", "typescript"],
        "Rust": ["Rust", "rust"],
        "Go": ["Go", "go"],
        "Java": ["Java", "java"],
        "C#": ["Java", "java"],  # Use Java examples for C#
        "Kotlin": ["Java", "kotlin"],
        "Scala": ["Java", "scala"],
    }

    # Prioritize examples based on language
    prioritized = []
    other = []

    keywords = language_keywords.get(language, [])

    for top, bottom, context in MEME_EXAMPLES:
        # Check if example is relevant to language
        is_relevant = any(kw.lower() in context.lower() for kw in keywords) if keywords else False

        if is_relevant:
            prioritized.append((top, bottom, context))
        else:
            other.append((top, bottom, context))

    # Combine: prioritized first, then others, up to limit
    selected = (prioritized + other)[:limit]

    # Format as string
    formatted_lines = []
    for top, bottom, context in selected:
        formatted_lines.append(f'TOP: "{top}" / BOTTOM: "{bottom}"')

    return "\n".join(formatted_lines)


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    "MEME_EXAMPLES",
    "format_examples_for_prompt",
]
