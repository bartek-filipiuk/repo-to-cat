"""
Workflow nodes for LangGraph repository analysis pipeline.

Each node function processes the WorkflowState, performs a specific task,
and returns a dictionary with state updates.

Nodes:
1. extract_metadata_node - Fetch repository metadata from GitHub
2. select_files_node - Select strategic files for analysis
3. fetch_files_node - Fetch file contents from GitHub
4. analyze_code_node - Analyze code quality using heuristics + LLM
5. map_attributes_node - Map analysis results to cat attributes
6. generate_prompt_node - Create image generation prompt
7. generate_image_node - Generate cat image using Together.ai
8. save_to_db_node - Save generation results to database
"""

import logging
import uuid
from typing import Dict, Any
from datetime import datetime

from app.langgraph.state import WorkflowState
from app.services.github_service import (
    get_repository_metadata,
    get_file_tree,
    select_strategic_files,
    fetch_file_contents
)
from app.services.analysis_service import AnalysisService
from app.providers.openrouter import OpenRouterProvider
from app.providers.together_ai import TogetherProvider
from app.core.database import SessionLocal
from app.models.database import Generation
from config.mappings import (
    LANGUAGE_BACKGROUNDS,
    DEFAULT_BACKGROUND,
    CAT_SIZE_MAPPING,
    CAT_AGE_MAPPING,
    CAT_EXPRESSION_MAPPING,
    get_language_background
)
from app.core.config import settings

logger = logging.getLogger(__name__)


# ============================================================================
# Node 1: Extract Metadata
# ============================================================================

def extract_metadata_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Extract repository metadata from GitHub.

    Fetches basic repository information including name, owner, size,
    stars, and primary language using GitHub API.

    Args:
        state: Current workflow state (requires github_url)

    Returns:
        dict: State update with metadata field

    Raises:
        ValueError: If GitHub URL is invalid
        GithubException: If repository not found or access denied
    """
    logger.info(f"Extracting metadata for {state['github_url']}")

    metadata = get_repository_metadata(state["github_url"])

    logger.info(f"Metadata extracted: {metadata['name']} ({metadata['primary_language']})")

    return {"metadata": metadata}


# ============================================================================
# Node 2: Select Files
# ============================================================================

def select_files_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Select strategic files for code analysis.

    Uses file selection strategy to pick representative files:
    - README files
    - Main entry points
    - Core source files
    - Test files
    - Configuration files

    Args:
        state: Current workflow state (requires github_url)

    Returns:
        dict: State update with files field (list of file paths)

    Raises:
        GithubException: If repository access fails
    """
    logger.info("Selecting strategic files for analysis")

    # Get file tree
    file_tree = get_file_tree(state["github_url"])

    # Select strategic files (returns list of paths)
    selected_files = select_strategic_files(file_tree)

    logger.info(f"Selected {len(selected_files)} files for analysis")

    return {"files": selected_files}


# ============================================================================
# Node 3: Fetch Files
# ============================================================================

def fetch_files_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Fetch file contents from GitHub.

    Downloads the actual content of selected files using GitHub Contents API.
    Handles binary file detection and large file truncation.

    Args:
        state: Current workflow state (requires github_url and files)

    Returns:
        dict: State update with files field (updated with content)

    Raises:
        GithubException: If file fetch fails
    """
    logger.info(f"Fetching contents for {len(state['files'])} files")

    # Fetch file contents (returns list of dicts with path, content, language)
    files_with_content = fetch_file_contents(
        state["github_url"],
        state["files"]
    )

    logger.info(f"Fetched {len(files_with_content)} file contents")

    return {"files": files_with_content}


# ============================================================================
# Node 4: Analyze Code
# ============================================================================

def analyze_code_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Analyze code quality using heuristics and LLM.

    Combines:
    - Heuristic analysis (30%): line length, function length, complexity
    - LLM analysis (70%): readability, maintainability, best practices

    Args:
        state: Current workflow state (requires files with content)

    Returns:
        dict: State update with analysis field

    Raises:
        APIError: If OpenRouter API call fails
    """
    logger.info("Analyzing code quality")

    # Create analysis service
    openrouter = OpenRouterProvider()
    analysis_service = AnalysisService(openrouter_provider=openrouter)

    # Analyze code files
    analysis_result = analysis_service.analyze_code_files(
        code_files=state["files"],
        primary_language=state["metadata"].get("primary_language", "Unknown")
    )

    # Convert AnalysisResult (Pydantic model) to dict
    analysis_dict = analysis_result.model_dump()

    logger.info(f"Code quality score: {analysis_dict['code_quality_score']}")

    return {"analysis": analysis_dict}


# ============================================================================
# Node 5: Map Attributes
# ============================================================================

def map_attributes_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Map analysis results to cat attributes.

    Uses configuration mappings to determine:
    - Size: Based on repository size
    - Age: Based on primary language
    - Beauty: Based on code quality score
    - Expression: Based on code quality and test presence
    - Background: Based on primary language

    Args:
        state: Current workflow state (requires metadata and analysis)

    Returns:
        dict: State update with cat_attrs field
    """
    logger.info("Mapping analysis results to cat attributes")

    metadata = state["metadata"]
    analysis = state["analysis"]
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

    # Map age (simplified for MVP - based on quality score)
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
    # For MVP, use quality score directly
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

    logger.info(f"Cat attributes: {size} {age} cat, beauty={beauty_score}, expression={expression}")

    return {"cat_attrs": cat_attrs}


# ============================================================================
# Node 6: Generate Prompt
# ============================================================================

def generate_prompt_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Generate image generation prompt for FLUX.1.1-pro.

    Creates a detailed prompt describing the cat based on attributes:
    - Size, age, expression
    - Code quality (beauty)
    - Language-specific background

    Args:
        state: Current workflow state (requires cat_attrs)

    Returns:
        dict: State update with cat_attrs containing 'prompt' field
    """
    logger.info("Generating image prompt")

    cat_attrs = state["cat_attrs"]

    # Get size description
    size_desc = CAT_SIZE_MAPPING.get(cat_attrs["size"], {}).get("prompt_modifier", "cat")

    # Get age description
    age_desc = CAT_AGE_MAPPING.get(cat_attrs["age"], {}).get("description", "cat")

    # Get expression description
    expression_desc = CAT_EXPRESSION_MAPPING.get(cat_attrs["expression"], {}).get("description", "neutral expression")

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

    # Update cat_attrs with prompt
    updated_cat_attrs = {**cat_attrs, "prompt": prompt}

    logger.info(f"Generated prompt: {prompt[:100]}...")

    return {"cat_attrs": updated_cat_attrs}


# ============================================================================
# Node 7: Generate Image
# ============================================================================

def generate_image_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Generate cat image using Together.ai FLUX.1.1-pro.

    Calls Together.ai API with the generated prompt to create a cat image
    reflecting the code quality.

    Args:
        state: Current workflow state (requires cat_attrs with prompt)

    Returns:
        dict: State update with image field (url, binary, prompt)

    Raises:
        ImageGenerationError: If image generation fails
    """
    logger.info("Generating cat image")

    together = TogetherProvider()
    prompt = state["cat_attrs"]["prompt"]

    # Generate image (returns tuple of (url, base64_binary))
    image_url, image_binary = together.generate_cat_image(prompt)

    # Construct image URL path
    generation_id = state["generation_id"]
    local_image_path = f"/images/{generation_id}.png"

    image_data = {
        "url": local_image_path,
        "binary": image_binary,
        "prompt": prompt,
        "original_url": image_url  # Together.ai URL
    }

    logger.info(f"Image generated successfully: {image_url}")

    return {"image": image_data}


# ============================================================================
# Node 8: Save to Database
# ============================================================================

def save_to_db_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Save generation results to PostgreSQL database.

    Creates a new Generation record with:
    - Repository metadata
    - Analysis results
    - Cat attributes
    - Image path and prompt

    Args:
        state: Current workflow state (requires all fields populated)

    Returns:
        dict: Empty dict (state not modified)

    Raises:
        SQLAlchemyError: If database save fails
    """
    logger.info("Saving generation to database")

    db = SessionLocal()
    try:
        generation = Generation(
            id=uuid.UUID(state["generation_id"]),
            github_url=state["github_url"],
            repo_owner=state["metadata"].get("owner"),
            repo_name=state["metadata"].get("name"),
            primary_language=state["metadata"].get("primary_language"),
            repo_size_kb=state["metadata"].get("size_kb"),
            code_quality_score=state["analysis"]["code_quality_score"],
            cat_attributes=state["cat_attrs"],
            analysis_data=state["analysis"],
            image_path=state["image"]["url"],
            image_prompt=state["image"]["prompt"]
        )

        db.add(generation)
        db.commit()
        db.refresh(generation)

        logger.info(f"Generation saved: {generation.id}")

        return {}  # No state updates

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to save generation: {str(e)}")
        raise

    finally:
        db.close()
