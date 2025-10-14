# Repo-to-Cat 🐱

Generate unique cat images based on GitHub repository code quality!

## Overview

Repo-to-Cat analyzes GitHub repositories and generates AI-powered cat images that reflect the codebase's quality. Each cat's appearance (size, age, beauty, expression, background) is determined by code metrics, providing an entertaining visualization of repository health.

## Features

- 🔍 **Smart Code Analysis**: Analyzes 3-5 strategic files using AI (no full repo cloning needed)
- 🎨 **Unique Cat Images**: Generated with FLUX.1.1-pro based on code quality
- 📖 **Funny Stories**: AI-generated 3-5 sentence stories about your repository (friendly roast style)
- 😹 **Meme Text Overlay**: Classic top/bottom meme text added to cat images
- 🤖 **AI-Powered**: Uses LangGraph workflow with google/gemini-2.5-flash for analysis
- 📊 **Detailed Insights**: Returns comprehensive JSON with analysis metrics
- 🚀 **Fast**: No repo cloning, uses GitHub Contents API directly

## Tech Stack

- **Backend**: FastAPI + Python 3.11+
- **AI**: LangChain 0.3.0 + LangGraph 0.2.74
- **LLM**: OpenRouter (google/gemini-2.5-flash)
- **Image Generation**: Together.ai (FLUX.1.1-pro, 768x432)
- **Image Processing**: Pillow (text overlay, meme generation)
- **GitHub**: PyGithub + GitHub Contents API
- **Database**: PostgreSQL + SQLAlchemy + Alembic
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
   # Edit .env with your API keys
   ```

4. **Start database:**
   ```bash
   docker-compose up -d db
   ```

5. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

6. **Start server:**
   ```bash
   uvicorn app.main:app --reload
   ```

7. **Visit API docs:**
   ```
   http://localhost:8000/docs
   ```

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
    "stars": 150000
  },
  "analysis": {
    "code_quality_score": 9.2,
    "files_analyzed": ["README.md", "kernel/main.c", "..."],
    "metrics": { "..." }
  },
  "cat_attributes": {
    "size": "large",
    "age": "old",
    "beauty_score": 9.2,
    "expression": "happy",
    "background": "gears and metal"
  },
  "image": {
    "url": "/generated_images/uuid-here.png",
    "binary": "base64-encoded-image",
    "prompt": "A large, beautiful old cat with happy expression..."
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

🚧 **MVP Development** - See [HANDOFF.md](PROJECT_FLOW_DOCS/HANDOFF.md) for progress

**Current Stage:** Stage 1.1 - Basic Project Structure ✅

### Documentation

- [PRD.md](PROJECT_FLOW_DOCS/PRD.md) - Product Requirements & Architecture
- [HANDOFF.md](PROJECT_FLOW_DOCS/HANDOFF.md) - Development Checklist (150+ tasks)
- [PROJECT_STRUCTURE.md](PROJECT_FLOW_DOCS/PROJECT_STRUCTURE.md) - Directory Layout
- [FILE_SELECTION_STRATEGY.md](PROJECT_FLOW_DOCS/FILE_SELECTION_STRATEGY.md) - File Analysis Algorithm
- [DEVELOPMENT_RULES.md](PROJECT_FLOW_DOCS/DEVELOPMENT_RULES.md) - TDD & Code Review Rules
- [INIT_PROMPT.md](PROJECT_FLOW_DOCS/INIT_PROMPT.md) - Reusable initialization prompt

## How It Works

1. **Input**: GitHub repository URL
2. **Metadata**: Fetch repo metadata (language, size, stars)
3. **File Selection**: Pick 5 strategic files (README, entry point, core, test, config)
4. **Analysis**: Analyze code quality with AI (gemini-2.5-flash)
5. **Mapping**: Map metrics to cat attributes
6. **Generation**: Create cat image with FLUX.1.1-pro
7. **Storage**: Save to database and local storage
8. **Output**: Return detailed JSON + image

## Cat Attribute Mapping

- **Size**: Repository size (kitten → chonky cat)
- **Age**: Language age + commit history (young → old)
- **Beauty**: Code quality score (ugly → pretty)
- **Background**: Language-specific (Python=snakes, JS=coffee, Go=gophers)
- **Expression**: Test coverage (grumpy → happy)

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
- [FastAPI](https://fastapi.tiangolo.com/)
- [LangChain](https://python.langchain.com/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [Together.ai](https://www.together.ai/)
- [OpenRouter](https://openrouter.ai/)

---

**Status**: 🚧 Early Development
**Version**: 0.2.0 (Stage 8 Complete - API + Stories + Memes)
**Last Updated**: 2025-10-13
