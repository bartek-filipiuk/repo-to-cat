# Stage 1.2: Docker & Database Setup

**Status:** ✅ Complete
**Pull Request:** [#1](https://github.com/bartek-filipiuk/repo-to-cat/pull/1)
**Last Updated:** 2025-10-08
**Branch:** `feature/stage-1.2-docker-database`

---

## Overview

Stage 1.2 implements the complete Docker and database infrastructure for Repo-to-Cat, including PostgreSQL setup, Alembic migrations, and comprehensive database testing.

**What you can do now:**
- Run PostgreSQL in Docker container
- Connect to database from host machine
- Create and apply database migrations with Alembic
- Perform CRUD operations on Users and Generations
- Run database connectivity tests

---

## What Was Built

### 1. Docker Infrastructure

**Files:**
- `Dockerfile` - Python 3.11 application container
- `docker-compose.yml` - PostgreSQL 15 service definition
- `.env` - Local environment configuration (not committed)
- `.env.example` - Environment template

**Features:**
- PostgreSQL 15 Alpine container
- Health checks for database readiness
- Persistent volume for data storage
- Port mapping (5434:5432) to avoid local conflicts
- Development mode with hot reload support

**See:** [docker-setup.md](../docker-setup.md)

---

### 2. Database Schema

**Models (SQLAlchemy ORM):**

#### `users` Table
```python
class User(Base):
    id: UUID (primary key)
    username: str (unique)
    api_token: str (unique)
    created_at: datetime
    updated_at: datetime
```

#### `generations` Table
```python
class Generation(Base):
    id: UUID (primary key)
    github_url: str
    repo_owner: str
    repo_name: str
    primary_language: str
    repo_size_kb: int
    code_quality_score: Decimal(3,1)
    cat_attributes: JSONB
    analysis_data: JSONB
    image_path: str
    image_prompt: str
    created_at: datetime
```

**Files:**
- `app/models/database.py` - SQLAlchemy models
- `app/core/database.py` - Database connection & session management

**See:** [database-guide.md](../database-guide.md)

---

### 3. Database Migrations

**Alembic Configuration:**
- `alembic.ini` - Alembic configuration file
- `alembic/env.py` - Environment setup (auto-loads models)
- `alembic/versions/c31bba7cdef1_*.py` - Initial migration

**Features:**
- Auto-generate migrations from model changes
- Programmatic DATABASE_URL loading from `.env`
- Support for upgrade/downgrade operations

**Commands:**
```bash
# Apply migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Description"

# View history
alembic history

# Rollback
alembic downgrade -1
```

**See:** [database-guide.md](../database-guide.md#alembic-migrations)

---

### 4. Testing

**Test Files:**
- `tests/unit/test_database.py` - Database connectivity tests (7 tests)
- `tests/unit/test_config.py` - Configuration tests (existing)

**Database Tests:**
1. ✅ Raw database connection
2. ✅ SQLAlchemy session creation
3. ✅ FastAPI dependency injection
4. ✅ Users table exists
5. ✅ Generations table exists
6. ✅ Create/delete user operations
7. ✅ Create/delete generation operations

**Coverage:**
- Core: 93%
- Database: 92%
- Models: 90%

**See:** [testing-guide.md](../testing-guide.md)

---

### 5. Support Scripts

**Files:**
- `scripts/init_db.sql` - Database initialization placeholder

---

## Quick Start

### 1. Start PostgreSQL

```bash
# Start database container
docker compose up -d postgres

# Verify it's running
docker compose ps

# Should show: repo-to-cat-postgres   Up (healthy)
```

### 2. Apply Migrations

```bash
# Apply database schema
alembic upgrade head

# Verify tables created
psql postgresql://repo_user:repo_password@localhost:5434/repo_to_cat -c "\dt"
```

### 3. Run Tests

```bash
# Run database tests
pytest tests/unit/test_database.py -v

# Should pass all 7 tests
```

### 4. Connect to Database

```bash
# Using psql
psql postgresql://repo_user:repo_password@localhost:5434/repo_to_cat

# Inside psql
\dt                    # List tables
\d generations         # Describe table
SELECT COUNT(*) FROM generations;
\q                     # Quit
```

---

## File Reference

### New Files Created

```
.
├── Dockerfile                           # Python app container
├── docker-compose.yml                   # PostgreSQL service
├── .env                                 # Local config (not committed)
├── .env.example                         # Updated with port 5434
├── alembic.ini                          # Alembic config
├── alembic/
│   ├── README                          # Alembic readme
│   ├── env.py                          # Auto-load models
│   ├── script.py.mako                  # Migration template
│   └── versions/
│       └── c31bba7cdef1_*.py           # Initial migration
├── app/
│   ├── core/
│   │   └── database.py                 # DB connection & sessions
│   └── models/
│       └── database.py                 # User & Generation models
├── scripts/
│   └── init_db.sql                     # DB init placeholder
└── tests/
    └── unit/
        └── test_database.py            # Database tests
```

### Modified Files

- `HANDOFF.md` - Marked Stage 1.2 complete
- `INIT_PROMPT.md` - Updated initialization prompt

---

## Verification Checklist

All items completed ✅:

- [x] Docker Compose builds successfully
- [x] PostgreSQL container starts and becomes healthy
- [x] Database accessible from host (port 5434)
- [x] Alembic migrations apply without errors
- [x] Tables created correctly (users, generations, alembic_version)
- [x] All 7 database tests passing
- [x] CRUD operations work (create, read, delete)
- [x] JSONB fields work correctly
- [x] UUID primary keys generated
- [x] Timestamps auto-populate
- [x] Code committed to feature branch
- [x] Pull Request created

---

## Common Tasks

### Start/Stop Database

```bash
# Start
docker compose up -d postgres

# Stop
docker compose stop postgres

# Stop and remove (keeps data)
docker compose down

# Stop and remove data (⚠️ destructive)
docker compose down -v
```

### Database Operations

```bash
# Connect
psql postgresql://repo_user:repo_password@localhost:5434/repo_to_cat

# Backup
docker compose exec postgres pg_dump -U repo_user repo_to_cat > backup.sql

# Restore
docker compose exec -T postgres psql -U repo_user repo_to_cat < backup.sql

# View logs
docker compose logs postgres

# Migration status
alembic current
```

### Development Workflow

```bash
# 1. Start database
docker compose up -d postgres

# 2. Apply migrations
alembic upgrade head

# 3. Run tests
pytest tests/unit/test_database.py -v

# 4. Make model changes in app/models/database.py

# 5. Generate migration
alembic revision --autogenerate -m "Description"

# 6. Apply migration
alembic upgrade head

# 7. Test changes
pytest tests/unit/ -v
```

---

## Troubleshooting

### Port Conflict

If port 5434 is in use:
1. Check: `ss -tulpn | grep :5434`
2. Change port in `docker-compose.yml` (e.g., 5435:5432)
3. Update `DATABASE_URL` in `.env`
4. Restart: `docker compose up -d postgres`

### Connection Refused

1. Check container: `docker compose ps`
2. Check logs: `docker compose logs postgres`
3. Verify DATABASE_URL in `.env`
4. Test: `psql postgresql://repo_user:repo_password@localhost:5434/repo_to_cat -c "SELECT 1"`

### Tests Failing

1. Ensure database is running: `docker compose ps`
2. Apply migrations: `alembic upgrade head`
3. Check `.env` has correct DATABASE_URL
4. Install dependencies: `pip install -r requirements.txt`

**See:** [docker-setup.md#troubleshooting](../docker-setup.md#troubleshooting) and [database-guide.md#troubleshooting](../database-guide.md#troubleshooting)

---

## Dependencies Added

**Database:**
- `sqlalchemy==2.0.35` - ORM
- `psycopg2-binary==2.9.9` - PostgreSQL adapter
- `alembic==1.13.3` - Migrations

**Already in requirements.txt** ✅

---

## What's Next

### Stage 1.3: FastAPI Skeleton

**Upcoming tasks:**
- Create `app/main.py` with FastAPI app
- Add CORS middleware
- Create health check endpoint
- Test FastAPI server startup
- Verify Swagger UI (`/docs`)

**See:** [HANDOFF.md](../../PROJECT_FLOW_DOCS/HANDOFF.md#13-fastapi-skeleton)

---

## Related Documentation

### Detailed Guides
- **[Docker Setup Guide](../docker-setup.md)** - Complete Docker & docker-compose reference
- **[Database Guide](../database-guide.md)** - PostgreSQL, Alembic, psql usage
- **[Testing Guide](../testing-guide.md)** - Running tests, coverage, best practices

### Project Documentation
- **[HANDOFF.md](../../PROJECT_FLOW_DOCS/HANDOFF.md)** - Development checklist
- **[DEVELOPMENT_RULES.md](../../PROJECT_FLOW_DOCS/DEVELOPMENT_RULES.md)** - TDD workflow, commit format
- **[PRD.md](../../PROJECT_FLOW_DOCS/PRD.md)** - Product requirements & API specs

---

## Key Learnings

### Docker
- Using port 5434 avoids conflicts with local PostgreSQL
- Health checks ensure container is ready before connections
- Volume persistence keeps data across container restarts

### Database
- UUID primary keys provide better scalability
- JSONB allows flexible schema for cat_attributes
- SQLAlchemy 2.0 requires `declarative_base()` from orm

### Testing
- Test database connection before running tests
- Clean up test data after assertions
- Use fixtures for database sessions

### Alembic
- Auto-generate saves time but review migrations
- Set DATABASE_URL programmatically in env.py
- Always test migrations on dev database first

---

## Metrics

**Files Changed:** 25
**Lines Added:** 2007
**Tests Added:** 7
**Test Coverage:** 93%
**Time to Complete:** ~2 hours

---

**Stage 1.2 Complete!** ✅
Next: [Stage 1.3 - FastAPI Skeleton](../../PROJECT_FLOW_DOCS/HANDOFF.md#13-fastapi-skeleton)
