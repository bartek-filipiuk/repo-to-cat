# Database Guide

**Last Updated:** 2025-10-08
**Stage:** 1.2 - Docker & Database Setup

---

## Overview

This project uses **PostgreSQL 15** for data persistence, with **Alembic** for database migrations and **SQLAlchemy** for ORM.

**Database Schema:**
- `users` - User accounts (post-MVP)
- `generations` - Cat image generation history
- `alembic_version` - Migration tracking

---

## Quick Start

### Connect to Database

**Using psql (command line):**
```bash
psql postgresql://repo_user:repo_password@localhost:5434/repo_to_cat
```

**Using GUI tools:**
- **Host:** `localhost`
- **Port:** `5434`
- **Database:** `repo_to_cat`
- **Username:** `repo_user`
- **Password:** `repo_password`

**Connection string:**
```
postgresql://repo_user:repo_password@localhost:5434/repo_to_cat
```

---

## Database Schema

### `users` Table

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) UNIQUE,
    api_token VARCHAR(255) UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

**Purpose:** User authentication and tracking (post-MVP feature)

### `generations` Table

```sql
CREATE TABLE generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    github_url TEXT NOT NULL,
    repo_owner VARCHAR(255),
    repo_name VARCHAR(255),
    primary_language VARCHAR(100),
    repo_size_kb INTEGER,
    code_quality_score NUMERIC(3,1),
    cat_attributes JSONB,
    analysis_data JSONB,
    image_path TEXT,
    image_prompt TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

**Purpose:** Store repository analysis results and generated cat images

**Key fields:**
- `cat_attributes` - JSONB: `{"size": "chonky", "color": "orange", ...}`
- `analysis_data` - JSONB: Full analysis metrics from LLM
- `code_quality_score` - Decimal (0.0-10.0)

---

## psql Commands

### Connect to Database

```bash
# Connect to database
psql postgresql://repo_user:repo_password@localhost:5434/repo_to_cat

# Or via Docker
docker compose exec postgres psql -U repo_user -d repo_to_cat
```

### Common psql Commands

```sql
-- List all tables
\dt

-- Describe table schema
\d users
\d generations

-- List all databases
\l

-- List all users
\du

-- View current database
SELECT current_database();

-- Quit psql
\q
```

### Query Examples

```sql
-- Count generations
SELECT COUNT(*) FROM generations;

-- View recent generations
SELECT github_url, code_quality_score, created_at
FROM generations
ORDER BY created_at DESC
LIMIT 10;

-- View cat attributes
SELECT
    github_url,
    cat_attributes->>'size' as cat_size,
    cat_attributes->>'color' as cat_color
FROM generations
WHERE cat_attributes IS NOT NULL;

-- Check database size
SELECT pg_size_pretty(pg_database_size('repo_to_cat'));

-- Check table sizes
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(tablename::regclass))
FROM pg_tables
WHERE schemaname = 'public';
```

---

## Alembic Migrations

Alembic manages database schema changes through migration scripts.

### Initial Setup (Already Done)

```bash
# Initialize Alembic (already done in Stage 1.2)
alembic init alembic

# Configure alembic/env.py to use our models
# (already configured)
```

### Check Migration Status

```bash
# View current migration version
alembic current

# View migration history
alembic history --verbose

# Show pending migrations
alembic show
```

### Apply Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade c31bba7cdef1

# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade c31bba7cdef1

# Rollback all migrations
alembic downgrade base
```

### Create New Migration

**Auto-generate from model changes:**
```bash
# 1. Modify models in app/models/database.py

# 2. Auto-generate migration
alembic revision --autogenerate -m "Add new column to users table"

# 3. Review generated migration in alembic/versions/

# 4. Apply migration
alembic upgrade head
```

**Create empty migration:**
```bash
# Create blank migration file
alembic revision -m "Custom data migration"

# Edit the generated file manually
# Then apply
alembic upgrade head
```

### Migration Best Practices

1. **Always review** auto-generated migrations
2. **Test migrations** on development DB first
3. **Include rollback** logic in `downgrade()`
4. **Commit migrations** with code changes
5. **Never edit** applied migrations
6. **Name descriptively:** `add_user_email_column` not `update_1`

---

## Database Operations from Python

### Get Database Session

```python
from app.core.database import SessionLocal, get_db

# Create session manually
session = SessionLocal()
try:
    # Your operations
    pass
finally:
    session.close()

# Or use dependency injection (in FastAPI)
def my_endpoint(db: Session = Depends(get_db)):
    # db session automatically managed
    pass
```

### CRUD Examples

```python
from app.models.database import User, Generation
from app.core.database import SessionLocal

session = SessionLocal()

# CREATE
new_gen = Generation(
    github_url="https://github.com/user/repo",
    repo_owner="user",
    repo_name="repo",
    primary_language="Python",
    code_quality_score=8.5,
    cat_attributes={"size": "chonky", "color": "orange"}
)
session.add(new_gen)
session.commit()

# READ
generations = session.query(Generation).all()
generation = session.query(Generation).filter_by(repo_owner="user").first()

# UPDATE
generation.code_quality_score = 9.0
session.commit()

# DELETE
session.delete(generation)
session.commit()

session.close()
```

---

## Backup & Restore

### Backup Database

```bash
# Full database dump
docker compose exec postgres pg_dump -U repo_user repo_to_cat > backup.sql

# Specific table
docker compose exec postgres pg_dump -U repo_user -t generations repo_to_cat > generations_backup.sql

# Compressed backup
docker compose exec postgres pg_dump -U repo_user repo_to_cat | gzip > backup.sql.gz

# With timestamp
docker compose exec postgres pg_dump -U repo_user repo_to_cat > "backup_$(date +%Y%m%d_%H%M%S).sql"
```

### Restore Database

```bash
# Restore from backup
docker compose exec -T postgres psql -U repo_user repo_to_cat < backup.sql

# Restore from compressed
gunzip -c backup.sql.gz | docker compose exec -T postgres psql -U repo_user repo_to_cat

# Drop and recreate database first (⚠️ destructive)
docker compose exec postgres psql -U repo_user -d postgres -c "DROP DATABASE repo_to_cat;"
docker compose exec postgres psql -U repo_user -d postgres -c "CREATE DATABASE repo_to_cat;"
docker compose exec -T postgres psql -U repo_user repo_to_cat < backup.sql
```

---

## Troubleshooting

### Can't Connect to Database

**Error:** `Connection refused` or `could not connect to server`

**Checklist:**
1. Container is running:
   ```bash
   docker compose ps
   ```
2. Container is healthy:
   ```bash
   docker compose logs postgres | tail -20
   ```
3. Port is correct (5434 not 5432):
   ```bash
   psql postgresql://repo_user:repo_password@localhost:5434/repo_to_cat
   ```
4. Credentials are correct (check `.env`)

**Test connection:**
```bash
# Quick test
psql postgresql://repo_user:repo_password@localhost:5434/repo_to_cat -c "SELECT 1"
```

### Alembic Can't Find Migrations

**Error:** `Can't locate revision identified by 'xyz'`

**Fix:**
```bash
# Check Alembic history
alembic history

# Check database version
alembic current

# Stamp database to specific version
alembic stamp head
```

### Migration Fails Halfway

**Error:** Migration partially applied

**Fix:**
```bash
# 1. Check what was applied
psql postgresql://repo_user:repo_password@localhost:5434/repo_to_cat

# 2. Check alembic_version table
SELECT * FROM alembic_version;

# 3. Manually fix data if needed

# 4. Stamp to correct version
alembic stamp <revision_id>
```

### JSONB Query Not Working

**Error:** `operator does not exist: jsonb -> text`

**Fix:** Use correct operator:
```sql
-- Wrong
SELECT cat_attributes->'size' FROM generations;

-- Correct for text
SELECT cat_attributes->>'size' FROM generations;

-- Correct for JSONB
SELECT cat_attributes->'nested_object' FROM generations;
```

### Database Locked

**Error:** `database is being accessed by other users`

**Fix:**
```bash
# Find active connections
psql postgresql://repo_user:repo_password@localhost:5434/postgres -c "
SELECT pid, usename, application_name, state
FROM pg_stat_activity
WHERE datname = 'repo_to_cat';
"

# Kill connections (⚠️ careful)
psql postgresql://repo_user:repo_password@localhost:5434/postgres -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'repo_to_cat' AND pid <> pg_backend_pid();
"
```

---

## Performance Tips

### Indexes

Current indexes (from migration):
- `generations_pkey` on `generations.id`
- `users_pkey` on `users.id`
- `users_username_key` on `users.username`
- `users_api_token_key` on `users.api_token`

**Add index if querying often by:**
```sql
-- Example: Index on github_url for lookups
CREATE INDEX idx_generations_github_url ON generations(github_url);

-- Or via Alembic migration:
op.create_index('idx_generations_github_url', 'generations', ['github_url'])
```

### Query Optimization

```sql
-- Use EXPLAIN to see query plan
EXPLAIN ANALYZE SELECT * FROM generations WHERE repo_owner = 'user';

-- Use indexes
CREATE INDEX idx_repo_owner ON generations(repo_owner);

-- JSONB index for cat attributes
CREATE INDEX idx_cat_attributes ON generations USING GIN (cat_attributes);
```

---

## GUI Tools

Recommended tools for database management:

### pgAdmin 4
- **Website:** https://www.pgadmin.org/
- **Connection:** localhost:5434

### DBeaver
- **Website:** https://dbeaver.io/
- **Free & open source**
- **Multi-platform**

### TablePlus
- **Website:** https://tableplus.com/
- **macOS/Windows/Linux**
- **Clean UI**

### DataGrip (JetBrains)
- **Website:** https://www.jetbrains.com/datagrip/
- **Paid**
- **Advanced features**

---

## Next Steps

- **Docker management:** See [docker-setup.md](docker-setup.md)
- **Running tests:** See [testing-guide.md](testing-guide.md)
- **Stage summary:** See [stages/stage-1.2-summary.md](stages/stage-1.2-summary.md)

---

## Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/15/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- Project files:
  - [app/models/database.py](../app/models/database.py) - ORM models
  - [app/core/database.py](../app/core/database.py) - DB config
  - [alembic/env.py](../alembic/env.py) - Alembic config
