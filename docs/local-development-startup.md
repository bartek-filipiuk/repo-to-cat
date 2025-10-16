# Local Development Startup Guide

Quick reference for starting the complete local development environment.

## Prerequisites

- Python 3.11+ installed
- Node.js 18+ and npm installed
- Docker Compose v2 installed
- PostgreSQL port 5434 available
- Backend port 8000 available
- Frontend port 4321 available

## Environment Setup (First Time Only)

### 1. Install Backend Dependencies

```bash
pip3 install -r requirements.txt
```

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your API keys:
# - GITHUB_TOKEN
# - OPENROUTER_API_KEY
# - TOGETHER_API_KEY
```

### 4. Run Database Migrations

```bash
alembic upgrade head
```

---

## Starting the Application

### Step 1: Start PostgreSQL Database

```bash
docker compose up -d postgres
```

**Verify database is running:**
```bash
docker compose ps
# Should show postgres container as "Up"
```

### Step 2: Start Backend Server (FastAPI)

```bash
uvicorn app.main:app --reload --port 8000
```

**Or run in background:**
```bash
uvicorn app.main:app --reload --port 8000 &
```

**Verify backend is running:**
```bash
curl -s http://localhost:8000/health | jq '.'
# Should show "status": "healthy"
```

### Step 3: Start Frontend Server (Astro)

**In a new terminal (or background):**
```bash
cd frontend
npm run dev
```

**Or run in background:**
```bash
cd frontend && npm run dev &
```

**Verify frontend is running:**
```bash
curl -s http://localhost:4321 | head -5
# Should return HTML
```

---

## Access Points

Once everything is running:

- **Web Application**: http://localhost:4321
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health
- **Database**: localhost:5434 (PostgreSQL)

---

## Full Startup Sequence (Copy-Paste)

```bash
# 1. Start database
docker compose up -d postgres

# 2. Wait for database to be ready
sleep 3

# 3. Start backend in background
uvicorn app.main:app --reload --port 8000 &

# 4. Wait for backend to start
sleep 3

# 5. Start frontend in background
cd frontend && npm run dev &

# 6. Wait for frontend to start
sleep 3

# 7. Check health
curl -s http://localhost:8000/health | jq '.status'

# 8. Open browser
echo "✅ Application ready at http://localhost:4321"
```

---

## Stopping the Application

### Stop Backend & Frontend

```bash
# Find and kill uvicorn process
pkill -f "uvicorn app.main:app"

# Find and kill npm/node process
pkill -f "npm run dev"
# OR
pkill -f "node.*astro"
```

### Stop Database

```bash
docker compose down
```

### Stop Everything

```bash
# Kill all servers
pkill -f "uvicorn app.main:app"
pkill -f "npm run dev"

# Stop database
docker compose down

# Verify nothing is running
docker compose ps
lsof -i :8000
lsof -i :4321
lsof -i :5434
```

---

## Troubleshooting

### Backend won't start

**Error: "Port 8000 already in use"**
```bash
# Find and kill process
lsof -i :8000
kill -9 <PID>
```

**Error: "Connection refused" (database)**
```bash
# Check if database is running
docker compose ps

# If not running, start it
docker compose up -d postgres

# Check logs
docker compose logs postgres
```

### Frontend won't start

**Error: "Port 4321 already in use"**
```bash
# Find and kill process
lsof -i :4321
kill -9 <PID>
```

**Error: "Module not found"**
```bash
cd frontend
npm install
```

### Database connection issues

**Check database is accepting connections:**
```bash
psql postgresql://repo_user:repo_password@localhost:5434/repo_to_cat -c "SELECT 1"
```

**Check database logs:**
```bash
docker compose logs postgres
```

---

## Quick Health Check

```bash
# Check all services
curl -s http://localhost:8000/health | jq '.'

# Expected output:
# {
#   "status": "healthy",
#   "services": {
#     "github_api": { "status": "up" },
#     "openrouter": { "status": "up" },
#     "together_ai": { "status": "up" },
#     "database": { "status": "up" }
#   }
# }
```

---

## Development Workflow

**Typical daily workflow:**

1. Start database: `docker compose up -d postgres`
2. Start backend: `uvicorn app.main:app --reload --port 8000`
3. Start frontend: `cd frontend && npm run dev`
4. Access UI: http://localhost:4321
5. Make changes (both servers auto-reload)
6. Run tests: `pytest`
7. Stop servers: Ctrl+C (or pkill commands)
8. Stop database: `docker compose down`

---

## Notes

- **Backend auto-reload**: Uvicorn with `--reload` watches Python files and restarts on changes
- **Frontend auto-reload**: Astro dev server watches files and hot-reloads on changes
- **Database persists**: Data stored in Docker volume, survives restarts
- **Logs**: Check terminal output for errors
- **Port conflicts**: Ensure ports 5434, 8000, 4321 are free before starting

---

**Last Updated**: 2025-10-15