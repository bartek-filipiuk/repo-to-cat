# Workflow Guide: Repository Analysis Pipeline

**Last Updated:** 2025-10-13
**Audience:** Internal team / System architecture understanding
**Complexity:** High-level overview (6 main steps)

---

## Overview

This guide explains how Repo-to-Cat processes a GitHub repository URL and generates a cat image visualization. The system uses an 11-node LangGraph workflow, grouped here into 6 logical high-level steps for clarity.

**Total Processing Time:** 15-25 seconds (varies by repository size and external API latency)

---

## Visual Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       REPO-TO-CAT WORKFLOW                              │
└─────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────┐
    │  GitHub URL      │
    │  Input Request   │
    └────────┬─────────┘
             │
             ▼
    ╔════════════════════════════════════════╗
    ║  STEP 1: Repository Discovery          ║  (5-8s)
    ║  ────────────────────────────          ║
    ║  • Extract metadata (GitHub API)       ║
    ║  • Select strategic files (3-5)        ║
    ║  • Fetch file contents                 ║
    ╚════════════════╦═══════════════════════╝
                     │
                     ▼
    ╔════════════════════════════════════════╗
    ║  STEP 2: Code Quality Analysis         ║  (3-5s)
    ║  ────────────────────────────          ║
    ║  • Analyze with OpenRouter/Gemini      ║
    ║  • Calculate quality score (0-10)      ║
    ║  • Extract metrics                     ║
    ╚════════════════╦═══════════════════════╝
                     │
                     ▼
    ╔════════════════════════════════════════╗
    ║  STEP 3: Mapping & Content Gen         ║  (3-5s)
    ║  ────────────────────────────          ║
    ║  • Map quality → cat attributes        ║
    ║  • Generate funny story (LLM)          ║
    ║  • Generate meme text (LLM)            ║
    ╚════════════════╦═══════════════════════╝
                     │
                     ▼
    ╔════════════════════════════════════════╗
    ║  STEP 4: Image Prompt Creation         ║  (<1s)
    ║  ────────────────────────────          ║
    ║  • Build detailed FLUX prompt          ║
    ║  • Include cat attributes              ║
    ║  • Add style instructions              ║
    ╚════════════════╦═══════════════════════╝
                     │
                     ▼
    ╔════════════════════════════════════════╗
    ║  STEP 5: Image Generation              ║  (6-9s)
    ║  ────────────────────────────          ║
    ║  • Generate cat image (Together.ai)    ║
    ║  • Add meme text overlay (Pillow)      ║
    ║  • Save image locally                  ║
    ╚════════════════╦═══════════════════════╝
                     │
                     ▼
    ╔════════════════════════════════════════╗
    ║  STEP 6: Storage & Output              ║  (1-2s)
    ║  ────────────────────────────          ║
    ║  • Save to PostgreSQL                  ║
    ║  • Build JSON response                 ║
    ║  • Return to client                    ║
    ╚════════════════╦═══════════════════════╝
                     │
                     ▼
    ┌──────────────────────────────────────┐
    │  Complete JSON Response              │
    │  • Repository info                   │
    │  • Analysis results                  │
    │  • Cat attributes                    │
    │  • Story + Meme text                 │
    │  • Image (URL + base64)              │
    └──────────────────────────────────────┘
```

---

## Step-by-Step Breakdown

### Step 1: Repository Discovery (5-8 seconds)

**Purpose:** Gather repository information and strategic code files

**Technical Nodes:**
1. `extract_metadata` - Fetch repo metadata from GitHub API
2. `select_files` - Select 3-5 strategic files for analysis
3. `fetch_files` - Download file contents via GitHub Contents API

**What Happens:**

1. **Extract Metadata**
   - Calls GitHub API: `GET /repos/{owner}/{repo}`
   - Retrieves: name, owner, language, size, stars, creation date
   - Stores in `WorkflowState["metadata"]`
   - Handles errors: 404 (not found), 403 (private repo)

2. **Select Files**
   - Uses file selection strategy:
     - **README**: Project documentation (always included if present)
     - **Entry point**: `main.py`, `index.js`, `app.py`, etc.
     - **Core module**: Main source file (largest in `src/` or `lib/`)
     - **Test file**: Representative test (from `tests/` or `test/`)
     - **Config**: `package.json`, `setup.py`, `.gitignore`
   - Limits to 5 files max (avoid overwhelming LLM)
   - Prioritizes files by strategic value

3. **Fetch Files**
   - Calls GitHub Contents API for each selected file
   - Downloads raw file content (base64 decoded)
   - Stores in `WorkflowState["code_files"]`
   - Total size limit: ~50KB combined (prevents token overflow)

**Services Used:**
- GitHub API (REST)
- PyGithub library

**Error Handling:**
- Repository not found → Return 404 error
- Private repository → Return 403 error
- Rate limit exceeded → Exponential backoff retry
- File too large → Skip and select alternative

**State Updates:**
```python
state["metadata"] = {
    "name": "repo-to-cat",
    "owner": "user",
    "primary_language": "Python",
    "size_kb": 1024,
    "stars": 42
}

state["code_files"] = [
    {"path": "README.md", "language": "markdown", "content": "..."},
    {"path": "app/main.py", "language": "python", "content": "..."},
    # ... up to 5 files
]
```

---

### Step 2: Code Quality Analysis (3-5 seconds)

**Purpose:** Analyze code quality using AI and calculate metrics

**Technical Nodes:**
1. `analyze_code` - Run LLM analysis and heuristic checks

**What Happens:**

1. **LLM Analysis** (OpenRouter + Gemini 2.5 Flash)
   - Formats code files into structured prompt
   - Sends to OpenRouter API with JSON schema response format
   - LLM evaluates:
     - **Readability**: How easy to understand (0-10)
     - **Maintainability**: How easy to modify (0-10)
     - **Complexity**: Overly complex sections? (0-10)
     - **Best Practices**: Follows conventions? (0-10)
     - **Error Handling**: Robust error management? (0-10)
   - Returns structured `CodeQualityAnalysis` object

2. **Heuristic Analysis** (Local calculations)
   - Line length statistics (avg, max, % too long)
   - Function length analysis (avg, max)
   - Detects: tests, type hints, documentation
   - Complexity scoring (basic cyclomatic complexity)

3. **Score Calculation**
   - Combines LLM scores (70% weight) + heuristics (30% weight)
   - Weighted average produces final score (0.0-10.0)
   - Rounds to 1 decimal place

**Services Used:**
- OpenRouter API (https://openrouter.ai)
- Model: `google/gemini-2.5-flash`
- Temperature: 0.3 (low for consistent analysis)

**Error Handling:**
- LLM timeout → Use heuristic-only scoring (fallback)
- Rate limit → Exponential backoff retry (3 attempts)
- Invalid response → Parse what's available, default missing scores

**State Updates:**
```python
state["analysis"] = {
    "code_quality_score": 7.8,
    "files_analyzed": ["README.md", "app/main.py", "tests/test_main.py"],
    "metrics": {
        "line_length_avg": 85,
        "line_length_max": 120,
        "has_tests": True,
        "has_type_hints": True,
        "readability_score": 8.5,
        "maintainability_score": 7.2,
        # ... more metrics
    }
}
```

---

### Step 3: Attribute Mapping & Content Generation (3-5 seconds)

**Purpose:** Convert analysis results into cat attributes and generate creative content

**Technical Nodes:**
1. `map_attributes` - Map quality metrics to cat characteristics
2. `generate_story` - Create funny story using LLM
3. `generate_meme_text` - Generate meme text using LLM

**What Happens:**

1. **Map Attributes** (Local logic)
   - Uses mapping rules from `config/mappings.py`
   - **Size**: Based on repository size (KB)
     - < 100 KB → "tiny"
     - 100-1000 KB → "small"
     - 1-10 MB → "medium"
     - 10-100 MB → "large"
     - > 100 MB → "huge"
   - **Age**: Based on language and history
     - New languages (Rust, Go) + recent repo → "kitten" or "young"
     - Mature languages (Python, Java) + old repo → "senior" or "legendary"
   - **Beauty**: Directly mirrors code quality score
   - **Expression**: Based on quality tiers
     - 0-3 → "grumpy"
     - 3-5 → "concerned"
     - 5-7 → "neutral"
     - 7-9 → "content"
     - 9-10 → "proud"
   - **Background**: Language-specific scenes
     - Python → "dev environment with code editor"
     - JavaScript → "coffee shop with laptop"
     - Go → "mountain landscape with gophers"
     - etc.
   - **Accessories**: Only for high quality (7+)
     - Medals, trophies, awards

2. **Generate Story** (OpenRouter + Gemini)
   - Constructs prompt with repo metadata, analysis, cat attributes
   - Tone: Playful, funny, friendly roast
   - Length: 3-5 sentences
   - Temperature: 0.9 (high creativity)
   - Fallback: Template-based story if LLM fails
   - Examples:
     - "This tiny qdrant_caddy cat, with its wise old eyes, has clearly seen a few things..."
     - "The Python repository is that ancient, wise cat who invented all nine lives..."

3. **Generate Meme Text** (OpenRouter + Gemini)
   - Constructs prompt requesting TOP and BOTTOM text
   - Style: Short (2-4 words), funny, uppercase
   - Temperature: 0.8 (creative but controlled)
   - Parses "TOP: ..." and "BOTTOM: ..." from response
   - Fallback: "{LANGUAGE} REPO" / "SUCH QUALITY" if LLM fails
   - Examples:
     - TOP: "PYTHON POWER" / BOTTOM: "NO TESTS YOLO"
     - TOP: "BIG CAT ENERGY" / BOTTOM: "ALL TESTS PASS"

**Services Used:**
- OpenRouter API (text generation)
- Model: `google/gemini-2.5-flash`
- Temperature: 0.8-0.9 (creative)

**Error Handling:**
- LLM timeout → Use fallback content
- Invalid format → Parse what's available
- Empty response → Use default templates

**State Updates:**
```python
state["cat_attrs"] = {
    "size": "small",
    "age": "senior",
    "beauty_score": 8.4,
    "expression": "content",
    "background": "a Python development environment with code editor",
    "accessories": None
}

state["story"] = "This tiny qdrant_caddy cat, with its wise old eyes..."

state["meme_text_top"] = "PYTHON POWER"
state["meme_text_bottom"] = "NO TESTS YOLO"
```

---

### Step 4: Image Prompt Creation (<1 second)

**Purpose:** Build detailed prompt for image generation model

**Technical Nodes:**
1. `generate_prompt` - Construct FLUX.1.1-pro prompt

**What Happens:**

1. **Prompt Construction**
   - Combines cat attributes into natural language prompt
   - Template structure:
     ```
     A {expression} {age} cat ({age_detail}), {size}, with {beauty_description}.
     Background: {background}.
     {accessories_if_any}.
     Photorealistic, detailed fur texture, professional photography, 8k quality.
     The cat should look natural and lifelike.
     ```
   - Example:
     ```
     A content senior cat (5-10 years old), small, with good quality fur.
     Background: a Python development environment with code editor and terminal.
     Photorealistic, detailed fur texture, professional photography, 8k quality.
     The cat should look natural and lifelike.
     ```

2. **Prompt Optimization**
   - Ensures prompt is clear and specific
   - Adds photorealism keywords for FLUX model
   - Avoids abstract concepts (focuses on visual elements)
   - Max length: ~200 tokens (FLUX has 512 token limit)

**Services Used:**
- None (local logic)

**Error Handling:**
- Missing attributes → Use defaults ("medium adult cat")
- Invalid values → Sanitize and use closest valid option

**State Updates:**
```python
state["image_prompt"] = "A content senior cat (5-10 years old), small, with good quality fur. Background: a Python development environment with code editor and terminal. Photorealistic, detailed fur texture, professional photography, 8k quality. The cat should look natural and lifelike."
```

---

### Step 5: Image Generation & Enhancement (6-9 seconds)

**Purpose:** Generate cat image and add meme text overlay

**Technical Nodes:**
1. `generate_image` - Call Together.ai to generate image
2. `add_text_overlay` - Add meme text using Pillow

**What Happens:**

1. **Generate Image** (Together.ai + FLUX.1.1-pro)
   - Sends prompt to Together.ai API
   - Model: `black-forest-labs/FLUX.1.1-pro`
   - Parameters:
     - Width: 768 pixels
     - Height: 432 pixels (16:9 aspect ratio)
     - Steps: 28 (quality vs speed balance)
     - Seed: Random (unique image every time)
   - Returns: Base64-encoded PNG image
   - Typical image size: 350-450 KB
   - Generation time: 5-8 seconds

2. **Add Text Overlay** (Pillow)
   - Decodes base64 image to PIL Image object
   - Loads font: DejaVuSans-Bold.ttf (60pt)
     - Fallback chain: DejaVu → Liberation → Arial → Default
   - Draws TOP text:
     - Position: 5% from top, centered horizontally
     - Style: White text, 4px black stroke outline
     - Uppercase
   - Draws BOTTOM text:
     - Position: 8% from bottom, centered horizontally
     - Same style as top
   - Re-encodes to PNG (base64)
   - Saves to local filesystem: `generated_images/{generation_id}.png`
   - Typical processing time: 1 second

**Services Used:**
- Together.ai API (https://api.together.xyz)
- Model: `black-forest-labs/FLUX.1.1-pro`
- Pillow (PIL) library

**Error Handling:**
- Image generation timeout → Retry once, then fail with 500
- Together.ai rate limit → Exponential backoff
- Font not found → Use TrueType fallback chain
- Text overlay failure → Return image without text (degraded)

**State Updates:**
```python
state["image"] = {
    "binary": "iVBORw0KGgo...base64...",  # ~500KB
    "url": "/generated_images/550e8400-e29b-41d4-a716-446655440000.png",
    "prompt": "A content senior cat (5-10 years old)..."
}
```

---

### Step 6: Storage & Output (1-2 seconds)

**Purpose:** Persist results to database and return JSON response

**Technical Nodes:**
1. `save_to_db` - Save generation record to PostgreSQL

**What Happens:**

1. **Database Persistence**
   - Creates `Generation` record with SQLAlchemy
   - Fields saved:
     - `id` (UUID) - generation_id
     - `github_url` - original request URL
     - `repo_owner` - repository owner
     - `repo_name` - repository name
     - `primary_language` - detected language
     - `repo_size_kb` - repository size
     - `code_quality_score` - final score (0.0-10.0)
     - `cat_attributes` - JSON object with cat attrs
     - `analysis_data` - JSON object with full analysis
     - `image_path` - local filesystem path
     - `image_prompt` - prompt sent to FLUX
     - `story` - generated story text
     - `meme_text_top` - top meme text
     - `meme_text_bottom` - bottom meme text
     - `created_at` - timestamp
   - Commits transaction to PostgreSQL

2. **Response Building** (in `app/api/routes.py`)
   - Extracts data from workflow state
   - Constructs `GenerateResponse` schema
   - Validates with Pydantic
   - Serializes to JSON
   - Returns with HTTP 200 status

**Services Used:**
- PostgreSQL (via SQLAlchemy)
- Database: `repo_to_cat`
- Table: `generations`

**Error Handling:**
- Database connection lost → Retry once, then fail with 500
- Unique constraint violation (duplicate generation_id) → Log warning, continue
- Validation error → Return 422 with details

**Final JSON Response:**
```json
{
  "success": true,
  "generation_id": "550e8400-e29b-41d4-a716-446655440000",
  "repository": { /* metadata */ },
  "analysis": { /* quality scores and metrics */ },
  "cat_attributes": { /* size, age, beauty, etc */ },
  "story": "This tiny qdrant_caddy cat...",
  "meme_text": {
    "top": "PYTHON POWER",
    "bottom": "NO TESTS YOLO"
  },
  "image": {
    "url": "/generated_images/550e8400.png",
    "binary": "iVBORw0KGgo...",
    "prompt": "A content senior cat..."
  },
  "timestamp": "2025-10-13T12:34:56.789Z"
}
```

See [response-examples.md](response-examples.md) for complete JSON reference.

---

## State Management

The workflow uses **LangGraph's state management** to pass data between nodes.

### WorkflowState Structure

```python
class WorkflowState(TypedDict):
    # Input
    github_url: str
    generation_id: str

    # Step 1: Repository Discovery
    metadata: NotRequired[Dict[str, Any]]
    selected_files: NotRequired[List[str]]
    code_files: NotRequired[List[Dict[str, str]]]

    # Step 2: Analysis
    analysis: NotRequired[Dict[str, Any]]

    # Step 3: Mapping & Content
    cat_attrs: NotRequired[Dict[str, Any]]
    story: NotRequired[str]
    meme_text_top: NotRequired[str]
    meme_text_bottom: NotRequired[str]

    # Step 4: Prompt
    image_prompt: NotRequired[str]

    # Step 5: Image
    image: NotRequired[Dict[str, str]]

    # Error handling
    error: NotRequired[str]
```

### State Flow

Each node:
1. **Reads** data from `state` (previous nodes' outputs)
2. **Processes** data (calls APIs, runs logic)
3. **Returns** dictionary with new/updated fields
4. LangGraph **merges** returned dict into state
5. Next node receives updated state

Example:
```python
def analyze_code_node(state: WorkflowState) -> Dict[str, Any]:
    code_files = state["code_files"]  # Read from state
    analysis = run_analysis(code_files)  # Process
    return {"analysis": analysis}  # Return updates
```

---

## Error Handling Strategy

### Node-Level Errors

Each node handles its own errors:
- **Transient errors** (rate limits, timeouts) → Retry with exponential backoff
- **Permanent errors** (404, 403) → Set `state["error"]` and halt workflow
- **Degraded operation** (LLM fails) → Use fallback values, continue

### Workflow-Level Errors

The workflow catches uncaught exceptions:
- Logs full error details
- Returns HTTP 500 with generic error message
- Does NOT expose internal details to client

### User-Facing Errors

API returns appropriate status codes:
- **404** - Repository not found
- **403** - Private repository, no access
- **422** - Invalid request format
- **500** - Internal processing error

---

## Performance Characteristics

### Timing Breakdown

| Step | Duration | Variance | Bottleneck |
|------|----------|----------|------------|
| 1. Repository Discovery | 5-8s | Medium | GitHub API latency |
| 2. Code Analysis | 3-5s | Low | OpenRouter LLM processing |
| 3. Mapping & Content | 3-5s | Medium | 2x LLM calls (story + meme) |
| 4. Prompt Creation | <1s | None | Local logic only |
| 5. Image Generation | 6-9s | High | Together.ai FLUX generation |
| 6. Storage & Output | 1-2s | Low | Database write + response build |
| **TOTAL** | **15-25s** | High | External APIs |

### Optimization Opportunities

**Current:**
- Sequential processing (step-by-step)
- No caching

**Future Improvements:**
1. **Parallel LLM calls**: Story + Meme text can run simultaneously (save 2-3s)
2. **Caching**: Cache by `repo_url + commit_sha` (instant for repeated requests)
3. **Async image generation**: Return immediately with `generation_id`, poll for completion
4. **Database pooling**: Already optimized (10 connections)
5. **CDN for images**: Serve images from CDN instead of local filesystem

---

## Technologies Used

### External APIs

| Service | Purpose | Model/Version | Rate Limits |
|---------|---------|---------------|-------------|
| **GitHub API** | Repository metadata, file contents | REST API v3 | 5000 req/hour (authenticated) |
| **OpenRouter** | Code analysis, story, meme text | google/gemini-2.5-flash | Varies by plan |
| **Together.ai** | Cat image generation | FLUX.1.1-pro | Varies by plan |

### Internal Services

| Service | Purpose | Technology |
|---------|---------|-----------|
| **LangGraph** | Workflow orchestration | LangChain 0.3.0 + LangGraph 0.2.74 |
| **PostgreSQL** | Data persistence | PostgreSQL 15 + SQLAlchemy 2.0 |
| **Pillow** | Image text overlay | PIL 10.4.0 |
| **FastAPI** | HTTP API server | FastAPI 0.115.0 |

---

## Debugging & Monitoring

### Logging

Each node logs key events:
```python
logger.info(f"Starting code analysis for {len(code_files)} files")
logger.info(f"Code quality score: {score}/10")
logger.warning(f"Using fallback story due to LLM timeout")
logger.error(f"Image generation failed: {error}")
```

Logs include:
- Timestamps
- Node names
- Processing durations
- Error details

### State Inspection

During development, inspect state at any point:
```python
# In any node
print(f"Current state: {json.dumps(state, indent=2)}")
```

### Database Queries

Check past generations:
```sql
SELECT
    id,
    repo_name,
    code_quality_score,
    LEFT(story, 50) as story_preview,
    meme_text_top,
    created_at
FROM generations
ORDER BY created_at DESC
LIMIT 10;
```

---

## Related Documentation

- **[Response Examples](response-examples.md)** - Complete JSON response reference
- **[API Endpoints](api-endpoints.md)** - API usage and integration
- **[Stage 8 Summary](stages/stage-8-summary.md)** - Implementation details
- **[Database Guide](database-guide.md)** - Schema and migrations

---

## Workflow Version History

| Version | Date | Changes | Nodes |
|---------|------|---------|-------|
| 1.0 | 2025-10-08 | Initial workflow (basic analysis + image) | 8 |
| 2.0 | 2025-10-13 | Added story, meme text, text overlay | 11 |

**Current Version:** 2.0 (11 nodes)
