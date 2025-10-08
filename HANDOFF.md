# HANDOFF: Repo-to-Cat Development Checklist

**Project:** Repo-to-Cat - GitHub Repository Quality Visualizer
**Status:** Planning → Development
**Last Updated:** 2025-10-07

---

## 📋 Development Stages

Following the incremental development principles from `DEVELOPMENT_RULES.md`, this document tracks all development tasks. Work on **ONE checkbox at a time**, get approval, then proceed.

---

## 🔄 Pull Request Workflow

**IMPORTANT:** Starting from Stage 1.2, each stage will be developed on a feature branch and submitted as a Pull Request.

### Before Starting Each Stage:
1. ✅ Ensure you're on `main` branch
2. ✅ Pull latest changes: `git pull origin main`
3. ✅ Create feature branch: `git checkout -b feature/stage-X.Y-description`
4. ✅ Work on stage checkboxes (one at a time, following TDD)

### After Completing Each Stage:
1. ✅ Commit all changes with descriptive message
2. ✅ Push feature branch: `git push -u origin feature/stage-X.Y-description`
3. ✅ Create Pull Request using `gh` CLI:
   ```bash
   gh pr create --title "Stage X.Y: Title" \
     --body "Summary of changes, tests, checklist" \
     --base main \
     --head feature/stage-X.Y-description
   ```
4. ✅ Wait for review and approval
5. ✅ After approval, merge PR and delete branch
6. ✅ Checkout main and pull: `git checkout main && git pull origin main`

### PR Template:
```markdown
## Stage X.Y: [Title] ✅

### Summary
[Brief description of what was accomplished]

### Changes Made
- [List of changes]

### Tests
- [Test results and coverage]

### Checklist
- [x] All checkboxes from HANDOFF.md completed
- [x] Tests written and passing
- [x] Code reviewed

**Next:** Stage X.Z - [Next Stage Name]
```

---

## 📋 Stage Completion Checklist Template

Before creating PR for each stage, verify:

```markdown
### Before Creating PR:
- [ ] All stage checkboxes marked complete (✅)
- [ ] Run tests: `pytest tests/ -v --cov=app --cov-report=term`
- [ ] Coverage ≥ 80% for new code
- [ ] All tests passing ✅
- [ ] Stage-specific manual verification completed
- [ ] Code committed with proper message format
- [ ] HANDOFF.md updated with ✅ marks
- [ ] Ready to push and create PR

### Test Commands:
# Run all tests with coverage
pytest tests/ -v --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_config.py -v

# Run integration tests only
pytest tests/integration/ -v

# Check Docker (if applicable)
docker-compose up -d
docker-compose ps
docker-compose logs

# FastAPI server test (if applicable)
uvicorn app.main:app --reload
curl http://localhost:8000/health
```

---

## Stage 1: Project Setup & Infrastructure ⚙️

### 1.1 Basic Project Structure ✅
- [x] Create directory structure as defined in PRD.md
- [x] Initialize Python project with `requirements.txt`
- [x] Create `.env.example` file with all required environment variables
- [x] Create `.gitignore` (include `.env`, `generated_images/`, `__pycache__/`)
- [x] Create basic `README.md` with setup instructions

**Stage 1.1 Completion Checklist:**
- [x] All checkboxes marked ✅
- [x] Manual verification: Directory structure matches PROJECT_STRUCTURE.md
- [x] Manual verification: `requirements.txt` has all dependencies
- [x] Manual verification: `.env.example` has all variables from PRD.md
- [x] Test: `python3 -m pytest tests/unit/test_config.py -v` (passed ✅)
- [x] Git: Committed to `main` branch with message "Stage 1.1: Basic project structure"

### 1.2 Docker & Database Setup
- [x] Create `Dockerfile` for Python app
- [x] Create `docker-compose.yml` with PostgreSQL service
- [x] Test Docker build and container startup
- [x] Create database initialization script
- [x] Create Alembic migration setup for database schema
- [x] Create initial migration for `users` and `generations` tables
- [x] Test database connection from Python

**Stage 1.2 Completion Checklist:**
- [x] All checkboxes marked ✅
- [x] Test: `docker-compose build` (succeeds)
- [x] Test: `docker-compose up -d` (containers running)
- [x] Test: `docker-compose ps` (postgres healthy)
- [x] Test: `docker-compose logs postgres` (no errors)
- [x] Test: `alembic upgrade head` (migration succeeds)
- [x] Test: `pytest tests/unit/test_database.py -v` (DB connection works)
- [x] Manual: Check PostgreSQL with `psql` or DB client
- [ ] Git: All changes committed on `feature/stage-1.2-docker-database` branch
- [ ] PR: Ready to create PR to `main` branch

### 1.3 FastAPI Skeleton
- [ ] Create `app/main.py` with basic FastAPI app
- [x] Create `app/core/config.py` for environment configuration (completed in 1.1)
- [ ] Create `app/core/database.py` for SQLAlchemy setup
- [ ] Add CORS middleware configuration
- [ ] Test FastAPI server startup (`uvicorn app.main:app --reload`)
- [ ] Create basic health check endpoint structure

**Stage 1.3 Completion Checklist:**
- [ ] All checkboxes marked ✅
- [ ] Test: `uvicorn app.main:app --reload` (server starts without errors)
- [ ] Test: `curl http://localhost:8000/health` (returns 200 OK)
- [ ] Test: `curl http://localhost:8000/docs` (Swagger UI loads)
- [ ] Test: `pytest tests/unit/test_main.py -v` (basic app tests pass)
- [ ] Test: `pytest tests/unit/test_database.py -v` (SQLAlchemy setup works)
- [ ] Coverage: Run `pytest --cov=app --cov-report=term` (≥80%)
- [ ] Manual: Verify CORS works (if testing from frontend)
- [ ] Git: All changes committed on `feature/stage-1.3-fastapi-skeleton` branch
- [ ] PR: Ready to create PR to `main` branch

---

## Stage 2: Configuration & Models 📦

### 2.1 Configuration Management
- [ ] Create `config/mappings.py` with cat attribute mappings
- [ ] Create `LANGUAGE_BACKGROUNDS` dictionary
- [ ] Create `QUALITY_INDICATORS` dictionary
- [ ] Create `CAT_SIZE_MAPPING` dictionary
- [ ] Write tests for configuration loading

### 2.2 Database Models
- [ ] Create `app/models/database.py` with SQLAlchemy models
- [ ] Implement `User` model
- [ ] Implement `Generation` model
- [ ] Add indexes for performance (github_url, created_at)
- [ ] Write unit tests for models

### 2.3 API Schemas
- [ ] Create `app/api/schemas.py` with Pydantic models
- [ ] Create `GenerateRequest` schema
- [ ] Create `GenerateResponse` schema
- [ ] Create `HealthCheckResponse` schema
- [ ] Create `RepositoryInfo` schema
- [ ] Create `AnalysisResult` schema
- [ ] Create `CatAttributes` schema
- [ ] Write validation tests for schemas

---

## Stage 3: GitHub Service Integration 🐙

### 3.1 GitHub API Client
- [ ] Create `app/services/github_service.py`
- [ ] Implement authentication with GITHUB_TOKEN
- [ ] Implement `get_repository_metadata()` function
- [ ] Implement `get_repository_languages()` function
- [ ] Implement `get_file_tree()` function
- [ ] Write unit tests with mocked GitHub responses

### 3.2 File Selection Logic
- [ ] Implement `select_strategic_files()` function
- [ ] Add logic to prioritize README files
- [ ] Add logic to find main entry point (main.py, index.js, etc.)
- [ ] Add logic to select random core files from /src or /lib
- [ ] Add logic to find test files
- [ ] Add logic to find config files
- [ ] Write tests for file selection with various repo structures

### 3.3 File Content Fetching
- [ ] Implement `fetch_file_contents()` function
- [ ] Handle binary file detection and skipping
- [ ] Handle large file truncation (>10KB per file)
- [ ] Add error handling for 404s and rate limits
- [ ] Write integration tests (may use test repos)

---

## Stage 4: AI Provider Integrations 🤖

### 4.1 OpenRouter Provider
- [ ] Create `app/providers/openrouter.py`
- [ ] Implement OpenRouter client initialization
- [ ] Implement `analyze_code_quality()` function
- [ ] Create prompt template for code analysis
- [ ] Handle API errors and retries
- [ ] Write unit tests with mocked responses
- [ ] Test with real OpenRouter API (manual test)

### 4.2 Together.ai Provider
- [ ] Create `app/providers/together_ai.py`
- [ ] Implement Together.ai client initialization
- [ ] Implement `generate_cat_image()` function using Flux Kontext
- [ ] Configure image parameters (1024x768, prompt, model)
- [ ] Handle API errors and retries
- [ ] Implement image download and base64 encoding
- [ ] Write unit tests with mocked responses
- [ ] Test with real Together.ai API (manual test)

---

## Stage 5: Code Analysis Service 🔍

### 5.1 Analysis Logic
- [ ] Create `app/services/analysis_service.py`
- [ ] Implement `calculate_code_quality_score()` function
- [ ] Implement line length analysis
- [ ] Implement function length detection
- [ ] Implement nesting depth detection
- [ ] Implement comment ratio calculation
- [ ] Implement test file detection
- [ ] Implement type hints detection (Python-specific)
- [ ] Write comprehensive unit tests

### 5.2 LLM-Based Analysis
- [ ] Implement `analyze_with_llm()` function
- [ ] Create structured prompt for OpenRouter
- [ ] Parse LLM response into structured metrics
- [ ] Combine heuristics + LLM analysis
- [ ] Write tests with sample code snippets

---

## Stage 6: LangGraph Workflow 🔄

### 6.1 State Management
- [ ] Create `app/langgraph/state.py`
- [ ] Define `WorkflowState` TypedDict
- [ ] Add fields: github_url, metadata, files, analysis, cat_attrs, image
- [ ] Write state validation tests

### 6.2 Workflow Nodes
- [ ] Create `app/langgraph/nodes.py`
- [ ] Implement `extract_metadata_node()`
- [ ] Implement `select_files_node()`
- [ ] Implement `fetch_files_node()`
- [ ] Implement `analyze_code_node()`
- [ ] Implement `map_attributes_node()`
- [ ] Implement `generate_prompt_node()`
- [ ] Implement `generate_image_node()`
- [ ] Implement `save_to_db_node()`
- [ ] Write unit tests for each node

### 6.3 Workflow Definition
- [ ] Create `app/langgraph/workflow.py`
- [ ] Define LangGraph StateGraph
- [ ] Add all nodes to graph
- [ ] Define edges between nodes
- [ ] Add conditional edges (error handling)
- [ ] Compile workflow
- [ ] Write integration tests for full workflow

---

## Stage 7: Image Service 🎨

### 7.1 Image Generation
- [ ] Create `app/services/image_service.py`
- [ ] Implement `map_analysis_to_cat_attributes()` function
- [ ] Implement `create_image_prompt()` function
- [ ] Use mapping config from `config/mappings.py`
- [ ] Write tests for prompt generation

### 7.2 Image Storage
- [ ] Implement `save_image_locally()` function
- [ ] Create `generated_images/` directory structure
- [ ] Implement UUID-based filename generation
- [ ] Implement base64 encoding for response
- [ ] Add file cleanup for old images (optional)
- [ ] Write tests for image storage

---

## Stage 8: API Endpoints 🌐

### 8.1 Health Check Endpoint
- [ ] Create `app/api/routes.py`
- [ ] Implement `GET /health` endpoint
- [ ] Check GitHub API connectivity
- [ ] Check OpenRouter API connectivity
- [ ] Check Together.ai API connectivity
- [ ] Check database connectivity
- [ ] Measure response times
- [ ] Write API tests for health endpoint

### 8.2 Generate Endpoint
- [ ] Implement `POST /generate` endpoint
- [ ] Validate GitHub URL format
- [ ] Trigger LangGraph workflow
- [ ] Handle private repository errors (403)
- [ ] Handle not found errors (404)
- [ ] Handle analysis failures (500)
- [ ] Return complete JSON response with image
- [ ] Write comprehensive API tests

### 8.3 Static File Serving
- [ ] Mount static files for `/generated_images/`
- [ ] Add CORS headers for image access
- [ ] Test image URL access from response

---

## Stage 9: Error Handling & Validation ⚠️

### 9.1 Input Validation
- [ ] Validate GitHub URL format (regex)
- [ ] Validate repository exists before processing
- [ ] Handle invalid/malformed URLs
- [ ] Write validation tests

### 9.2 Error Handling
- [ ] Implement custom exception classes
- [ ] Add global exception handler to FastAPI
- [ ] Handle GitHub API errors gracefully
- [ ] Handle OpenRouter API errors gracefully
- [ ] Handle Together.ai API errors gracefully
- [ ] Handle database errors gracefully
- [ ] Return user-friendly error messages
- [ ] Write tests for all error scenarios

---

## Stage 10: Testing & Quality 🧪

### 10.1 Unit Tests
- [ ] Write tests for all services
- [ ] Write tests for all providers
- [ ] Write tests for LangGraph nodes
- [ ] Write tests for utilities
- [ ] Achieve 80%+ code coverage

### 10.2 Integration Tests
- [ ] Write end-to-end test for `/generate` endpoint
- [ ] Write end-to-end test for `/health` endpoint
- [ ] Test with real GitHub repositories (small samples)
- [ ] Test error scenarios (private repo, 404, etc.)

### 10.3 Code Quality
- [ ] Run linter (ruff or flake8)
- [ ] Run type checker (mypy)
- [ ] Fix all linting errors
- [ ] Fix all type errors
- [ ] Review code coverage report

---

## Stage 11: Documentation 📚

### 11.1 README
- [ ] Write comprehensive README.md
- [ ] Add project description
- [ ] Add setup instructions
- [ ] Add Docker setup guide
- [ ] Add environment variables documentation
- [ ] Add API usage examples
- [ ] Add troubleshooting section

### 11.2 API Documentation
- [ ] Ensure FastAPI auto-docs are complete
- [ ] Add docstrings to all endpoints
- [ ] Add request/response examples
- [ ] Test `/docs` endpoint

### 11.3 Code Documentation
- [ ] Add docstrings to all functions
- [ ] Add type hints to all functions
- [ ] Add inline comments for complex logic

---

## Stage 12: Deployment Preparation 🚀

### 12.1 Docker Finalization
- [ ] Test full Docker Compose setup
- [ ] Optimize Docker image size
- [ ] Add health check to Docker Compose
- [ ] Test container restart behavior
- [ ] Document Docker commands

### 12.2 Production Checklist
- [ ] Create production `.env` template
- [ ] Add security headers to FastAPI
- [ ] Configure logging (structured logs)
- [ ] Add request ID tracking
- [ ] Test with production-like data volume

### 12.3 Deployment Guide
- [ ] Write deployment instructions for cloud (AWS/GCP/Azure)
- [ ] Document environment setup
- [ ] Document database migration process
- [ ] Document monitoring setup

---

## Stage 13: MVP Review & Launch ✅

### 13.1 Final Review
- [ ] Review all tests pass
- [ ] Review code coverage ≥80%
- [ ] Review all endpoints working
- [ ] Review error handling complete
- [ ] Review documentation complete

### 13.2 Manual Testing
- [ ] Test with 5 different public repositories
- [ ] Test with various languages (Python, JS, Go, Rust)
- [ ] Test with different repo sizes
- [ ] Verify cat images match code quality
- [ ] Verify response JSON structure

### 13.3 Performance Testing
- [ ] Measure end-to-end generation time (<30s)
- [ ] Test concurrent requests (5+ simultaneous)
- [ ] Monitor memory usage
- [ ] Monitor API costs

### 13.4 Launch
- [ ] Deploy to staging environment
- [ ] Final smoke tests
- [ ] Deploy to production
- [ ] Monitor logs and errors
- [ ] Celebrate! 🎉

---

## 📊 Progress Tracking

**Total Tasks:** 150+
**Completed:** 0
**In Progress:** 0
**Remaining:** 150+

**Current Stage:** Stage 1 - Project Setup & Infrastructure
**Current Task:** Create directory structure

---

## 🔄 Review Process

After completing each checkbox:
1. ✅ Mark the checkbox as complete
2. 🧪 Run tests for that specific change
3. 📝 Commit changes with descriptive message
4. 👀 Request code review (human or AI)
5. ✨ Get approval before moving to next checkbox

---

## 📝 Notes & Decisions

### Key Decisions Made:
- Using LangGraph for agentic workflow orchestration
- OpenRouter for flexible LLM provider (allows model switching)
- Flux Kontext for in-context image generation
- PostgreSQL for structured data storage
- Local file storage for MVP (cloud storage post-MVP)

### Open Questions:
- [ ] Which OpenRouter model for code analysis? (suggest: claude-3.5-sonnet)
- [ ] Max repo size limit? (suggest: 50MB)
- [ ] Image resolution? (suggest: 1024x768 for portrait cats)
- [ ] Rate limiting strategy? (post-MVP)

---

**Remember:** Work incrementally, test thoroughly, and celebrate small wins! 🚀
