# LL-DEV-001: Docker-First Development (Production Parity)

**Category:** Development Workflow
**Date:** 2025-10-08
**Severity:** Medium
**Stage:** 1.2 & 1.3

---

## What Happened

During Stage 1.2 (Docker & Database Setup), tests were run on the **host machine** instead of inside Docker containers. This continued into Stage 1.3 (FastAPI Skeleton) planning.

**Specific Actions:**
- Installed Python dependencies on host (`pip install -r requirements.txt`)
- Ran `pytest tests/unit/test_database.py -v` on host
- Planned to run `uvicorn app.main:app --reload` on host

**Why This Is Wrong:**
- Violates production parity principle
- Docker configuration exists but wasn't used for development
- Tests passing on host don't guarantee Docker setup works
- Creates "works on my machine" scenarios
- Inconsistent with production deployment strategy

---

## The Mistake

**Root Cause:** Assumed host-based development was acceptable despite having Docker setup ready.

**Impact:**
- Stage 1.2 tests need re-validation inside Docker
- Potential Docker configuration issues not caught early
- Development environment differs from production

---

## The Fix

**Immediate Actions:**
1. Re-run all Stage 1.2 tests inside Docker container
2. Run Stage 1.3 app using `docker compose up` (not host uvicorn)
3. Document proper Docker-based development workflow

**Correct Workflow:**
```bash
# Build and start all services
docker compose up -d --build

# Run tests inside Docker
docker compose exec app pytest tests/ -v

# Check logs
docker compose logs app -f

# Access app
curl http://localhost:8000/health

# Stop services
docker compose down
```

---

## Prevention Strategy

### 1. Always Use Docker for Development

**Rule:** If `docker-compose.yml` exists, ALL development MUST happen in Docker.

**Commands to use:**
```bash
# Start services
docker compose up -d --build

# Run tests
docker compose exec app pytest tests/ -v --cov=app

# View logs
docker compose logs app -f

# Shell access
docker compose exec app bash

# Stop services
docker compose down
```

### 2. Update Documentation

**In CLAUDE.md:**
```markdown
## Development Environment

**IMPORTANT:** This project uses Docker for development (production parity).

### Never Run on Host:
- ❌ `uvicorn app.main:app --reload`
- ❌ `pytest tests/`
- ❌ `python app/main.py`

### Always Use Docker:
- ✅ `docker compose up -d --build`
- ✅ `docker compose exec app pytest tests/ -v`
- ✅ `docker compose logs app -f`
```

### 3. Verification Checklist

Before marking any stage complete:
- [ ] App runs in Docker: `docker compose up -d`
- [ ] Tests run in Docker: `docker compose exec app pytest`
- [ ] All containers healthy: `docker compose ps`
- [ ] No host-based commands used

---

## Related Issues

- None yet (caught early in Stage 1.3)

---

## References

- **12-Factor App:** Dev/prod parity - https://12factor.net/dev-prod-parity
- **Docker Compose Best Practices**
- **Stage 1.2:** Database setup (needs re-validation)

---

## Lesson Learned

**Golden Rule:** If production uses Docker, development MUST use Docker.

**Benefits:**
- Catches Docker-specific issues early
- Consistent environment for all developers
- No "works on my machine" problems
- Easier CI/CD integration
- True production parity

**Apply to:** All future stages, update existing documentation.
