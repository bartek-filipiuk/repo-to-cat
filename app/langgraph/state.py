"""
Workflow state definition for LangGraph.

Defines the WorkflowState TypedDict that tracks data through the entire
repository analysis and image generation workflow.
"""

from typing_extensions import TypedDict, NotRequired
from typing import Dict, List, Any


class WorkflowState(TypedDict):
    """
    State schema for the repository analysis workflow.

    This state is passed through all nodes in the LangGraph workflow,
    with each node reading from and updating specific fields.

    Required fields (must be provided at workflow invocation):
        github_url: GitHub repository URL to analyze
        generation_id: Unique UUID for this generation
        user_id: UUID of the authenticated user

    Optional fields (populated during workflow execution):
        metadata: Repository metadata (name, owner, size, stars, language)
        files: List of selected strategic files to analyze
        analysis: Code quality analysis results (score, metrics)
        cat_attrs: Mapped cat attributes (size, age, beauty, expression, background)
        story: Funny story about the repository (3-5 sentences)
        meme_text_top: Top meme text for image overlay
        meme_text_bottom: Bottom meme text for image overlay
        image: Generated image data (url, binary, prompt)
        error: Error message if workflow fails (None if successful)
    """

    # Required input fields
    github_url: str
    generation_id: str
    user_id: str

    # Optional intermediate state fields
    metadata: NotRequired[Dict[str, Any]]
    files: NotRequired[List[Dict[str, str]]]
    analysis: NotRequired[Dict[str, Any]]
    cat_attrs: NotRequired[Dict[str, Any]]
    story: NotRequired[str]
    meme_text_top: NotRequired[str]
    meme_text_bottom: NotRequired[str]
    image: NotRequired[Dict[str, str]]

    # Error tracking
    error: NotRequired[str | None]
