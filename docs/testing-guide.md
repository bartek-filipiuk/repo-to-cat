# Testing Guide

**Last Updated:** 2025-10-08
**Stage:** 1.3 - FastAPI Skeleton

---

## Overview

This project uses **pytest** for testing with:
- `pytest-asyncio` for async tests
- `pytest-cov` for code coverage
- `httpx` for API testing (FastAPI)

**Coverage target:** 80%+

**⚠️ IMPORTANT:** All tests MUST be run inside Docker containers for production parity (see [LL-DEV-001](../.agent/lessons-learned/LL-DEV-001-docker-first-development.md)).

---

## Running Tests in Docker

**Docker-First Development** - Always use Docker commands for testing:

### Run All Tests

```bash
# Run all tests in Docker
docker compose exec app pytest

# Verbose output
docker compose exec app pytest -v

# Very verbose (show all output)
docker compose exec app pytest -vv

# Run with coverage
docker compose exec app pytest --cov=app --cov-report=term
```

### Quick Commands

```bash
# Most common: Run all tests with verbose output
docker compose exec app pytest -v

# Run with coverage report
docker compose exec app pytest tests/ -v --cov=app --cov-report=term

# Fast check: Run specific test file
docker compose exec app pytest tests/unit/test_main.py -v
```

---

## Quick Start (Legacy - Host-Based)

**⚠️ NOT RECOMMENDED:** Only use host-based commands for quick local debugging.

```bash
# Run all tests (host)
pytest

# Verbose output (host)
pytest -v

# Run with coverage (host)
pytest --cov=app --cov-report=term
```

**Expected output:**
```
========================= test session starts =========================
collected 7 items

tests/unit/test_database.py::test_database_connection PASSED    [ 14%]
tests/unit/test_database.py::test_session_creation PASSED       [ 28%]
tests/unit/test_database.py::test_get_db_dependency PASSED      [ 42%]
tests/unit/test_database.py::test_user_table_exists PASSED      [ 57%]
tests/unit/test_database.py::test_generation_table_exists PASSED [ 71%]
tests/unit/test_database.py::test_create_user PASSED            [ 85%]
tests/unit/test_database.py::test_create_generation PASSED      [100%]

========================== 7 passed in 0.45s ==========================
```

---

## Test Organization

```
tests/
├── __init__.py
├── unit/                    # Unit tests (isolated, fast)
│   ├── __init__.py
│   ├── test_config.py       # Configuration tests
│   └── test_database.py     # Database connection tests
├── integration/             # Integration tests (slower)
│   └── __init__.py
└── conftest.py             # Shared fixtures (future)
```

---

## Running Tests

### Run Specific Tests

```bash
# Run specific file
pytest tests/unit/test_database.py

# Run specific test function
pytest tests/unit/test_database.py::test_database_connection

# Run tests matching pattern
pytest -k "database"

# Run tests matching multiple patterns
pytest -k "database or config"
```

### Run by Test Type

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Exclude integration tests
pytest --ignore=tests/integration/
```

### Control Output

```bash
# Show print() output
pytest -s

# Show local variables on failure
pytest -l

# Stop on first failure
pytest -x

# Stop after N failures
pytest --maxfail=3

# Show slowest tests
pytest --durations=10
```

---

## Code Coverage

### Generate Coverage Report

```bash
# Terminal report
pytest --cov=app --cov-report=term

# HTML report (browsable)
pytest --cov=app --cov-report=html

# Open HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# XML report (for CI/CD)
pytest --cov=app --cov-report=xml

# Show missing lines
pytest --cov=app --cov-report=term-missing
```

### Coverage Example Output

```
---------- coverage: platform linux, python 3.12.7 -----------
Name                          Stmts   Miss  Cover   Missing
-----------------------------------------------------------
app/__init__.py                   0      0   100%
app/core/__init__.py              0      0   100%
app/core/config.py               10      0   100%
app/core/database.py             12      1    92%   25
app/models/__init__.py            0      0   100%
app/models/database.py           20      2    90%   15-16
-----------------------------------------------------------
TOTAL                            42      3    93%
```

### Coverage Goals

**Stage 1.2 targets:**
- Core modules: 90%+
- Database models: 85%+
- Overall: 80%+

**Exclusions:**
```python
# In code, mark lines to exclude
if __name__ == "__main__":  # pragma: no cover
    main()
```

---

## Database Tests

### Test: `test_database.py`

**Purpose:** Verify database connection, session management, and CRUD operations

**Tests included:**
1. `test_database_connection` - Raw DB connection works
2. `test_session_creation` - SQLAlchemy session creation
3. `test_get_db_dependency` - FastAPI dependency works
4. `test_user_table_exists` - Users table created
5. `test_generation_table_exists` - Generations table created
6. `test_create_user` - Can create/delete user
7. `test_create_generation` - Can create/delete generation

**Run database tests:**
```bash
pytest tests/unit/test_database.py -v
```

**Prerequisites:**
- PostgreSQL container running (`docker compose ps`)
- Database migrations applied (`alembic upgrade head`)
- Correct `DATABASE_URL` in `.env`

---

## Configuration Tests

### Test: `test_config.py`

**Purpose:** Verify environment configuration loading

**Run config tests:**
```bash
pytest tests/unit/test_config.py -v
```

---

## Writing New Tests

### Test Structure

```python
# tests/unit/test_example.py
import pytest
from app.some_module import some_function

def test_something():
    """Test description goes here."""
    # Arrange
    input_data = "test"

    # Act
    result = some_function(input_data)

    # Assert
    assert result == expected_output
```

### Using Fixtures

```python
# tests/conftest.py
import pytest
from app.core.database import SessionLocal

@pytest.fixture
def db_session():
    """Provide a database session for tests."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

# tests/unit/test_example.py
def test_with_db(db_session):
    """Use the db_session fixture."""
    result = db_session.query(User).count()
    assert result >= 0
```

### Async Tests

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Test async function."""
    result = await some_async_function()
    assert result is not None
```

### Parametrized Tests

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    ("python", "Python"),
    ("javascript", "JavaScript"),
    ("go", "Go"),
])
def test_language_format(input, expected):
    result = format_language(input)
    assert result == expected
```

---

## Test Best Practices

### 1. Test Naming

```python
# Good
def test_create_user_with_valid_data():
    pass

def test_create_user_raises_error_with_duplicate_username():
    pass

# Bad
def test_user():
    pass

def test1():
    pass
```

### 2. One Assertion Per Test

```python
# Good
def test_user_has_id():
    user = create_user()
    assert user.id is not None

def test_user_has_timestamp():
    user = create_user()
    assert user.created_at is not None

# Acceptable for related checks
def test_user_creation():
    user = create_user("test_user")
    assert user.id is not None
    assert user.username == "test_user"
```

### 3. Clean Up Test Data

```python
def test_create_generation():
    session = SessionLocal()
    try:
        # Create test data
        gen = Generation(github_url="https://github.com/test/repo")
        session.add(gen)
        session.commit()

        # Test
        assert gen.id is not None

        # Clean up
        session.delete(gen)
        session.commit()
    finally:
        session.close()
```

### 4. Use Descriptive Test Data

```python
# Good
test_user = User(username="test_user_123", api_token="test_token_abc")

# Bad
test_user = User(username="a", api_token="b")
```

---

## Continuous Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: repo_to_cat
          POSTGRES_USER: repo_user
          POSTGRES_PASSWORD: repo_password
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests
        run: pytest --cov=app --cov-report=xml
        env:
          DATABASE_URL: postgresql://repo_user:repo_password@localhost:5432/repo_to_cat

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Troubleshooting

### Docker: Tests Can't Connect to Database

**Error:** `OperationalError: could not connect to server`

**Fix:**
```bash
# 1. Ensure PostgreSQL is running
docker compose ps

# 2. Check postgres health
docker compose logs postgres --tail=20

# 3. Test connection from inside app container
docker compose exec app psql postgresql://repo_user:repo_password@postgres:5432/repo_to_cat -c "SELECT 1"

# 4. Apply migrations (if needed)
docker compose exec app alembic upgrade head

# 5. Restart containers
docker compose restart app
```

### Docker: Container Not Running

**Error:** `Error response from daemon: Container ... is not running`

**Fix:**
```bash
# Start all services
docker compose up -d

# Check container status
docker compose ps

# View startup logs
docker compose logs app --tail=50
```

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'app'`

**Fix:**
```bash
# Ensure you're in project root
pwd  # Should be /path/to/repo-to-cat

# Install dependencies
pip install -r requirements.txt

# Set PYTHONPATH if needed
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Tests Passing Locally, Failing in CI

**Common causes:**
1. Different environment variables
2. Database not initialized
3. Missing dependencies
4. Port conflicts

**Fix:**
```yaml
# In CI config, ensure:
- env:
    DATABASE_URL: postgresql://...
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

- name: Apply migrations
  run: alembic upgrade head
```

### Slow Tests

**Identify slow tests:**
```bash
pytest --durations=10
```

**Common causes:**
1. Not using database fixtures (creating new connections)
2. Not cleaning up test data
3. Running integration tests in unit test suite

**Fix:**
- Use shared fixtures
- Mock external services
- Separate unit and integration tests

---

## Test Coverage Goals by Stage

| Stage | Module | Target Coverage |
|-------|--------|----------------|
| 1.1 | config.py | 100% ✅ |
| 1.2 | database.py | 90% ✅ |
| 1.2 | models/ | 90% ✅ |
| 1.3 | main.py | 85% |
| 2.x | services/ | 80% |
| 3.x | providers/ | 75% |

---

## Next Steps

- **Docker setup:** See [docker-setup.md](docker-setup.md)
- **Database access:** See [database-guide.md](database-guide.md)
- **Stage summary:** See [stages/stage-1.2-summary.md](stages/stage-1.2-summary.md)

---

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- Project files:
  - [tests/unit/test_database.py](../tests/unit/test_database.py)
  - [tests/unit/test_config.py](../tests/unit/test_config.py)
  - [requirements.txt](../requirements.txt)
