"""
GitHub service for repository analysis.

This module provides functions to interact with GitHub API using PyGithub:
- Fetch repository metadata (name, owner, size, stars, language)
- Get repository language breakdown
- Retrieve file tree structure
- Select strategic files for analysis
- Fetch file contents

Uses GitHub Contents API - no repository cloning required.
"""

import os
import random
from typing import Dict, List, Optional
from github import Github, GithubException


def _parse_github_url(url: str) -> tuple[str, str]:
    """
    Parse GitHub URL to extract owner and repository name.

    Args:
        url: GitHub repository URL (https://github.com/owner/repo)

    Returns:
        Tuple of (owner, repo_name)

    Raises:
        ValueError: If URL is not a valid GitHub URL
    """
    if not url.startswith("https://github.com/"):
        raise ValueError("Invalid GitHub URL: must start with 'https://github.com/'")

    # Remove the base URL
    path = url.replace("https://github.com/", "").rstrip("/")

    # Split into parts
    parts = path.split("/")

    if len(parts) < 2:
        raise ValueError("GitHub URL must include owner and repository name")

    # Validate segments are not empty (LL-VALIDATION-001)
    if not parts[0] or not parts[1]:
        raise ValueError("GitHub URL must have non-empty owner and repository name")

    return parts[0], parts[1]


def _get_github_client() -> Github:
    """
    Create authenticated GitHub client.

    Returns:
        Github: Authenticated PyGithub client

    Note:
        Uses GITHUB_TOKEN from environment variables.
        If not set, creates unauthenticated client (rate limit: 60 req/hour)
    """
    token = os.getenv("GITHUB_TOKEN")
    if token:
        return Github(token)
    return Github()  # Unauthenticated (for testing)


def get_repository_metadata(github_url: str) -> Dict[str, any]:
    """
    Fetch repository metadata from GitHub API.

    Args:
        github_url: GitHub repository URL

    Returns:
        Dictionary with repository metadata:
            - name: Repository name
            - owner: Repository owner
            - size_kb: Repository size in KB
            - stars: Stargazers count
            - primary_language: Primary language
            - description: Repository description

    Raises:
        ValueError: If URL is invalid
        GithubException: If repository not found (404) or forbidden (403)
    """
    owner, repo_name = _parse_github_url(github_url)

    client = _get_github_client()
    repo = client.get_repo(f"{owner}/{repo_name}")

    return {
        "name": repo.name,
        "owner": repo.owner.login,
        "size_kb": repo.size,
        "stars": repo.stargazers_count,
        "primary_language": repo.language,
        "description": repo.description,
    }


def get_repository_languages(github_url: str) -> Dict[str, int]:
    """
    Get repository language breakdown.

    Args:
        github_url: GitHub repository URL

    Returns:
        Dictionary mapping language names to bytes of code:
            {"Python": 85000, "JavaScript": 12000}

    Raises:
        ValueError: If URL is invalid
        GithubException: If repository not found (404) or forbidden (403)
    """
    owner, repo_name = _parse_github_url(github_url)

    client = _get_github_client()
    repo = client.get_repo(f"{owner}/{repo_name}")

    return repo.get_languages()


def get_file_tree(github_url: str) -> List[str]:
    """
    Get recursive file tree for repository.

    Args:
        github_url: GitHub repository URL

    Returns:
        List of file paths (only files, not directories):
            ["README.md", "src/main.py", "tests/test_main.py"]

    Raises:
        ValueError: If URL is invalid
        GithubException: If repository not found (404) or forbidden (403)
    """
    owner, repo_name = _parse_github_url(github_url)

    client = _get_github_client()
    repo = client.get_repo(f"{owner}/{repo_name}")

    # Get git tree recursively
    tree = repo.get_git_tree(sha="HEAD", recursive=True)

    # Return only files (blobs), not directories (trees)
    files = [item.path for item in tree.tree if item.type == "blob"]

    return files


# File selection constants (from FILE_SELECTION_STRATEGY.md)

README_PATTERNS = [
    "README.md",
    "README.rst",
    "README.txt",
    "README",
    "readme.md",
    "readme.rst",
    "readme.txt",
    "readme",
]

ENTRY_POINT_PATTERNS = {
    "Python": [
        "main.py",
        "app.py",
        "__main__.py",
        "run.py",
        "manage.py",
        "wsgi.py",
        "src/main.py",
        "app/main.py",
    ],
    "JavaScript": [
        "index.js",
        "app.js",
        "main.js",
        "server.js",
        "src/index.js",
    ],
    "TypeScript": [
        "index.ts",
        "app.ts",
        "main.ts",
        "server.ts",
        "src/index.ts",
        "src/index.tsx",
        "src/app.ts",
    ],
    "Go": [
        "main.go",
        "cmd/main.go",
    ],
    "Rust": [
        "src/main.rs",
        "src/lib.rs",
        "main.rs",
    ],
    "Java": [
        "Main.java",
        "Application.java",
    ],
    "C": [
        "main.c",
        "src/main.c",
    ],
    "C++": [
        "main.cpp",
        "src/main.cpp",
    ],
    "Ruby": [
        "main.rb",
        "app.rb",
        "config.ru",
    ],
    "PHP": [
        "index.php",
        "app.php",
        "public/index.php",
    ],
}

CORE_DIRECTORIES = [
    "src/",
    "lib/",
    "app/",
    "core/",
    "pkg/",
    "internal/",
]

LANGUAGE_EXTENSIONS = {
    "Python": [".py"],
    "JavaScript": [".js", ".jsx"],
    "TypeScript": [".ts", ".tsx"],
    "Go": [".go"],
    "Rust": [".rs"],
    "Java": [".java"],
    "C": [".c", ".h"],
    "C++": [".cpp", ".hpp", ".cc", ".hh"],
    "Ruby": [".rb"],
    "PHP": [".php"],
}

TEST_PATTERNS = [
    "test_",
    "_test.",
    ".test.",
    ".spec.",
]

TEST_DIRECTORIES = [
    "tests/",
    "test/",
    "__tests__/",
    "spec/",
]

CONFIG_FILES = {
    "Python": [
        "requirements.txt",
        "Pipfile",
        "pyproject.toml",
        "setup.py",
        "poetry.lock",
    ],
    "JavaScript": [
        "package.json",
        "package-lock.json",
        "yarn.lock",
    ],
    "TypeScript": [
        "package.json",
        "tsconfig.json",
    ],
    "Go": [
        "go.mod",
        "go.sum",
    ],
    "Rust": [
        "Cargo.toml",
        "Cargo.lock",
    ],
    "Java": [
        "pom.xml",
        "build.gradle",
    ],
    "Ruby": [
        "Gemfile",
        "Gemfile.lock",
    ],
    "PHP": [
        "composer.json",
        "composer.lock",
    ],
}

# Exclusion patterns
EXCLUDE_PATTERNS = [
    "node_modules/",
    "vendor/",
    "dist/",
    "build/",
    ".min.js",
    ".bundle.js",
]


def _find_first_match(file_tree: List[str], patterns: List[str]) -> Optional[str]:
    """Find first file matching any pattern."""
    for pattern in patterns:
        for file_path in file_tree:
            if file_path.lower() == pattern.lower():
                return file_path
            if file_path.endswith(pattern):
                return file_path
    return None


def _find_entry_point(file_tree: List[str], language: Optional[str]) -> Optional[str]:
    """Find main entry point for given language."""
    if not language or language not in ENTRY_POINT_PATTERNS:
        return None

    patterns = ENTRY_POINT_PATTERNS[language]

    for pattern in patterns:
        for file_path in file_tree:
            # Exact match
            if file_path == pattern:
                return file_path
            # Pattern match (e.g., cmd/*/main.go)
            if pattern.endswith(file_path.split("/")[-1]):
                return file_path

    return None


def _find_core_file(file_tree: List[str], language: Optional[str]) -> Optional[str]:
    """Find a random core implementation file."""
    if not language or language not in LANGUAGE_EXTENSIONS:
        return None

    extensions = LANGUAGE_EXTENSIONS[language]

    # Get files from core directories
    core_files = []
    for file_path in file_tree:
        # Check if in core directory
        if any(file_path.startswith(dir_) for dir_ in CORE_DIRECTORIES):
            # Check if has correct extension
            if any(file_path.endswith(ext) for ext in extensions):
                # Exclude test files
                if not any(pattern in file_path for pattern in TEST_PATTERNS):
                    # Exclude excluded patterns
                    if not any(exclude in file_path for exclude in EXCLUDE_PATTERNS):
                        core_files.append(file_path)

    # If no core files found in core directories, look in root
    if not core_files:
        for file_path in file_tree:
            # Only files in root (no directory path)
            if "/" not in file_path:
                # Check if has correct extension
                if any(file_path.endswith(ext) for ext in extensions):
                    # Exclude test files
                    if not any(pattern in file_path for pattern in TEST_PATTERNS):
                        # Exclude excluded patterns
                        if not any(exclude in file_path for exclude in EXCLUDE_PATTERNS):
                            core_files.append(file_path)

    if core_files:
        return random.choice(core_files)

    return None


def _find_test_file(file_tree: List[str], language: Optional[str]) -> Optional[str]:
    """Find a test file."""
    test_files = []

    for file_path in file_tree:
        # Check if in test directory or matches test pattern
        if any(dir_ in file_path for dir_ in TEST_DIRECTORIES):
            test_files.append(file_path)
        elif any(pattern in file_path for pattern in TEST_PATTERNS):
            test_files.append(file_path)

    if test_files:
        return random.choice(test_files)

    return None


def _find_config_file(file_tree: List[str], language: Optional[str]) -> Optional[str]:
    """Find a configuration file."""
    if not language or language not in CONFIG_FILES:
        return None

    patterns = CONFIG_FILES[language]

    for pattern in patterns:
        for file_path in file_tree:
            if file_path == pattern or file_path.endswith(pattern):
                return file_path

    return None


def select_strategic_files(file_tree: List[str], language: Optional[str] = None) -> List[str]:
    """
    Select 3-5 strategic files for code analysis.

    Selection priority (from FILE_SELECTION_STRATEGY.md):
    1. README file (documentation quality indicator)
    2. Main entry point (language-specific)
    3. Core implementation file (from src/, lib/, app/)
    4. Test file (testing practices indicator)
    5. Config file (dependency management)

    Args:
        file_tree: List of all file paths in repository
        language: Primary language of repository (optional)

    Returns:
        List of up to 5 selected file paths

    Example:
        >>> select_strategic_files(
        ...     ["README.md", "main.py", "src/utils.py", "tests/test_main.py"],
        ...     "Python"
        ... )
        ["README.md", "main.py", "src/utils.py", "tests/test_main.py"]
    """
    if not file_tree:
        return []

    selected_files = []

    # Priority 1: README
    readme = _find_first_match(file_tree, README_PATTERNS)
    if readme:
        selected_files.append(readme)

    # Priority 2: Entry point
    if len(selected_files) < 5:
        entry_point = _find_entry_point(file_tree, language)
        if entry_point and entry_point not in selected_files:
            selected_files.append(entry_point)

    # Priority 3: Core file
    if len(selected_files) < 5:
        core_file = _find_core_file(file_tree, language)
        if core_file and core_file not in selected_files:
            selected_files.append(core_file)

    # Priority 4: Test file
    if len(selected_files) < 5:
        test_file = _find_test_file(file_tree, language)
        if test_file and test_file not in selected_files:
            selected_files.append(test_file)

    # Priority 5: Config file
    if len(selected_files) < 5:
        config_file = _find_config_file(file_tree, language)
        if config_file and config_file not in selected_files:
            selected_files.append(config_file)

    return selected_files[:5]  # Max 5 files


# File size limit for analysis (50KB per file)
MAX_FILE_SIZE = 50_000


def fetch_file_contents(github_url: str, file_paths: List[str]) -> Dict[str, str]:
    """
    Fetch raw file contents from GitHub repository.

    Uses GitHub Contents API to read files without cloning.
    Handles binary files, large files, and missing files gracefully.

    Args:
        github_url: GitHub repository URL
        file_paths: List of file paths to fetch

    Returns:
        Dictionary mapping file paths to their contents:
            {"README.md": "# Project\n...", "main.py": "def main():..."}

        Binary files and files that fail to fetch are excluded.

    Features:
        - Binary file detection and skipping
        - Large file truncation (>50KB → first 50KB)
        - Graceful error handling (404, encoding errors)
        - UTF-8 decoding with fallback

    Example:
        >>> fetch_file_contents(
        ...     "https://github.com/owner/repo",
        ...     ["README.md", "src/main.py"]
        ... )
        {"README.md": "# My Project", "src/main.py": "def main(): pass"}
    """
    if not file_paths:
        return {}

    owner, repo_name = _parse_github_url(github_url)
    client = _get_github_client()
    repo = client.get_repo(f"{owner}/{repo_name}")

    file_contents = {}

    for file_path in file_paths:
        try:
            # Fetch file content
            content = repo.get_contents(file_path)

            # Get raw bytes
            raw_content = content.decoded_content

            # Try to decode as UTF-8
            try:
                # Truncate if too large (>50KB)
                if len(raw_content) > MAX_FILE_SIZE:
                    raw_content = raw_content[:MAX_FILE_SIZE]

                # Decode to string
                text_content = raw_content.decode("utf-8")

                # Store the content
                file_contents[file_path] = text_content

            except UnicodeDecodeError:
                # Binary file - skip it
                continue

        except GithubException as e:
            # File not found (404) or other errors - skip it
            if e.status == 404:
                continue
            # For other errors, also skip
            continue

        except Exception:
            # Any other unexpected errors - skip the file
            continue

    return file_contents
