# API Endpoints Reference

**Last Updated:** 2025-10-13
**API Version:** 1.0
**Base URL:** `http://localhost:8000`

---

## Overview

Repo-to-Cat exposes a FastAPI REST API for analyzing GitHub repositories and generating cat visualizations. The API includes health monitoring and a main generation endpoint that orchestrates an 11-node workflow.

### Quick Links

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Generate**: http://localhost:8000/generate

### Related Documentation

- **[Workflow Guide](workflow-guide.md)** - How the system works internally (11-node pipeline)
- **[Response Examples](response-examples.md)** - Complete JSON response reference with real examples
- **[Stage 8 Summary](stages/stage-8-summary.md)** - Implementation details and troubleshooting

---

## Authentication

**System:** Session-based authentication with httpOnly cookies

**Implementation:** Bcrypt password hashing, 7-day session tokens

**Protected Endpoints:**
- POST /generate (requires authentication)
- GET /generations (requires authentication)

**Public Endpoints:**
- GET /health (public)
- GET /auth/login, /auth/logout, /auth/me, /auth/status (auth management)
- GET /generation/:id (public, shareable)

**Session Cookie:** `session_token` (httpOnly, secure in production, sameSite=lax, 7-day expiration)

---

## Endpoints

### 1. GET /health

Health check endpoint that monitors all external service dependencies.

**Purpose:** Verify system is operational and identify failing services

**Method:** `GET`

**URL:** `/health`

**Query Parameters:** None

**Request Headers:** None

**Response Codes:**
- `200 OK` - Always returns 200, check `status` field for overall health

**Response Body:**
```json
{
  "status": "healthy" | "degraded",
  "services": {
    "github_api": {
      "status": "up" | "down",
      "response_time_ms": 245,
      "error": "optional error message"
    },
    "openrouter": {
      "status": "up" | "down",
      "response_time_ms": 312,
      "error": "optional error message"
    },
    "together_ai": {
      "status": "up" | "down",
      "response_time_ms": 189,
      "error": "optional error message"
    },
    "database": {
      "status": "up" | "down",
      "response_time_ms": 0,
      "error": "optional error message"
    }
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Overall health status: `"healthy"` if all services up, `"degraded"` if any down |
| `services.github_api.status` | string | GitHub API connectivity: `"up"` or `"down"` |
| `services.github_api.response_time_ms` | integer | Response time in milliseconds |
| `services.github_api.error` | string | Error message if status is down (optional) |
| `services.openrouter.*` | object | OpenRouter (LLM) service status |
| `services.together_ai.*` | object | Together.ai (image generation) service status |
| `services.database.*` | object | PostgreSQL database status |

**Service Check Details:**

- **GitHub API**: Tests `/user` endpoint with auth token (200 or 401 = up)
- **OpenRouter**: Tests `/api/v1/models` endpoint (200 or 401 = up)
- **Together.ai**: Tests `/v1/models` endpoint (200 or 401 = up)
- **Database**: Executes `SELECT 1` query

**Example Request:**

```bash
curl -X GET http://localhost:8000/health | jq
```

**Example Response (All Services Up):**

```json
{
  "status": "healthy",
  "services": {
    "github_api": {
      "status": "up",
      "response_time_ms": 245
    },
    "openrouter": {
      "status": "up",
      "response_time_ms": 312
    },
    "together_ai": {
      "status": "up",
      "response_time_ms": 189
    },
    "database": {
      "status": "up",
      "response_time_ms": 0
    }
  }
}
```

**Example Response (Service Down):**

```json
{
  "status": "degraded",
  "services": {
    "github_api": {
      "status": "down",
      "error": "HTTP 401",
      "response_time_ms": 156
    },
    "openrouter": {
      "status": "up",
      "response_time_ms": 312
    },
    "together_ai": {
      "status": "up",
      "response_time_ms": 189
    },
    "database": {
      "status": "up",
      "response_time_ms": 0
    }
  }
}
```

**Use Cases:**

- **Monitoring**: Regular polling to detect service outages
- **Deployment Verification**: Confirm all dependencies configured correctly
- **Load Balancer**: Health check target for traffic routing
- **CI/CD**: Pre-deployment smoke test

**Performance:**

- Typical response time: 300-500ms (parallel checks)
- Sequential would take: ~900-1200ms (3x slower)

---

### 2. POST /generate

Analyze a GitHub repository and generate a cat image visualization.

**Authentication:** **Required** (session cookie)

**Purpose:** Process repository code and return comprehensive analysis with AI-generated cat image. The generation is linked to the authenticated user's account.

**Method:** `POST`

**URL:** `/generate`

**Request Headers:**
```
Content-Type: application/json
Cookie: session_token=<token>
```

**Request Body:**
```json
{
  "github_url": "https://github.com/owner/repository"
}
```

**Request Schema:**

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|-----------|
| `github_url` | string | Yes | Full GitHub repository URL | Must match GitHub URL pattern |

**Valid URL Formats:**
- `https://github.com/owner/repo`
- `https://github.com/owner/repo.git`
- `http://github.com/owner/repo` (auto-upgraded to https)

**Response Codes:**

| Code | Status | Description |
|------|--------|-------------|
| `200` | OK | Generation successful |
| `401` | Unauthorized | Not authenticated or session expired |
| `403` | Forbidden | Private repository without access |
| `404` | Not Found | Repository doesn't exist |
| `422` | Unprocessable Entity | Invalid request body (validation error) |
| `500` | Internal Server Error | Analysis or generation failed |

**Response Body (Success):**

```json
{
  "success": true,
  "generation_id": "550e8400-e29b-41d4-a716-446655440000",
  "repository": {
    "url": "https://github.com/python/cpython",
    "name": "cpython",
    "owner": "python",
    "primary_language": "Python",
    "size_kb": 150000,
    "stars": 50000
  },
  "analysis": {
    "code_quality_score": 9.5,
    "files_analyzed": [
      "README.md",
      "Python/main.c",
      "Lib/test/test_sys.py"
    ],
    "metrics": {
      "line_length_avg": 85,
      "line_length_max": 120,
      "function_length_avg": 15,
      "has_tests": true,
      "has_type_hints": true,
      "has_documentation": true
    }
  },
  "cat_attributes": {
    "size": "huge",
    "age": "legendary",
    "beauty_score": 9.5,
    "expression": "proud",
    "background": "tech conference stage with adoring crowd",
    "accessories": "multiple gold medals and trophies"
  },
  "story": "The Python repository is that ancient, wise cat who invented all nine lives and now just watches lesser felines struggle with their mere single existence. With its pristine 9.5/10 code quality and 50,000 star entourage, this legendary beast doesn't even need to meow – everyone already knows it's royalty. It sits on its tech conference throne, draped in medals, probably wondering when the rest of the world will catch up to 1991.",
  "meme_text": {
    "top": "PYTHON POWER",
    "bottom": "LEGENDARY CODE"
  },
  "image": {
    "url": "/generated_images/550e8400-e29b-41d4-a716-446655440000.png",
    "binary": "iVBORw0KGgoAAAANSUhEUgAA...(base64)...AAABJRU5ErkJggg==",
    "prompt": "A magnificent legendary cat (10+ years old), huge, with pristine fur and a proud expression. Background: tech conference stage with adoring crowd. The cat wears multiple gold medals and trophies. Photorealistic, detailed fur texture, professional photography, 8k quality. The cat should look natural and lifelike."
  },
  "timestamp": "2025-10-13T12:34:56.789Z"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether generation succeeded |
| `generation_id` | string | Unique UUID for this generation |
| `repository.url` | string | Original GitHub URL |
| `repository.name` | string | Repository name |
| `repository.owner` | string | Repository owner/organization |
| `repository.primary_language` | string | Main programming language (null if none) |
| `repository.size_kb` | integer | Repository size in kilobytes |
| `repository.stars` | integer | Number of GitHub stars (null if private) |
| `analysis.code_quality_score` | float | Overall quality score (0.0-10.0) |
| `analysis.files_analyzed` | array | List of files that were analyzed |
| `analysis.metrics` | object | Detailed code metrics |
| `cat_attributes.size` | string | Cat size: tiny, small, medium, large, huge |
| `cat_attributes.age` | string | Cat age: kitten, young, adult cat, senior, legendary |
| `cat_attributes.beauty_score` | float | Visual quality score (mirrors code quality) |
| `cat_attributes.expression` | string | Facial expression based on quality |
| `cat_attributes.background` | string | Scene background description |
| `cat_attributes.accessories` | string | Optional accessories/props (null if none) |
| `story` | string | Funny 3-5 sentence story about repository |
| `meme_text.top` | string | Top meme text (2-4 words, uppercase) |
| `meme_text.bottom` | string | Bottom meme text (2-4 words, uppercase) |
| `image.url` | string | Relative URL path to image file |
| `image.binary` | string | Base64-encoded PNG image data |
| `image.prompt` | string | Exact prompt sent to image generator |
| `timestamp` | string | ISO 8601 timestamp of generation |

**Workflow Pipeline (11 Nodes):**

1. **extract_metadata** (3-5s) - Fetch repo metadata from GitHub API
2. **select_files** (1s) - Choose strategic files for analysis
3. **fetch_files** (2-3s) - Download file contents via Contents API
4. **analyze_code** (3-5s) - LLM code quality analysis (Gemini 2.5 Flash)
5. **map_attributes** (<1s) - Map quality to cat attributes
6. **generate_story** (2-3s) - LLM story generation
7. **generate_meme_text** (1-2s) - LLM meme text generation
8. **generate_prompt** (<1s) - Create image prompt
9. **generate_image** (5-8s) - Generate cat image (FLUX.1.1-pro)
10. **add_text_overlay** (1s) - Add meme text to image (Pillow)
11. **save_to_db** (<1s) - Persist to PostgreSQL

**Total Time:** ~15-25 seconds (varies by repository size and API latency)

**Error Response (401 Unauthorized):**

```json
{
  "detail": "Not authenticated. Please log in."
}
```

**Error Response (403 Forbidden):**

```json
{
  "detail": "Repository is private and requires authentication"
}
```

**Error Response (404 Not Found):**

```json
{
  "detail": "Repository not found: https://github.com/nonexistent/repo"
}
```

**Error Response (500 Internal Server Error):**

```json
{
  "detail": "Internal server error: Image generation failed"
}
```

**Example Requests:**

**Basic Request (with authentication):**
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"github_url": "https://github.com/python/cpython"}'
```

**Save Response to File:**
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"github_url": "https://github.com/python/cpython"}' \
  -o response.json
```

**Extract Image URL:**
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"github_url": "https://github.com/python/cpython"}' \
  | jq -r '.image.url'
```

**Extract Story Only:**
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"github_url": "https://github.com/python/cpython"}' \
  | jq -r '.story'
```

**Pretty Print Response:**
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"github_url": "https://github.com/python/cpython"}' \
  | jq '.'
```

**Use Cases:**

- **Portfolio Visualization**: Generate unique images for project showcases
- **Code Review Reports**: Include fun visualizations in reports
- **GitHub Bot**: Automated PR comments with cat images
- **Gamification**: Reward contributors with cat quality scores
- **Marketing**: Social media content from repository analysis

**Rate Limiting:**

- Currently: No rate limiting
- Future: Will implement per-IP or per-API-key limits
- External APIs have their own limits (GitHub: 5000/hour, OpenRouter: varies by plan)

**Caching:**

- Currently: No caching (always fresh analysis)
- Future: Will cache results by repo URL + commit SHA for repeated requests

---

## Authentication Endpoints

### 3. POST /auth/login

Authenticate user and create session.

**Purpose:** Login with username/password, receive httpOnly session cookie

**Method:** `POST`

**URL:** `/auth/login`

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "testuser",
  "password": "securepassword123"
}
```

**Request Schema:**

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|-----------|
| `username` | string | Yes | User's username | 1-255 characters |
| `password` | string | Yes | User's password | Min 1 character |

**Response Codes:**

| Code | Status | Description |
|------|--------|-------------|
| `200` | OK | Login successful, session cookie set |
| `401` | Unauthorized | Invalid username or password |
| `422` | Unprocessable Entity | Missing required fields |

**Response Body (Success):**

```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "testuser",
    "email": "test@example.com",
    "created_at": "2025-10-07T12:34:56Z"
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Always true for successful login |
| `message` | string | Success message |
| `user.id` | string | User UUID |
| `user.username` | string | Username |
| `user.email` | string | Email (null if not set) |
| `user.created_at` | string | ISO 8601 account creation timestamp |

**Session Cookie:**

The `session_token` cookie is set with the following properties:
- **Name:** `session_token`
- **Value:** 64-character hex token
- **httpOnly:** `true` (prevents XSS attacks)
- **secure:** `false` (development), `true` (production with HTTPS)
- **sameSite:** `lax` (CSRF protection)
- **maxAge:** 604800 seconds (7 days)

**Error Response (401):**

```json
{
  "detail": "Invalid username or password"
}
```

**Example Request:**

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "mypassword"}' \
  -c cookies.txt
```

**Notes:**
- Password is hashed with bcrypt (never stored in plain text)
- Session token is cryptographically random (64-char hex)
- Multiple concurrent sessions allowed (login doesn't invalidate existing sessions)
- Cookies persist across browser restarts (7-day expiration)

---

### 4. POST /auth/logout

Logout user and delete session.

**Purpose:** Destroy session and clear session cookie

**Method:** `POST`

**URL:** `/auth/logout`

**Request Headers:** None required

**Request Body:** None

**Authentication:** Optional (logout always succeeds)

**Response Codes:**

| Code | Status | Description |
|------|--------|-------------|
| `200` | OK | Logout successful (always) |

**Response Body:**

```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Always true |
| `message` | string | Success message |

**Behavior:**
- Deletes session from database (if exists)
- Clears `session_token` cookie
- Always returns 200 (idempotent operation)
- Works even if not authenticated or session expired

**Example Request:**

```bash
curl -X POST http://localhost:8000/auth/logout \
  -b cookies.txt \
  -c cookies.txt
```

**Notes:**
- Logout is idempotent (can call multiple times safely)
- Does not invalidate other sessions (if user logged in from multiple devices)
- Cookie is cleared from browser regardless of database result

---

### 5. GET /auth/me

Get current user information.

**Purpose:** Retrieve authenticated user's profile

**Method:** `GET`

**URL:** `/auth/me`

**Authentication:** **Required** (session cookie)

**Request Headers:** None

**Response Codes:**

| Code | Status | Description |
|------|--------|-------------|
| `200` | OK | User information returned |
| `401` | Unauthorized | Not authenticated or session expired |

**Response Body (Success):**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "testuser",
  "email": "test@example.com",
  "created_at": "2025-10-07T12:34:56Z"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | User UUID |
| `username` | string | Username |
| `email` | string | Email (null if not set) |
| `created_at` | string | ISO 8601 account creation timestamp |

**Error Response (401 - Not Authenticated):**

```json
{
  "detail": "Not authenticated. Please log in."
}
```

**Error Response (401 - Expired Session):**

```json
{
  "detail": "Invalid or expired session. Please log in again."
}
```

**Example Request:**

```bash
curl -X GET http://localhost:8000/auth/me \
  -b cookies.txt
```

**Use Cases:**
- Check if user is logged in
- Display user profile in UI
- Verify session validity
- Get user ID for API requests

**Notes:**
- Session is verified and expired sessions are deleted automatically
- No sensitive fields returned (password_hash, api_token excluded)

---

### 6. GET /auth/status

Check authentication status (optional auth).

**Purpose:** Determine if user is authenticated without requiring login

**Method:** `GET`

**URL:** `/auth/status`

**Authentication:** Optional (works for both authenticated and unauthenticated)

**Request Headers:** None

**Response Codes:**

| Code | Status | Description |
|------|--------|-------------|
| `200` | OK | Always returns 200 |

**Response Body (Authenticated):**

```json
{
  "authenticated": true,
  "username": "testuser"
}
```

**Response Body (Not Authenticated):**

```json
{
  "authenticated": false,
  "username": null
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `authenticated` | boolean | Whether user has valid session |
| `username` | string | Username if authenticated, null otherwise |

**Example Request:**

```bash
curl -X GET http://localhost:8000/auth/status \
  -b cookies.txt
```

**Use Cases:**
- Frontend auth check without triggering 401 errors
- Conditional UI rendering (show login vs. dashboard)
- Public pages that adapt to logged-in users
- Health check for authentication system

**Notes:**
- Never returns error (always 200)
- Safe to call repeatedly (lightweight check)
- Useful for frontend state management

---

## Generation Management Endpoints

### 7. GET /generations

List user's generations (paginated).

**Authentication:** **Required** (session cookie)

**Purpose:** Retrieve a list of all generations created by the authenticated user

**Method:** `GET`

**URL:** `/generations`

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 50 | Maximum results per page (max: 100) |
| `offset` | integer | 0 | Number of results to skip (pagination) |

**Request Headers:**
```
Cookie: session_token=<token>
```

**Response Codes:**

| Code | Status | Description |
|------|--------|-------------|
| `200` | OK | List retrieved successfully |
| `401` | Unauthorized | Not authenticated or session expired |

**Response Body:**

```json
{
  "success": true,
  "count": 2,
  "total": 15,
  "limit": 50,
  "offset": 0,
  "has_more": true,
  "generations": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "github_url": "https://github.com/python/cpython",
      "repo_owner": "python",
      "repo_name": "cpython",
      "primary_language": "Python",
      "code_quality_score": 9.5,
      "image_path": "/generated_images/550e8400.png",
      "created_at": "2025-10-14T12:34:56.000Z"
    },
    {
      "id": "660f9511-f39c-52e5-b827-557766551111",
      "github_url": "https://github.com/facebook/react",
      "repo_owner": "facebook",
      "repo_name": "react",
      "primary_language": "JavaScript",
      "code_quality_score": 8.5,
      "image_path": "/generated_images/660f9511.png",
      "created_at": "2025-10-13T08:15:30.000Z"
    }
  ]
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Always true for successful requests |
| `count` | integer | Number of results in this response |
| `total` | integer | Total number of user's generations |
| `limit` | integer | Maximum results per page (from query) |
| `offset` | integer | Results skipped (from query) |
| `has_more` | boolean | Whether more results are available |
| `generations` | array | List of generation summaries |
| `generations[].id` | string | Generation UUID |
| `generations[].github_url` | string | Repository URL |
| `generations[].repo_owner` | string | Repository owner |
| `generations[].repo_name` | string | Repository name |
| `generations[].primary_language` | string | Main programming language |
| `generations[].code_quality_score` | float | Quality score (0.0-10.0) |
| `generations[].image_path` | string | Path to generated image |
| `generations[].created_at` | string | ISO 8601 creation timestamp |

**Example Requests:**

**Get first page:**
```bash
curl -X GET http://localhost:8000/generations \
  -b cookies.txt
```

**Get with pagination:**
```bash
curl -X GET "http://localhost:8000/generations?limit=10&offset=20" \
  -b cookies.txt
```

**Extract generation IDs:**
```bash
curl -X GET http://localhost:8000/generations \
  -b cookies.txt \
  | jq -r '.generations[].id'
```

**Use Cases:**
- Display user dashboard with generation history
- Pagination for long lists of generations
- Building gallery views
- Analytics on user activity

**Notes:**
- Results ordered by creation date (most recent first)
- Only returns authenticated user's generations (privacy)
- Empty list if user has no generations
- `has_more` field helps implement infinite scroll or pagination UI

---

### 8. GET /generation/{generation_id}

Get generation details by ID (public).

**Authentication:** Not required (public endpoint for sharing)

**Purpose:** Retrieve complete details about a specific generation, including repository analysis, cat attributes, story, and image data. This endpoint is public to enable sharing generation links.

**Method:** `GET`

**URL:** `/generation/{generation_id}`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `generation_id` | string | Yes | UUID of the generation |

**Request Headers:** None required

**Response Codes:**

| Code | Status | Description |
|------|--------|-------------|
| `200` | OK | Generation found and returned |
| `404` | Not Found | Generation not found |

**Response Body:**

```json
{
  "success": true,
  "generation_id": "550e8400-e29b-41d4-a716-446655440000",
  "repository": {
    "url": "https://github.com/python/cpython",
    "name": "cpython",
    "owner": "python",
    "primary_language": "Python",
    "size_kb": 150000,
    "stars": null
  },
  "analysis": {
    "code_quality_score": 9.5,
    "files_analyzed": ["README.md", "Python/main.c"],
    "metrics": {
      "has_tests": true,
      "has_type_hints": true,
      "has_documentation": true
    }
  },
  "cat_attributes": {
    "size": "huge",
    "age": "legendary",
    "beauty_score": 9.5,
    "expression": "proud",
    "background": "tech conference stage",
    "accessories": "multiple gold medals"
  },
  "story": "The Python repository is that ancient, wise cat...",
  "meme_text": {
    "top": "PYTHON POWER",
    "bottom": "LEGENDARY CODE"
  },
  "image": {
    "url": "/generated_images/550e8400.png",
    "binary": null,
    "prompt": "A magnificent legendary cat..."
  },
  "timestamp": "2025-10-14T12:34:56.000Z"
}
```

**Response Fields:**

Same structure as POST /generate response, except:
- `image.binary` is `null` (use static file endpoint for image)
- `repository.stars` may be `null` (not stored in database)

**Error Response (404):**

```json
{
  "detail": "Generation not found: 550e8400-e29b-41d4-a716-446655440000"
}
```

**Example Requests:**

**Get generation details:**
```bash
curl -X GET http://localhost:8000/generation/550e8400-e29b-41d4-a716-446655440000
```

**Get and extract story:**
```bash
curl -X GET http://localhost:8000/generation/550e8400-e29b-41d4-a716-446655440000 \
  | jq -r '.story'
```

**Get image URL:**
```bash
IMAGE_URL=$(curl -s http://localhost:8000/generation/550e8400-e29b-41d4-a716-446655440000 \
  | jq -r '.image.url')
echo "http://localhost:8000${IMAGE_URL}"
```

**Use Cases:**
- Shareable generation links (no authentication needed)
- Embedding in external websites
- Social media sharing
- Public portfolio/gallery pages
- Detail view in frontend application

**Notes:**
- Public endpoint (no authentication required)
- Works for both authenticated and anonymous users
- Returns complete generation data (except base64 image)
- Use static file endpoint to download actual image file
- Returns 404 for non-existent or deleted generations

---

## Static File Serving

### GET /generated_images/{filename}

Serve generated cat images as static files.

**Method:** `GET`

**URL Pattern:** `/generated_images/{generation_id}.png`

**Example:** `http://localhost:8000/generated_images/550e8400-e29b-41d4-a716-446655440000.png`

**Response:**
- **Content-Type**: `image/png`
- **Body**: PNG image binary data

**Configuration:**

```python
# In app/main.py
from fastapi.staticfiles import StaticFiles

app.mount(
    "/generated_images",
    StaticFiles(directory="/generated_images"),
    name="generated_images"
)
```

**Storage Location:** `./generated_images/` (relative to project root)

**File Naming:** `{generation_id}.png` (UUID from /generate response)

**Example Usage:**

```bash
# Get image URL from response
IMAGE_URL=$(curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"github_url": "https://github.com/python/cpython"}' \
  | jq -r '.image.url')

# Download image
curl "http://localhost:8000${IMAGE_URL}" -o cat.png

# Or open in browser
open "http://localhost:8000${IMAGE_URL}"
```

---

## Interactive Documentation

### Swagger UI

**URL:** http://localhost:8000/docs

**Features:**
- Interactive API testing
- Request/response examples
- Schema documentation
- Try-it-out functionality
- Authentication testing (when added)

**Usage:**

1. Navigate to http://localhost:8000/docs
2. Click on endpoint to expand
3. Click "Try it out"
4. Enter request parameters
5. Click "Execute"
6. View response

### ReDoc

**URL:** http://localhost:8000/redoc

**Features:**
- Cleaner, read-only documentation
- Better for sharing with stakeholders
- Hierarchical navigation
- Printable format

---

## Python Client Example

```python
import requests
import json
from pathlib import Path

class RepoToCatClient:
    """Python client for Repo-to-Cat API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()

    def health_check(self) -> dict:
        """Check API health status."""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def generate(self, github_url: str, save_image: str = None) -> dict:
        """
        Generate cat image for repository.

        Args:
            github_url: GitHub repository URL
            save_image: Optional path to save image file

        Returns:
            dict: Generation response with analysis and image data
        """
        response = self.session.post(
            f"{self.base_url}/generate",
            json={"github_url": github_url},
            timeout=30
        )
        response.raise_for_status()

        data = response.json()

        # Optionally download and save image
        if save_image and data.get("image", {}).get("url"):
            image_url = f"{self.base_url}{data['image']['url']}"
            image_response = self.session.get(image_url)
            image_response.raise_for_status()

            Path(save_image).write_bytes(image_response.content)
            print(f"Image saved to: {save_image}")

        return data

# Usage example
if __name__ == "__main__":
    client = RepoToCatClient()

    # Check health
    health = client.health_check()
    print(f"API Status: {health['status']}")

    # Generate cat image
    result = client.generate(
        github_url="https://github.com/python/cpython",
        save_image="python_cat.png"
    )

    print(f"\nGeneration ID: {result['generation_id']}")
    print(f"Quality Score: {result['analysis']['code_quality_score']}/10")
    print(f"Cat Size: {result['cat_attributes']['size']}")
    print(f"Cat Age: {result['cat_attributes']['age']}")
    print(f"\nStory:\n{result['story']}")
    print(f"\nMeme Text:")
    print(f"  TOP: {result['meme_text']['top']}")
    print(f"  BOTTOM: {result['meme_text']['bottom']}")
```

---

## JavaScript Client Example

```javascript
class RepoToCatClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }

    async healthCheck() {
        const response = await fetch(`${this.baseUrl}/health`);
        if (!response.ok) throw new Error('Health check failed');
        return response.json();
    }

    async generate(githubUrl) {
        const response = await fetch(`${this.baseUrl}/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ github_url: githubUrl })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Generation failed');
        }

        return response.json();
    }

    getImageUrl(imageUrl) {
        return `${this.baseUrl}${imageUrl}`;
    }
}

// Usage example
(async () => {
    const client = new RepoToCatClient();

    // Check health
    const health = await client.healthCheck();
    console.log('API Status:', health.status);

    // Generate cat image
    const result = await client.generate('https://github.com/python/cpython');

    console.log('Generation ID:', result.generation_id);
    console.log('Quality Score:', result.analysis.code_quality_score);
    console.log('Story:', result.story);
    console.log('Image URL:', client.getImageUrl(result.image.url));
})();
```

---

## Testing Endpoints

### Using pytest

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "services" in data

def test_generate_success(mocker):
    """Test generate endpoint with valid repository."""
    # Mock workflow to avoid external API calls
    mock_workflow = mocker.patch("app.api.routes.create_workflow")
    mock_workflow.return_value.invoke.return_value = {
        "metadata": {"name": "test-repo", "owner": "test"},
        "analysis": {"code_quality_score": 7.5},
        "cat_attrs": {"size": "medium", "age": "adult cat"},
        "story": "A test story",
        "meme_text_top": "TEST TOP",
        "meme_text_bottom": "TEST BOTTOM",
        "image": {"url": "/test.png", "binary": "base64data", "prompt": "test"}
    }

    response = client.post(
        "/generate",
        json={"github_url": "https://github.com/test/repo"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "generation_id" in data
    assert "story" in data
    assert "meme_text" in data
```

### Using curl

```bash
# Health check
curl -X GET http://localhost:8000/health \
  -H "Accept: application/json"

# Generate (expect 200)
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"github_url": "https://github.com/octocat/Hello-World"}' \
  -w "\nHTTP Status: %{http_code}\n"

# Invalid request (expect 422)
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"invalid": "data"}' \
  -w "\nHTTP Status: %{http_code}\n"

# Non-existent repo (expect 404)
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"github_url": "https://github.com/nonexistent/repo"}' \
  -w "\nHTTP Status: %{http_code}\n"
```

---

## CORS Configuration

**Status:** Enabled for all origins (development mode)

**Configuration in `app/main.py`:**

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Development: allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Production Recommendation:**

```python
# Restrict to specific origins
allow_origins=[
    "https://repo-to-cat.com",
    "https://www.repo-to-cat.com"
]
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | When It Occurs |
|------|---------|----------------|
| 200 | OK | Successful request |
| 403 | Forbidden | Private repository, no access |
| 404 | Not Found | Repository doesn't exist |
| 422 | Unprocessable Entity | Invalid request body (validation error) |
| 500 | Internal Server Error | Unexpected error during processing |

### Error Response Format

All errors return JSON with `detail` field:

```json
{
  "detail": "Human-readable error message"
}
```

### Common Error Messages

| Message | Cause | Solution |
|---------|-------|----------|
| "Repository not found: ..." | Invalid GitHub URL or deleted repo | Verify URL is correct |
| "Repository is private and requires authentication" | Private repo, no access | Make repo public or add access token |
| "Internal server error: ..." | LLM/image service failure | Check /health endpoint, retry |
| "Field required" | Missing required field | Check request schema |

---

## Performance

### Response Times

| Endpoint | Typical | Notes |
|----------|---------|-------|
| GET /health | 300-500ms | Parallel health checks |
| POST /generate | 15-25s | Depends on repo size and API latency |

### Optimization Tips

1. **Caching**: Cache repeated requests by `repo_url + commit_sha`
2. **Async Processing**: Return `generation_id` immediately, poll for results
3. **CDN**: Serve images from CDN instead of local filesystem
4. **Database Pooling**: Already configured (10 connections)
5. **Load Balancing**: Multiple uvicorn workers for high traffic

---

## Security

### Current State

- ✅ Input validation (Pydantic schemas)
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ CORS configured
- ❌ No authentication
- ❌ No rate limiting
- ❌ No API keys

### Future Improvements

1. **API Keys**: Require API key for /generate endpoint
2. **Rate Limiting**: 100 requests/hour per IP/key
3. **Request Timeouts**: 30s timeout for /generate
4. **Input Sanitization**: Strict GitHub URL validation
5. **HTTPS**: Require HTTPS in production

---

## Related Documentation

- **Stage 8 Summary**: [docs/stages/stage-8-summary.md](stages/stage-8-summary.md)
- **Health Check Guide**: [docs/health-check.md](health-check.md)
- **FastAPI Guide**: [docs/fastapi-guide.md](fastapi-guide.md)
- **Testing Guide**: [docs/testing-guide.md](testing-guide.md)

---

**API Reference Complete!** For interactive testing, visit http://localhost:8000/docs
