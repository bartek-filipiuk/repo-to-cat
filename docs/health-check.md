# Health Check Guide

**Last Updated:** 2025-10-08
**Project:** Repo-to-Cat

---

## Overview

This guide helps you verify that the Repo-to-Cat application is healthy and running correctly. Use this checklist before starting development, after deployment, or when troubleshooting issues.

**Quick health check:** Run `./scripts/health-check.sh`

---

## Quick Automated Check

### Using the Script

```bash
# Full health check (includes tests)
./scripts/health-check.sh

# Quick check (skip tests, ~5 seconds)
./scripts/health-check.sh --quick

# Verbose output (show all details)
./scripts/health-check.sh --verbose
```

**What it checks:**
- ✅ Docker daemon running
- ✅ Containers status (postgres + app)
- ✅ Database connectivity
- ✅ API endpoints (/, /health, /docs)
- ✅ Database health from /health endpoint
- ✅ All tests passing
- ✅ Coverage ≥80%

**Output:**
- Checklist-style with ✅/❌ for each check
- Suggested fixes for failures
- Saves log to `health-check-TIMESTAMP.log`
- Exit code: 0 (healthy) or 1 (issues)

---

## Manual Health Check Checklist

### 1. Infrastructure Checks

#### ✅ Docker Daemon Running

```bash
docker ps
```

**Expected:** List of containers (no error)

**If fails:**
- Linux: `sudo systemctl start docker`
- macOS/Windows: Start Docker Desktop app

---

#### ✅ PostgreSQL Container: Running & Healthy

```bash
docker compose ps postgres
```

**Expected:**
```
NAME                   STATUS
repo-to-cat-postgres   Up X minutes (healthy)
```

**If fails:**
- Not running: `docker compose up -d postgres`
- Unhealthy: `docker compose logs postgres --tail=20`
- Still failing: `docker compose restart postgres`

---

#### ✅ App Container: Running

```bash
docker compose ps app
```

**Expected:**
```
NAME              STATUS
repo-to-cat-app   Up X minutes
```

**If fails:**
- Not running: `docker compose up -d app`
- Restarting: `docker compose logs app --tail=50`
- Build errors: `docker compose up -d --build app`

---

### 2. Database Checks

#### ✅ PostgreSQL Connection Works

```bash
docker compose exec app psql postgresql://repo_user:repo_password@postgres:5432/repo_to_cat -c "SELECT 1"
```

**Expected:**
```
 ?column?
----------
        1
(1 row)
```

**If fails:**
- Connection refused: Check postgres is healthy (step above)
- Authentication failed: Check `.env` for correct credentials
- Database doesn't exist: `docker compose exec app alembic upgrade head`

---

### 3. API Endpoint Checks

#### ✅ Root Endpoint (/)

```bash
curl -s http://localhost:8000/ | jq
```

**Expected:**
```json
{
  "message": "Welcome to Repo-to-Cat API",
  "description": "GitHub Repository Quality Visualizer",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

**If fails:**
- Connection refused: Check app container is running
- 404: App not started correctly, check logs
- Empty response: Check port mapping in docker-compose.yml

---

#### ✅ Health Endpoint (/health)

```bash
curl -s http://localhost:8000/health | jq
```

**Expected:**
```json
{
  "status": "healthy",
  "database": {
    "status": "up"
  },
  "timestamp": "2025-10-08T17:17:40.568562+00:00"
}
```

**If fails:**
- `"status": "unhealthy"`: Check database (see next check)
- Connection refused: App not running
- 500 error: Check app logs for Python errors

---

#### ✅ Database Status from /health

```bash
curl -s http://localhost:8000/health | jq '.database.status'
```

**Expected:**
```
"up"
```

**If fails:**
- `"down"`: Check postgres connection (step 2.1)
- Error in response: Check app logs for SQLAlchemy errors

---

#### ✅ API Documentation (/docs)

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs
```

**Expected:** `200`

**If fails:**
- 404: FastAPI docs disabled (check app/main.py)
- 500: App startup error, check logs

---

### 4. Test Checks

#### ✅ All Tests Pass

```bash
docker compose exec app pytest -v
```

**Expected:**
```
======================== 18 passed in 1.5s ========================
```

**If fails:**
- Check which tests failed
- Run specific test: `docker compose exec app pytest path/to/test.py::test_name -vv`
- Check test logs for error details

---

#### ✅ Coverage ≥80%

```bash
docker compose exec app pytest --cov=app --cov-report=term | grep TOTAL
```

**Expected:**
```
TOTAL    75    5    93%
```

**Coverage should be ≥80%**

**If fails:**
- Review uncovered code
- Add tests for critical paths
- See [testing-guide.md](testing-guide.md)

---

## Complete Health Check (Copy-Paste)

```bash
#!/bin/bash
# Quick manual health check

echo "🏥 Repo-to-Cat Health Check"
echo "================================"

echo ""
echo "Infrastructure:"

echo -n "  Docker daemon: "
docker ps > /dev/null 2>&1 && echo "✅" || echo "❌"

echo -n "  Postgres container: "
docker compose ps postgres 2>&1 | grep -q "healthy" && echo "✅ healthy" || echo "❌"

echo -n "  App container: "
docker compose ps app 2>&1 | grep -q "Up" && echo "✅ running" || echo "❌"

echo ""
echo "Database:"

echo -n "  Postgres connection: "
docker compose exec app psql postgresql://repo_user:repo_password@postgres:5432/repo_to_cat -c "SELECT 1" > /dev/null 2>&1 && echo "✅" || echo "❌"

echo ""
echo "API Endpoints:"

echo -n "  GET /: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ | grep -q "200" && echo "✅ 200" || echo "❌"

echo -n "  GET /health: "
curl -s http://localhost:8000/health | jq -e '.status == "healthy"' > /dev/null 2>&1 && echo "✅ healthy" || echo "❌"

echo -n "  GET /docs: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs | grep -q "200" && echo "✅ 200" || echo "❌"

echo ""
echo "Tests:"

echo -n "  Running pytest... "
docker compose exec app pytest -q > /dev/null 2>&1 && echo "✅ all passed" || echo "❌ failures"

echo ""
echo "================================"
```

---

## When to Run Health Checks

### 1. Before Starting Development

**Scenario:** Starting work for the day

**Check:**
```bash
./scripts/health-check.sh --quick
```

**Why:** Ensure environment is ready before making changes

---

### 2. After Making Changes

**Scenario:** Just coded a new feature

**Check:**
```bash
./scripts/health-check.sh
```

**Why:** Verify nothing broke, tests pass, coverage maintained

---

### 3. After Deployment

**Scenario:** Deployed to staging/production

**Check:**
```bash
./scripts/health-check.sh --quick
# Then manually verify critical paths
```

**Why:** Ensure deployment successful, services communicating

---

### 4. When Troubleshooting

**Scenario:** Something's not working

**Check:**
```bash
./scripts/health-check.sh --verbose
```

**Why:** Identify what's broken systematically

---

### 5. After Docker Restart

**Scenario:** Restarted computer, Docker Desktop, or ran `docker compose down`

**Check:**
```bash
# Start services
docker compose up -d

# Wait a moment for startup
sleep 5

# Check health
./scripts/health-check.sh --quick
```

**Why:** Ensure containers started correctly

---

## Troubleshooting Failed Checks

### Docker Daemon Not Running

**Symptoms:**
- ❌ Docker daemon check fails
- Error: "Cannot connect to Docker daemon"

**Fix:**
```bash
# Linux
sudo systemctl start docker
sudo systemctl enable docker

# macOS/Windows
# Start Docker Desktop app

# Verify
docker ps
```

---

### Containers Not Running

**Symptoms:**
- ❌ Postgres or app container checks fail
- Status shows "Exited" or container missing

**Fix:**
```bash
# Start all services
docker compose up -d

# Check status
docker compose ps

# If still failing, check logs
docker compose logs app --tail=50
docker compose logs postgres --tail=50

# Rebuild if needed
docker compose up -d --build
```

---

### Database Connection Failed

**Symptoms:**
- ❌ Postgres connection check fails
- Health endpoint shows database "down"

**Fix:**
```bash
# Check postgres logs
docker compose logs postgres --tail=20

# Wait for postgres to be ready
sleep 5 && docker compose ps postgres

# Test connection
docker compose exec app psql postgresql://repo_user:repo_password@postgres:5432/repo_to_cat -c "SELECT 1"

# Apply migrations if needed
docker compose exec app alembic upgrade head

# Restart app
docker compose restart app
```

---

### API Endpoints Failing

**Symptoms:**
- ❌ API endpoint checks fail (/, /health, /docs)
- Connection refused or 500 errors

**Fix:**
```bash
# Check app logs
docker compose logs app --tail=50

# Look for Python errors
docker compose logs app | grep -i error

# Restart app
docker compose restart app

# If code changes, rebuild
docker compose up -d --build app

# Check environment variables
docker compose exec app env | grep -E "DATABASE_URL|API_PORT"
```

---

### Tests Failing

**Symptoms:**
- ❌ Test check fails
- Some tests showing failures

**Fix:**
```bash
# Run tests with verbose output
docker compose exec app pytest -vv

# Run only failed tests
docker compose exec app pytest --lf -vv

# Check specific test
docker compose exec app pytest tests/unit/test_main.py::test_name -vv

# Ensure database is ready
docker compose ps postgres
docker compose exec app alembic current

# Check test logs
docker compose logs app
```

---

### Low Coverage

**Symptoms:**
- ❌ Coverage check fails
- Coverage below 80%

**Fix:**
```bash
# Generate detailed coverage report
docker compose exec app pytest --cov=app --cov-report=term-missing

# Identify uncovered lines
docker compose exec app pytest --cov=app --cov-report=html

# Copy report to host
docker cp repo-to-cat-app:/app/htmlcov ./htmlcov

# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# Add tests for uncovered code
```

---

## Health Check Logs

The automated script saves logs to `health-check-TIMESTAMP.log`.

### View Recent Logs

```bash
# List health check logs
ls -lht health-check-*.log | head -5

# View latest log
cat health-check-*.log | tail -1 | xargs cat

# Search for failures
grep "❌" health-check-*.log
```

### Clean Up Old Logs

```bash
# Remove logs older than 7 days
find . -name "health-check-*.log" -mtime +7 -delete

# Remove all health check logs
rm health-check-*.log
```

---

## Integration with CI/CD

### GitHub Actions Example

```yaml
# .github/workflows/health-check.yml
name: Health Check

on: [push, pull_request]

jobs:
  health-check:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Start services
        run: docker compose up -d

      - name: Wait for services
        run: sleep 10

      - name: Run health check
        run: |
          chmod +x scripts/health-check.sh
          ./scripts/health-check.sh

      - name: Upload health check log
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: health-check-log
          path: health-check-*.log
```

---

## Related Documentation

- **Docker Commands:** [docker-commands.md](docker-commands.md) - Docker reference
- **Pytest Commands:** [pytest-commands.md](pytest-commands.md) - Testing reference
- **Testing Guide:** [testing-guide.md](testing-guide.md) - Complete testing guide
- **FastAPI Guide:** [fastapi-guide.md](fastapi-guide.md) - API troubleshooting

---

## Resources

- **Health Check Script:** `scripts/health-check.sh`
- **Docker Logs:** `docker compose logs app -f`
- **Test Logs:** `docker compose exec app pytest -v`
