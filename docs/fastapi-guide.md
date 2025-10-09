# FastAPI Application Guide

**Last Updated:** 2025-10-08
**Stage:** 1.3 - FastAPI Skeleton

---

## Overview

Repo-to-Cat uses FastAPI as its web framework. This guide covers the FastAPI application setup, endpoints, middleware, and development workflow.

**What's included:**
- FastAPI app initialization with auto-docs
- Health check endpoint with database connectivity test
- CORS middleware for cross-origin requests
- Swagger UI at `/docs` and ReDoc at `/redoc`

---

## Quick Start

### Start the API Server

```bash
# Start all services (PostgreSQL + FastAPI)
docker compose up -d

# Check containers are running
docker compose ps

# View app logs
docker compose logs app -f
```

### Test the API

```bash
# Root endpoint
curl http://localhost:8000/

# Health check
curl http://localhost:8000/health

# Swagger UI (open in browser)
http://localhost:8000/docs

# ReDoc UI (open in browser)
http://localhost:8000/redoc
```

---

## Application Structure

### Main Application File

Location: `app/main.py`

**Key components:**
1. **FastAPI app initialization** - Title, description, version, docs URLs
2. **CORS middleware** - Configured for localhost origins
3. **Endpoints** - Root (`/`) and health check (`/health`)
4. **Database integration** - Uses `get_db()` dependency

### Configuration

```python
# app/main.py
app = FastAPI(
    title="Repo-to-Cat API",
    description="GitHub Repository Quality Visualizer",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)
```

---

## Endpoints

### GET / (Root)

Returns basic API information and navigation links.

**Request:**
```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "message": "Welcome to Repo-to-Cat API",
  "description": "GitHub Repository Quality Visualizer",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

### GET /health

Health check endpoint that verifies database connectivity.

**Request:**
```bash
curl http://localhost:8000/health
```

**Response (healthy):**
```json
{
  "status": "healthy",
  "database": {
    "status": "up"
  },
  "timestamp": "2025-10-08T17:17:40.568562+00:00"
}
```

**Response (unhealthy):**
```json
{
  "status": "unhealthy",
  "database": {
    "status": "down",
    "error": "connection refused"
  },
  "timestamp": "2025-10-08T17:17:40.568562+00:00"
}
```

**What it checks:**
- Database connectivity via `SELECT 1` query
- Returns ISO 8601 timestamp
- Overall status based on database health

---

## CORS Configuration

### Allowed Origins

The API allows cross-origin requests from:
- `http://localhost:3000` (React dev server)
- `http://localhost:8000` (API itself)
- `http://localhost:8080` (Alternative frontend port)

### Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Testing CORS

```bash
# OPTIONS request
curl -X OPTIONS http://localhost:8000/health \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET" \
  -v
```

---

## API Documentation

FastAPI provides automatic interactive API documentation.

### Swagger UI

**URL:** http://localhost:8000/docs

**Features:**
- Interactive API explorer
- Try out endpoints directly
- View request/response schemas
- Authentication testing (future)

### ReDoc UI

**URL:** http://localhost:8000/redoc

**Features:**
- Clean, responsive documentation
- Searchable
- Downloadable as PDF
- Better for reading/reference

### OpenAPI JSON

**URL:** http://localhost:8000/openapi.json

Raw OpenAPI 3.0 specification for API clients and code generation.

---

## Development Workflow

### Making Changes

1. **Edit code** in `app/main.py` or other modules
2. **Restart container** to pick up changes:
   ```bash
   docker compose restart app
   ```
3. **Check logs** for errors:
   ```bash
   docker compose logs app -f
   ```
4. **Test changes**:
   ```bash
   curl http://localhost:8000/health
   ```

### Hot Reload (Optional)

To enable hot reload, modify `docker-compose.yml`:

```yaml
services:
  app:
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./app:/app/app  # Mount app directory
```

**Note:** Current setup doesn't have --reload enabled in production mode.

---

## Testing the API

### Run Tests

```bash
# Run all FastAPI tests
docker compose exec app pytest tests/unit/test_main.py -v

# Run specific test
docker compose exec app pytest tests/unit/test_main.py::TestHealthEndpoint::test_health_endpoint_exists -v

# Run with coverage
docker compose exec app pytest tests/unit/test_main.py --cov=app.main
```

### Test Coverage

Stage 1.3 includes 11 comprehensive tests:

**FastAPI App Tests (2):**
- App initialization
- Version attribute

**Health Endpoint Tests (5):**
- Endpoint exists (200 OK)
- Returns JSON
- Response structure validation
- Database connectivity check
- Timestamp format validation

**API Docs Tests (3):**
- Swagger UI accessible
- OpenAPI JSON endpoint
- ReDoc UI accessible

**CORS Tests (1):**
- CORS headers present

**Coverage:** 93% (app/main.py: 22 statements, 3 missed)

---

## Common Tasks

### Add a New Endpoint

1. **Define route in `app/main.py`:**
   ```python
   @app.get("/repositories")
   async def list_repositories():
       return {"repositories": []}
   ```

2. **Restart container:**
   ```bash
   docker compose restart app
   ```

3. **Test endpoint:**
   ```bash
   curl http://localhost:8000/repositories
   ```

4. **Check Swagger UI:**
   http://localhost:8000/docs

### Add Request/Response Models

1. **Create Pydantic schemas** in `app/api/schemas.py` (future stage)
2. **Use in endpoint:**
   ```python
   @app.post("/generate")
   async def generate(request: GenerateRequest) -> GenerateResponse:
       ...
   ```

### Add Middleware

```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

---

## Troubleshooting

### Issue: "Connection refused" on /health

**Cause:** PostgreSQL not running or wrong connection string

**Solution:**
```bash
# Check postgres is running
docker compose ps postgres

# Check database logs
docker compose logs postgres

# Restart postgres
docker compose restart postgres

# Verify connection string in .env
DATABASE_URL=postgresql://repo_user:repo_password@postgres:5432/repo_to_cat
```

### Issue: "Textual SQL expression should be text()"

**Cause:** SQLAlchemy 2.0 requires explicit `text()` for raw SQL

**Solution:**
```python
from sqlalchemy import text

# Wrong
db.execute("SELECT 1")

# Correct
db.execute(text("SELECT 1"))
```

### Issue: Changes not reflected after editing code

**Cause:** Docker container not restarted or volume not mounted

**Solution:**
```bash
# Restart container
docker compose restart app

# Or rebuild if Dockerfile changed
docker compose up -d --build app
```

### Issue: Port 8000 already in use

**Cause:** Another service using port 8000

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Stop the process or change port in docker-compose.yml
ports:
  - "8001:8000"  # Map to 8001 on host
```

### Issue: 404 on /docs

**Cause:** FastAPI docs disabled or wrong URL

**Solution:**
```python
# Ensure docs URLs are set
app = FastAPI(
    docs_url="/docs",      # Must be set
    redoc_url="/redoc",    # Must be set
    openapi_url="/openapi.json"
)
```

---

## Database Integration

### Using Database Dependency

```python
from sqlalchemy.orm import Session
from app.core.database import get_db

@app.get("/users")
async def list_users(db: Session = Depends(get_db)):
    # db is a SQLAlchemy session
    users = db.query(User).all()
    return {"users": users}
```

### Connection Pooling

FastAPI uses SQLAlchemy's connection pooling automatically:
- **pool_pre_ping:** Enabled (checks connections before use)
- **echo:** Enabled in development (logs SQL queries)

---

## Best Practices

### 1. Always Use Docker

❌ Don't run: `uvicorn app.main:app --reload`
✅ Do run: `docker compose up -d`

**Why:** Production parity (see LL-DEV-001)

### 2. Use Dependency Injection

```python
# Good
@app.get("/endpoint")
async def endpoint(db: Session = Depends(get_db)):
    ...

# Bad - manual connection
@app.get("/endpoint")
async def endpoint():
    engine = create_engine(...)  # Don't do this
```

### 3. Test All Endpoints

Write tests for:
- Status codes (200, 404, 500)
- Response structure
- Error handling
- Edge cases

### 4. Document with Docstrings

```python
@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint.

    Checks database connectivity and returns system status.

    Returns:
        dict: Health status with database status and timestamp
    """
```

Docstrings appear in Swagger UI automatically.

---

## Performance Tips

### 1. Use Async Endpoints When Possible

```python
@app.get("/fast")
async def fast_endpoint():
    return {"message": "fast"}
```

### 2. Add Response Models

```python
@app.get("/data", response_model=DataResponse)
async def get_data():
    return DataResponse(...)
```

Enables validation and faster serialization.

### 3. Enable HTTP Caching (Future)

```python
from fastapi import Response

@app.get("/static-data")
async def static_data(response: Response):
    response.headers["Cache-Control"] = "max-age=3600"
    return {"data": "cached for 1 hour"}
```

---

## Related Documentation

- **Docker Setup:** `docs/docker-setup.md`
- **Database Guide:** `docs/database-guide.md`
- **Testing Guide:** `docs/testing-guide.md`
- **Stage 1.3 Summary:** `docs/stages/stage-1.3-summary.md`

---

## Next Steps

**Future stages will add:**
- `/generate` endpoint (Stage 8.2)
- Request/response schemas (Stage 2.3)
- Error handling middleware (Stage 9.2)
- Authentication (post-MVP)

**For now, you have:**
- ✅ Working FastAPI app
- ✅ Health check endpoint
- ✅ Auto-generated docs
- ✅ CORS configured
- ✅ Database integration ready

Continue to **Stage 2.1: Configuration Management**
