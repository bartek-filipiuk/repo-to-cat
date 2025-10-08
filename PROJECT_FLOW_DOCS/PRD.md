# Product Requirements Document (PRD)
## Repo-to-Cat: GitHub Repository Quality Visualizer

### 1. Overview

**Product Name:** Repo-to-Cat
**Version:** MVP 1.0
**Date:** 2025-10-07
**Status:** Planning

#### 1.1 Product Vision
A fun, AI-powered API that analyzes GitHub repositories and generates unique cat images reflecting the codebase's quality, language, and characteristics. Each cat's appearance (age, beauty, expression, background) is determined by code quality metrics, providing an entertaining visualization of repository health.

#### 1.2 Target Users
- Developers seeking a fun way to showcase their code quality
- GitHub project maintainers
- Tech communities and developer portfolios
- Future: General users with simple web interface

---

### 2. Core Functionality

#### 2.1 MVP Features
1. **GitHub Repository Analysis**
   - Accept GitHub repository URL
   - Fetch repository metadata (size, languages, structure)
   - Sample 3-5 strategic files (README, main entry point, core files, tests, config)
   - Analyze code quality using LLM (OpenRouter: google/gemini-2.5-flash)

2. **Cat Attribute Mapping**
   - **Size:** Repository size (kitten → chonky cat)
   - **Age:** Language age + commit history (young → old)
   - **Beauty:** Code quality score (ugly → pretty)
   - **Background:** Language-specific themes (Python = snakes, JS = coffee, Go = gophers)
   - **Expression:** Test coverage and code health (grumpy → happy)

3. **Image Generation**
   - Generate image using FLUX.1.1-pro (Together.ai)
   - Image dimensions: 768x432 (landscape, 20 steps)
   - Optional LoRAs support for style customization
   - Store locally in `/generated_images/`
   - Return image URL and binary in response

4. **API Endpoints**
   - `POST /generate` - Main generation endpoint
   - `GET /health` - Health check for all services (GitHub API, OpenRouter, Together.ai)

5. **Database & Persistence**
   - PostgreSQL database (Docker)
   - Schema: `users`, `generations` (history tracking)
   - Store generation metadata and results

#### 2.2 Technical Architecture

**Tech Stack:**
- **Backend:** FastAPI (Python)
- **AI Orchestration:** LangChain + LangGraph (agentic workflow)
- **LLM Provider:** OpenRouter - google/gemini-2.5-flash (code analysis)
- **Image Generation:** Together.ai - FLUX.1.1-pro (768x432)
- **Database:** PostgreSQL (Docker)
- **Dependency Management:** pip3
- **Deployment:** Docker for local, production deployment instructions

**Workflow (LangGraph Pipeline):**
1. **Input Node:** Receive GitHub URL
2. **Metadata Extraction Node:** Fetch repo metadata via GitHub API
3. **File Selection Node:** Select 3-5 representative files
4. **File Fetch Node:** Retrieve raw file contents
5. **Code Analysis Node:** Analyze quality using OpenRouter LLM (gemini-2.5-flash)
6. **Attribute Mapping Node:** Map analysis to cat attributes
7. **Prompt Generation Node:** Create image generation prompt
8. **Image Generation Node:** Call Together.ai FLUX.1.1-pro (768x432, 20 steps)
9. **Storage Node:** Save to database and local storage
10. **Output Node:** Return JSON with image + metadata

---

### 3. API Specifications

#### 3.1 POST /generate

**Request:**
```json
{
  "github_url": "https://github.com/owner/repo"
}
```

**Response:**
```json
{
  "success": true,
  "generation_id": "uuid-here",
  "repository": {
    "url": "https://github.com/owner/repo",
    "name": "repo",
    "owner": "owner",
    "primary_language": "Python",
    "size_kb": 1234,
    "stars": 567
  },
  "analysis": {
    "code_quality_score": 7.5,
    "files_analyzed": [
      "README.md",
      "src/main.py",
      "tests/test_main.py"
    ],
    "metrics": {
      "line_length_avg": 85,
      "function_length_avg": 25,
      "has_tests": true,
      "has_type_hints": true,
      "has_documentation": true
    }
  },
  "cat_attributes": {
    "size": "medium",
    "age": "young",
    "beauty_score": 7.5,
    "expression": "happy",
    "background": "snakes and code",
    "accessories": ["bow tie", "collar"]
  },
  "image": {
    "url": "/generated_images/uuid-here.png",
    "binary": "base64-encoded-image-data",
    "prompt": "A young, beautiful medium-sized cat with a happy expression..."
  },
  "timestamp": "2025-10-07T12:34:56Z"
}
```

**Error Responses:**
- `400` - Invalid GitHub URL
- `403` - Private repository (not accessible)
- `404` - Repository not found
- `500` - Analysis or generation failed

#### 3.2 GET /health

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "github_api": {
      "status": "up",
      "response_time_ms": 145
    },
    "openrouter": {
      "status": "up",
      "response_time_ms": 320
    },
    "together_ai": {
      "status": "up",
      "response_time_ms": 280
    },
    "database": {
      "status": "up",
      "response_time_ms": 12
    }
  },
  "timestamp": "2025-10-07T12:34:56Z"
}
```

---

### 4. Data Models

#### 4.1 Database Schema

**Users Table** (Post-MVP full implementation)
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) UNIQUE,
    api_token VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Generations Table**
```sql
CREATE TABLE generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    github_url TEXT NOT NULL,
    repo_owner VARCHAR(255),
    repo_name VARCHAR(255),
    primary_language VARCHAR(100),
    repo_size_kb INTEGER,
    code_quality_score DECIMAL(3,1),
    cat_attributes JSONB,
    analysis_data JSONB,
    image_path TEXT,
    image_prompt TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

### 5. Configuration & Environment

**Environment Variables (.env):**
```
# GitHub
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx

# AI Providers
OPENROUTER_API_KEY=sk-or-xxxxxxxxxxxxx
TOGETHER_API_KEY=xxxxxxxxxxxxx

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/repo_to_cat

# Application
IMAGE_STORAGE_PATH=/app/generated_images
API_PORT=8000
```

---

### 6. Code Quality Analysis Heuristics

**Hardcoded Mapping Configuration:**
```python
# config/code_quality_mappings.py

LANGUAGE_BACKGROUNDS = {
    "Python": "snakes and code snippets",
    "JavaScript": "coffee cups and laptops",
    "TypeScript": "coffee cups with bow tie",
    "Go": "gophers and mountains",
    "Rust": "gears and metal",
    "Java": "coffee beans",
}

QUALITY_INDICATORS = {
    "spaghetti": {
        "line_length": ">200",
        "function_length": ">100",
        "nesting_depth": ">4",
        "no_comments": True,
        "no_tests": True,
    },
    "legit": {
        "consistent_formatting": True,
        "type_hints": True,
        "tests_exist": True,
        "documentation": True,
        "modular_structure": True,
    }
}

CAT_SIZE_MAPPING = {
    "range": [0, 10000],  # KB
    "small": "kitten",
    "medium": "cat",
    "large": "chonky cat",
}
```

---

### 7. Development Workflow

#### 7.1 Development Principles
- Incremental development (one checkbox at a time)
- Mandatory code review for every change
- Test-Driven Development (TDD)
- Minimum 80% code coverage

#### 7.2 Project Structure
```
repo-to-cat/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py           # API endpoints
│   │   └── schemas.py          # Pydantic models
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration
│   │   └── database.py         # DB connection
│   ├── services/
│   │   ├── __init__.py
│   │   ├── github_service.py   # GitHub API integration
│   │   ├── analysis_service.py # Code analysis logic
│   │   └── image_service.py    # Image generation
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── openrouter.py       # OpenRouter client
│   │   └── together_ai.py      # Together.ai client
│   ├── langgraph/
│   │   ├── __init__.py
│   │   ├── workflow.py         # LangGraph pipeline
│   │   ├── nodes.py            # Individual nodes
│   │   └── state.py            # State definitions
│   └── models/
│       ├── __init__.py
│       └── database.py         # SQLAlchemy models
├── config/
│   ├── __init__.py
│   └── mappings.py             # Cat attribute mappings
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_github_service.py
│   └── test_analysis.py
├── generated_images/           # Local image storage
├── docker-compose.yml          # Docker services
├── Dockerfile
├── requirements.txt            # pip3 dependencies
├── .env.example
├── .env                        # gitignored
├── PRD.md                      # This file
├── HANDOFF.md                  # Task tracking
├── DEVELOPMENT_RULES.md        # Dev principles
└── README.md                   # Setup instructions
```

---

### 8. Dependencies (requirements.txt)

```
# Web Framework
fastapi==0.115.0
uvicorn[standard]==0.32.0
pydantic==2.9.0
pydantic-settings==2.5.0

# AI & LLM
langchain==0.3.0
langgraph==0.2.74
openai==1.54.0  # For OpenRouter compatibility
together==1.3.0

# GitHub
PyGithub==2.4.0
requests==2.32.0

# Database
sqlalchemy==2.0.35
psycopg2-binary==2.9.9
alembic==1.13.3

# Utilities
python-dotenv==1.0.1
python-multipart==0.0.12

# Testing
pytest==8.3.0
pytest-asyncio==0.24.0
pytest-cov==5.0.0
httpx==0.27.0
```

---

### 9. MVP Scope & Post-MVP

#### 9.1 MVP Scope (In Scope)
- ✅ GitHub URL → Cat image generation
- ✅ Code analysis with OpenRouter
- ✅ Image generation with Flux Kontext
- ✅ LangGraph workflow orchestration
- ✅ PostgreSQL database with generations history
- ✅ Health check endpoint
- ✅ Detailed JSON response with analysis
- ✅ Local image storage
- ✅ Docker setup

#### 9.2 Post-MVP (Out of Scope for MVP)
- ❌ User authentication (cat_xxx tokens)
- ❌ Rate limiting
- ❌ Frontend web interface
- ❌ User-specific GitHub tokens
- ❌ Advanced caching
- ❌ Webhook integration
- ❌ Social sharing features
- ❌ Cat image gallery

---

### 10. Success Metrics

**MVP Success Criteria:**
1. Successfully analyze any public GitHub repository
2. Generate unique cat images reflecting code quality
3. < 30 seconds end-to-end generation time
4. 80%+ test coverage
5. All health checks passing
6. Clean Docker deployment

---

### 11. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| GitHub API rate limits | High | Use authenticated token (5000 req/hr) |
| OpenRouter/Together.ai downtime | High | Implement health checks + error handling |
| Large repository analysis timeout | Medium | Limit to 3-5 files only |
| Private repo access | Low | Return clear error message |
| Image generation cost | Medium | Track usage in DB, set limits post-MVP |

---

### 12. Timeline & Milestones

**Phase 1: Setup (Week 1)**
- Project structure
- Docker + PostgreSQL setup
- Basic FastAPI skeleton

**Phase 2: GitHub Integration (Week 2)**
- GitHub API integration
- File selection logic
- Tests

**Phase 3: AI Pipeline (Week 3)**
- LangGraph workflow
- OpenRouter integration
- Code analysis logic

**Phase 4: Image Generation (Week 4)**
- Together.ai Flux integration
- Attribute mapping
- Image storage

**Phase 5: Polish & Deploy (Week 5)**
- Health checks
- Error handling
- Documentation
- Docker deployment

---

### 13. Decisions Made
- ✅ **OpenRouter Model:** google/gemini-2.5-flash (cost-effective, fast)
- ✅ **Repository Size:** No download needed - use GitHub API to read files directly (no size limit concerns)
- ✅ **Image Resolution:** 768x432 landscape with FLUX.1.1-pro, 20 steps
- ✅ **GitHub Access:** Read files via GitHub Contents API (no cloning required)

### 14. GitHub API Strategy - No Repo Cloning

**Key Insight:** We use GitHub API's `/repos/{owner}/{repo}/contents/{path}` endpoint to read files directly without downloading the entire repository.

**Benefits:**
- No disk space needed
- No repo size limitations
- Faster analysis (only fetch 3-5 files)
- Works with repos of any size (even 10GB+ repos)

**API Endpoints Used:**
```python
# Metadata
GET /repos/{owner}/{repo}

# Languages
GET /repos/{owner}/{repo}/languages

# File tree (recursive)
GET /repos/{owner}/{repo}/git/trees/{sha}?recursive=1

# File contents (raw)
GET /repos/{owner}/{repo}/contents/{path}
# Header: Accept: application/vnd.github.raw
```

**Example Flow:**
1. Get repo metadata → identify primary language
2. Get file tree → list all files
3. Select 3-5 strategic files (README, main.py, test files)
4. Fetch only those 3-5 files' raw content
5. Analyze only the fetched content

**Rate Limits:**
- Authenticated: 5,000 requests/hour
- Each generation uses ~10-15 API calls
- Can handle 300+ generations/hour

---

**Approved By:** [To be filled]
**Last Updated:** 2025-10-07
