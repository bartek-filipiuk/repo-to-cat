# Response Examples: Complete JSON Reference

**Last Updated:** 2025-10-13
**Audience:** Internal team / Integration developers
**API Version:** 1.0

---

## Overview

This guide provides complete JSON response examples from the `/generate` endpoint with field-by-field annotations. Use these examples to understand the response structure and implement integrations.

**Response Format:** JSON (application/json)
**Size:** ~500-600 KB (with base64 image), ~2-3 KB (without image)

---

## Complete Response Example

This is a real response from analyzing the `qdrant_caddy` repository:

```json
{
  "success": true,
  "generation_id": "27a0b19c-3758-45d5-bf5f-d425a5e8df31",

  "repository": {
    "url": "https://github.com/bartek-filipiuk/qdrant_caddy",
    "name": "qdrant_caddy",
    "owner": "bartek-filipiuk",
    "primary_language": "Python",
    "size_kb": 48,
    "stars": 0
  },

  "analysis": {
    "code_quality_score": 8.4,
    "files_analyzed": [
      "README.md",
      "docker-compose.yml",
      "Caddyfile"
    ],
    "metrics": {
      "line_length_avg": 45,
      "line_length_max": 120,
      "lines_too_long_pct": 0.0,
      "function_length_avg": 0,
      "function_length_max": 0,
      "has_tests": false,
      "has_type_hints": false,
      "has_documentation": true,
      "complexity_score": 2,
      "maintainability_score": 8.5,
      "readability_score": 9.0,
      "best_practices_score": 7.8
    }
  },

  "cat_attributes": {
    "size": "small",
    "age": "senior",
    "beauty_score": 8.4,
    "expression": "neutral",
    "background": "a Python development environment with code editor and terminal",
    "accessories": null
  },

  "story": "This tiny `qdrant_caddy` cat, with its wise old eyes, has clearly seen a few things. It calmly observes its domain, perhaps pondering the mysteries of vector databases, yet it's still a kitten when it comes to getting attention – bless its zero-starred, inexperienced little heart. Despite its humble beginnings and surprising lack of tests (someone get this cat a toy to bat around!), its 8.4/10 code quality score confirms it's silently judging all of us, and doing a darn good job of it.",

  "meme_text": {
    "top": "PYTHON POWER",
    "bottom": "NO TESTS YOLO"
  },

  "image": {
    "url": "/generated_images/27a0b19c-3758-45d5-bf5f-d425a5e8df31.png",
    "binary": "iVBORw0KGgoAAAANSUhEUgAAA...(~500KB base64 PNG)...CYII=",
    "prompt": "A wise senior cat (5-10 years old), small, with a neutral expression. Background: a Python development environment with code editor and terminal. Photorealistic, detailed fur texture, professional photography, 8k quality. The cat should look natural and lifelike."
  },

  "timestamp": "2025-10-13T05:18:45.123456Z"
}
```

---

## Field Reference

### Top-Level Fields

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `success` | boolean | Yes | Whether generation succeeded | `true` |
| `generation_id` | string (UUID) | Yes | Unique identifier for this generation | `"27a0b19c-..."` |
| `repository` | object | Yes | Repository metadata | See below |
| `analysis` | object | Yes | Code quality analysis results | See below |
| `cat_attributes` | object | Yes | Mapped cat visualization attributes | See below |
| `story` | string | No | Funny 3-5 sentence story about repository | `"This tiny cat..."` |
| `meme_text` | object | No | Meme text overlay (top + bottom) | See below |
| `image` | object | Yes | Generated image data | See below |
| `timestamp` | string (ISO 8601) | Yes | Generation timestamp | `"2025-10-13T..."` |

### repository Object

| Field | Type | Can be null? | Description |
|-------|------|--------------|-------------|
| `url` | string | No | Original GitHub repository URL |
| `name` | string | No | Repository name (without owner) |
| `owner` | string | No | Repository owner or organization name |
| `primary_language` | string | **Yes** | Main programming language detected by GitHub |
| `size_kb` | integer | No | Repository size in kilobytes |
| `stars` | integer | **Yes** | Number of GitHub stars (null for private repos) |

**Example:**
```json
{
  "url": "https://github.com/python/cpython",
  "name": "cpython",
  "owner": "python",
  "primary_language": "Python",
  "size_kb": 150000,
  "stars": 50000
}
```

**Null Cases:**
- `primary_language`: null when GitHub can't detect language (rare, usually documentation-only repos)
- `stars`: null when repository is private (star count not public)

### analysis Object

| Field | Type | Description | Range/Format |
|-------|------|-------------|--------------|
| `code_quality_score` | float | Overall code quality score | 0.0 - 10.0 |
| `files_analyzed` | array[string] | List of filenames analyzed | 3-5 files |
| `metrics` | object | Detailed code metrics | See below |

**metrics Sub-object:**

| Field | Type | Description |
|-------|------|-------------|
| `line_length_avg` | integer | Average line length across all files |
| `line_length_max` | integer | Maximum line length found |
| `lines_too_long_pct` | float | Percentage of lines exceeding 120 chars |
| `function_length_avg` | integer | Average function length (lines) |
| `function_length_max` | integer | Longest function (lines) |
| `has_tests` | boolean | Whether test files were found |
| `has_type_hints` | boolean | Whether type hints detected (Python) |
| `has_documentation` | boolean | Whether documentation found (README, docstrings) |
| `complexity_score` | float | Code complexity (0-10, lower = simpler) |
| `maintainability_score` | float | How maintainable (0-10) |
| `readability_score` | float | How readable (0-10) |
| `best_practices_score` | float | Adherence to best practices (0-10) |

**Example:**
```json
{
  "code_quality_score": 8.4,
  "files_analyzed": ["README.md", "docker-compose.yml", "Caddyfile"],
  "metrics": {
    "line_length_avg": 45,
    "line_length_max": 120,
    "lines_too_long_pct": 0.0,
    "function_length_avg": 0,
    "function_length_max": 0,
    "has_tests": false,
    "has_type_hints": false,
    "has_documentation": true,
    "complexity_score": 2.0,
    "maintainability_score": 8.5,
    "readability_score": 9.0,
    "best_practices_score": 7.8
  }
}
```

### cat_attributes Object

| Field | Type | Description | Possible Values |
|-------|------|-------------|-----------------|
| `size` | string | Cat size based on repo size | "tiny", "small", "medium", "large", "huge" |
| `age` | string | Cat age based on language/history | "kitten", "young", "adult cat", "senior", "legendary" |
| `beauty_score` | float | Visual quality (mirrors code quality) | 0.0 - 10.0 |
| `expression` | string | Facial expression based on quality | "grumpy", "concerned", "neutral", "content", "proud" |
| `background` | string | Scene description (language-specific) | Free text |
| `accessories` | string or null | Optional props for high-quality code | Free text or null |

**Mapping Rules:**

**Size:**
- < 100 KB → "tiny"
- 100-1000 KB → "small"
- 1-10 MB → "medium"
- 10-100 MB → "large"
- \> 100 MB → "huge"

**Age:**
- New languages (Rust, Go, TypeScript) + recent repo → "kitten" or "young"
- Mature languages (Python, Java, C++) + old repo → "senior" or "legendary"

**Expression:**
- 0-3 score → "grumpy"
- 3-5 score → "concerned"
- 5-7 score → "neutral"
- 7-9 score → "content"
- 9-10 score → "proud"

**Accessories:**
- Only present if quality score ≥ 7.0
- Examples: "medals", "trophies", "crown", "glasses"
- null for lower quality scores

**Example:**
```json
{
  "size": "small",
  "age": "senior",
  "beauty_score": 8.4,
  "expression": "neutral",
  "background": "a Python development environment with code editor and terminal",
  "accessories": null
}
```

### story Field

| Type | Can be null? | Description |
|------|--------------|-------------|
| string | Yes | Funny 3-5 sentence narrative about repository |

**Characteristics:**
- **Length:** 150-400 characters (3-5 sentences)
- **Tone:** Playful, friendly roast, never mean
- **Content:** References repo name, language, quality, stars, tests
- **Generated by:** OpenRouter (Gemini 2.5 Flash) with temperature 0.9
- **Fallback:** Template-based story if LLM fails

**Example:**
```json
"story": "This tiny `qdrant_caddy` cat, with its wise old eyes, has clearly seen a few things. It calmly observes its domain, perhaps pondering the mysteries of vector databases, yet it's still a kitten when it comes to getting attention – bless its zero-starred, inexperienced little heart. Despite its humble beginnings and surprising lack of tests (someone get this cat a toy to bat around!), its 8.4/10 code quality score confirms it's silently judging all of us, and doing a darn good job of it."
```

**Fallback Example:**
```json
"story": "The repo-to-cat repository is a ordinary young cat that just discovered what Python is. Despite having a neutral expression, this small creature has somehow accumulated 0 stars from sympathetic onlookers. Its code quality of 8.4/10 suggests it's living its best life."
```

### meme_text Object

| Field | Type | Can be null? | Description |
|-------|------|--------------|-------------|
| `top` | string | No | Top meme text (2-4 words, uppercase) |
| `bottom` | string | No | Bottom meme text (2-4 words, uppercase) |

**Characteristics:**
- **Style:** Classic meme format (Impact font style)
- **Length:** 2-4 words per line
- **Format:** Always uppercase
- **Content:** Funny, references language or quality
- **Generated by:** OpenRouter (Gemini 2.5 Flash) with temperature 0.8
- **Fallback:** "{LANG} REPO" / "SUCH QUALITY" if LLM fails

**Examples:**
```json
// Good quality, has tests
{
  "top": "BIG CAT ENERGY",
  "bottom": "ALL TESTS PASS"
}

// Python, no tests
{
  "top": "PYTHON POWER",
  "bottom": "NO TESTS YOLO"
}

// High quality repository
{
  "top": "LEGENDARY CODE",
  "bottom": "8K STARS"
}

// Fallback example
{
  "top": "PYTHON REPO",
  "bottom": "SUCH QUALITY"
}
```

### image Object

| Field | Type | Description |
|-------|------|-------------|
| `url` | string | Relative URL path to image file |
| `binary` | string | Base64-encoded PNG image data |
| `prompt` | string | Exact prompt sent to FLUX.1.1-pro |

**Details:**

**url:**
- Format: `/generated_images/{generation_id}.png`
- Use with base URL: `http://localhost:8000/generated_images/...`
- File served as static file via FastAPI

**binary:**
- Format: Base64-encoded PNG
- Size: ~500-600 KB typical (with text overlay)
- Dimensions: 768x432 pixels (16:9 aspect ratio)
- Decode with: `base64.b64decode(binary_string)`

**prompt:**
- Natural language description sent to FLUX.1.1-pro
- Length: 100-200 tokens
- Includes cat attributes, background, style instructions
- Example: "A wise senior cat (5-10 years old), small, with a neutral expression..."

**Example:**
```json
{
  "url": "/generated_images/27a0b19c-3758-45d5-bf5f-d425a5e8df31.png",
  "binary": "iVBORw0KGgoAAAANSUhEUgAA...(500KB)...CYII=",
  "prompt": "A wise senior cat (5-10 years old), small, with a neutral expression. Background: a Python development environment with code editor and terminal. Photorealistic, detailed fur texture, professional photography, 8k quality. The cat should look natural and lifelike."
}
```

---

## Example Responses by Scenario

### Scenario 1: High-Quality Python Repository

**Repository:** `python/cpython` (Python core language)

```json
{
  "success": true,
  "generation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "repository": {
    "url": "https://github.com/python/cpython",
    "name": "cpython",
    "owner": "python",
    "primary_language": "C",
    "size_kb": 150000,
    "stars": 50000
  },
  "analysis": {
    "code_quality_score": 9.5,
    "files_analyzed": [
      "README.rst",
      "Python/ceval.c",
      "Lib/test/test_sys.py"
    ],
    "metrics": {
      "line_length_avg": 75,
      "line_length_max": 100,
      "lines_too_long_pct": 2.3,
      "has_tests": true,
      "has_type_hints": true,
      "has_documentation": true,
      "complexity_score": 4.5,
      "maintainability_score": 9.0,
      "readability_score": 9.2,
      "best_practices_score": 9.8
    }
  },
  "cat_attributes": {
    "size": "huge",
    "age": "legendary",
    "beauty_score": 9.5,
    "expression": "proud",
    "background": "tech conference stage with adoring crowd and spotlights",
    "accessories": "multiple gold medals, trophies, and a crown"
  },
  "story": "The Python repository is that ancient, wise cat who invented all nine lives and now just watches lesser felines struggle with their mere single existence. With its pristine 9.5/10 code quality and 50,000 star entourage, this legendary beast doesn't even need to meow – everyone already knows it's royalty. It sits on its tech conference throne, draped in medals, probably wondering when the rest of the world will catch up to 1991.",
  "meme_text": {
    "top": "LEGENDARY CODE",
    "bottom": "50K STARS FLEX"
  },
  "image": {
    "url": "/generated_images/a1b2c3d4-e5f6-7890-abcd-ef1234567890.png",
    "binary": "iVBORw0KGgoAAAA...",
    "prompt": "A magnificent legendary cat (10+ years old), huge, with pristine fur and a proud expression. Background: tech conference stage with adoring crowd and spotlights. The cat wears multiple gold medals, trophies, and a crown. Photorealistic, detailed fur texture, professional photography, 8k quality. The cat should look natural and lifelike."
  },
  "timestamp": "2025-10-13T12:00:00.000000Z"
}
```

### Scenario 2: Small Project, Low Quality

**Repository:** `user/hello-world` (Beginner project)

```json
{
  "success": true,
  "generation_id": "f9e8d7c6-b5a4-3210-9876-543210fedcba",
  "repository": {
    "url": "https://github.com/user/hello-world",
    "name": "hello-world",
    "owner": "user",
    "primary_language": "JavaScript",
    "size_kb": 12,
    "stars": 1
  },
  "analysis": {
    "code_quality_score": 3.2,
    "files_analyzed": [
      "README.md",
      "index.js"
    ],
    "metrics": {
      "line_length_avg": 120,
      "line_length_max": 250,
      "lines_too_long_pct": 45.0,
      "has_tests": false,
      "has_type_hints": false,
      "has_documentation": false,
      "complexity_score": 8.5,
      "maintainability_score": 2.1,
      "readability_score": 3.5,
      "best_practices_score": 2.0
    }
  },
  "cat_attributes": {
    "size": "tiny",
    "age": "kitten",
    "beauty_score": 3.2,
    "expression": "grumpy",
    "background": "coffee shop with messy laptop and tangled cables",
    "accessories": null
  },
  "story": "This tiny hello-world kitten stumbled into a coffee shop, pawed at a keyboard for exactly 17 minutes, and somehow created... this. With its grumpy little face and 3.2/10 code quality, it's basically a living 'TODO: fix later' comment. The single pity star suggests even Mom had second thoughts about clicking it, but hey, we all start somewhere – preferably with tests next time.",
  "meme_text": {
    "top": "JAVASCRIPT CHAOS",
    "bottom": "NO TESTS NO GLORY"
  },
  "image": {
    "url": "/generated_images/f9e8d7c6-b5a4-3210-9876-543210fedcba.png",
    "binary": "iVBORw0KGgoAAAA...",
    "prompt": "A grumpy kitten (0-6 months old), tiny, with messy fur and a frustrated expression. Background: coffee shop with messy laptop and tangled cables. Photorealistic, detailed fur texture, professional photography, 8k quality. The cat should look natural and lifelike."
  },
  "timestamp": "2025-10-13T13:00:00.000000Z"
}
```

### Scenario 3: Medium Quality, No Language Detected

**Repository:** `user/documentation` (Markdown only)

```json
{
  "success": true,
  "generation_id": "11223344-5566-7788-99aa-bbccddeeff00",
  "repository": {
    "url": "https://github.com/user/documentation",
    "name": "documentation",
    "owner": "user",
    "primary_language": null,
    "size_kb": 256,
    "stars": 15
  },
  "analysis": {
    "code_quality_score": 6.5,
    "files_analyzed": [
      "README.md",
      "docs/guide.md",
      "CONTRIBUTING.md"
    ],
    "metrics": {
      "line_length_avg": 90,
      "line_length_max": 120,
      "lines_too_long_pct": 5.0,
      "has_tests": false,
      "has_type_hints": false,
      "has_documentation": true,
      "complexity_score": 1.0,
      "maintainability_score": 7.5,
      "readability_score": 8.0,
      "best_practices_score": 6.0
    }
  },
  "cat_attributes": {
    "size": "small",
    "age": "adult cat",
    "beauty_score": 6.5,
    "expression": "neutral",
    "background": "cozy library with bookshelves and soft lighting",
    "accessories": null
  },
  "story": "The documentation repository is that responsible adult cat who knows exactly where all the manuals are but secretly wishes someone would ask about its feelings instead. With a respectable 6.5/10 and its 15 stars, it's doing okay – not setting the world on fire, but at least it's well-organized and readable. If only someone would add some actual code to keep it company.",
  "meme_text": {
    "top": "DOCS ONLY",
    "bottom": "WHERE CODE?"
  },
  "image": {
    "url": "/generated_images/11223344-5566-7788-99aa-bbccddeeff00.png",
    "binary": "iVBORw0KGgoAAAA...",
    "prompt": "A neutral adult cat (1-5 years old), small, with average fur quality. Background: cozy library with bookshelves and soft lighting. Photorealistic, detailed fur texture, professional photography, 8k quality. The cat should look natural and lifelike."
  },
  "timestamp": "2025-10-13T14:00:00.000000Z"
}
```

---

## Response Size Information

### With base64 Image Binary

| Component | Typical Size | Format |
|-----------|--------------|--------|
| Metadata + Analysis | 2-3 KB | JSON |
| Story | 0.3-0.5 KB | String |
| Meme Text | 0.1 KB | JSON |
| Image (base64) | 500-600 KB | Base64 string |
| **TOTAL** | **~500-605 KB** | JSON |

### Without Image Binary

If you don't need the base64 image (e.g., just fetch via URL):

| Component | Size |
|-----------|------|
| Full response - image.binary | ~2-3 KB |

**Tip:** To save bandwidth, fetch image separately:
```bash
# 1. Get metadata only (extract URL)
IMAGE_URL=$(curl POST /generate | jq -r '.image.url')

# 2. Download image separately
curl "http://localhost:8000${IMAGE_URL}" -o cat.png
```

---

## Extracting Specific Fields

### Using jq (Command Line)

```bash
# Get just the quality score
curl POST /generate | jq '.analysis.code_quality_score'
# Output: 8.4

# Get story
curl POST /generate | jq -r '.story'
# Output: "This tiny cat..."

# Get meme text
curl POST /generate | jq '.meme_text'
# Output: {"top": "PYTHON POWER", "bottom": "NO TESTS YOLO"}

# Get image URL
curl POST /generate | jq -r '.image.url'
# Output: "/generated_images/27a0b19c-..."

# Get cat attributes
curl POST /generate | jq '.cat_attributes'
# Output: {"size": "small", "age": "senior", ...}

# Get repository name and quality
curl POST /generate | jq '{repo: .repository.name, quality: .analysis.code_quality_score}'
# Output: {"repo": "qdrant_caddy", "quality": 8.4}
```

### Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/generate",
    json={"github_url": "https://github.com/user/repo"}
)
data = response.json()

# Extract specific fields
quality_score = data["analysis"]["code_quality_score"]
story = data["story"]
meme_top = data["meme_text"]["top"]
meme_bottom = data["meme_text"]["bottom"]
image_url = data["image"]["url"]

# Decode base64 image
import base64
image_bytes = base64.b64decode(data["image"]["binary"])

# Save image
with open("cat.png", "wb") as f:
    f.write(image_bytes)
```

### Using JavaScript

```javascript
const response = await fetch('http://localhost:8000/generate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({github_url: 'https://github.com/user/repo'})
});
const data = await response.json();

// Extract specific fields
const qualityScore = data.analysis.code_quality_score;
const story = data.story;
const memeText = data.meme_text;
const imageUrl = `http://localhost:8000${data.image.url}`;

// Display image
document.getElementById('cat-image').src = imageUrl;
document.getElementById('story').textContent = story;
document.getElementById('meme-top').textContent = memeText.top;
document.getElementById('meme-bottom').textContent = memeText.bottom;
```

---

## Common Integration Patterns

### Pattern 1: Display Quality Badge

```javascript
// Map score to badge color
function getQualityBadge(score) {
    if (score >= 9) return { color: 'gold', label: 'Legendary' };
    if (score >= 7) return { color: 'green', label: 'Good' };
    if (score >= 5) return { color: 'yellow', label: 'Fair' };
    if (score >= 3) return { color: 'orange', label: 'Needs Work' };
    return { color: 'red', label: 'Critical' };
}

const badge = getQualityBadge(data.analysis.code_quality_score);
```

### Pattern 2: Social Media Share

```javascript
// Generate shareable content
const shareText = `
Check out this cat representing ${data.repository.name}!
Quality: ${data.analysis.code_quality_score}/10
${data.meme_text.top} / ${data.meme_text.bottom}
${data.story}
`;

// Twitter share link
const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}`;
```

### Pattern 3: Repository Comparison

```python
# Compare multiple repositories
repos = [
    "https://github.com/python/cpython",
    "https://github.com/user/hello-world"
]

results = []
for repo_url in repos:
    response = requests.post(API_URL, json={"github_url": repo_url})
    data = response.json()
    results.append({
        "name": data["repository"]["name"],
        "quality": data["analysis"]["code_quality_score"],
        "size": data["cat_attributes"]["size"],
        "expression": data["cat_attributes"]["expression"]
    })

# Sort by quality
results.sort(key=lambda x: x["quality"], reverse=True)
```

---

## Related Documentation

- **[API Endpoints](api-endpoints.md)** - API usage and integration guide
- **[Workflow Guide](workflow-guide.md)** - How the system works internally
- **[Stage 8 Summary](stages/stage-8-summary.md)** - Implementation details

---

**Last Updated:** 2025-10-13
