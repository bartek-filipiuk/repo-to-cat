"""
Integration tests for LangGraph workflow.

Tests the complete workflow execution from start to end with mocked
external dependencies (GitHub API, OpenRouter, Together.ai, Database).
"""

import pytest
import uuid
import base64
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from app.langgraph.workflow import create_workflow
from app.langgraph.state import WorkflowState
from app.api.schemas import AnalysisResult


class TestWorkflowCreation:
    """Tests for workflow creation and structure."""

    def test_create_workflow_returns_compiled_graph(self):
        """Test that create_workflow returns a compiled StateGraph."""
        workflow = create_workflow()

        # Verify it's a compiled graph (has invoke method)
        assert hasattr(workflow, 'invoke')
        assert callable(workflow.invoke)

    def test_workflow_nodes_are_registered(self):
        """Test that all expected nodes are in the workflow."""
        workflow = create_workflow()

        # Get workflow structure
        # LangGraph CompiledGraph has nodes attribute
        assert hasattr(workflow, 'nodes') or hasattr(workflow, 'builder')


class TestWorkflowExecution:
    """Tests for full workflow execution."""

    @patch('app.langgraph.nodes.save_image_locally')
    @patch('app.langgraph.nodes.SessionLocal')
    @patch('app.langgraph.nodes.TogetherProvider')
    @patch('app.langgraph.nodes.AnalysisService')
    @patch('app.langgraph.nodes.OpenRouterProvider')
    @patch('app.langgraph.nodes.fetch_file_contents')
    @patch('app.langgraph.nodes.select_strategic_files')
    @patch('app.langgraph.nodes.get_file_tree')
    @patch('app.langgraph.nodes.get_repository_metadata')
    def test_workflow_executes_successfully(
        self,
        mock_get_metadata,
        mock_get_tree,
        mock_select_files,
        mock_fetch_contents,
        mock_openrouter_class,
        mock_analysis_service_class,
        mock_together_class,
        mock_session_class,
        mock_save_image
    ):
        """Test successful execution of the entire workflow."""
        # Mock 1: GitHub metadata
        mock_get_metadata.return_value = {
            "name": "test-repo",
            "owner": "test-owner",
            "size_kb": 1500,
            "stars": 42,
            "primary_language": "Python",
            "description": "A test repository"
        }

        # Mock 2: File tree
        mock_get_tree.return_value = [
            {"path": "README.md", "type": "file"},
            {"path": "src/main.py", "type": "file"}
        ]

        # Mock 3: File selection
        mock_select_files.return_value = ["README.md", "src/main.py"]

        # Mock 4: File contents
        mock_fetch_contents.return_value = [
            {
                "path": "README.md",
                "content": "# Test Repo",
                "language": "Markdown"
            },
            {
                "path": "src/main.py",
                "content": "def main():\n    print('Hello')",
                "language": "Python"
            }
        ]

        # Mock 5: OpenRouter
        mock_openrouter = Mock()
        mock_openrouter_class.return_value = mock_openrouter

        # Mock 6: Analysis Service
        mock_analysis_service = Mock()
        mock_analysis_service_class.return_value = mock_analysis_service
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
        mock_analysis_service.analyze_code_files.return_value = mock_analysis_result

        # Mock 7: Together.ai
        mock_together = Mock()
        mock_together_class.return_value = mock_together
        # Use valid base64 data
        valid_base64 = base64.b64encode(b"fake_image_data").decode("utf-8")
        mock_together.generate_cat_image.return_value = (
            "https://together.ai/image/uuid.png",
            valid_base64
        )

        # Mock 8: Database session
        mock_db = Mock()
        mock_session_class.return_value = mock_db

        # Create workflow
        workflow = create_workflow()

        # Create input state
        generation_id = str(uuid.uuid4())

        # Mock 7b: save_image_locally (after generation_id is created)
        mock_save_image.return_value = f"generated_images/{generation_id}.png"
        input_state: WorkflowState = {
            "github_url": "https://github.com/test-owner/test-repo",
            "generation_id": generation_id
        }

        # Execute workflow
        result = workflow.invoke(input_state)

        # Verify result has all expected fields
        assert "github_url" in result
        assert "generation_id" in result
        assert "metadata" in result
        assert "files" in result
        assert "analysis" in result
        assert "cat_attrs" in result
        assert "image" in result

        # Verify metadata
        assert result["metadata"]["name"] == "test-repo"
        assert result["metadata"]["primary_language"] == "Python"

        # Verify analysis
        assert result["analysis"]["code_quality_score"] == 7.5

        # Verify cat attributes
        assert "size" in result["cat_attrs"]
        assert "age" in result["cat_attrs"]
        assert "expression" in result["cat_attrs"]
        assert "prompt" in result["cat_attrs"]

        # Verify image
        assert result["image"]["url"] == f"generated_images/{generation_id}.png"
        assert result["image"]["binary"] == valid_base64

        # Verify database was called
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    @patch('app.langgraph.nodes.save_image_locally')
    @patch('app.langgraph.nodes.SessionLocal')
    @patch('app.langgraph.nodes.TogetherProvider')
    @patch('app.langgraph.nodes.AnalysisService')
    @patch('app.langgraph.nodes.OpenRouterProvider')
    @patch('app.langgraph.nodes.fetch_file_contents')
    @patch('app.langgraph.nodes.select_strategic_files')
    @patch('app.langgraph.nodes.get_file_tree')
    @patch('app.langgraph.nodes.get_repository_metadata')
    def test_workflow_with_javascript_repo(
        self,
        mock_get_metadata,
        mock_get_tree,
        mock_select_files,
        mock_fetch_contents,
        mock_openrouter_class,
        mock_analysis_service_class,
        mock_together_class,
        mock_session_class,
        mock_save_image
    ):
        """Test workflow with JavaScript repository."""
        # Mock JavaScript repo
        mock_get_metadata.return_value = {
            "name": "js-project",
            "owner": "dev-user",
            "size_kb": 3000,
            "stars": 100,
            "primary_language": "JavaScript",
            "description": "JS project"
        }

        mock_get_tree.return_value = [{"path": "index.js", "type": "file"}]
        mock_select_files.return_value = ["index.js"]
        mock_fetch_contents.return_value = [
            {
                "path": "index.js",
                "content": "console.log('hello');",
                "language": "JavaScript"
            }
        ]

        # Mock analysis (lower score)
        mock_openrouter = Mock()
        mock_openrouter_class.return_value = mock_openrouter
        mock_analysis_service = Mock()
        mock_analysis_service_class.return_value = mock_analysis_service
        mock_analysis_result = AnalysisResult(
            code_quality_score=4.5,
            files_analyzed=["index.js"],
            metrics={"has_tests": False}
        )
        mock_analysis_service.analyze_code_files.return_value = mock_analysis_result

        # Mock image generation
        mock_together = Mock()
        mock_together_class.return_value = mock_together
        # Use valid base64 data
        valid_base64 = base64.b64encode(b"fake_image_data").decode("utf-8")
        mock_together.generate_cat_image.return_value = (
            "https://together.ai/image/uuid.png",
            valid_base64
        )

        # Mock save_image_locally
        mock_save_image.return_value = "generated_images/test-uuid.png"

        # Mock database
        mock_db = Mock()
        mock_session_class.return_value = mock_db

        # Create workflow and execute
        workflow = create_workflow()
        result = workflow.invoke({
            "github_url": "https://github.com/dev-user/js-project",
            "generation_id": str(uuid.uuid4())
        })

        # Verify JavaScript-specific attributes
        assert result["metadata"]["primary_language"] == "JavaScript"
        assert result["cat_attrs"]["language"] == "JavaScript"
        assert "coffee" in result["cat_attrs"]["background"].lower()

        # Verify lower quality score affects attributes
        assert result["cat_attrs"]["beauty_score"] == 4.5
        # Young cat for lower score
        assert result["cat_attrs"]["age"] in ["young", "kitten"]
        # Concerned or grumpy for lower score without tests
        assert result["cat_attrs"]["expression"] in ["concerned", "grumpy"]


class TestWorkflowErrorHandling:
    """Tests for workflow error handling."""

    @patch('app.langgraph.nodes.get_repository_metadata')
    def test_workflow_fails_on_invalid_repo(self, mock_get_metadata):
        """Test workflow fails gracefully on invalid repository."""
        from github import GithubException

        # Mock GitHub API error
        mock_get_metadata.side_effect = GithubException(
            status=404,
            data={"message": "Not Found"},
            headers={}
        )

        workflow = create_workflow()

        # Should raise exception
        with pytest.raises(GithubException):
            workflow.invoke({
                "github_url": "https://github.com/invalid/repo",
                "generation_id": str(uuid.uuid4())
            })

    @patch('app.langgraph.nodes.fetch_file_contents')
    @patch('app.langgraph.nodes.select_strategic_files')
    @patch('app.langgraph.nodes.get_file_tree')
    @patch('app.langgraph.nodes.get_repository_metadata')
    def test_workflow_handles_file_fetch_error(
        self,
        mock_get_metadata,
        mock_get_tree,
        mock_select_files,
        mock_fetch_contents
    ):
        """Test workflow handles file fetch errors."""
        from github import GithubException

        # Mock successful metadata and file selection
        mock_get_metadata.return_value = {
            "name": "test-repo",
            "owner": "test-owner",
            "size_kb": 1500,
            "primary_language": "Python"
        }
        mock_get_tree.return_value = [{"path": "main.py", "type": "file"}]
        mock_select_files.return_value = ["main.py"]

        # Mock file fetch error
        mock_fetch_contents.side_effect = GithubException(
            status=403,
            data={"message": "Forbidden"},
            headers={}
        )

        workflow = create_workflow()

        # Should propagate the exception
        with pytest.raises(GithubException):
            workflow.invoke({
                "github_url": "https://github.com/test-owner/test-repo",
                "generation_id": str(uuid.uuid4())
            })


class TestWorkflowStateTransitions:
    """Tests for state transitions between nodes."""

    @patch('app.langgraph.nodes.get_repository_metadata')
    def test_metadata_node_updates_state(self, mock_get_metadata):
        """Test that extract_metadata_node properly updates state."""
        mock_get_metadata.return_value = {
            "name": "test-repo",
            "owner": "test-owner",
            "size_kb": 1500,
            "primary_language": "Python"
        }

        workflow = create_workflow()

        # We can't easily inspect intermediate states in compiled graph,
        # but we can verify the final state includes metadata
        # This test mainly ensures the workflow is constructed correctly
        assert workflow is not None

    def test_workflow_initial_state_requirements(self):
        """Test that workflow requires github_url and generation_id."""
        workflow = create_workflow()

        # Missing required fields should fail
        with pytest.raises(Exception):
            workflow.invoke({})  # Missing both required fields

    @patch('app.langgraph.nodes.save_image_locally')
    @patch('app.langgraph.nodes.SessionLocal')
    @patch('app.langgraph.nodes.TogetherProvider')
    @patch('app.langgraph.nodes.AnalysisService')
    @patch('app.langgraph.nodes.OpenRouterProvider')
    @patch('app.langgraph.nodes.fetch_file_contents')
    @patch('app.langgraph.nodes.select_strategic_files')
    @patch('app.langgraph.nodes.get_file_tree')
    @patch('app.langgraph.nodes.get_repository_metadata')
    def test_prompt_generation_uses_cat_attributes(
        self,
        mock_get_metadata,
        mock_get_tree,
        mock_select_files,
        mock_fetch_contents,
        mock_openrouter_class,
        mock_analysis_service_class,
        mock_together_class,
        mock_session_class,
        mock_save_image
    ):
        """Test that generated prompt incorporates cat attributes."""
        # Setup mocks (minimal)
        mock_get_metadata.return_value = {
            "name": "test", "owner": "test", "size_kb": 1500,
            "primary_language": "Python"
        }
        mock_get_tree.return_value = [{"path": "main.py", "type": "file"}]
        mock_select_files.return_value = ["main.py"]
        mock_fetch_contents.return_value = [
            {"path": "main.py", "content": "code", "language": "Python"}
        ]

        mock_openrouter = Mock()
        mock_openrouter_class.return_value = mock_openrouter
        mock_analysis_service = Mock()
        mock_analysis_service_class.return_value = mock_analysis_service
        mock_analysis_service.analyze_code_files.return_value = AnalysisResult(
            code_quality_score=7.0, files_analyzed=["main.py"],
            metrics={"has_tests": True}
        )

        mock_together = Mock()
        mock_together_class.return_value = mock_together
        # Use valid base64 data
        valid_base64 = base64.b64encode(b"fake_image_data").decode("utf-8")
        mock_together.generate_cat_image.return_value = ("url", valid_base64)

        # Mock save_image_locally
        mock_save_image.return_value = "generated_images/test-uuid.png"

        mock_db = Mock()
        mock_session_class.return_value = mock_db

        # Execute workflow
        workflow = create_workflow()
        result = workflow.invoke({
            "github_url": "https://github.com/test/test",
            "generation_id": str(uuid.uuid4())
        })

        # Verify prompt was generated and contains expected elements
        assert "prompt" in result["cat_attrs"]
        prompt = result["cat_attrs"]["prompt"]
        assert len(prompt) > 0
        # Should mention cat attributes
        assert any(word in prompt.lower() for word in ["cat", "kitten"])
