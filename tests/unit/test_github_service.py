"""
Unit tests for GitHub service.

Tests GitHub API integration including:
- Repository metadata fetching
- Language detection
- File tree retrieval
- Strategic file selection
- File content fetching
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from github import GithubException

from app.services.github_service import (
    get_repository_metadata,
    get_repository_languages,
    get_file_tree,
    select_strategic_files,
    fetch_file_contents,
)


class TestGetRepositoryMetadata:
    """Test get_repository_metadata() function."""

    @patch('app.services.github_service.Github')
    def test_get_metadata_success(self, mock_github):
        """Test successful metadata retrieval."""
        # Setup mock
        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.owner.login = "test-owner"
        mock_repo.size = 1234
        mock_repo.stargazers_count = 567
        mock_repo.language = "Python"
        mock_repo.description = "Test description"

        mock_github.return_value.get_repo.return_value = mock_repo

        # Execute
        result = get_repository_metadata("https://github.com/test-owner/test-repo")

        # Assert
        assert result["name"] == "test-repo"
        assert result["owner"] == "test-owner"
        assert result["size_kb"] == 1234
        assert result["stars"] == 567
        assert result["primary_language"] == "Python"
        assert result["description"] == "Test description"

    @patch('app.services.github_service.Github')
    def test_get_metadata_invalid_url(self, mock_github):
        """Test metadata retrieval with invalid URL."""
        with pytest.raises(ValueError, match="Invalid GitHub URL"):
            get_repository_metadata("https://gitlab.com/owner/repo")

    @patch('app.services.github_service.Github')
    def test_get_metadata_repo_not_found(self, mock_github):
        """Test metadata retrieval for non-existent repository."""
        mock_github.return_value.get_repo.side_effect = GithubException(404, "Not Found")

        with pytest.raises(GithubException):
            get_repository_metadata("https://github.com/test-owner/nonexistent-repo")

    @patch('app.services.github_service.Github')
    def test_get_metadata_private_repo(self, mock_github):
        """Test metadata retrieval for private repository."""
        mock_github.return_value.get_repo.side_effect = GithubException(403, "Forbidden")

        with pytest.raises(GithubException):
            get_repository_metadata("https://github.com/test-owner/private-repo")

    @patch('app.services.github_service.Github')
    def test_get_metadata_with_git_suffix(self, mock_github):
        """Test metadata retrieval with .git suffix in URL."""
        # Setup mock
        mock_repo = Mock()
        mock_repo.name = "test-repo"
        mock_repo.owner.login = "test-owner"
        mock_repo.size = 1234
        mock_repo.stargazers_count = 567
        mock_repo.language = "Python"
        mock_repo.description = "Test description"

        mock_github.return_value.get_repo.return_value = mock_repo

        # Execute with .git suffix
        result = get_repository_metadata("https://github.com/test-owner/test-repo.git")

        # Assert - should call get_repo without .git suffix
        mock_github.return_value.get_repo.assert_called_once_with("test-owner/test-repo")
        assert result["name"] == "test-repo"
        assert result["owner"] == "test-owner"


class TestGetRepositoryLanguages:
    """Test get_repository_languages() function."""

    @patch('app.services.github_service.Github')
    def test_get_languages_success(self, mock_github):
        """Test successful language breakdown retrieval."""
        # Setup mock
        mock_repo = Mock()
        mock_repo.get_languages.return_value = {
            "Python": 85000,
            "JavaScript": 12000,
            "HTML": 3000
        }

        mock_github.return_value.get_repo.return_value = mock_repo

        # Execute
        result = get_repository_languages("https://github.com/test-owner/test-repo")

        # Assert
        assert result["Python"] == 85000
        assert result["JavaScript"] == 12000
        assert result["HTML"] == 3000

    @patch('app.services.github_service.Github')
    def test_get_languages_empty(self, mock_github):
        """Test language retrieval for repo with no detected languages."""
        mock_repo = Mock()
        mock_repo.get_languages.return_value = {}

        mock_github.return_value.get_repo.return_value = mock_repo

        result = get_repository_languages("https://github.com/test-owner/docs-repo")

        assert result == {}


class TestGetFileTree:
    """Test get_file_tree() function."""

    @patch('app.services.github_service.Github')
    def test_get_file_tree_success(self, mock_github):
        """Test successful file tree retrieval."""
        # Setup mock
        mock_tree_element_1 = Mock()
        mock_tree_element_1.path = "README.md"
        mock_tree_element_1.type = "blob"

        mock_tree_element_2 = Mock()
        mock_tree_element_2.path = "src/main.py"
        mock_tree_element_2.type = "blob"

        mock_tree_element_3 = Mock()
        mock_tree_element_3.path = "src"
        mock_tree_element_3.type = "tree"

        mock_repo = Mock()
        mock_repo.get_git_tree.return_value.tree = [
            mock_tree_element_1,
            mock_tree_element_2,
            mock_tree_element_3
        ]

        mock_github.return_value.get_repo.return_value = mock_repo

        # Execute
        result = get_file_tree("https://github.com/test-owner/test-repo")

        # Assert - should only return files (blobs), not directories (trees)
        assert "README.md" in result
        assert "src/main.py" in result
        assert "src" not in result

    @patch('app.services.github_service.Github')
    def test_get_file_tree_empty_repo(self, mock_github):
        """Test file tree retrieval for empty repository."""
        mock_repo = Mock()
        mock_repo.get_git_tree.return_value.tree = []

        mock_github.return_value.get_repo.return_value = mock_repo

        result = get_file_tree("https://github.com/test-owner/empty-repo")

        assert result == []


class TestSelectStrategicFiles:
    """Test select_strategic_files() function."""

    def test_python_django_project(self):
        """Test file selection for Python Django project."""
        file_tree = [
            "README.md",
            "manage.py",
            "requirements.txt",
            "app/views.py",
            "app/models.py",
            "app/urls.py",
            "tests/test_views.py",
            "tests/test_models.py",
            ".gitignore",
        ]

        result = select_strategic_files(file_tree, "Python")

        # Should select: README, manage.py, core file, test, requirements.txt
        assert "README.md" in result
        assert "manage.py" in result
        assert "requirements.txt" in result
        assert len(result) <= 5
        # At least one test file
        assert any("test" in f for f in result)

    def test_typescript_react_project(self):
        """Test file selection for TypeScript React project."""
        file_tree = [
            "README.md",
            "package.json",
            "src/index.tsx",
            "src/App.tsx",
            "src/components/Button.tsx",
            "src/components/Button.test.tsx",
            "tsconfig.json",
            "node_modules/some-package/index.js",  # Should be excluded
        ]

        result = select_strategic_files(file_tree, "TypeScript")

        assert "README.md" in result
        assert "src/index.tsx" in result
        assert "package.json" in result
        assert len(result) <= 5
        # Should exclude node_modules
        assert not any("node_modules" in f for f in result)

    def test_go_microservice(self):
        """Test file selection for Go microservice."""
        file_tree = [
            "README.md",
            "go.mod",
            "go.sum",
            "cmd/server/main.go",
            "internal/handlers/user.go",
            "internal/handlers/user_test.go",
            "pkg/utils/helper.go",
        ]

        result = select_strategic_files(file_tree, "Go")

        assert "README.md" in result
        assert "cmd/server/main.go" in result
        assert "go.mod" in result
        assert len(result) <= 5

    def test_rust_cli_tool(self):
        """Test file selection for Rust CLI project."""
        file_tree = [
            "README.md",
            "Cargo.toml",
            "Cargo.lock",
            "src/main.rs",
            "src/parser.rs",
            "src/lib.rs",
            "tests/integration_test.rs",
        ]

        result = select_strategic_files(file_tree, "Rust")

        assert "README.md" in result
        assert "src/main.rs" in result
        assert "Cargo.toml" in result
        assert len(result) <= 5

    def test_no_readme(self):
        """Test file selection when README is missing."""
        file_tree = [
            "src/main.py",
            "src/utils.py",
            "tests/test_main.py",
            "requirements.txt",
        ]

        result = select_strategic_files(file_tree, "Python")

        # Should still find other files
        assert "src/main.py" in result
        assert len(result) > 0
        assert len(result) <= 5

    def test_no_tests(self):
        """Test file selection when no test files exist."""
        file_tree = [
            "README.md",
            "main.py",
            "utils.py",
            "requirements.txt",
        ]

        result = select_strategic_files(file_tree, "Python")

        assert "README.md" in result
        assert "main.py" in result
        # Should still return up to 5 files
        assert len(result) <= 5

    def test_max_five_files(self):
        """Test that maximum 5 files are returned."""
        file_tree = [
            "README.md",
            "main.py",
            "utils.py",
            "models.py",
            "views.py",
            "urls.py",
            "tests/test_main.py",
            "tests/test_utils.py",
            "requirements.txt",
            "setup.py",
        ]

        result = select_strategic_files(file_tree, "Python")

        assert len(result) == 5
        # README should always be included if present
        assert "README.md" in result

    def test_empty_file_tree(self):
        """Test file selection with empty file tree."""
        file_tree = []

        result = select_strategic_files(file_tree, "Python")

        assert result == []

    def test_docs_only_repo(self):
        """Test file selection for documentation-only repository."""
        file_tree = [
            "README.md",
            "docs/guide.md",
            "docs/api.md",
            "LICENSE",
        ]

        result = select_strategic_files(file_tree, "Python")

        # Should at least return README
        assert "README.md" in result
        assert len(result) <= 5

    def test_case_insensitive_readme(self):
        """Test that README matching is case-insensitive."""
        file_tree = [
            "readme.md",
            "main.py",
            "requirements.txt",
        ]

        result = select_strategic_files(file_tree, "Python")

        assert "readme.md" in result


class TestFetchFileContents:
    """Test fetch_file_contents() function."""

    @patch('app.services.github_service.Github')
    def test_fetch_single_file_success(self, mock_github):
        """Test successful fetch of single file."""
        # Setup mock
        mock_repo = Mock()
        mock_content = Mock()
        mock_content.decoded_content = b"print('Hello, World!')"

        mock_repo.get_contents.return_value = mock_content
        mock_github.return_value.get_repo.return_value = mock_repo

        # Execute
        result = fetch_file_contents(
            "https://github.com/test-owner/test-repo",
            ["main.py"]
        )

        # Assert
        assert "main.py" in result
        assert result["main.py"] == "print('Hello, World!')"

    @patch('app.services.github_service.Github')
    def test_fetch_multiple_files(self, mock_github):
        """Test fetching multiple files."""
        # Setup mock
        mock_repo = Mock()

        def mock_get_contents(path):
            mock_content = Mock()
            if path == "README.md":
                mock_content.decoded_content = b"# Test Project"
            elif path == "main.py":
                mock_content.decoded_content = b"print('test')"
            return mock_content

        mock_repo.get_contents.side_effect = mock_get_contents
        mock_github.return_value.get_repo.return_value = mock_repo

        # Execute
        result = fetch_file_contents(
            "https://github.com/test-owner/test-repo",
            ["README.md", "main.py"]
        )

        # Assert
        assert len(result) == 2
        assert result["README.md"] == "# Test Project"
        assert result["main.py"] == "print('test')"

    @patch('app.services.github_service.Github')
    def test_fetch_file_not_found(self, mock_github):
        """Test handling of 404 when file not found."""
        # Setup mock
        mock_repo = Mock()
        mock_repo.get_contents.side_effect = GithubException(404, "Not Found")

        mock_github.return_value.get_repo.return_value = mock_repo

        # Execute
        result = fetch_file_contents(
            "https://github.com/test-owner/test-repo",
            ["nonexistent.py"]
        )

        # Should skip the missing file
        assert "nonexistent.py" not in result
        assert len(result) == 0

    @patch('app.services.github_service.Github')
    def test_fetch_binary_file_skipped(self, mock_github):
        """Test that binary files are skipped."""
        # Setup mock
        mock_repo = Mock()
        mock_content = Mock()
        # Simulate binary content that can't be decoded
        mock_content.decoded_content = b"\x89PNG\r\n\x1a\n\x00\x00"

        mock_repo.get_contents.return_value = mock_content
        mock_github.return_value.get_repo.return_value = mock_repo

        # Execute
        result = fetch_file_contents(
            "https://github.com/test-owner/test-repo",
            ["image.png"]
        )

        # Binary file should be skipped
        assert "image.png" not in result or result.get("image.png") is None

    @patch('app.services.github_service.Github')
    def test_fetch_large_file_truncated(self, mock_github):
        """Test that large files (>50KB) are truncated."""
        # Setup mock
        mock_repo = Mock()
        mock_content = Mock()
        # Create content > 50KB
        large_content = "x" * 60000
        mock_content.decoded_content = large_content.encode()

        mock_repo.get_contents.return_value = mock_content
        mock_github.return_value.get_repo.return_value = mock_repo

        # Execute
        result = fetch_file_contents(
            "https://github.com/test-owner/test-repo",
            ["large.py"]
        )

        # File should be truncated to 50KB
        assert "large.py" in result
        assert len(result["large.py"]) <= 50000

    @patch('app.services.github_service.Github')
    def test_fetch_empty_file_list(self, mock_github):
        """Test fetching with empty file list."""
        result = fetch_file_contents(
            "https://github.com/test-owner/test-repo",
            []
        )

        assert result == {}

    @patch('app.services.github_service.Github')
    def test_fetch_partial_success(self, mock_github):
        """Test that partial failures don't break the whole fetch."""
        # Setup mock
        mock_repo = Mock()

        def mock_get_contents(path):
            mock_content = Mock()
            if path == "success.py":
                mock_content.decoded_content = b"# Success"
                return mock_content
            elif path == "missing.py":
                raise GithubException(404, "Not Found")

        mock_repo.get_contents.side_effect = mock_get_contents
        mock_github.return_value.get_repo.return_value = mock_repo

        # Execute
        result = fetch_file_contents(
            "https://github.com/test-owner/test-repo",
            ["success.py", "missing.py"]
        )

        # Should have the successful file
        assert "success.py" in result
        assert result["success.py"] == "# Success"
        # Should skip the missing file
        assert "missing.py" not in result
