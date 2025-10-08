# Docker Commands Reference

**Last Updated:** 2025-10-08
**Project:** Repo-to-Cat

---

## Overview

Quick reference for Docker commands used in Repo-to-Cat project. All development happens in Docker for production parity.

**Containers:**
- `postgres` - PostgreSQL 15 database (port 5434→5432)
- `app` - FastAPI application (port 8000)

---

## Quick Reference Table

| Task | Command |
|------|---------|
| Start all services | `docker compose up -d` |
| Stop all services | `docker compose down` |
| View logs (follow) | `docker compose logs -f` |
| View app logs | `docker compose logs app -f` |
| Check container status | `docker compose ps` |
| Restart app | `docker compose restart app` |
| Rebuild app | `docker compose up -d --build app` |
| Shell into app | `docker compose exec app bash` |
| Run tests | `docker compose exec app pytest -v` |
| Clean up everything | `docker compose down -v` |

---

## Starting & Stopping

### Start Services

```bash
# Start all services (detached mode)
docker compose up -d

# Start and rebuild if Dockerfile changed
docker compose up -d --build

# Start specific service
docker compose up -d postgres

# Start with logs (not detached)
docker compose up
```

### Stop Services

```bash
# Stop all services (keeps volumes)
docker compose down

# Stop and remove volumes (deletes data)
docker compose down -v

# Stop specific service
docker compose stop app

# Stop and remove specific container
docker compose rm -f app
```

### Restart Services

```bash
# Restart all services
docker compose restart

# Restart specific service
docker compose restart app

# Restart after code changes
docker compose restart app && docker compose logs app -f
```

---

## Viewing Logs

### Follow Logs (Real-Time)

```bash
# Follow all logs
docker compose logs -f

# Follow app logs only
docker compose logs app -f

# Follow postgres logs only
docker compose logs postgres -f

# Follow multiple services
docker compose logs app postgres -f

# Stop following: Ctrl+C
```

### View Past Logs

```bash
# Last 50 lines
docker compose logs app --tail=50

# Last 100 lines with timestamps
docker compose logs app --tail=100 -t

# All logs
docker compose logs app

# Logs since 5 minutes ago
docker compose logs app --since=5m

# Logs since specific time
docker compose logs app --since=2025-10-08T10:00:00
```

### Search Logs

```bash
# Find errors
docker compose logs app | grep -i error

# Find warnings
docker compose logs app | grep -i warning

# Find specific text
docker compose logs app | grep "database"

# Search with context (3 lines before/after)
docker compose logs app | grep -C 3 "health check"

# Case-insensitive search
docker compose logs app | grep -i "startup"
```

---

## Container Management

### Check Status

```bash
# List running containers
docker compose ps

# Detailed status (includes health)
docker ps

# Show all containers (including stopped)
docker ps -a

# Filter by project
docker ps --filter "name=repo-to-cat"
```

### Execute Commands in Container

```bash
# Open bash shell in app container
docker compose exec app bash

# Run single command
docker compose exec app pwd

# Run pytest
docker compose exec app pytest -v

# Check Python version
docker compose exec app python --version

# Check database from app container
docker compose exec app psql postgresql://repo_user:repo_password@postgres:5432/repo_to_cat -c "SELECT 1"
```

### Container Inspection

```bash
# Inspect container details
docker inspect repo-to-cat-app

# Get IP address
docker inspect repo-to-cat-app | grep IPAddress

# Check environment variables
docker compose exec app env

# Check disk usage
docker compose exec app df -h
```

---

## Building & Rebuilding

### Build Images

```bash
# Build all images
docker compose build

# Build specific service
docker compose build app

# Build without cache (clean build)
docker compose build --no-cache app

# Build and start
docker compose up -d --build
```

### When to Rebuild

Rebuild when you change:
- ✅ `Dockerfile`
- ✅ `requirements.txt`
- ❌ Python code in `app/` (just restart)
- ❌ Tests (just re-run)

```bash
# Changed requirements.txt
docker compose up -d --build app

# Changed app/main.py (no rebuild needed)
docker compose restart app
```

---

## Database Operations

### Connect to PostgreSQL

```bash
# From host (port 5434)
psql postgresql://repo_user:repo_password@localhost:5434/repo_to_cat

# From app container (port 5432, hostname: postgres)
docker compose exec app psql postgresql://repo_user:repo_password@postgres:5432/repo_to_cat

# Run SQL query
docker compose exec postgres psql -U repo_user -d repo_to_cat -c "SELECT * FROM users;"
```

### Database Management

```bash
# Apply migrations
docker compose exec app alembic upgrade head

# Check migration status
docker compose exec app alembic current

# Create new migration
docker compose exec app alembic revision --autogenerate -m "Description"

# View database logs
docker compose logs postgres --tail=100
```

---

## Testing in Docker

### Run Tests

```bash
# All tests
docker compose exec app pytest -v

# Specific file
docker compose exec app pytest tests/unit/test_main.py -v

# With coverage
docker compose exec app pytest --cov=app --cov-report=term

# Stop on first failure
docker compose exec app pytest -x

# Show print statements
docker compose exec app pytest -s
```

See [pytest-commands.md](pytest-commands.md) for more pytest options.

---

## Cleanup

### Remove Containers

```bash
# Stop and remove containers (keeps volumes)
docker compose down

# Remove containers and volumes (deletes data!)
docker compose down -v

# Remove containers, volumes, and images
docker compose down -v --rmi all
```

### Clean Up Docker System

```bash
# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Remove all unused resources
docker system prune

# Nuclear option (removes EVERYTHING)
docker system prune -a --volumes
```

### View Disk Usage

```bash
# Docker disk usage summary
docker system df

# Detailed breakdown
docker system df -v
```

---

## Troubleshooting

### Issue: "Cannot connect to Docker daemon"

**Error:** `Cannot connect to the Docker daemon at unix:///var/run/docker.sock`

**Fix:**
```bash
# Start Docker daemon (Linux)
sudo systemctl start docker

# Check Docker status
sudo systemctl status docker

# macOS/Windows: Start Docker Desktop app
```

### Issue: "Port already in use"

**Error:** `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Fix:**
```bash
# Find process using port
lsof -i :8000
# or
sudo netstat -tulpn | grep :8000

# Kill the process
kill -9 <PID>

# Or change port in docker-compose.yml:
ports:
  - "8001:8000"
```

### Issue: Container keeps restarting

**Error:** Container status shows "Restarting"

**Fix:**
```bash
# Check logs for error
docker compose logs app --tail=100

# Common causes:
# 1. Syntax error in code
# 2. Missing environment variables
# 3. Database not ready

# Stop and debug
docker compose stop app
docker compose logs app --tail=50
```

### Issue: "No space left on device"

**Error:** `no space left on device`

**Fix:**
```bash
# Check Docker disk usage
docker system df

# Clean up
docker system prune -a
docker volume prune

# Check host disk space
df -h
```

### Issue: Changes not reflected

**Symptom:** Code changes don't appear after editing

**Fix:**
```bash
# Restart container
docker compose restart app

# If still not working, check volumes are mounted:
docker compose config | grep volumes

# Should see: ./app:/app/app

# Rebuild if needed
docker compose up -d --build app
```

### Issue: Database connection refused

**Error:** `Connection refused: postgres:5432`

**Fix:**
```bash
# Check postgres is running
docker compose ps postgres

# Check postgres health
docker compose logs postgres --tail=20

# Wait for health check
sleep 5 && docker compose ps postgres

# Restart postgres
docker compose restart postgres

# Check from app container
docker compose exec app psql postgresql://repo_user:repo_password@postgres:5432/repo_to_cat -c "SELECT 1"
```

---

## Advanced Usage

### View Container Resource Usage

```bash
# Real-time stats
docker stats

# Stats for specific containers
docker stats repo-to-cat-app repo-to-cat-postgres

# One-time snapshot
docker stats --no-stream
```

### Copy Files To/From Container

```bash
# Copy file from host to container
docker cp local-file.txt repo-to-cat-app:/app/

# Copy file from container to host
docker cp repo-to-cat-app:/app/logs/app.log ./

# Copy directory
docker cp ./docs/ repo-to-cat-app:/app/
```

### Network Inspection

```bash
# List Docker networks
docker network ls

# Inspect project network
docker network inspect repo-to-cat_repo-to-cat-network

# Test connectivity between containers
docker compose exec app ping postgres
```

### Save/Load Images

```bash
# Save image to tar file
docker save repo-to-cat-app > app-image.tar

# Load image from tar file
docker load < app-image.tar

# Export container (not recommended)
docker export repo-to-cat-app > app-container.tar
```

---

## Environment-Specific Commands

### Development

```bash
# Start with live reload (if configured)
docker compose up -d

# Follow logs while developing
docker compose logs app -f

# Run tests on file change (requires watchdog)
docker compose exec app pytest-watch
```

### Production

```bash
# Build optimized images
docker compose -f docker-compose.prod.yml build

# Start production stack
docker compose -f docker-compose.prod.yml up -d

# Health check
docker compose -f docker-compose.prod.yml ps
```

---

## Docker Compose File Overrides

### Use Different Config

```bash
# Use custom compose file
docker compose -f docker-compose.custom.yml up -d

# Use multiple files (merge)
docker compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

### Environment Variables

```bash
# Load from specific .env file
docker compose --env-file .env.production up -d

# Override variable
DATABASE_URL="postgresql://..." docker compose up -d
```

---

## Best Practices

### DO ✅

- Always use `docker compose` (with space) not `docker-compose`
- Start database before running migrations
- Check logs when troubleshooting (`docker compose logs`)
- Use `docker compose ps` to verify health
- Clean up unused resources regularly (`docker system prune`)
- Use specific service names (`docker compose logs app`)

### DON'T ❌

- Don't use `docker-compose` (old v1 syntax)
- Don't skip health checks before running tests
- Don't forget to rebuild after changing Dockerfile
- Don't commit with containers stopped
- Don't use `docker system prune -a` in production
- Don't expose sensitive ports publicly

---

## Related Documentation

- **Testing Guide:** [testing-guide.md](testing-guide.md) - Running tests in Docker
- **Pytest Commands:** [pytest-commands.md](pytest-commands.md) - Pytest reference
- **Database Guide:** [database-guide.md](database-guide.md) - Database operations
- **Health Check:** [health-check.md](health-check.md) - System health verification
- **Docker Setup:** [docker-setup.md](docker-setup.md) - Initial setup guide

---

## Quick Workflow

**Typical development session:**

```bash
# 1. Start everything
docker compose up -d

# 2. Check status
docker compose ps

# 3. Watch logs
docker compose logs app -f &

# 4. Make code changes...

# 5. Restart app
docker compose restart app

# 6. Run tests
docker compose exec app pytest -v

# 7. Done - stop services
docker compose down
```

---

## Resources

- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Docker CLI Reference](https://docs.docker.com/engine/reference/commandline/cli/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
