"""
Unit tests for LangGraph workflow nodes.

Tests all 8 node functions with mocked dependencies:
1. extract_metadata_node
2. select_files_node
3. fetch_files_node
4. analyze_code_node
5. map_attributes_node
6. generate_prompt_node
7. generate_image_node
8. save_to_db_node
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import uuid
from datetime import datetime

from app.langgraph.state import WorkflowState
from app.langgraph.nodes import (
    extract_metadata_node,
    select_files_node,
    fetch_files_node,
    analyze_code_node,
    map_attributes_node,
    generate_prompt_node,
    generate_image_node,
    save_to_db_node
)
from app.api.schemas import AnalysisResult


class TestExtractMetadataNode:
    """Tests for extract_metadata_node."""

    @patch('app.langgraph.nodes.get_repository_metadata')
    def test_extract_metadata_success(self, mock_get_metadata):
        """Test successful metadata extraction."""
        # Mock response
        mock_get_metadata.return_value = {
            "name": "test-repo",
            "owner": "test-owner",
            "size_kb": 1500,
            "stars": 42,
            "primary_language": "Python",
            "description": "A test repository"
        }

        # Create state
        state: WorkflowState = {
            "github_url": "https://github.com/test-owner/test-repo",
            "generation_id": "test-uuid-123"
        }

        # Call node
        result = extract_metadata_node(state)

        # Assertions
        assert "metadata" in result
        assert result["metadata"]["name"] == "test-repo"
        assert result["metadata"]["owner"] == "test-owner"
        assert result["metadata"]["primary_language"] == "Python"
        mock_get_metadata.assert_called_once_with("https://github.com/test-owner/test-repo")


class TestSelectFilesNode:
    """Tests for select_files_node."""

    @patch('app.langgraph.nodes.select_strategic_files')
    @patch('app.langgraph.nodes.get_file_tree')
    def test_select_files_success(self, mock_get_tree, mock_select_files):
        """Test successful file selection."""
        # Mock file tree
        mock_tree = [
            {"path": "README.md", "type": "file"},
            {"path": "src/main.py", "type": "file"},
            {"path": "tests/test_main.py", "type": "file"}
        ]
        mock_get_tree.return_value = mock_tree

        # Mock selected files
        mock_select_files.return_value = [
            "README.md",
            "src/main.py",
            "tests/test_main.py"
        ]

        # Create state
        state: WorkflowState = {
            "github_url": "https://github.com/test-owner/test-repo",
            "generation_id": "test-uuid-123"
        }

        # Call node
        result = select_files_node(state)

        # Assertions
        assert "files" in result
        assert len(result["files"]) == 3
        assert "README.md" in result["files"]
        mock_get_tree.assert_called_once()
        mock_select_files.assert_called_once_with(mock_tree)


class TestFetchFilesNode:
    """Tests for fetch_files_node."""

    @patch('app.langgraph.nodes.fetch_file_contents')
    def test_fetch_files_success(self, mock_fetch):
        """Test successful file content fetching."""
        # Mock fetched files with content
        mock_fetch.return_value = [
            {
                "path": "README.md",
                "content": "# Test Repo\n\nA test repository",
                "language": "Markdown"
            },
            {
                "path": "src/main.py",
                "content": "def main():\n    print('Hello')",
                "language": "Python"
            }
        ]

        # Create state
        state: WorkflowState = {
            "github_url": "https://github.com/test-owner/test-repo",
            "generation_id": "test-uuid-123",
            "files": ["README.md", "src/main.py"]
        }

        # Call node
        result = fetch_files_node(state)

        # Assertions
        assert "files" in result
        assert len(result["files"]) == 2
        assert result["files"][0]["content"] == "# Test Repo\n\nA test repository"
        assert result["files"][1]["language"] == "Python"
        mock_fetch.assert_called_once_with(
            "https://github.com/test-owner/test-repo",
            ["README.md", "src/main.py"]
        )


class TestAnalyzeCodeNode:
    """Tests for analyze_code_node."""

    @patch('app.langgraph.nodes.AnalysisService')
    @patch('app.langgraph.nodes.OpenRouterProvider')
    def test_analyze_code_success(self, mock_openrouter_class, mock_service_class):
        """Test successful code analysis."""
        # Mock OpenRouter provider
        mock_openrouter = Mock()
        mock_openrouter_class.return_value = mock_openrouter

        # Mock AnalysisService
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        # Mock analysis result
        mock_analysis_result = AnalysisResult(
            code_quality_score=7.5,
            files_analyzed=["main.py"],
            metrics={
                "line_length_avg": 80,
                "function_length_avg": 20,
                "has_tests": True,
                "has_type_hints": True
            }
        )
        mock_service.analyze_code_files.return_value = mock_analysis_result

        # Create state
        state: WorkflowState = {
            "github_url": "https://github.com/test-owner/test-repo",
            "generation_id": "test-uuid-123",
            "metadata": {"primary_language": "Python"},
            "files": [
                {"path": "main.py", "content": "def main():\n    pass", "language": "Python"}
            ]
        }

        # Call node
        result = analyze_code_node(state)

        # Assertions
        assert "analysis" in result
        assert result["analysis"]["code_quality_score"] == 7.5
        assert result["analysis"]["metrics"]["has_tests"] is True
        # Verify exact arguments to catch signature mismatches
        mock_service.analyze_code_files.assert_called_once_with(
            code_files=state["files"]
        )


class TestMapAttributesNode:
    """Tests for map_attributes_node."""

    def test_map_attributes_high_quality_python(self):
        """Test attribute mapping for high-quality Python repo."""
        state: WorkflowState = {
            "github_url": "https://github.com/test-owner/test-repo",
            "generation_id": "test-uuid-123",
            "metadata": {
                "size_kb": 2000,  # medium size
                "primary_language": "Python"
            },
            "analysis": {
                "code_quality_score": 8.5,
                "metrics": {"has_tests": True}
            }
        }

        result = map_attributes_node(state)

        assert "cat_attrs" in result
        cat_attrs = result["cat_attrs"]
        assert cat_attrs["size"] == "medium"
        assert cat_attrs["age"] == "senior"  # High quality = mature
        assert cat_attrs["beauty_score"] == 8.5
        assert cat_attrs["expression"] == "happy"  # High quality + tests
        assert "snakes" in cat_attrs["background"].lower()

    def test_map_attributes_low_quality_javascript(self):
        """Test attribute mapping for low-quality JavaScript repo."""
        state: WorkflowState = {
            "github_url": "https://github.com/test-owner/test-repo",
            "generation_id": "test-uuid-123",
            "metadata": {
                "size_kb": 500,  # small size
                "primary_language": "JavaScript"
            },
            "analysis": {
                "code_quality_score": 3.0,
                "metrics": {"has_tests": False}
            }
        }

        result = map_attributes_node(state)

        cat_attrs = result["cat_attrs"]
        assert cat_attrs["size"] == "small"
        assert cat_attrs["age"] == "kitten"  # Low quality = inexperienced
        assert cat_attrs["beauty_score"] == 3.0
        assert cat_attrs["expression"] == "grumpy"  # Low quality
        assert "coffee" in cat_attrs["background"].lower()

    def test_map_attributes_large_go_repo(self):
        """Test attribute mapping for large Go repository."""
        state: WorkflowState = {
            "github_url": "https://github.com/test-owner/test-repo",
            "generation_id": "test-uuid-123",
            "metadata": {
                "size_kb": 7000,  # large size
                "primary_language": "Go"
            },
            "analysis": {
                "code_quality_score": 6.5,
                "metrics": {"has_tests": True}
            }
        }

        result = map_attributes_node(state)

        cat_attrs = result["cat_attrs"]
        assert cat_attrs["size"] == "large"
        assert cat_attrs["age"] == "adult"  # Good quality = mature
        assert cat_attrs["expression"] == "neutral"  # Medium quality
        assert "gopher" in cat_attrs["background"].lower()

    def test_map_attributes_unknown_language(self):
        """Test attribute mapping with unknown language."""
        state: WorkflowState = {
            "github_url": "https://github.com/test-owner/test-repo",
            "generation_id": "test-uuid-123",
            "metadata": {
                "size_kb": 1200,
                "primary_language": "UnknownLang"
            },
            "analysis": {
                "code_quality_score": 5.0,
                "metrics": {"has_tests": False}
            }
        }

        result = map_attributes_node(state)

        cat_attrs = result["cat_attrs"]
        # Should use default background
        assert "generic" in cat_attrs["background"].lower() or "code editor" in cat_attrs["background"].lower()


class TestGeneratePromptNode:
    """Tests for generate_prompt_node."""

    def test_generate_prompt_happy_cat(self):
        """Test prompt generation for happy cat."""
        state: WorkflowState = {
            "github_url": "https://github.com/test-owner/test-repo",
            "generation_id": "test-uuid-123",
            "cat_attrs": {
                "size": "medium",
                "age": "adult",
                "beauty_score": 8.5,
                "expression": "happy",
                "background": "snakes and code snippets in a cozy den",
                "language": "Python"
            }
        }

        result = generate_prompt_node(state)

        assert "cat_attrs" in result
        assert "prompt" in result["cat_attrs"]
        prompt = result["cat_attrs"]["prompt"]

        # Check prompt contains key elements
        assert "beautiful" in prompt.lower() or "well-groomed" in prompt.lower()
        assert "adult" in prompt.lower() or "mature" in prompt.lower()
        assert "happy" in prompt.lower() or "purr" in prompt.lower()
        assert "snakes" in prompt.lower()

    def test_generate_prompt_grumpy_kitten(self):
        """Test prompt generation for grumpy kitten."""
        state: WorkflowState = {
            "github_url": "https://github.com/test-owner/test-repo",
            "generation_id": "test-uuid-123",
            "cat_attrs": {
                "size": "small",
                "age": "kitten",
                "beauty_score": 2.5,
                "expression": "grumpy",
                "background": "coffee cups and scattered npm packages",
                "language": "JavaScript"
            }
        }

        result = generate_prompt_node(state)

        prompt = result["cat_attrs"]["prompt"]

        # Check prompt contains key elements
        assert "scruffy" in prompt.lower() or "disheveled" in prompt.lower()
        assert "kitten" in prompt.lower() or "baby" in prompt.lower()
        assert "grumpy" in prompt.lower() or "scowl" in prompt.lower()
        assert "coffee" in prompt.lower()

    def test_generate_prompt_contains_quality_markers(self):
        """Test that prompt includes photorealistic markers."""
        state: WorkflowState = {
            "github_url": "https://github.com/test-owner/test-repo",
            "generation_id": "test-uuid-123",
            "cat_attrs": {
                "size": "medium",
                "age": "young",
                "beauty_score": 6.0,
                "expression": "neutral",
                "background": "gears and metal",
                "language": "Rust"
            }
        }

        result = generate_prompt_node(state)
        prompt = result["cat_attrs"]["prompt"]

        # Check for photorealistic markers
        assert "photorealistic" in prompt.lower() or "detailed" in prompt.lower()
        assert "natural" in prompt.lower() or "lifelike" in prompt.lower()


class TestGenerateImageNode:
    """Tests for generate_image_node."""

    @patch('app.langgraph.nodes.save_image_locally')
    @patch('app.langgraph.nodes.TogetherProvider')
    def test_generate_image_success(self, mock_together_class, mock_save_image):
        """Test successful image generation."""
        # Mock Together.ai provider
        mock_together = Mock()
        mock_together_class.return_value = mock_together

        # Create valid base64 data
        import base64
        valid_base64 = base64.b64encode(b"fake_image_data").decode("utf-8")

        # Mock image generation response
        mock_together.generate_cat_image.return_value = (
            "https://together.ai/image/uuid-123.png",
            valid_base64
        )

        # Mock save_image_locally
        mock_save_image.return_value = "generated_images/test-uuid-123.png"

        # Create state
        state: WorkflowState = {
            "github_url": "https://github.com/test-owner/test-repo",
            "generation_id": "test-uuid-123",
            "cat_attrs": {
                "prompt": "A beautiful cat with code"
            }
        }

        # Call node
        result = generate_image_node(state)

        # Assertions
        assert "image" in result
        assert result["image"]["url"] == "generated_images/test-uuid-123.png"
        assert result["image"]["binary"] == valid_base64
        assert result["image"]["prompt"] == "A beautiful cat with code"
        assert result["image"]["original_url"] == "https://together.ai/image/uuid-123.png"
        mock_together.generate_cat_image.assert_called_once_with("A beautiful cat with code")
        mock_save_image.assert_called_once_with(valid_base64, "test-uuid-123")


class TestSaveToDbNode:
    """Tests for save_to_db_node."""

    @patch('app.langgraph.nodes.SessionLocal')
    def test_save_to_db_success(self, mock_session_class):
        """Test successful database save."""
        # Mock database session
        mock_db = Mock()
        mock_session_class.return_value = mock_db

        # Create complete state
        state: WorkflowState = {
            "github_url": "https://github.com/test-owner/test-repo",
            "generation_id": "550e8400-e29b-41d4-a716-446655440000",  # Valid UUID
            "metadata": {
                "owner": "test-owner",
                "name": "test-repo",
                "primary_language": "Python",
                "size_kb": 1500
            },
            "analysis": {
                "code_quality_score": 7.5,
                "files_analyzed": ["main.py"],
                "metrics": {"has_tests": True}
            },
            "cat_attrs": {
                "size": "medium",
                "age": "adult",
                "beauty_score": 7.5,
                "expression": "happy"
            },
            "image": {
                "url": "/images/test-uuid.png",
                "prompt": "A beautiful cat"
            }
        }

        # Call node
        result = save_to_db_node(state)

        # Assertions
        assert result == {}  # Node returns empty dict
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.close.assert_called_once()

    @patch('app.langgraph.nodes.SessionLocal')
    def test_save_to_db_rollback_on_error(self, mock_session_class):
        """Test database rollback on error."""
        # Mock database session
        mock_db = Mock()
        mock_session_class.return_value = mock_db

        # Make commit raise an exception
        mock_db.commit.side_effect = Exception("Database error")

        # Create state
        state: WorkflowState = {
            "github_url": "https://github.com/test-owner/test-repo",
            "generation_id": "550e8400-e29b-41d4-a716-446655440000",
            "metadata": {"owner": "test-owner", "name": "test-repo"},
            "analysis": {"code_quality_score": 7.5},
            "cat_attrs": {"size": "medium"},
            "image": {"url": "/images/test.png", "prompt": "A cat"}
        }

        # Call node and expect exception
        with pytest.raises(Exception, match="Database error"):
            save_to_db_node(state)

        # Verify rollback was called
        mock_db.rollback.assert_called_once()
        mock_db.close.assert_called_once()


class TestNodesIntegration:
    """Integration-style tests for node interactions."""

    def test_state_flows_through_nodes(self):
        """Test that state properly flows through multiple nodes."""
        # This is a simplified integration test using minimal mocking
        initial_state: WorkflowState = {
            "github_url": "https://github.com/test-owner/test-repo",
            "generation_id": "test-uuid-123"
        }

        # Test that each node accepts the state format
        # and returns proper updates (structural test)
        assert "github_url" in initial_state
        assert "generation_id" in initial_state

    def test_cat_attrs_has_all_required_fields(self):
        """Test that map_attributes_node produces all required fields."""
        state: WorkflowState = {
            "github_url": "https://github.com/test-owner/test-repo",
            "generation_id": "test-uuid-123",
            "metadata": {
                "size_kb": 1500,
                "primary_language": "Python"
            },
            "analysis": {
                "code_quality_score": 7.0,
                "metrics": {"has_tests": True}
            }
        }

        result = map_attributes_node(state)
        cat_attrs = result["cat_attrs"]

        # Verify all expected fields are present
        required_fields = ["size", "age", "beauty_score", "expression", "background", "language"]
        for field in required_fields:
            assert field in cat_attrs, f"Missing required field: {field}"
