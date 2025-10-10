"""
Image service for cat attribute mapping and image storage.

This service handles:
1. Mapping code analysis results to cat attributes
2. Creating image generation prompts
3. Saving generated images locally

Functions:
- map_analysis_to_cat_attributes() - Maps analysis → cat attributes
- create_image_prompt() - Creates FLUX.1.1-pro prompt
- save_image_locally() - Saves base64 image to disk
"""
import base64
import logging
from pathlib import Path
from typing import Dict, Any

from config.mappings import (
    CAT_SIZE_MAPPING,
    CAT_AGE_MAPPING,
    CAT_EXPRESSION_MAPPING,
    get_language_background
)

logger = logging.getLogger(__name__)


class ImageServiceError(Exception):
    """Custom exception for image service errors."""
    pass


# ============================================================================
# Function 1: Map Analysis to Cat Attributes
# ============================================================================

def map_analysis_to_cat_attributes(
    metadata: Dict[str, Any],
    analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Map analysis results to cat attributes.

    Uses configuration mappings to determine:
    - Size: Based on repository size
    - Age: Based on code quality (higher quality = more mature)
    - Beauty: Based on code quality score
    - Expression: Based on code quality and test presence
    - Background: Based on primary language

    Args:
        metadata: Repository metadata dict (from GitHub API)
            - size_kb: Repository size in KB
            - primary_language: Primary programming language
        analysis: Code analysis result dict
            - code_quality_score: Quality score (0-10)
            - metrics: Dict with has_tests, etc.

    Returns:
        dict: Cat attributes with keys:
            - size: str (small, medium, large, very_large)
            - age: str (kitten, young, adult, senior)
            - beauty_score: float (0-10)
            - expression: str (happy, neutral, concerned, grumpy)
            - background: str (language-specific background)
            - language: str (primary language)

    Example:
        >>> metadata = {"size_kb": 3000, "primary_language": "Python"}
        >>> analysis = {"code_quality_score": 8.0, "metrics": {"has_tests": True}}
        >>> result = map_analysis_to_cat_attributes(metadata, analysis)
        >>> result["size"]
        'medium'
        >>> result["age"]
        'senior'
    """
    logger.info("Mapping analysis results to cat attributes")

    quality_score = analysis["code_quality_score"]
    repo_size_kb = metadata.get("size_kb", 0)
    primary_language = metadata.get("primary_language", "Unknown")

    # Map size (based on repository size)
    size = "medium"  # default
    for size_key, size_config in CAT_SIZE_MAPPING.items():
        range_min, range_max = size_config["range"]
        if range_min <= repo_size_kb <= range_max:
            size = size_key
            break

    # Map age (based on quality score)
    # Higher quality = more mature codebase = older cat
    age = "young"  # default
    if quality_score >= 8:
        age = "senior"  # Excellent code = wise old cat
    elif quality_score >= 6:
        age = "adult"   # Good code = mature cat
    elif quality_score >= 4:
        age = "young"   # Average code = young cat
    else:
        age = "kitten"  # Poor code = inexperienced kitten

    # Map expression (based on code quality and tests)
    expression = "neutral"  # default
    has_tests = analysis.get("metrics", {}).get("has_tests", False)

    if quality_score >= 8 and has_tests:
        expression = "happy"      # Excellent code with tests
    elif quality_score >= 6:
        expression = "neutral"    # Good code
    elif quality_score >= 4:
        expression = "concerned"  # Mediocre code
    else:
        expression = "grumpy"     # Poor code

    # Map background (based on language)
    background = get_language_background(primary_language)

    # Beauty score is directly the code quality score
    beauty_score = quality_score

    cat_attrs = {
        "size": size,
        "age": age,
        "beauty_score": beauty_score,
        "expression": expression,
        "background": background,
        "language": primary_language
    }

    logger.info(
        f"Cat attributes: {size} {age} cat, "
        f"beauty={beauty_score}, expression={expression}"
    )

    return cat_attrs


# ============================================================================
# Function 2: Create Image Prompt
# ============================================================================

def create_image_prompt(cat_attrs: Dict[str, Any]) -> str:
    """
    Generate image generation prompt for FLUX.1.1-pro.

    Creates a detailed prompt describing the cat based on attributes:
    - Size, age, expression
    - Code quality (beauty)
    - Language-specific background

    Args:
        cat_attrs: Cat attributes dict with keys:
            - size: Cat size (small, medium, large, very_large)
            - age: Cat age (kitten, young, adult, senior)
            - beauty_score: Beauty/quality score (0-10)
            - expression: Cat expression (happy, neutral, concerned, grumpy)
            - background: Background theme

    Returns:
        str: Detailed image generation prompt

    Example:
        >>> cat_attrs = {
        ...     "size": "medium",
        ...     "age": "adult",
        ...     "beauty_score": 7.5,
        ...     "expression": "happy",
        ...     "background": "snakes and code snippets"
        ... }
        >>> prompt = create_image_prompt(cat_attrs)
        >>> "medium" in prompt.lower()
        True
    """
    logger.info("Generating image prompt")

    # Get size description
    size_desc = CAT_SIZE_MAPPING.get(
        cat_attrs["size"], {}
    ).get("prompt_modifier", "cat")

    # Get age description
    age_desc = CAT_AGE_MAPPING.get(
        cat_attrs["age"], {}
    ).get("description", "cat")

    # Get expression description
    expression_desc = CAT_EXPRESSION_MAPPING.get(
        cat_attrs["expression"], {}
    ).get("description", "neutral expression")

    # Get background
    background = cat_attrs["background"]

    # Beauty modifier based on score
    beauty_score = cat_attrs["beauty_score"]
    if beauty_score >= 8:
        beauty_modifier = "beautiful, well-groomed"
    elif beauty_score >= 6:
        beauty_modifier = "pleasant-looking"
    elif beauty_score >= 4:
        beauty_modifier = "ordinary"
    else:
        beauty_modifier = "scruffy, disheveled"

    # Construct prompt
    prompt = (
        f"A {beauty_modifier} {age_desc}, {size_desc} with a {expression_desc}. "
        f"Background: {background}. "
        f"Photorealistic, detailed fur texture, professional photography, 8k quality. "
        f"The cat should look natural and lifelike."
    )

    logger.info(f"Generated prompt: {prompt[:100]}...")

    return prompt


# ============================================================================
# Function 3: Save Image Locally
# ============================================================================

def save_image_locally(base64_data: str, generation_id: str) -> str:
    """
    Save base64-encoded image to local filesystem.

    Creates the generated_images directory if it doesn't exist,
    decodes the base64 image data, and saves it as a PNG file
    with a UUID-based filename.

    Args:
        base64_data: Base64-encoded image string (from Together.ai)
        generation_id: UUID string for filename

    Returns:
        str: Relative path to saved image (e.g., "generated_images/uuid.png")

    Raises:
        ImageServiceError: If image saving fails (permission, invalid data, etc.)

    Example:
        >>> import base64
        >>> image_data = base64.b64encode(b"fake_image").decode("utf-8")
        >>> path = save_image_locally(image_data, "550e8400-e29b-41d4-a716")
        >>> "generated_images" in path
        True
        >>> ".png" in path
        True
    """
    logger.info(f"Saving image locally: {generation_id}")

    # Validation
    if not base64_data or not base64_data.strip():
        raise ImageServiceError("base64_data cannot be empty")

    if not generation_id:
        raise ImageServiceError("generation_id cannot be empty")

    try:
        # Decode base64 to binary
        try:
            image_binary = base64.b64decode(base64_data)
        except Exception as e:
            raise ImageServiceError(f"Failed to decode base64 data: {str(e)}")

        # Define paths
        images_dir = Path("generated_images")
        filename = f"{generation_id}.png"
        file_path = images_dir / filename

        # Create directory if it doesn't exist
        try:
            images_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            raise ImageServiceError(f"Permission denied creating directory: {str(e)}")

        # Write binary data to file
        try:
            with open(file_path, "wb") as f:
                f.write(image_binary)
        except PermissionError as e:
            raise ImageServiceError(f"Permission denied writing file: {str(e)}")
        except Exception as e:
            raise ImageServiceError(f"Failed to write image file: {str(e)}")

        # Return relative path for database storage
        relative_path = f"generated_images/{filename}"

        logger.info(f"Image saved successfully: {relative_path}")

        return relative_path

    except ImageServiceError:
        # Re-raise ImageServiceError as-is
        raise
    except Exception as e:
        # Wrap any other exceptions
        raise ImageServiceError(f"Unexpected error saving image: {str(e)}")


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "map_analysis_to_cat_attributes",
    "create_image_prompt",
    "save_image_locally",
    "ImageServiceError"
]
