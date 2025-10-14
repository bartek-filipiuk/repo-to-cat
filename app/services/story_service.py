"""
Story generation service for creating funny repository narratives.

This service generates 3-5 sentence humorous stories about repositories
based on their metadata, code analysis, and cat attributes. Uses OpenRouter
with Google Gemini 2.5 Flash for creative text generation.

Functions:
- generate_repository_story() - Creates funny story about repo
"""
import logging
from typing import Dict, Any

from app.providers.openrouter import OpenRouterProvider

logger = logging.getLogger(__name__)


class StoryServiceError(Exception):
    """Custom exception for story service errors."""
    pass


def generate_repository_story(
    metadata: Dict[str, Any],
    analysis: Dict[str, Any],
    cat_attrs: Dict[str, Any],
    openrouter_provider: OpenRouterProvider
) -> str:
    """
    Generate a funny, friendly roast story about a GitHub repository.

    Creates a 3-5 sentence humorous narrative that describes the repository
    as a cat character. The tone is playful and friendly, never harsh.

    Args:
        metadata: Repository metadata dict
            - name: Repository name
            - owner: Repository owner
            - primary_language: Main language
            - size_kb: Size in KB
            - stars: GitHub stars count
        analysis: Code analysis results dict
            - code_quality_score: Quality score (0-10)
            - metrics: Dict with has_tests, etc.
        cat_attrs: Cat attributes dict
            - size: Cat size (small, medium, large, very_large)
            - age: Cat age (kitten, young, adult, senior)
            - expression: Cat expression (happy, neutral, concerned, grumpy)
            - beauty_score: Beauty score (0-10)
        openrouter_provider: OpenRouter API provider instance

    Returns:
        str: Funny 3-5 sentence story about the repository

    Raises:
        StoryServiceError: If story generation fails

    Example:
        >>> metadata = {"name": "Hello-World", "primary_language": "Unknown", "size_kb": 1}
        >>> analysis = {"code_quality_score": 5.6, "metrics": {"has_tests": False}}
        >>> cat_attrs = {"size": "small", "age": "young", "expression": "concerned"}
        >>> story = generate_repository_story(metadata, analysis, cat_attrs, provider)
        >>> len(story) > 100
        True
    """
    logger.info(f"Generating story for repository: {metadata.get('name', 'Unknown')}")

    # Extract relevant info
    repo_name = metadata.get("name", "Unknown")
    owner = metadata.get("owner", "Unknown")
    language = metadata.get("primary_language", "Unknown")
    size_kb = metadata.get("size_kb", 0)
    stars = metadata.get("stars", 0)
    quality_score = analysis.get("code_quality_score", 5.0)
    has_tests = analysis.get("metrics", {}).get("has_tests", False)

    # Cat personality
    cat_size = cat_attrs.get("size", "medium")
    cat_age = cat_attrs.get("age", "young")
    cat_expression = cat_attrs.get("expression", "neutral")

    # Map cat attributes to personality traits
    size_personality = {
        "small": "tiny, inexperienced",
        "medium": "average-sized, ordinary",
        "large": "chunky, well-established",
        "very_large": "massive, legendary"
    }.get(cat_size, "ordinary")

    age_personality = {
        "kitten": "baby kitten who's still learning the ropes",
        "young": "young cat with some growing up to do",
        "adult": "mature cat who knows its way around",
        "senior": "wise old cat with years of experience"
    }.get(cat_age, "cat")

    expression_meaning = {
        "happy": "purring with satisfaction",
        "neutral": "calmly observing its domain",
        "concerned": "looking worried about its life choices",
        "grumpy": "scowling at everyone who looks its way"
    }.get(cat_expression, "neutral")

    # Build prompt for OpenRouter
    prompt = f"""Generate a funny, friendly 3-5 sentence story about this GitHub repository as if it were a cat.

Repository Details:
- Name: {owner}/{repo_name}
- Language: {language}
- Size: {size_kb} KB
- Stars: {stars}
- Code Quality: {quality_score}/10
- Has Tests: {"Yes" if has_tests else "No"}

Cat Personality:
- This is a {size_personality} {age_personality}
- Expression: {expression_meaning}
- Quality interpretation: {"excellent code" if quality_score >= 8 else "decent code" if quality_score >= 6 else "questionable code" if quality_score >= 4 else "spaghetti code"}

Writing Style:
- Tone: Funny, friendly roast - playful but NOT mean or harsh
- Length: 3-5 sentences
- Style: Meme-friendly, relatable programmer humor
- Focus: Connect the cat's personality to the code quality and repository characteristics
- Avoid: Harsh insults, profanity, or mean-spirited comments

Example style:
"The {repo_name} repository is like a {age_personality} that just discovered what {language} is. Despite {expression_meaning}, this {size_personality} creature has somehow accumulated {stars} stars from sympathetic onlookers. Its code quality of {quality_score}/10 suggests it's {'living its best life' if quality_score >= 7 else 'still figuring things out' if quality_score >= 5 else 'having a bit of an identity crisis'}."

Generate a similarly funny but kind story:"""

    try:
        # Call OpenRouter to generate story
        story = openrouter_provider.generate_text(
            prompt=prompt,
            system_message="You are a witty technical writer who creates funny, friendly roasts about code repositories. Your tone is playful and humorous, never mean or harsh.",
            temperature=0.9,  # Higher temperature for more creativity
            max_tokens=300
        )

        logger.info(f"Story generated successfully: {len(story)} characters")
        return story.strip()

    except Exception as e:
        logger.error(f"Failed to generate story: {str(e)}")
        # Fallback story if generation fails
        fallback = (
            f"The {repo_name} repository is a {age_personality} {expression_meaning}. "
            f"With a code quality score of {quality_score}/10, this {size_personality} feline "
            f"{'confidently struts around' if quality_score >= 7 else 'nervously tiptoes through its codebase' if quality_score >= 4 else 'stumbles around wondering where it all went wrong'}. "
            f"{'Tests? Never heard of them.' if not has_tests else 'At least it has tests!'}"
        )
        logger.warning(f"Using fallback story due to error: {str(e)}")
        return fallback


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "generate_repository_story",
    "StoryServiceError"
]
