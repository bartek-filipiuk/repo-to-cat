"""
Unit tests for LangGraph state definition.

Tests the WorkflowState TypedDict structure and field requirements.
"""

import pytest
from typing import get_type_hints
from app.langgraph.state import WorkflowState


class TestWorkflowState:
    """Test suite for WorkflowState TypedDict."""

    def test_workflow_state_required_fields(self):
        """Test that WorkflowState has required fields."""
        # Create minimal valid state with only required fields
        state: WorkflowState = {
            "github_url": "https://github.com/owner/repo",
            "generation_id": "test-uuid-123"
        }

        assert state["github_url"] == "https://github.com/owner/repo"
        assert state["generation_id"] == "test-uuid-123"

    def test_workflow_state_with_all_fields(self):
        """Test WorkflowState with all fields populated."""
        state: WorkflowState = {
            "github_url": "https://github.com/owner/repo",
            "generation_id": "test-uuid-123",
            "metadata": {
                "name": "repo",
                "owner": "owner",
                "size_kb": 1234,
                "stars": 100,
                "primary_language": "Python"
            },
            "files": [
                {"path": "README.md", "content": "# Test", "language": "Markdown"},
                {"path": "main.py", "content": "def main():\n    pass", "language": "Python"}
            ],
            "analysis": {
                "code_quality_score": 7.5,
                "files_analyzed": ["main.py"],
                "metrics": {
                    "line_length_avg": 85,
                    "function_length_avg": 25
                }
            },
            "cat_attrs": {
                "size": "medium",
                "age": "young",
                "beauty_score": 7.5,
                "expression": "happy",
                "background": "snakes and code"
            },
            "image": {
                "url": "/images/test-uuid-123.png",
                "binary": "base64-encoded-data",
                "prompt": "A young cat with code"
            },
            "error": None
        }

        assert state["github_url"] == "https://github.com/owner/repo"
        assert state["metadata"]["name"] == "repo"
        assert len(state["files"]) == 2
        assert state["analysis"]["code_quality_score"] == 7.5
        assert state["cat_attrs"]["size"] == "medium"
        assert state["image"]["url"] == "/images/test-uuid-123.png"
        assert state["error"] is None

    def test_workflow_state_with_error(self):
        """Test WorkflowState with error message."""
        state: WorkflowState = {
            "github_url": "https://github.com/owner/repo",
            "generation_id": "test-uuid-123",
            "error": "Repository not found"
        }

        assert state["error"] == "Repository not found"

    def test_workflow_state_metadata_structure(self):
        """Test metadata field structure."""
        state: WorkflowState = {
            "github_url": "https://github.com/owner/repo",
            "generation_id": "test-uuid-123",
            "metadata": {
                "name": "test-repo",
                "owner": "test-owner",
                "size_kb": 500,
                "stars": 42,
                "primary_language": "JavaScript",
                "description": "A test repository"
            }
        }

        metadata = state["metadata"]
        assert metadata["name"] == "test-repo"
        assert metadata["owner"] == "test-owner"
        assert metadata["size_kb"] == 500
        assert metadata["stars"] == 42
        assert metadata["primary_language"] == "JavaScript"

    def test_workflow_state_files_structure(self):
        """Test files field structure."""
        state: WorkflowState = {
            "github_url": "https://github.com/owner/repo",
            "generation_id": "test-uuid-123",
            "files": [
                {
                    "path": "src/main.py",
                    "content": "print('hello')",
                    "language": "Python"
                },
                {
                    "path": "tests/test_main.py",
                    "content": "def test_main(): pass",
                    "language": "Python"
                }
            ]
        }

        files = state["files"]
        assert len(files) == 2
        assert files[0]["path"] == "src/main.py"
        assert files[1]["language"] == "Python"

    def test_workflow_state_analysis_structure(self):
        """Test analysis field structure."""
        state: WorkflowState = {
            "github_url": "https://github.com/owner/repo",
            "generation_id": "test-uuid-123",
            "analysis": {
                "code_quality_score": 8.2,
                "files_analyzed": ["main.py", "utils.py"],
                "metrics": {
                    "line_length_avg": 75,
                    "function_length_avg": 20,
                    "has_tests": True,
                    "has_type_hints": True
                }
            }
        }

        analysis = state["analysis"]
        assert analysis["code_quality_score"] == 8.2
        assert len(analysis["files_analyzed"]) == 2
        assert analysis["metrics"]["has_tests"] is True

    def test_workflow_state_cat_attrs_structure(self):
        """Test cat_attrs field structure."""
        state: WorkflowState = {
            "github_url": "https://github.com/owner/repo",
            "generation_id": "test-uuid-123",
            "cat_attrs": {
                "size": "large",
                "age": "old",
                "beauty_score": 9.0,
                "expression": "wise",
                "background": "gophers and mountains",
                "accessories": ["glasses", "bow tie"]
            }
        }

        cat_attrs = state["cat_attrs"]
        assert cat_attrs["size"] == "large"
        assert cat_attrs["age"] == "old"
        assert cat_attrs["beauty_score"] == 9.0
        assert cat_attrs["expression"] == "wise"

    def test_workflow_state_image_structure(self):
        """Test image field structure."""
        state: WorkflowState = {
            "github_url": "https://github.com/owner/repo",
            "generation_id": "test-uuid-123",
            "image": {
                "url": "/images/test-uuid-123.png",
                "binary": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                "prompt": "A beautiful cat in a coding environment"
            }
        }

        image = state["image"]
        assert image["url"] == "/images/test-uuid-123.png"
        assert len(image["binary"]) > 0
        assert "cat" in image["prompt"].lower()

    def test_workflow_state_optional_fields_not_required(self):
        """Test that optional fields are truly optional."""
        # State with only required fields should be valid
        state: WorkflowState = {
            "github_url": "https://github.com/test/repo",
            "generation_id": "uuid-456"
        }

        # Should not raise any errors
        assert "github_url" in state
        assert "generation_id" in state
        # Optional fields may or may not be present
        assert "metadata" not in state
        assert "files" not in state
        assert "analysis" not in state

    def test_workflow_state_partial_population(self):
        """Test WorkflowState with only some optional fields."""
        state: WorkflowState = {
            "github_url": "https://github.com/owner/repo",
            "generation_id": "test-uuid-123",
            "metadata": {
                "name": "repo",
                "owner": "owner"
            },
            # Files, analysis, cat_attrs, image not included
            "error": None
        }

        assert "metadata" in state
        assert "files" not in state
        assert "analysis" not in state
        assert state["error"] is None
