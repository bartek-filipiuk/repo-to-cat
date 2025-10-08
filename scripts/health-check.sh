#!/bin/bash

# Repo-to-Cat Health Check Script
# Verifies Docker containers, database, API endpoints, and tests
# Usage: ./scripts/health-check.sh [--quick] [--verbose]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
QUICK_MODE=false
VERBOSE=false
ISSUES_FOUND=false
LOG_FILE="health-check-$(date +%Y%m%d-%H%M%S).log"

# Parse arguments
for arg in "$@"; do
    case $arg in
        --quick)
            QUICK_MODE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --quick     Skip tests (fast infrastructure check only)"
            echo "  --verbose   Show detailed output"
            echo "  --help, -h  Show this help message"
            echo ""
            echo "Exit codes:"
            echo "  0 - All checks passed"
            echo "  1 - One or more checks failed"
            exit 0
            ;;
        *)
            echo "Unknown option: $arg"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Logging functions
log() {
    echo "$@" | tee -a "$LOG_FILE"
}

log_no_newline() {
    echo -n "$@" | tee -a "$LOG_FILE"
}

log_verbose() {
    if [ "$VERBOSE" = true ]; then
        echo "$@" | tee -a "$LOG_FILE"
    else
        echo "$@" >> "$LOG_FILE"
    fi
}

check_pass() {
    log " ${GREEN}✅${NC}"
}

check_fail() {
    log " ${RED}❌${NC}"
    ISSUES_FOUND=true
}

# Start health check
log ""
log "🏥 ${BLUE}Repo-to-Cat Health Check${NC}"
log "================================"
log ""

# 1. Infrastructure Checks
log "${YELLOW}Infrastructure:${NC}"

# Check Docker daemon
log_no_newline "  Docker daemon:"
if docker ps > /dev/null 2>&1; then
    check_pass
    log_verbose "    Docker daemon is accessible"
else
    check_fail
    log_verbose "    ${RED}ERROR:${NC} Cannot connect to Docker daemon"
    log_verbose "    Fix: Start Docker (systemctl start docker or Docker Desktop)"
fi

# Check Postgres container
log_no_newline "  Postgres container:"
if docker compose ps postgres 2>&1 | grep -q "healthy"; then
    check_pass
    log_verbose "    Postgres is running and healthy"
elif docker compose ps postgres 2>&1 | grep -q "Up"; then
    log " ${YELLOW}⚠${NC}  (running, waiting for healthy)"
    log_verbose "    Postgres is starting up, health check not yet passing"
else
    check_fail
    log_verbose "    ${RED}ERROR:${NC} Postgres container not running"
    log_verbose "    Fix: docker compose up -d postgres"
fi

# Check App container
log_no_newline "  App container:"
if docker compose ps app 2>&1 | grep -q "Up"; then
    check_pass
    log_verbose "    App container is running"
else
    check_fail
    log_verbose "    ${RED}ERROR:${NC} App container not running"
    log_verbose "    Fix: docker compose up -d app"
fi

log ""

# 2. Database Checks
log "${YELLOW}Database:${NC}"

# Check Postgres connection
log_no_newline "  Postgres connection:"
if docker compose exec -T app psql postgresql://repo_user:repo_password@postgres:5432/repo_to_cat -c "SELECT 1" > /dev/null 2>&1; then
    check_pass
    log_verbose "    Can connect to PostgreSQL"
else
    check_fail
    log_verbose "    ${RED}ERROR:${NC} Cannot connect to PostgreSQL"
    log_verbose "    Fix: docker compose logs postgres --tail=20"
fi

log ""

# 3. API Endpoint Checks
log "${YELLOW}API Endpoints:${NC}"

# Check root endpoint
log_no_newline "  GET /:"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    check_pass
    log_verbose "    Root endpoint returned 200 OK"
else
    check_fail
    log_verbose "    ${RED}ERROR:${NC} Root endpoint returned $HTTP_CODE"
    log_verbose "    Fix: docker compose logs app --tail=50"
fi

# Check health endpoint
log_no_newline "  GET /health:"
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health 2>/dev/null || echo "{}")
HEALTH_STATUS=$(echo "$HEALTH_RESPONSE" | jq -r '.status' 2>/dev/null || echo "error")
if [ "$HEALTH_STATUS" = "healthy" ]; then
    check_pass
    log_verbose "    Health endpoint reports healthy"
elif [ "$HEALTH_STATUS" = "unhealthy" ]; then
    check_fail
    log_verbose "    ${RED}ERROR:${NC} Health endpoint reports unhealthy"
    DB_STATUS=$(echo "$HEALTH_RESPONSE" | jq -r '.database.status' 2>/dev/null)
    log_verbose "    Database status: $DB_STATUS"
    log_verbose "    Fix: Check database connectivity"
else
    check_fail
    log_verbose "    ${RED}ERROR:${NC} Cannot reach health endpoint or invalid response"
    log_verbose "    Fix: docker compose restart app"
fi

# Check docs endpoint
log_no_newline "  GET /docs:"
DOCS_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs 2>/dev/null || echo "000")
if [ "$DOCS_CODE" = "200" ]; then
    check_pass
    log_verbose "    API docs accessible"
else
    check_fail
    log_verbose "    ${RED}ERROR:${NC} API docs returned $DOCS_CODE"
fi

# Check database from health endpoint
log_no_newline "  Database health:"
DB_STATUS=$(echo "$HEALTH_RESPONSE" | jq -r '.database.status' 2>/dev/null || echo "error")
if [ "$DB_STATUS" = "up" ]; then
    check_pass
    log_verbose "    Database reports as up"
else
    check_fail
    log_verbose "    ${RED}ERROR:${NC} Database status: $DB_STATUS"
    log_verbose "    Fix: Check postgres container and connection"
fi

log ""

# 4. Test Checks (unless --quick)
if [ "$QUICK_MODE" = false ]; then
    log "${YELLOW}Tests:${NC}"

    # Run pytest
    log_no_newline "  Running tests:"
    if [ "$VERBOSE" = true ]; then
        log ""
        if docker compose exec -T app pytest -v 2>&1 | tee -a "$LOG_FILE"; then
            log_no_newline "  Result:"
            check_pass
        else
            log_no_newline "  Result:"
            check_fail
            log_verbose "    ${RED}ERROR:${NC} Some tests failed"
            log_verbose "    Fix: docker compose exec app pytest -vv"
        fi
    else
        TEST_OUTPUT=$(docker compose exec -T app pytest -q 2>&1)
        echo "$TEST_OUTPUT" >> "$LOG_FILE"
        if echo "$TEST_OUTPUT" | grep -q "passed"; then
            PASSED=$(echo "$TEST_OUTPUT" | grep -oP '\d+(?= passed)' | head -1)
            check_pass
            log_verbose "    $PASSED tests passed"
        else
            check_fail
            log_verbose "    ${RED}ERROR:${NC} Tests failed"
            log_verbose "$TEST_OUTPUT"
        fi
    fi

    # Check coverage
    log_no_newline "  Coverage:"
    COVERAGE_OUTPUT=$(docker compose exec -T app pytest --cov=app --cov-report=term 2>&1 || echo "")
    echo "$COVERAGE_OUTPUT" >> "$LOG_FILE"
    COVERAGE=$(echo "$COVERAGE_OUTPUT" | grep "TOTAL" | awk '{print $NF}' | tr -d '%' || echo "0")

    if [ -n "$COVERAGE" ] && [ "$COVERAGE" -ge 80 ] 2>/dev/null; then
        log " ${GREEN}✅${NC} ${COVERAGE}% (≥80%)"
        log_verbose "    Coverage meets target"
    elif [ -n "$COVERAGE" ]; then
        check_fail
        log " ${COVERAGE}%"
        log_verbose "    ${RED}ERROR:${NC} Coverage below 80% target"
        log_verbose "    Fix: Add tests to improve coverage"
    else
        check_fail
        log_verbose "    ${RED}ERROR:${NC} Could not determine coverage"
    fi

    log ""
fi

# Summary
log "================================"
if [ "$ISSUES_FOUND" = true ]; then
    log "${RED}❌ ISSUES FOUND${NC}"
    log ""
    log "Suggested fixes:"
    if ! docker ps > /dev/null 2>&1; then
        log "  → Start Docker: ${YELLOW}systemctl start docker${NC} (or Docker Desktop)"
    fi
    if ! docker compose ps postgres 2>&1 | grep -q "Up"; then
        log "  → Start services: ${YELLOW}docker compose up -d${NC}"
    fi
    if ! docker compose ps app 2>&1 | grep -q "Up"; then
        log "  → Start app: ${YELLOW}docker compose up -d app${NC}"
    fi
    log "  → Check logs: ${YELLOW}docker compose logs app -f${NC}"
    log "  → See docs: ${YELLOW}docs/health-check.md${NC}"
    log ""
    log "Log saved: ${YELLOW}$LOG_FILE${NC}"
    exit 1
else
    log "${GREEN}✅ ALL CHECKS PASSED - System Healthy!${NC}"
    log ""
    log "Log saved: ${YELLOW}$LOG_FILE${NC}"
    exit 0
fi
