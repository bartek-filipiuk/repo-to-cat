# Docker Setup Guide

**Last Updated:** 2025-10-08
**Stage:** 1.2 - Docker & Database Setup

---

## Overview

This project uses Docker to run PostgreSQL in an isolated container. The application itself can run either:
- **On the host** (for development with hot reload)
- **In a Docker container** (for production-like testing)

---

## Prerequisites

- Docker Engine 20.10+
- Docker Compose v2.0+

**Check your installation:**
```bash
docker --version
docker compose version
```

---

## Quick Start

### Start PostgreSQL Container

```bash
# Start PostgreSQL in detached mode
docker compose up -d postgres

# Check container status
docker compose ps

# View logs
docker compose logs postgres

# Follow logs (Ctrl+C to exit)
docker compose logs -f postgres
```

**Expected output:**
```
NAME                   STATUS                  PORTS
repo-to-cat-postgres   Up (healthy)           0.0.0.0:5434->5432/tcp
```

### Stop Containers

```bash
# Stop all containers
docker compose down

# Stop and remove volumes (⚠️ deletes all data)
docker compose down -v
```

---

## Docker Configuration

### `docker-compose.yml` Overview

**Services:**
- `postgres` - PostgreSQL 15 database
- `app` - Python FastAPI application (optional, for production)

**Key settings:**
- PostgreSQL port: `5434` (host) → `5432` (container)
  - Using 5434 to avoid conflict with local PostgreSQL on 5432
- Health check: Runs `pg_isready` every 10s
- Persistent volume: `postgres_data`

### Environment Variables

Docker Compose reads from your `.env` file:
```bash
DATABASE_URL=postgresql://repo_user:repo_password@localhost:5434/repo_to_cat
GITHUB_TOKEN=your_token_here
OPENROUTER_API_KEY=your_key_here
TOGETHER_API_KEY=your_key_here
```

**Note:** For the `app` service, the DATABASE_URL uses `postgres:5432` (internal Docker network).

---

## Common Commands

### Container Management

```bash
# Start all services
docker compose up -d

# Start specific service
docker compose up -d postgres

# Restart service
docker compose restart postgres

# Stop service
docker compose stop postgres

# View running containers
docker compose ps

# View all containers (including stopped)
docker compose ps -a
```

### Logs & Debugging

```bash
# View logs for all services
docker compose logs

# View logs for specific service
docker compose logs postgres

# Follow logs (real-time)
docker compose logs -f postgres

# Last 100 lines
docker compose logs --tail=100 postgres

# Execute command in running container
docker compose exec postgres psql -U repo_user -d repo_to_cat
```

### Building & Rebuilding

```bash
# Build services (run after Dockerfile changes)
docker compose build

# Build without cache
docker compose build --no-cache

# Build and start
docker compose up -d --build
```

### Data Management

```bash
# List volumes
docker volume ls | grep repo-to-cat

# Inspect volume
docker volume inspect repo-to-cat_postgres_data

# Remove volumes (⚠️ deletes data)
docker compose down -v

# Backup database (see database-guide.md)
docker compose exec postgres pg_dump -U repo_user repo_to_cat > backup.sql
```

---

## Troubleshooting

### Port Already in Use

**Error:**
```
Error: Bind for 0.0.0.0:5434 failed: port is already allocated
```

**Solution:**
1. Check what's using the port:
   ```bash
   ss -tulpn | grep :5434
   ```
2. Change the port in `docker-compose.yml`:
   ```yaml
   ports:
     - "5435:5432"  # Change 5434 to 5435
   ```
3. Update `DATABASE_URL` in `.env` to match

### Container Not Healthy

**Check health status:**
```bash
docker compose ps
```

**View health check logs:**
```bash
docker compose logs postgres | grep health
```

**Common causes:**
- Database still initializing (wait 10-20 seconds)
- Wrong credentials in healthcheck
- Port conflict

**Fix:**
```bash
# Restart container
docker compose restart postgres

# Or recreate container
docker compose down
docker compose up -d postgres
```

### Can't Connect from Host

**Error:** `Connection refused` or `timeout`

**Checklist:**
1. Container is running and healthy:
   ```bash
   docker compose ps
   ```
2. Port mapping is correct (5434:5432)
3. `DATABASE_URL` uses `localhost:5434` (not `postgres:5432`)
4. Firewall allows port 5434

**Test connection:**
```bash
psql postgresql://repo_user:repo_password@localhost:5434/repo_to_cat -c "SELECT 1"
```

### Container Keeps Restarting

**View logs:**
```bash
docker compose logs postgres
```

**Common causes:**
- Corrupted data volume
- Incompatible PostgreSQL version
- Memory/resource limits

**Fix:**
```bash
# Remove and recreate
docker compose down -v
docker compose up -d postgres
```

### Out of Disk Space

**Check volume size:**
```bash
docker system df
```

**Clean up:**
```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune -a

# Remove unused volumes (⚠️ careful)
docker volume prune
```

---

## Running the Application in Docker

**Start both PostgreSQL and app:**
```bash
docker compose up -d
```

**The app service:**
- Runs `uvicorn` with hot reload
- Mounts `./app` for live code changes
- Uses internal network (`postgres:5432`)
- Exposed on port `8000`

**Test the app:**
```bash
# Check if running
curl http://localhost:8000/health

# View app logs
docker compose logs -f app
```

---

## Docker Compose Reference

### Full Command List

```bash
# Lifecycle
docker compose up -d              # Start in background
docker compose down               # Stop and remove
docker compose restart            # Restart services
docker compose stop               # Stop without removing
docker compose start              # Start stopped services

# Monitoring
docker compose ps                 # List containers
docker compose logs               # View logs
docker compose top                # View processes

# Execution
docker compose exec SERVICE CMD   # Run command in container
docker compose run SERVICE CMD    # Run one-off command

# Building
docker compose build              # Build services
docker compose pull               # Pull latest images

# Cleanup
docker compose down -v            # Remove volumes
docker compose rm                 # Remove stopped containers
```

---

## Best Practices

1. **Always use `-d` flag** for background execution
2. **Check logs** after starting containers
3. **Wait for health checks** before connecting
4. **Back up data** before running `down -v`
5. **Use `.env` file** for sensitive credentials
6. **Don't commit `.env`** (use `.env.example`)
7. **Monitor disk space** (logs and volumes can grow)

---

## Next Steps

- **Database access:** See [database-guide.md](database-guide.md)
- **Running tests:** See [testing-guide.md](testing-guide.md)
- **Stage summary:** See [stages/stage-1.2-summary.md](stages/stage-1.2-summary.md)

---

## Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- Project: [docker-compose.yml](../docker-compose.yml)
