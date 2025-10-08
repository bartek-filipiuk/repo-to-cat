# File Selection Strategy for Code Analysis

## Overview
This document defines the strategy for selecting 3-5 representative files from any GitHub repository for code quality analysis. The selection is language-aware and prioritized by file importance.

---

## Selection Algorithm

### Step 1: Always Include (Priority 1)
**README File** - Project documentation quality indicator
```python
PRIORITY_1_PATTERNS = [
    "README.md",
    "README.rst",
    "README.txt",
    "README",
    "readme.md",
]
```
**Why:** README quality correlates with project maturity and documentation standards.

---

### Step 2: Language-Specific Entry Points (Priority 2)

Select **ONE** main entry point based on detected primary language:

#### Python
```python
PYTHON_ENTRY_POINTS = [
    "main.py",
    "app.py",
    "__main__.py",
    "run.py",
    "manage.py",           # Django
    "wsgi.py",             # Flask/Django
    "src/main.py",
    "app/main.py",
]
```

#### JavaScript/TypeScript
```python
JS_TS_ENTRY_POINTS = [
    "index.js",
    "index.ts",
    "app.js",
    "app.ts",
    "main.js",
    "main.ts",
    "server.js",
    "src/index.js",
    "src/index.ts",
    "src/app.ts",
]
```

#### Go
```python
GO_ENTRY_POINTS = [
    "main.go",
    "cmd/main.go",
    "cmd/*/main.go",       # Common Go project structure
]
```

#### Rust
```python
RUST_ENTRY_POINTS = [
    "src/main.rs",
    "src/lib.rs",
    "main.rs",
]
```

#### Java
```python
JAVA_ENTRY_POINTS = [
    "src/main/java/**/Main.java",
    "src/main/java/**/Application.java",
    "src/main/java/**/*Application.java",  # Spring Boot
]
```

#### C/C++
```python
C_CPP_ENTRY_POINTS = [
    "main.c",
    "main.cpp",
    "src/main.c",
    "src/main.cpp",
]
```

#### Ruby
```python
RUBY_ENTRY_POINTS = [
    "main.rb",
    "app.rb",
    "config.ru",           # Rack applications
    "bin/rails",           # Rails
]
```

#### PHP
```python
PHP_ENTRY_POINTS = [
    "index.php",
    "app.php",
    "public/index.php",    # Laravel/Symfony
]
```

---

### Step 3: Core Implementation File (Priority 3)

Select **ONE** random file from core directories:

```python
CORE_DIRECTORIES = [
    "src/",
    "lib/",
    "app/",
    "core/",
    "pkg/",               # Go
    "internal/",          # Go
]

# Filter by language extension
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
```

**Selection Logic:**
```python
# 1. Get all files from core directories
core_files = get_files_from_dirs(CORE_DIRECTORIES)

# 2. Filter by language extension
filtered_files = [f for f in core_files if has_extension(f, language)]

# 3. Exclude test files and examples
filtered_files = exclude_patterns(filtered_files, ["test_", "_test.", "spec.", "example"])

# 4. Pick random file (preferably medium-sized, 100-500 lines)
selected_file = random.choice(filtered_files)
```

---

### Step 4: Test File (Priority 4)

Select **ONE** test file to assess testing practices:

```python
TEST_PATTERNS = [
    "test_*.py",          # Python pytest
    "tests/*.py",
    "*_test.py",
    "*.test.js",          # JavaScript Jest
    "*.spec.js",
    "*.test.ts",          # TypeScript
    "*.spec.ts",
    "*_test.go",          # Go
    "*_test.rs",          # Rust
    "**/*Test.java",      # Java JUnit
    "*_spec.rb",          # Ruby RSpec
]

TEST_DIRECTORIES = [
    "tests/",
    "test/",
    "__tests__/",
    "spec/",
]
```

**Why:** Test presence and quality indicate code maintainability.

---

### Step 5: Configuration File (Priority 5)

Select **ONE** config file to assess dependencies and tooling:

```python
CONFIG_FILES_BY_LANGUAGE = {
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
        "pom.xml",          # Maven
        "build.gradle",     # Gradle
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

# Also check for linter configs (good practice indicator)
LINTER_CONFIGS = [
    ".eslintrc.json",
    ".eslintrc.js",
    "pylintrc",
    ".flake8",
    "ruff.toml",
    ".rubocop.yml",
    "phpcs.xml",
]
```

---

## Complete Selection Flow

```python
def select_files(repo_url: str, file_tree: list) -> list[str]:
    """
    Select 3-5 representative files from a repository.

    Returns:
        List of file paths (3-5 files)
    """
    selected_files = []

    # Step 1: README (Priority 1)
    readme = find_first_match(file_tree, PRIORITY_1_PATTERNS)
    if readme:
        selected_files.append(readme)

    # Step 2: Main entry point (Priority 2)
    language = detect_primary_language(repo_url)
    entry_point = find_entry_point(file_tree, language)
    if entry_point and entry_point not in selected_files:
        selected_files.append(entry_point)

    # Step 3: Core implementation file (Priority 3)
    if len(selected_files) < 5:
        core_file = find_core_file(file_tree, language)
        if core_file and core_file not in selected_files:
            selected_files.append(core_file)

    # Step 4: Test file (Priority 4)
    if len(selected_files) < 5:
        test_file = find_test_file(file_tree, language)
        if test_file and test_file not in selected_files:
            selected_files.append(test_file)

    # Step 5: Config file (Priority 5)
    if len(selected_files) < 5:
        config_file = find_config_file(file_tree, language)
        if config_file and config_file not in selected_files:
            selected_files.append(config_file)

    return selected_files[:5]  # Max 5 files
```

---

## Fallback Strategy

If we can't find files in the priority order:

1. **No README?** → Look for `CONTRIBUTING.md`, `docs/README.md`
2. **No entry point?** → Pick most recently modified file in `src/`
3. **No core file?** → Pick random file from root directory
4. **No tests?** → Note in analysis (negative signal)
5. **No config?** → Check for `.gitignore` or `Makefile`

---

## Example Scenarios

### Scenario 1: Python Django Project
```
Repository: https://github.com/owner/django-app
Primary Language: Python (85%)

Selected Files:
1. README.md                          ← Priority 1
2. manage.py                          ← Priority 2 (Django entry point)
3. app/views.py                       ← Priority 3 (random core file)
4. tests/test_views.py                ← Priority 4 (test file)
5. requirements.txt                   ← Priority 5 (config)
```

### Scenario 2: TypeScript React Project
```
Repository: https://github.com/owner/react-app
Primary Language: TypeScript (72%)

Selected Files:
1. README.md                          ← Priority 1
2. src/index.tsx                      ← Priority 2 (entry point)
3. src/components/Button.tsx          ← Priority 3 (random core)
4. src/components/Button.test.tsx     ← Priority 4 (test)
5. package.json                       ← Priority 5 (config)
```

### Scenario 3: Go Microservice
```
Repository: https://github.com/owner/go-service
Primary Language: Go (95%)

Selected Files:
1. README.md                          ← Priority 1
2. cmd/server/main.go                 ← Priority 2 (entry point)
3. internal/handlers/user.go          ← Priority 3 (core)
4. internal/handlers/user_test.go     ← Priority 4 (test)
5. go.mod                             ← Priority 5 (config)
```

### Scenario 4: Rust CLI Tool
```
Repository: https://github.com/owner/rust-cli
Primary Language: Rust (98%)

Selected Files:
1. README.md                          ← Priority 1
2. src/main.rs                        ← Priority 2 (entry point)
3. src/parser.rs                      ← Priority 3 (core module)
4. tests/integration_test.rs          ← Priority 4 (test)
5. Cargo.toml                         ← Priority 5 (config)
```

---

## Edge Cases

### Monorepo
```
If repository contains multiple projects:
- Detect primary language from root
- Focus on root-level files first
- If no root files, select from largest subdirectory
```

### Documentation-Only Repo
```
If no code files found:
- Select README.md
- Select any .md files in docs/
- Return analysis: "Documentation-only repository"
```

### No Clear Entry Point
```
If can't find entry point:
- Pick most starred/largest file in root
- Pick most recently modified file
- Ensure we still get 3-5 files total
```

### Binary/Generated Files
```
Skip files:
- Lock files > 1MB
- node_modules/*
- vendor/*
- dist/*, build/*
- *.min.js, *.bundle.js
- Images, videos
```

---

## File Size Limits

```python
MAX_FILE_SIZE = 50_000  # 50KB per file (approx 1000-1500 lines)

# If file > 50KB, read first 50KB only
# This prevents analyzing generated/minified code
```

---

## Quality Signals from File Selection

After selecting files, we can already infer some quality signals:

```python
QUALITY_SIGNALS = {
    "readme_exists": +1,
    "has_tests": +2,
    "has_config": +1,
    "has_linter_config": +1,
    "entry_point_found": +1,
    "core_files_exist": +1,
}

# Example scoring:
# All files found + linter = 7/7 → High quality indicator
# Only README + entry point = 2/7 → Low quality indicator
```

---

## Implementation Notes

1. **Caching:** Cache file tree for 5 minutes to avoid repeated API calls
2. **Parallelization:** Fetch all 5 files in parallel using asyncio
3. **Error Handling:** If file fetch fails (404), skip and try next priority
4. **Logging:** Log which files were selected for debugging

---

## Future Enhancements (Post-MVP)

- [ ] Machine learning model to predict "best" files to analyze
- [ ] User preference for file selection (via API parameter)
- [ ] Support for analyzing specific branches/commits
- [ ] Weighted selection based on file modification frequency
- [ ] Support for more languages (Kotlin, Swift, Scala, etc.)

---

**Last Updated:** 2025-10-07
