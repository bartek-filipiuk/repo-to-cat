"""
Image service for cat attribute mapping and image storage.

This service handles:
1. Mapping code analysis results to cat attributes
2. Creating image generation prompts
3. Saving generated images locally
4. Generating meme text overlays
5. Adding text to images

Functions:
- map_analysis_to_cat_attributes() - Maps analysis → cat attributes
- create_image_prompt() - Creates FLUX.1.1-pro prompt
- save_image_locally() - Saves base64 image to disk
- generate_meme_text() - Generates meme text for overlay
- add_text_to_image() - Adds text overlay to image using PIL
"""
import base64
import logging
from pathlib import Path
from typing import Dict, Any, Tuple
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

from config.mappings import (
    CAT_SIZE_MAPPING,
    CAT_AGE_MAPPING,
    CAT_EXPRESSION_MAPPING,
    CAT_BREED_MAPPING,
    get_language_background,
    get_cat_breed
)
from app.core.config import settings

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
# Function 1.5: Add Creative Spice
# ============================================================================

def add_creative_spice(base_prompt: str, quality_score: float) -> str:
    """
    Enhance base image prompt with creative, cinematic details using LLM.

    Adds stylized elements to cat and makes background more dramatic/cinematic
    based on code quality score. Uses LLM for maximum creativity.

    Args:
        base_prompt: Basic cat description (size, breed, expression, background)
        quality_score: Code quality score (0-10)

    Returns:
        str: Enhanced prompt with creative details

    Example:
        >>> base = "A medium, adult Tabby cat with neutral expression, coffee shop background"
        >>> enhanced = add_creative_spice(base, 8.5)
        >>> "glowing" in enhanced or "cyber" in enhanced or "dramatic" in enhanced
        True
    """
    from app.providers.openrouter import OpenRouterProvider

    logger.info(f"Adding creative spice to prompt (quality: {quality_score})")

    # Determine environment vibe based on quality
    if quality_score >= 9:
        vibe = "epic, majestic, powerful"
    elif quality_score >= 7:
        vibe = "professional, elegant, accomplished"
    elif quality_score >= 5:
        vibe = "decent, functional, ordinary"
    elif quality_score >= 3:
        vibe = "chaotic, messy, concerning"
    else:
        vibe = "disaster, apocalyptic, terrible"

    enhancement_prompt = f"""Enhance this cat image prompt with creative, cinematic details:

BASE PROMPT: {base_prompt}

CODE QUALITY VIBE: {vibe} ({quality_score}/10)

Your task:
1. Add stylized elements to the cat (examples: glowing patterns, geometric shapes, cyber details, ethereal aura, crystalline features, neon accents)
2. Transform the background into a cinematic, dramatic scene matching the quality vibe
3. Keep it concise (2-3 sentences total)
4. Make it movie-like and memorable

Return only the enhanced prompt, nothing else."""

    try:
        openrouter = OpenRouterProvider()
        response = openrouter.generate_text(
            prompt=enhancement_prompt,
            system_message="You are a creative director for dramatic, cinematic cat portraits. Add creative flair while keeping descriptions concise.",
            temperature=1.0,  # Maximum creativity
            max_tokens=150
        )

        enhanced = response.strip()
        logger.info(f"Enhanced prompt generated: {enhanced[:100]}...")
        return enhanced

    except Exception as e:
        logger.warning(f"Failed to enhance prompt with LLM: {str(e)}, using base prompt")
        return base_prompt


# ============================================================================
# Function 2: Create Image Prompt
# ============================================================================

def create_image_prompt(cat_attrs: Dict[str, Any]) -> str:
    """
    Generate image generation prompt for FLUX.1.1-pro.

    Creates a detailed prompt describing the cat based on attributes:
    - Size, age, expression
    - Breed (based on programming language)
    - Code quality (beauty)
    - Language-specific background

    Args:
        cat_attrs: Cat attributes dict with keys:
            - size: Cat size (small, medium, large, very_large)
            - age: Cat age (kitten, young, adult, senior)
            - beauty_score: Beauty/quality score (0-10)
            - expression: Cat expression (happy, neutral, concerned, grumpy)
            - background: Background theme
            - language: Programming language (for breed selection)

    Returns:
        str: Detailed image generation prompt

    Example:
        >>> cat_attrs = {
        ...     "size": "medium",
        ...     "age": "adult",
        ...     "beauty_score": 7.5,
        ...     "expression": "happy",
        ...     "background": "snakes and code snippets",
        ...     "language": "Python"
        ... }
        >>> prompt = create_image_prompt(cat_attrs)
        >>> "tabby" in prompt.lower()
        True
    """
    logger.info("Generating image prompt")

    # Get breed based on language
    language = cat_attrs.get("language", "Unknown")
    breed_key = get_cat_breed(language)
    breed_desc = CAT_BREED_MAPPING[breed_key]["prompt_modifier"]

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

    # Construct base prompt with breed
    base_prompt = (
        f"A {beauty_modifier} {age_desc}, {size_desc} {breed_desc} with a {expression_desc}. "
        f"Background: {background}."
    )

    # Add creative spice with LLM
    enhanced_prompt = add_creative_spice(base_prompt, beauty_score)

    # Add technical details
    final_prompt = (
        f"{enhanced_prompt} "
        f"Photorealistic, cinematic lighting, dramatic composition, detailed fur texture, 8k quality."
    )

    logger.info(f"Generated enhanced prompt ({breed_key} breed): {final_prompt[:100]}...")

    return final_prompt


# ============================================================================
# Function 3: Save Image Locally
# ============================================================================

def save_image_locally(base64_data: str, generation_id: str) -> str:
    """
    Save base64-encoded image to local filesystem.

    Uses settings.IMAGE_STORAGE_PATH for the storage directory,
    decodes the base64 image data, and saves it as a PNG file
    with a UUID-based filename.

    Args:
        base64_data: Base64-encoded image string (from Together.ai)
        generation_id: UUID string for filename

    Returns:
        str: Absolute URL path to image (e.g., "/generated_images/uuid.png")

    Raises:
        ImageServiceError: If image saving fails (permission, invalid data, etc.)

    Example:
        >>> import base64
        >>> image_data = base64.b64encode(b"fake_image").decode("utf-8")
        >>> path = save_image_locally(image_data, "550e8400-e29b-41d4-a716")
        >>> path.startswith("/")
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

        # Define paths using settings
        images_dir = Path(settings.IMAGE_STORAGE_PATH)
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

        # Return absolute URL path (with leading slash for API serving)
        url_path = f"/generated_images/{filename}"

        logger.info(f"Image saved successfully to {file_path}, URL: {url_path}")

        return url_path

    except ImageServiceError:
        # Re-raise ImageServiceError as-is
        raise
    except Exception as e:
        # Wrap any other exceptions
        raise ImageServiceError(f"Unexpected error saving image: {str(e)}")


# ============================================================================
# Function 4: Generate Meme Text
# ============================================================================

def generate_meme_text(
    metadata: Dict[str, Any],
    analysis: Dict[str, Any],
    cat_attrs: Dict[str, Any],
    openrouter_provider
) -> Tuple[str, str]:
    """
    Generate meme-style text for image overlay using LLM with example-based prompting.

    Creates funny, short (3-8 words) text for top and bottom of image.
    Uses 100% LLM generation with curated examples for style inspiration,
    ensuring unique, context-aware content every time.

    Args:
        metadata: Repository metadata dict
            - name: Repository name
            - owner: Repository owner
            - primary_language: Main language
            - language_breakdown: List of language percentages
            - size_kb: Size in KB
            - stars: GitHub stars count
        analysis: Code analysis results dict
            - code_quality_score: Quality score (0-10)
            - metrics: Dict with has_tests, etc.
        cat_attrs: Cat attributes dict
            - expression: Cat expression
            - size: Cat size
        openrouter_provider: OpenRouter API provider instance

    Returns:
        Tuple[str, str]: (top_text, bottom_text) - both uppercase, 3-8 words each

    Example:
        >>> metadata = {"name": "react", "owner": "facebook", "primary_language": "JavaScript"}
        >>> analysis = {"code_quality_score": 9.0, "metrics": {"has_tests": True}}
        >>> cat_attrs = {"expression": "happy", "size": "large"}
        >>> top, bottom = generate_meme_text(metadata, analysis, cat_attrs, provider)
        >>> len(top.split()) <= 8
        True
    """
    logger.info("Generating LLM-based meme text for image overlay")

    # Extract repository context
    repo_name = metadata.get("name", "Unknown")
    owner = metadata.get("owner", "Unknown")
    language = metadata.get("primary_language", "Unknown")
    stars = metadata.get("stars", 0)
    language_breakdown = metadata.get("language_breakdown", [])

    # Extract metrics
    quality_score = analysis.get("code_quality_score", 5.0)
    has_tests = analysis.get("metrics", {}).get("has_tests", False)
    expression = cat_attrs.get("expression", "neutral")
    size = cat_attrs.get("size", "medium")

    # Determine code health description
    if quality_score >= 8:
        health = "Excellent ✓"
    elif quality_score >= 6:
        health = "Good"
    elif quality_score >= 4:
        health = "Needs Work"
    else:
        health = "Spaghetti Code"

    # Build language context
    lang_context = f"Primary Language: {language}"
    if language_breakdown and len(language_breakdown) > 1:
        langs_str = ", ".join([
            f"{item['language']} ({item['percentage']}%)"
            for item in language_breakdown[:3]  # Top 3
        ])
        lang_context = f"Languages: {langs_str}"

    # Build enhanced prompt (format-focused, no content examples)
    prompt = f"""Generate meme text for GitHub repository: {owner}/{repo_name}

REPOSITORY CONTEXT:
- Repository: {owner}/{repo_name}
- Stars: {stars:,}
- {lang_context}
- Code Quality Score: {quality_score}/10
- Code Health: {health}
- Has Tests: {"Yes ✓" if has_tests else "No ✗"}

FORMAT REQUIREMENTS:
- Generate TWO text phrases: TOP and BOTTOM
- Each phrase: 2-8 words (keep it punchy!)
- ALL UPPERCASE letters
- Use this exact format:
  TOP: [your text]
  BOTTOM: [your text]

STYLE GUIDELINES:
- Energetic programmer humor with creative internet slang
- Reference the actual repository language, name, or code quality
- Friendly roast tone (funny but not mean)
- Be HIGHLY CREATIVE - never repeat the same phrases
- Use varied, unexpected combinations

HUMOR THEMES (be creative, don't copy these literally):
- Language jokes: Reference language-specific concepts (imports, types, syntax quirks)
- Code quality: Match the vibe to the score (8+: proud/epic, 6-7: decent, 4-5: messy, <4: disaster)
- Testing: Has tests = confident/professional, No tests = risky/chaotic
- Repository specific: Use the actual repo name, owner, or language in creative ways

CREATIVE VARIETY:
- Mix technical terms with humor
- Use metaphors and comparisons
- Play with code concepts (compile, deploy, debug, refactor)
- Internet culture (but vary it - don't repeat the same slang)
- Keep it fresh and unexpected

IMPORTANT: Every meme should be UNIQUE. Avoid repeating phrases across generations. Think outside the box!

Generate meme text in this EXACT format:
TOP: [your creative text here]
BOTTOM: [your punchline here]"""

    try:
        # Call OpenRouter with higher temperature for creativity
        response = openrouter_provider.generate_text(
            prompt=prompt,
            system_message="You are a hilarious meme text generator who creates funny, energetic programmer humor. Use internet slang and be creative!",
            temperature=0.9,  # Higher temperature for more variety
            max_tokens=150  # Allow more space for creative responses
        )

        # Parse response
        lines = [line.strip() for line in response.strip().split('\n') if line.strip()]

        top_text = ""
        bottom_text = ""

        for line in lines:
            if line.startswith("TOP:"):
                top_text = line.replace("TOP:", "").strip().upper()
            elif line.startswith("BOTTOM:"):
                bottom_text = line.replace("BOTTOM:", "").strip().upper()

        # Validate
        if not top_text or not bottom_text:
            raise ValueError("Could not parse TOP and BOTTOM from response")

        logger.info(f"Generated meme text - TOP: '{top_text}', BOTTOM: '{bottom_text}'")
        return (top_text, bottom_text)

    except Exception as e:
        logger.error(f"Failed to generate meme text: {str(e)}")
        # Fallback meme text
        lang_text = language.upper() if language else "CODE"
        top_text = f"{lang_text} REPO"
        bottom_text = "SUCH QUALITY" if quality_score >= 7 else "NEEDS WORK" if quality_score >= 4 else "OH NO"
        logger.warning(f"Using fallback meme text: {top_text} / {bottom_text}")
        return (top_text, bottom_text)


# ============================================================================
# Function 5: Add Text to Image
# ============================================================================

def add_text_to_image(
    image_bytes: bytes,
    top_text: str,
    bottom_text: str,
    font_size: int = 60,
    stroke_width: int = 4
) -> bytes:
    """
    Add meme-style text overlay to image using PIL with dynamic font sizing.

    Draws white text with black outline at top and bottom of image,
    centered horizontally. Font size adjusts based on text length:
    - Short text (≤20 chars): 60px
    - Medium text (21-35 chars): 45px
    - Long text (>35 chars): 30px

    Args:
        image_bytes: Image data as bytes
        top_text: Text for top (will be uppercased)
        bottom_text: Text for bottom (will be uppercased)
        font_size: Base font size in points (default: 60, auto-adjusted)
        stroke_width: Width of black outline (default: 4)

    Returns:
        bytes: Modified image as bytes

    Raises:
        ImageServiceError: If image processing fails

    Example:
        >>> with open("test.png", "rb") as f:
        ...     img_bytes = f.read()
        >>> result = add_text_to_image(img_bytes, "TOP TEXT", "BOTTOM TEXT")
        >>> len(result) > 0
        True
    """
    logger.info(f"Adding text overlay - TOP: '{top_text}', BOTTOM: '{bottom_text}'")

    try:
        # Load image from bytes
        img = Image.open(BytesIO(image_bytes))
        width, height = img.size

        # Create drawing context
        draw = ImageDraw.Draw(img)

        # Convert text to uppercase
        top_text = top_text.upper()
        bottom_text = bottom_text.upper()

        # Calculate dynamic font size for top text
        top_length = len(top_text)
        if top_length <= 15:
            top_font_size = 60
        elif top_length <= 25:
            top_font_size = 45
        elif top_length <= 35:
            top_font_size = 35
        else:
            top_font_size = 28

        # Calculate dynamic font size for bottom text
        bottom_length = len(bottom_text)
        if bottom_length <= 15:
            bottom_font_size = 60
        elif bottom_length <= 25:
            bottom_font_size = 45
        elif bottom_length <= 35:
            bottom_font_size = 35
        else:
            bottom_font_size = 28

        logger.info(f"Font sizes - TOP: {top_font_size}px ({top_length} chars), BOTTOM: {bottom_font_size}px ({bottom_length} chars)")

        # Load fonts with calculated sizes
        top_font = _find_font("impact.ttf", top_font_size)
        bottom_font = _find_font("impact.ttf", bottom_font_size)

        # Draw top text
        if top_text:
            bbox = draw.textbbox((0, 0), top_text, font=top_font)
            text_width = bbox[2] - bbox[0]
            # Account for stroke width (adds pixels on both sides)
            total_width = text_width + (stroke_width * 2)

            # Ensure text fits within image bounds with margin
            margin = int(width * 0.02)  # 2% margin on each side
            available_width = width - (margin * 2)

            if total_width > available_width:
                # Reduce font size to fit
                scale_factor = available_width / total_width
                top_font_size = int(top_font_size * scale_factor)
                top_font = _find_font("impact.ttf", top_font_size)
                bbox = draw.textbbox((0, 0), top_text, font=top_font)
                text_width = bbox[2] - bbox[0]
                logger.info(f"TOP text scaled down to {top_font_size}px to fit")

            top_x = (width - text_width) // 2
            top_y = int(height * 0.05)

            draw.text(
                (top_x, top_y),
                top_text,
                font=top_font,
                fill="white",
                stroke_width=stroke_width,
                stroke_fill="black"
            )

        # Draw bottom text
        if bottom_text:
            bbox = draw.textbbox((0, 0), bottom_text, font=bottom_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            # Account for stroke width (adds pixels on both sides)
            total_width = text_width + (stroke_width * 2)

            # Ensure text fits within image bounds with margin
            margin = int(width * 0.02)  # 2% margin on each side
            available_width = width - (margin * 2)

            if total_width > available_width:
                # Reduce font size to fit
                scale_factor = available_width / total_width
                bottom_font_size = int(bottom_font_size * scale_factor)
                bottom_font = _find_font("impact.ttf", bottom_font_size)
                bbox = draw.textbbox((0, 0), bottom_text, font=bottom_font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                logger.info(f"BOTTOM text scaled down to {bottom_font_size}px to fit")

            bottom_x = (width - text_width) // 2
            bottom_y = height - text_height - int(height * 0.08)

            draw.text(
                (bottom_x, bottom_y),
                bottom_text,
                font=bottom_font,
                fill="white",
                stroke_width=stroke_width,
                stroke_fill="black"
            )

        # Convert back to bytes
        output = BytesIO()
        img.save(output, format="PNG")
        result_bytes = output.getvalue()

        logger.info(f"Text overlay added successfully ({len(result_bytes)} bytes)")
        return result_bytes

    except Exception as e:
        logger.error(f"Failed to add text overlay: {str(e)}")
        raise ImageServiceError(f"Text overlay failed: {str(e)}")


def _find_font(font_name: str, font_size: int):
    """
    Find and load a font, trying multiple common locations.

    Args:
        font_name: Font filename (e.g., "impact.ttf")
        font_size: Font size in points

    Returns:
        ImageFont object
    """
    # Common font paths
    font_paths = [
        f"/usr/share/fonts/truetype/msttcorefonts/{font_name}",
        f"/usr/share/fonts/TTF/{font_name}",
        f"/usr/share/fonts/truetype/{font_name}",
        f"/System/Library/Fonts/{font_name}",  # macOS
        f"C:\\Windows\\Fonts\\{font_name}",     # Windows
    ]

    # Try each path
    for font_path in font_paths:
        try:
            return ImageFont.truetype(font_path, font_size)
        except (OSError, IOError):
            continue

    # Try without path
    try:
        return ImageFont.truetype(font_name, font_size)
    except (OSError, IOError):
        pass

    # Fallback to DejaVu Sans Bold (widely available, supports sizing)
    fallback_fonts = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",  # macOS
        "C:\\Windows\\Fonts\\arialbd.ttf",      # Windows Arial Bold
    ]

    for fallback in fallback_fonts:
        try:
            logger.warning(f"Could not find {font_name}, using fallback: {fallback}")
            return ImageFont.truetype(fallback, font_size)
        except (OSError, IOError):
            continue

    # Last resort: default font (fixed size, doesn't respect font_size)
    logger.error(f"No TrueType fonts found, using fixed-size default font")
    return ImageFont.load_default()


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "map_analysis_to_cat_attributes",
    "create_image_prompt",
    "save_image_locally",
    "generate_meme_text",
    "add_text_to_image",
    "ImageServiceError"
]
