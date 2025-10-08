# Project Structure: Repo-to-Cat

This document defines the complete directory structure for the Repo-to-Cat project.

```
repo-to-cat/
│
├── app/                                # Main application package
│   ├── __init__.py
│   ├── main.py                         # FastAPI application entry point
│   │
│   ├── api/                            # API layer
│   │   ├── __init__.py
│   │   ├── routes.py                   # API endpoint definitions
│   │   └── schemas.py                  # Pydantic request/response models
│   │
│   ├── core/                           # Core configuration and utilities
│   │   ├── __init__.py
│   │   ├── config.py                   # Environment and app configuration
│   │   ├── database.py                 # Database connection and session
│   │   └── exceptions.py               # Custom exception classes
│   │
│   ├── models/                         # Database models
│   │   ├── __init__.py
│   │   └── database.py                 # SQLAlchemy ORM models (User, Generation)
│   │
│   ├── services/                       # Business logic layer
│   │   ├── __init__.py
│   │   ├── github_service.py           # GitHub API integration
│   │   ├── analysis_service.py         # Code quality analysis logic
│   │   └── image_service.py            # Image generation and storage
│   │
│   ├── providers/                      # External API providers
│   │   ├── __init__.py
│   │   ├── openrouter.py               # OpenRouter LLM client
│   │   └── together_ai.py              # Together.ai image generation client
│   │
│   ├── langgraph/                      # LangGraph workflow orchestration
│   │   ├── __init__.py
│   │   ├── workflow.py                 # Main LangGraph pipeline definition
│   │   ├── nodes.py                    # Individual workflow nodes
│   │   └── state.py                    # State management (TypedDict definitions)
│   │
│   └── utils/                          # Utility functions
│       ├── __init__.py
│       ├── validators.py               # Input validation helpers
│       └── helpers.py                  # General helper functions
│
├── config/                             # Configuration files
│   ├── __init__.py
│   └── mappings.py                     # Cat attribute mappings (hardcoded configs)
│
├── alembic/                            # Database migrations
│   ├── versions/                       # Migration scripts
│   ├── env.py                          # Alembic environment config
│   └── script.py.mako                  # Migration template
│
├── tests/                              # Test suite
│   ├── __init__.py
│   ├── conftest.py                     # Pytest fixtures and configuration
│   │
│   ├── unit/                           # Unit tests
│   │   ├── __init__.py
│   │   ├── test_github_service.py
│   │   ├── test_analysis_service.py
│   │   ├── test_image_service.py
│   │   ├── test_openrouter.py
│   │   ├── test_together_ai.py
│   │   ├── test_nodes.py
│   │   └── test_mappings.py
│   │
│   ├── integration/                    # Integration tests
│   │   ├── __init__.py
│   │   ├── test_workflow.py            # End-to-end LangGraph workflow tests
│   │   └── test_api_endpoints.py       # API integration tests
│   │
│   └── fixtures/                       # Test data and fixtures
│       ├── sample_repos.py             # Sample repository data
│       ├── sample_code.py              # Sample code snippets
│       └── mock_responses.py           # Mock API responses
│
├── generated_images/                   # Local image storage (gitignored)
│   └── .gitkeep                        # Keep directory in git
│
├── scripts/                            # Utility scripts
│   ├── init_db.py                      # Database initialization script
│   ├── seed_data.py                    # Seed sample data for testing
│   └── test_apis.py                    # Manual API testing script
│
├── docs/                               # Additional documentation
│   ├── api.md                          # API documentation
│   ├── deployment.md                   # Deployment guide
│   └── architecture.md                 # Architecture overview
│
├── .github/                            # GitHub-specific files
│   └── workflows/                      # CI/CD workflows
│       ├── test.yml                    # Automated testing
│       └── lint.yml                    # Linting checks
│
├── docker-compose.yml                  # Docker services configuration
├── Dockerfile                          # Docker image definition
├── requirements.txt                    # Python dependencies (pip3)
├── alembic.ini                         # Alembic configuration
│
├── .env.example                        # Example environment variables
├── .env                                # Actual environment variables (gitignored)
├── .gitignore                          # Git ignore rules
│
├── PRD.md                              # Product Requirements Document
├── HANDOFF.md                          # Development checklist
├── PROJECT_STRUCTURE.md                # This file
├── DEVELOPMENT_RULES.md                # Development principles
├── START.md                            # Initial project notes
└── README.md                           # Project overview and setup
```

---

## Directory Descriptions

### `/app` - Main Application
Contains all application code organized by layer (API, services, models, etc.)

### `/app/api` - API Layer
- **routes.py**: FastAPI endpoint definitions (`/generate`, `/health`)
- **schemas.py**: Pydantic models for request/response validation

### `/app/core` - Core Infrastructure
- **config.py**: Application settings, environment variables (using pydantic-settings)
- **database.py**: SQLAlchemy engine, session management
- **exceptions.py**: Custom exceptions (e.g., `RepositoryNotFoundError`, `AnalysisFailedError`)

### `/app/models` - Database Models
- **database.py**: SQLAlchemy ORM models (`User`, `Generation`)

### `/app/services` - Business Logic
- **github_service.py**: GitHub API client, metadata fetching, file selection
- **analysis_service.py**: Code quality analysis, heuristics, LLM integration
- **image_service.py**: Image prompt generation, storage, retrieval

### `/app/providers` - External API Clients
- **openrouter.py**: OpenRouter API client for LLM-based code analysis
- **together_ai.py**: Together.ai client for Flux Kontext image generation

### `/app/langgraph` - Workflow Orchestration
- **workflow.py**: LangGraph `StateGraph` definition and compilation
- **nodes.py**: Individual workflow nodes (extract_metadata, analyze_code, etc.)
- **state.py**: `WorkflowState` TypedDict and state management

### `/config` - Configuration Files
- **mappings.py**: Hardcoded mappings (language backgrounds, quality indicators, cat attributes)

### `/alembic` - Database Migrations
- Alembic migration scripts for database schema evolution

### `/tests` - Test Suite
- **unit/**: Unit tests for individual components (80%+ coverage target)
- **integration/**: End-to-end tests for workflows and API
- **fixtures/**: Reusable test data and mock responses

### `/generated_images` - Image Storage
- Local storage for generated cat images (gitignored except `.gitkeep`)

### `/scripts` - Utility Scripts
- **init_db.py**: Initialize database and run migrations
- **seed_data.py**: Populate database with test data
- **test_apis.py**: Manual script to test external APIs

### `/docs` - Documentation
- Additional documentation for API, deployment, architecture

---

## Key Files

### `app/main.py`
```python
# FastAPI application entry point
# - Initialize FastAPI app
# - Configure CORS
# - Include routers
# - Add middleware
# - Mount static files
```

### `app/api/routes.py`
```python
# API endpoints:
# - POST /generate
# - GET /health
```

### `app/langgraph/workflow.py`
```python
# LangGraph workflow definition
# Nodes: extract_metadata → select_files → fetch_files → analyze_code
#        → map_attributes → generate_prompt → generate_image → save_to_db
```

### `config/mappings.py`
```python
# Hardcoded configurations:
# - LANGUAGE_BACKGROUNDS
# - QUALITY_INDICATORS
# - CAT_SIZE_MAPPING
# - CAT_AGE_MAPPING
# - CAT_EXPRESSION_MAPPING
```

### `docker-compose.yml`
```yaml
# Services:
# - app: FastAPI application
# - db: PostgreSQL database
# - volumes: generated_images, postgres_data
```

### `requirements.txt`
```
# Main dependencies:
# - fastapi, uvicorn
# - langchain, langgraph
# - openai (for OpenRouter)
# - together
# - PyGithub, requests
# - sqlalchemy, psycopg2-binary, alembic
# - pytest, pytest-asyncio, pytest-cov
```

---

## File Naming Conventions

1. **Python files**: `snake_case.py`
2. **Test files**: `test_<module_name>.py`
3. **Config files**: `UPPER_CASE.md` or `lowercase.yml`
4. **Directories**: `lowercase`

---

## Import Guidelines

### Absolute Imports (Preferred)
```python
from app.services.github_service import GitHubService
from app.providers.openrouter import OpenRouterClient
from config.mappings import LANGUAGE_BACKGROUNDS
```

### Relative Imports (Within Package)
```python
# In app/services/analysis_service.py
from .github_service import GitHubService
from ..providers.openrouter import OpenRouterClient
```

---

## Next Steps

After reviewing this structure:
1. Begin Stage 1.1 in HANDOFF.md: Create directory structure
2. Create empty `__init__.py` files for all packages
3. Set up version control and `.gitignore`
4. Initialize pip3 project with `requirements.txt`

---

**Last Updated:** 2025-10-07
