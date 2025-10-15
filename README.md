# Repo-to-Cat 🐱

Generate unique cat images based on GitHub repository code quality!

## Overview

Repo-to-Cat analyzes GitHub repositories and generates AI-powered cat images that reflect the codebase's quality. Each cat's appearance (size, age, beauty, expression, background, breed) is determined by code metrics, providing an entertaining visualization of repository health. Features a modern web interface and 100% LLM-generated meme text for maximum creativity.

## Features

- 🔍 **Smart Code Analysis**: Analyzes 3-5 strategic files using AI (no full repo cloning needed)
- 🎨 **Unique Cat Images**: Generated with FLUX.1.1-pro based on code quality
- 🐾 **Breed Variation**: Language-specific cat breeds (Python→Tabby, JavaScript→Siamese, Rust→Maine Coon, etc.)
- 📖 **Funny Stories**: AI-generated 3-5 sentence stories about your repository (friendly roast style)
- 🌍 **Multi-Language Support**: Handles repos with multiple languages, mentions breakdown in stories
- 😹 **AI Meme Generation**: 100% LLM-generated meme text with context-aware humor
- 🎯 **Dynamic Text Sizing**: Auto-adjusts font size to prevent text overflow
- 🤖 **AI-Powered**: Uses LangGraph workflow with google/gemini-2.5-flash for analysis
- 📊 **Detailed Insights**: Returns comprehensive JSON with analysis metrics
- 🚀 **Fast**: No repo cloning, uses GitHub Contents API directly
- 🖥️ **Modern Web Interface**: Astro 5.1 frontend with responsive design

## Tech Stack

### Frontend
- **Framework**: Astro 5.1
- **Styling**: Tailwind CSS
- **Deployment**: Static site (4321 dev port)

### Backend
- **API**: FastAPI + Python 3.11+
- **AI Orchestration**: LangChain 0.3.0 + LangGraph 0.2.74
- **Code Analysis**: OpenRouter (google/gemini-2.5-flash)
- **Story Generation**: OpenRouter (google/gemini-2.5-flash, temperature 0.9)
- **Meme Generation**: OpenRouter (google/gemini-2.5-flash, temperature 0.9)
- **Image Generation**: Together.ai (FLUX.1.1-pro, 768x432)
- **Image Processing**: Pillow (text overlay, dynamic font sizing)
- **GitHub Integration**: PyGithub + GitHub Contents API
- **Database**: PostgreSQL 15 + SQLAlchemy 2.0 + Alembic
- **Testing**: pytest + pytest-asyncio (80% coverage target)

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL (via Docker)
- API Keys:
  - GitHub Personal Access Token
  - OpenRouter API Key
  - Together.ai API Key

### Installation

#### Backend Setup

1. **Clone repository:**
   ```bash
   git clone https://github.com/yourusername/repo-to-cat.git
   cd repo-to-cat
   ```

2. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys:
   # - GITHUB_TOKEN
   # - OPENROUTER_API_KEY
   # - TOGETHER_API_KEY
   ```

4. **Start database:**
   ```bash
   docker compose up -d postgres
   ```

5. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

6. **Start backend server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

#### Frontend Setup

1. **Navigate to frontend:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start frontend dev server:**
   ```bash
   npm run dev
   ```

#### Access Application

- **Web Interface**: http://localhost:4321
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## API Usage

### Generate Cat Image

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"github_url": "https://github.com/torvalds/linux"}'
```

**Response:**
```json
{
  "success": true,
  "generation_id": "uuid-here",
  "repository": {
    "url": "https://github.com/torvalds/linux",
    "name": "linux",
    "owner": "torvalds",
    "primary_language": "C",
    "size_kb": 1234567,
    "stars": 150000,
    "language_breakdown": [
      {"language": "C", "percentage": 97.8},
      {"language": "Assembly", "percentage": 1.2},
      {"language": "Python", "percentage": 0.5}
    ]
  },
  "analysis": {
    "code_quality_score": 9.2,
    "files_analyzed": ["README.md", "kernel/main.c", "..."],
    "metrics": {
      "has_tests": true,
      "has_ci": true,
      "has_documentation": true
    }
  },
  "cat_attributes": {
    "size": "very_large",
    "age": "senior",
    "breed": "Norwegian Forest Cat",
    "beauty_score": 9.2,
    "expression": "happy",
    "background": "gears and metal"
  },
  "story": "The linux repository is a wise old cat that has seen it all...",
  "meme_text": {
    "top": "KERNEL LEVEL MASTERY",
    "bottom": "C CODE GOES BRRRR"
  },
  "image": {
    "url": "/generated_images/uuid-here.png",
    "binary": "base64-encoded-image",
    "prompt": "A very large, beautiful senior Norwegian Forest Cat with happy expression..."
  }
}
```

### Health Check

```bash
curl http://localhost:8000/health
```

## Development

### Run Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=app --cov-report=html

# Specific test
pytest tests/unit/test_config.py -v
```

### Project Status

✅ **MVP Complete** - See [HANDOFF.md](PROJECT_FLOW_DOCS/HANDOFF.md) for full development history

**Completed:**
- Stage 1: Project setup, database, FastAPI skeleton
- Stage 8: Full API endpoints, story generation, meme generation
- MVP Improvements: Breed variation, multi-language support, LLM meme generation

### Documentation

- [PRD.md](PROJECT_FLOW_DOCS/PRD.md) - Product Requirements & Architecture
- [HANDOFF.md](PROJECT_FLOW_DOCS/HANDOFF.md) - Development Checklist (150+ tasks)
- [PROJECT_STRUCTURE.md](PROJECT_FLOW_DOCS/PROJECT_STRUCTURE.md) - Directory Layout
- [FILE_SELECTION_STRATEGY.md](PROJECT_FLOW_DOCS/FILE_SELECTION_STRATEGY.md) - File Analysis Algorithm
- [DEVELOPMENT_RULES.md](PROJECT_FLOW_DOCS/DEVELOPMENT_RULES.md) - TDD & Code Review Rules
- [INIT_PROMPT.md](PROJECT_FLOW_DOCS/INIT_PROMPT.md) - Reusable initialization prompt

## How It Works

1. **Input**: GitHub repository URL (via web interface or API)
2. **Metadata**: Fetch repo metadata (language, size, stars, language breakdown)
3. **File Selection**: Pick 5 strategic files (README, entry point, core, test, config)
4. **Code Analysis**: Analyze code quality with AI (gemini-2.5-flash)
5. **Cat Mapping**: Map metrics to cat attributes (size, age, expression, breed)
6. **Story Generation**: Generate funny 3-5 sentence story (gemini-2.5-flash, temp 0.9)
7. **Image Generation**: Create cat image with FLUX.1.1-pro (768x432)
8. **Meme Text**: Generate context-aware meme text (gemini-2.5-flash, temp 0.9)
9. **Text Overlay**: Add meme text with dynamic font sizing
10. **Storage**: Save to PostgreSQL + local storage
11. **Output**: Return JSON + image via API or display in web UI

## Cat Attribute Mapping

- **Size**: Repository size (small → medium → large → very_large)
- **Age**: Code quality score (kitten → young → adult → senior)
- **Beauty**: Code quality score (0-10 directly mapped)
- **Expression**: Test coverage & quality (grumpy → concerned → neutral → happy)
- **Background**: Language-specific (Python=snakes, JS=coffee, Rust=gears, Go=mountains, Java=office)
- **Breed**: Language-specific (Python=Tabby, JS=Siamese, Rust=Maine Coon, Go=British Shorthair, etc.)

## Documentation

### Guides

- **[API Endpoints](docs/api-endpoints.md)** - Complete API reference with examples
- **[Workflow Guide](docs/workflow-guide.md)** - How the system works (11-node pipeline)
- **[Response Examples](docs/response-examples.md)** - JSON response reference with real examples
- **[Docker Setup](docs/docker-setup.md)** - Docker and PostgreSQL configuration
- **[Database Guide](docs/database-guide.md)** - Schema, migrations, and queries
- **[Testing Guide](docs/testing-guide.md)** - Running tests and coverage
- **[FastAPI Guide](docs/fastapi-guide.md)** - Server configuration and usage
- **[Health Check](docs/health-check.md)** - Service monitoring

### Stage Documentation

- **[Stage 1.2 Summary](docs/stages/stage-1.2-summary.md)** - Database infrastructure
- **[Stage 1.3 Summary](docs/stages/stage-1.3-summary.md)** - FastAPI skeleton
- **[Stage 8 Summary](docs/stages/stage-8-summary.md)** - API endpoints + story/meme features

---

## Contributing

This project follows strict TDD and incremental development principles:

1. Work on ONE checkbox from HANDOFF.md at a time
2. Write tests FIRST for all logic/code
3. Run tests after each change
4. Request review before moving to next checkbox
5. Maintain 80%+ code coverage

See [DEVELOPMENT_RULES.md](PROJECT_FLOW_DOCS/DEVELOPMENT_RULES.md) for details.

## License

MIT

## Credits

Built with:
- [Astro](https://astro.build/) - Modern web framework
- [FastAPI](https://fastapi.tiangolo.com/) - Python web framework
- [LangChain](https://python.langchain.com/) - LLM framework
- [LangGraph](https://langchain-ai.github.io/langgraph/) - Workflow orchestration
- [Together.ai](https://www.together.ai/) - Image generation (FLUX.1.1-pro)
- [OpenRouter](https://openrouter.ai/) - LLM API gateway (Gemini 2.5 Flash)

---

**Status**: ✅ MVP Complete with Improvements
**Version**: 0.3.0 (MVP + Breed Variation + Multi-Language + LLM Memes)
**Last Updated**: 2025-10-15
