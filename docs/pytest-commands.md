# Pytest Commands Reference

**Last Updated:** 2025-10-08
**Project:** Repo-to-Cat

---

## Overview

Quick reference for pytest commands used in Repo-to-Cat project. All commands assume Docker-first development.

**Current tests:** 18 tests (Stage 1.3)
**Coverage target:** 80%+

---

## Quick Reference Table

| Task | Command |
|------|---------|
| Run all tests | `docker compose exec app pytest` |
| Verbose output | `docker compose exec app pytest -v` |
| Run with coverage | `docker compose exec app pytest --cov=app --cov-report=term` |
| Run specific file | `docker compose exec app pytest tests/unit/test_main.py` |
| Run specific test | `docker compose exec app pytest tests/unit/test_main.py::test_app_exists` |
| Stop on first fail | `docker compose exec app pytest -x` |
| Show print output | `docker compose exec app pytest -s` |
| Run matching pattern | `docker compose exec app pytest -k "health"` |
| Slowest tests | `docker compose exec app pytest --durations=10` |

---

## Basic Usage

### Run Tests

```bash
# Run all tests (Docker)
docker compose exec app pytest

# Verbose mode (shows each test)
docker compose exec app pytest -v

# Very verbose (shows all output)
docker compose exec app pytest -vv

# Quiet mode (minimal output)
docker compose exec app pytest -q

# Show print() output
docker compose exec app pytest -s
```

### Run Specific Tests

```bash
# Run specific file
docker compose exec app pytest tests/unit/test_main.py

# Run specific directory
docker compose exec app pytest tests/unit/

# Run specific test function
docker compose exec app pytest tests/unit/test_main.py::test_app_exists

# Run specific test class
docker compose exec app pytest tests/unit/test_main.py::TestHealthEndpoint

# Run specific test in class
docker compose exec app pytest tests/unit/test_main.py::TestHealthEndpoint::test_health_endpoint_exists
```

### Run by Pattern

```bash
# Run tests matching keyword
docker compose exec app pytest -k "health"

# Run tests NOT matching keyword
docker compose exec app pytest -k "not slow"

# Multiple patterns (OR)
docker compose exec app pytest -k "health or database"

# Multiple patterns (AND)
docker compose exec app pytest -k "health and endpoint"
```

---

## Code Coverage

### Generate Coverage Reports

```bash
# Terminal report (default)
docker compose exec app pytest --cov=app --cov-report=term

# Show missing lines
docker compose exec app pytest --cov=app --cov-report=term-missing

# HTML report (browsable)
docker compose exec app pytest --cov=app --cov-report=html

# Copy HTML report from container
docker cp repo-to-cat-app:/app/htmlcov ./htmlcov
# Then open: htmlcov/index.html

# XML report (for CI/CD)
docker compose exec app pytest --cov=app --cov-report=xml

# Multiple report formats
docker compose exec app pytest --cov=app --cov-report=term --cov-report=html
```

### Coverage Options

```bash
# Coverage for specific module
docker compose exec app pytest --cov=app.main

# Coverage for multiple modules
docker compose exec app pytest --cov=app.main --cov=app.core

# Minimum coverage (fail if below)
docker compose exec app pytest --cov=app --cov-fail-under=80

# Show coverage in terminal
docker compose exec app pytest --cov=app --cov-report=term

# No coverage output
docker compose exec app pytest --no-cov
```

---

## Output Control

### Verbosity

```bash
# Normal output
docker compose exec app pytest

# Verbose (-v)
docker compose exec app pytest -v

# Very verbose (-vv)
docker compose exec app pytest -vv

# Quiet (-q)
docker compose exec app pytest -q

# Show local variables on failure (-l)
docker compose exec app pytest -l

# Full diff on assertion errors
docker compose exec app pytest --tb=long
```

### Control Execution

```bash
# Stop on first failure
docker compose exec app pytest -x

# Stop after 3 failures
docker compose exec app pytest --maxfail=3

# Run last failed tests only
docker compose exec app pytest --lf

# Run first failed, then all
docker compose exec app pytest --ff

# Show slowest 10 tests
docker compose exec app pytest --durations=10

# Show all durations
docker compose exec app pytest --durations=0
```

---

## Filtering Tests

### By Directory

```bash
# Unit tests only
docker compose exec app pytest tests/unit/

# Integration tests only
docker compose exec app pytest tests/integration/

# Multiple directories
docker compose exec app pytest tests/unit/ tests/integration/
```

### By Markers (Future)

```bash
# Run tests marked as 'slow'
docker compose exec app pytest -m slow

# Run tests NOT marked as 'slow'
docker compose exec app pytest -m "not slow"

# Multiple markers
docker compose exec app pytest -m "unit and not slow"
```

### By File Pattern

```bash
# Run all test files matching pattern
docker compose exec app pytest tests/unit/test_*.py

# Exclude files
docker compose exec app pytest --ignore=tests/integration/
```

---

## Debugging

### Show More Information

```bash
# Show print statements
docker compose exec app pytest -s

# Show local variables
docker compose exec app pytest -l

# Full traceback
docker compose exec app pytest --tb=long

# Short traceback
docker compose exec app pytest --tb=short

# No traceback
docker compose exec app pytest --tb=no

# Show captured output even on pass
docker compose exec app pytest --capture=no
```

### Interactive Debugging

```bash
# Drop into debugger on failure
docker compose exec app pytest --pdb

# Drop into debugger on first failure
docker compose exec app pytest --pdb -x

# Use ipdb (if installed)
docker compose exec app pytest --pdbcls=IPython.terminal.debugger:TerminalPdb
```

---

## Performance

### Parallel Execution (Future)

```bash
# Install pytest-xdist first
# pip install pytest-xdist

# Run tests in parallel (4 workers)
docker compose exec app pytest -n 4

# Auto-detect CPU count
docker compose exec app pytest -n auto
```

### Show Timing

```bash
# Show 10 slowest tests
docker compose exec app pytest --durations=10

# Show all test durations
docker compose exec app pytest --durations=0

# Show durations above 0.5s
docker compose exec app pytest --durations-min=0.5
```

---

## Common Workflows

### Development Workflow

```bash
# Run tests while developing
docker compose exec app pytest -v

# After making changes (fast)
docker compose exec app pytest tests/unit/test_main.py -v

# Before committing (full check)
docker compose exec app pytest -v --cov=app --cov-report=term

# If tests fail (debug)
docker compose exec app pytest -x -vv -s
```

### Quick Checks

```bash
# Smoke test (just run, no coverage)
docker compose exec app pytest

# Fast health check (main + database tests only)
docker compose exec app pytest tests/unit/test_main.py tests/unit/test_database.py -v

# Coverage check only
docker compose exec app pytest --cov=app --cov-report=term | grep TOTAL
```

### Pre-Commit Workflow

```bash
# Full test suite with coverage
docker compose exec app pytest tests/ -v --cov=app --cov-report=term

# If all pass, commit
# If tests fail, fix and re-run:
docker compose exec app pytest --lf -v
```

---

## Project-Specific Examples

### Stage 1.3 Tests (FastAPI)

```bash
# All FastAPI tests
docker compose exec app pytest tests/unit/test_main.py -v

# Just health endpoint tests
docker compose exec app pytest tests/unit/test_main.py::TestHealthEndpoint -v

# Just API docs tests
docker compose exec app pytest tests/unit/test_main.py::TestAPIDocs -v

# Single health check test
docker compose exec app pytest tests/unit/test_main.py::TestHealthEndpoint::test_health_endpoint_exists -v
```

### Stage 1.2 Tests (Database)

```bash
# All database tests
docker compose exec app pytest tests/unit/test_database.py -v

# Just connection tests
docker compose exec app pytest -k "connection" -v

# Just CRUD tests
docker compose exec app pytest -k "create" -v
```

### Combined Stages

```bash
# Run both Stage 1.2 and 1.3 tests
docker compose exec app pytest tests/unit/test_database.py tests/unit/test_main.py -v

# All unit tests
docker compose exec app pytest tests/unit/ -v

# With coverage for both
docker compose exec app pytest tests/unit/ --cov=app --cov-report=term
```

---

## Coverage Analysis

### View Coverage by Module

```bash
# Detailed coverage report
docker compose exec app pytest --cov=app --cov-report=term-missing

# Example output:
# Name                    Stmts   Miss  Cover   Missing
# -----------------------------------------------------
# app/main.py                22      3    86%   45-47
# app/core/config.py         11      0   100%
# app/core/database.py       12      0   100%
```

### Generate HTML Coverage Report

```bash
# Generate HTML report
docker compose exec app pytest --cov=app --cov-report=html

# Copy to host
docker cp repo-to-cat-app:/app/htmlcov ./htmlcov

# Open in browser (Linux)
xdg-open htmlcov/index.html

# Open in browser (macOS)
open htmlcov/index.html
```

### Coverage Thresholds

```bash
# Fail if coverage below 80%
docker compose exec app pytest --cov=app --cov-fail-under=80

# Fail if coverage below 90%
docker compose exec app pytest --cov=app --cov-fail-under=90

# Check if meets target
docker compose exec app pytest --cov=app --cov-fail-under=80 && echo "✅ Coverage OK"
```

---

## Troubleshooting

### Tests Not Found

**Error:** `ERROR: file or directory not found`

**Fix:**
```bash
# Ensure container is running
docker compose ps

# Check you're in correct directory inside container
docker compose exec app pwd
# Should be: /app

# List test files
docker compose exec app ls tests/unit/

# Try absolute path
docker compose exec app pytest /app/tests/unit/test_main.py
```

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'app'`

**Fix:**
```bash
# Check PYTHONPATH in container
docker compose exec app env | grep PYTHON

# Check app directory exists
docker compose exec app ls /app/app/

# Restart container
docker compose restart app

# Rebuild if needed
docker compose up -d --build app
```

### Tests Pass Locally, Fail in Docker

**Possible causes:**
1. Different Python version
2. Missing environment variables
3. Database not ready
4. Port conflicts

**Fix:**
```bash
# Check Python version matches
docker compose exec app python --version

# Check environment variables
docker compose exec app env | grep DATABASE_URL

# Ensure database is healthy
docker compose ps postgres

# Check logs
docker compose logs app --tail=50
```

---

## Best Practices

### DO ✅

- Run tests in Docker (not on host)
- Use `-v` for verbose output during development
- Check coverage before committing (`--cov=app`)
- Run specific tests when debugging (`-k` or file path)
- Use `-x` to stop on first failure (saves time)
- Show print output when debugging (`-s`)
- Check slowest tests (`--durations=10`)

### DON'T ❌

- Don't skip Docker (`pytest` on host is inconsistent)
- Don't ignore test failures (fix before committing)
- Don't commit with coverage below 80%
- Don't run `pytest` without specifying path in large projects
- Don't use `--no-cov` for pre-commit checks

---

## Useful Combinations

```bash
# Development: Fast feedback
docker compose exec app pytest -x -v tests/unit/test_main.py

# Debugging: Verbose with prints
docker compose exec app pytest -vv -s -x tests/unit/test_main.py

# Pre-commit: Full check
docker compose exec app pytest tests/ -v --cov=app --cov-report=term

# CI/CD: XML report
docker compose exec app pytest --cov=app --cov-report=xml --junitxml=junit.xml

# Quick smoke test
docker compose exec app pytest -q --tb=no

# Find slow tests
docker compose exec app pytest --durations=10 -q
```

---

## Related Documentation

- **Testing Guide:** [testing-guide.md](testing-guide.md) - Complete testing guide
- **Docker Commands:** [docker-commands.md](docker-commands.md) - Docker reference
- **Health Check:** [health-check.md](health-check.md) - System health verification

---

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
