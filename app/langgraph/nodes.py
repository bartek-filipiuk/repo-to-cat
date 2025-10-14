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
import base64
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
from app.services.image_service import (
    map_analysis_to_cat_attributes,
    create_image_prompt,
    save_image_locally
)
from app.providers.openrouter import OpenRouterProvider
from app.providers.together_ai import TogetherProvider
from app.core.database import SessionLocal
from app.models.database import Generation
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

    # Fetch file contents (returns dict mapping paths to contents)
    file_contents_dict = fetch_file_contents(
        state["github_url"],
        state["files"]
    )

    # Transform dict to list of dicts with path, content, language
    files_with_content = []
    for path, content in file_contents_dict.items():
        # Determine language from file extension
        language = "Unknown"
        if path.endswith(".py"):
            language = "Python"
        elif path.endswith((".js", ".jsx")):
            language = "JavaScript"
        elif path.endswith((".ts", ".tsx")):
            language = "TypeScript"
        elif path.endswith(".go"):
            language = "Go"
        elif path.endswith(".rs"):
            language = "Rust"
        elif path.endswith(".java"):
            language = "Java"
        elif path.endswith((".c", ".cpp", ".cc", ".h", ".hpp")):
            language = "C/C++"
        elif path.endswith(".rb"):
            language = "Ruby"
        elif path.endswith(".php"):
            language = "PHP"

        files_with_content.append({
            "path": path,
            "content": content,
            "language": language
        })

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
    openrouter = OpenRouterProvider(api_key=settings.OPENROUTER_API_KEY)
    analysis_service = AnalysisService(openrouter_provider=openrouter)

    # Analyze code files
    analysis_result = analysis_service.analyze_code_files(
        code_files=state["files"]
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

    # Use image service to map attributes
    cat_attrs = map_analysis_to_cat_attributes(metadata, analysis)

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

    # Use image service to create prompt
    prompt = create_image_prompt(cat_attrs)

    # Update cat_attrs with prompt
    updated_cat_attrs = {**cat_attrs, "prompt": prompt}

    return {"cat_attrs": updated_cat_attrs}


# ============================================================================
# Node 7: Generate Image
# ============================================================================

def generate_image_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Generate cat image using Together.ai FLUX.1.1-pro.

    Calls Together.ai API with the generated prompt to create a cat image
    reflecting the code quality, then saves it locally.

    Args:
        state: Current workflow state (requires cat_attrs with prompt)

    Returns:
        dict: State update with image field (url, binary, prompt)

    Raises:
        ImageGenerationError: If image generation fails
    """
    logger.info("Generating cat image")

    together = TogetherProvider(api_key=settings.TOGETHER_API_KEY)
    prompt = state["cat_attrs"]["prompt"]
    generation_id = state["generation_id"]

    # Generate image (returns tuple of (url, base64_binary))
    image_url, image_binary = together.generate_cat_image(prompt)

    # Save image locally using image service
    local_image_path = save_image_locally(image_binary, generation_id)

    image_data = {
        "url": local_image_path,
        "binary": image_binary,
        "prompt": prompt,
        "original_url": image_url  # Together.ai URL
    }

    logger.info(f"Image generated and saved successfully: {local_image_path}")

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
            image_prompt=state["image"]["prompt"],
            story=state.get("story"),
            meme_text_top=state.get("meme_text_top"),
            meme_text_bottom=state.get("meme_text_bottom")
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


# ============================================================================
# Node 9: Generate Story
# ============================================================================

def generate_story_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Generate funny story about the repository.

    Uses OpenRouter to create a 3-5 sentence humorous narrative about
    the repository based on its characteristics and code quality.

    Args:
        state: Current workflow state (requires metadata, analysis, cat_attrs)

    Returns:
        dict: State update with story field

    Raises:
        Exception: If story generation fails (uses fallback story)
    """
    logger.info("Generating repository story")

    from app.services.story_service import generate_repository_story

    # Create provider
    openrouter = OpenRouterProvider(api_key=settings.OPENROUTER_API_KEY)

    # Generate story
    story = generate_repository_story(
        metadata=state["metadata"],
        analysis=state["analysis"],
        cat_attrs=state["cat_attrs"],
        openrouter_provider=openrouter
    )

    logger.info(f"Story generated: {len(story)} characters")

    return {"story": story}


# ============================================================================
# Node 10: Generate Meme Text
# ============================================================================

def generate_meme_text_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Generate meme text for image overlay.

    Uses OpenRouter to create short, funny text for top and bottom
    of the cat image in classic meme style.

    Args:
        state: Current workflow state (requires metadata, analysis, cat_attrs)

    Returns:
        dict: State update with meme_text_top and meme_text_bottom fields

    Raises:
        Exception: If text generation fails (uses fallback text)
    """
    logger.info("Generating meme text")

    from app.services.image_service import generate_meme_text

    # Create provider
    openrouter = OpenRouterProvider(api_key=settings.OPENROUTER_API_KEY)

    # Generate meme text
    top_text, bottom_text = generate_meme_text(
        metadata=state["metadata"],
        analysis=state["analysis"],
        cat_attrs=state["cat_attrs"],
        openrouter_provider=openrouter
    )

    logger.info(f"Meme text generated - TOP: '{top_text}', BOTTOM: '{bottom_text}'")

    return {
        "meme_text_top": top_text,
        "meme_text_bottom": bottom_text
    }


# ============================================================================
# Node 11: Add Text Overlay
# ============================================================================

def add_text_overlay_node(state: WorkflowState) -> Dict[str, Any]:
    """
    Add meme text overlay to generated image.

    Takes the generated cat image and adds the meme text overlay
    using PIL. Saves the modified image locally.

    Args:
        state: Current workflow state (requires image, meme_text_top, meme_text_bottom)

    Returns:
        dict: State update with modified image field

    Raises:
        ImageServiceError: If text overlay fails
    """
    logger.info("Adding text overlay to image")

    from app.services.image_service import add_text_to_image

    # Get image binary from state
    image_binary_base64 = state["image"]["binary"]

    # Decode base64 to bytes
    image_bytes = base64.b64decode(image_binary_base64)

    # Add text overlay
    modified_bytes = add_text_to_image(
        image_bytes=image_bytes,
        top_text=state["meme_text_top"],
        bottom_text=state["meme_text_bottom"]
    )

    # Encode back to base64
    modified_base64 = base64.b64encode(modified_bytes).decode()

    # Save modified image locally (overwrite original)
    local_path = save_image_locally(modified_base64, state["generation_id"])

    # Update image in state
    updated_image = {
        **state["image"],
        "binary": modified_base64,
        "url": local_path
    }

    logger.info(f"Text overlay added, image saved to {local_path}")

    return {"image": updated_image}
