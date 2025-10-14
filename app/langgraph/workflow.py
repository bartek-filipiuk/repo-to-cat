"""
LangGraph workflow definition for repository analysis.

Defines the StateGraph workflow that orchestrates the entire pipeline:
1. Extract repository metadata from GitHub
2. Select strategic files for analysis
3. Fetch file contents
4. Analyze code quality with LLM
5. Map analysis results to cat attributes
6. Generate funny story about repository
7. Generate meme text for image overlay
8. Generate image prompt
9. Generate cat image
10. Add text overlay to image
11. Save results to database
"""

import logging
from langgraph.graph import StateGraph, START, END

from app.langgraph.state import WorkflowState
from app.langgraph.nodes import (
    extract_metadata_node,
    select_files_node,
    fetch_files_node,
    analyze_code_node,
    map_attributes_node,
    generate_story_node,
    generate_meme_text_node,
    generate_prompt_node,
    generate_image_node,
    add_text_overlay_node,
    save_to_db_node
)

logger = logging.getLogger(__name__)


def create_workflow() -> StateGraph:
    """
    Create and compile the LangGraph workflow for repository analysis.

    The workflow executes the following steps in sequence:
    1. extract_metadata: Fetch repository metadata from GitHub
    2. select_files: Choose strategic files to analyze
    3. fetch_files: Download file contents
    4. analyze_code: Perform code quality analysis
    5. map_attributes: Map analysis to cat attributes
    6. generate_story: Generate funny story about repository
    7. generate_meme_text: Generate meme text for image overlay
    8. generate_prompt: Create image generation prompt
    9. generate_image: Generate cat image with FLUX
    10. add_text_overlay: Add meme text overlay to image
    11. save_to_db: Save results to PostgreSQL

    Returns:
        Compiled LangGraph workflow ready for invocation

    Example:
        ```python
        workflow = create_workflow()
        result = workflow.invoke({
            "github_url": "https://github.com/owner/repo",
            "generation_id": str(uuid.uuid4())
        })
        ```
    """
    logger.info("Creating LangGraph workflow")

    # Create StateGraph with WorkflowState schema
    builder = StateGraph(WorkflowState)

    # Add all nodes to the graph
    builder.add_node("extract_metadata", extract_metadata_node)
    builder.add_node("select_files", select_files_node)
    builder.add_node("fetch_files", fetch_files_node)
    builder.add_node("analyze_code", analyze_code_node)
    builder.add_node("map_attributes", map_attributes_node)
    builder.add_node("generate_story", generate_story_node)
    builder.add_node("generate_meme_text", generate_meme_text_node)
    builder.add_node("generate_prompt", generate_prompt_node)
    builder.add_node("generate_image", generate_image_node)
    builder.add_node("add_text_overlay", add_text_overlay_node)
    builder.add_node("save_to_db", save_to_db_node)

    # Define edges (sequential flow)
    builder.add_edge(START, "extract_metadata")
    builder.add_edge("extract_metadata", "select_files")
    builder.add_edge("select_files", "fetch_files")
    builder.add_edge("fetch_files", "analyze_code")
    builder.add_edge("analyze_code", "map_attributes")
    builder.add_edge("map_attributes", "generate_story")
    builder.add_edge("generate_story", "generate_meme_text")
    builder.add_edge("generate_meme_text", "generate_prompt")
    builder.add_edge("generate_prompt", "generate_image")
    builder.add_edge("generate_image", "add_text_overlay")
    builder.add_edge("add_text_overlay", "save_to_db")
    builder.add_edge("save_to_db", END)

    # Compile the workflow
    workflow = builder.compile()

    logger.info("Workflow compiled successfully")

    return workflow
