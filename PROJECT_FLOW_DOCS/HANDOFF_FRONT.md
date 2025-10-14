# Frontend Development Handoff: Astro + Authentication

**Project:** Repo-to-Cat Frontend
**Last Updated:** 2025-10-14
**Status:** 🚧 Stage F1 Complete, F2 In Progress
**Branch:** `feature/frontend-auth-backend`
**Commit:** `7d8648b` (Stage F1)

---

## Overview

Build an Astro SSR frontend with username/password authentication for the Repo-to-Cat application. Users can log in, generate cat images from GitHub repositories, and view past generations.

**Design Inspiration:** [Oxide Computer](https://oxide.computer/)
**Color Palette:** Dark theme (#0a0a0a) with green accents (#00ffa3)
**Architecture:** Astro SSR (port 4321) → FastAPI backend (port 8000)

---

## Progress Tracker

### Stage F1: Database Schema & Backend Auth Foundation ✅
- [x] F1.1: Add password_hash and email to users table
- [x] F1.2: Create sessions table for auth tokens
- [x] F1.3: Add user_id foreign key to generations table
- [x] F1.4: Update documentation (database-guide.md)
- **Commit:** `7d8648b` - Stage F1: Database schema for authentication

### Stage F2: Backend Authentication Endpoints
- [ ] F2.1: Create password utility functions (bcrypt)
- [ ] F2.2: Create auth dependencies (session validation)
- [ ] F2.3: Implement POST /auth/login endpoint
- [ ] F2.4: Implement POST /auth/logout endpoint
- [ ] F2.5: Implement GET /auth/me endpoint
- [ ] F2.6: Write integration tests for auth endpoints
- [ ] F2.7: Update documentation (api-endpoints.md)

### Stage F3: Backend Protected Routes
- [ ] F3.1: Protect POST /generate endpoint (require auth)
- [ ] F3.2: Update workflow to save user_id with generation
- [ ] F3.3: Create GET /generations endpoint (list user's generations)
- [ ] F3.4: Create GET /generation/:id endpoint (public, with status)
- [ ] F3.5: Write tests for protected routes
- [ ] F3.6: Update documentation (api-endpoints.md)

### Stage F4: Astro Project Setup
- [ ] F4.1: Initialize Astro project in frontend/ directory
- [ ] F4.2: Install dependencies (@astrojs/node, tailwind)
- [ ] F4.3: Configure SSR and Tailwind
- [ ] F4.4: Create project structure (pages, components, lib)
- [ ] F4.5: Set up environment variables
- [ ] F4.6: Create documentation (docs/frontend-guide.md)

### Stage F5: Authentication UI
- [ ] F5.1: Create auth helper library (lib/auth.ts)
- [ ] F5.2: Create API client library (lib/api.ts)
- [ ] F5.3: Create login page (pages/login.astro)
- [ ] F5.4: Create auth middleware (middleware.ts)
- [ ] F5.5: Create Layout and Header components
- [ ] F5.6: Test login/logout flow manually
- [ ] F5.7: Update documentation (docs/frontend-guide.md)

### Stage F6: Dashboard & Generate Form
- [ ] F6.1: Create GenerateForm component with polling
- [ ] F6.2: Create GenerationCard component
- [ ] F6.3: Create GenerationList component (grid layout)
- [ ] F6.4: Create dashboard page (index.astro)
- [ ] F6.5: Test generate flow with polling
- [ ] F6.6: Update documentation (docs/frontend-guide.md)

### Stage F7: Generation Detail Page
- [ ] F7.1: Create generation detail page (generation/[id].astro)
- [ ] F7.2: Implement full-width image display
- [ ] F7.3: Implement story section
- [ ] F7.4: Implement repo data cards section
- [ ] F7.5: Test public shareable links
- [ ] F7.6: Update documentation (docs/frontend-guide.md)

### Stage F8: Design System Implementation
- [ ] F8.1: Configure Tailwind with Oxide color palette
- [ ] F8.2: Create global styles (styles/global.css)
- [ ] F8.3: Style all components with Oxide theme
- [ ] F8.4: Add hover effects and transitions
- [ ] F8.5: Test responsive design (mobile, tablet, desktop)
- [ ] F8.6: Create design system documentation

### Stage F9: Testing & Polish
- [ ] F9.1: Manual testing checklist (see below)
- [ ] F9.2: Fix bugs and edge cases
- [ ] F9.3: Performance optimization
- [ ] F9.4: Accessibility audit
- [ ] F9.5: Final documentation review

### Stage F10: Deployment Preparation
- [ ] F10.1: Update README.md with frontend setup
- [ ] F10.2: Create development startup script
- [ ] F10.3: Create PR with comprehensive description
- [ ] F10.4: Demo video or screenshots

---

## Stage F1: Database Schema & Backend Auth Foundation

### Task F1.1: Add password_hash and email to users table

**File:** `app/models/database.py`

**Changes to User model:**
```python
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(255), unique=True, nullable=False)  # Change nullable to False
    email = Column(String(255), unique=True, nullable=True)  # NEW
    password_hash = Column(String(255), nullable=False)  # NEW
    api_token = Column(String(255), unique=True, nullable=True)  # Keep for future
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship to generations
    generations = relationship("Generation", back_populates="user")  # NEW
```

**Create migration:**
```bash
alembic revision --autogenerate -m "Add password_hash and email to users table"
alembic upgrade head
```

**Testing:**
- Test that new users can be created with password_hash
- Test email uniqueness constraint
- Test username is now required (not nullable)

**Acceptance Criteria:**
- [ ] Migration created and applied successfully
- [ ] User model updated with new fields
- [ ] Tests pass for user creation with password_hash
- [ ] Database schema matches model

---

### Task F1.2: Create sessions table for auth tokens

**File:** `app/models/database.py`

**New Session model:**
```python
class Session(Base):
    """
    Session model for authentication tokens.

    Stores session tokens with expiration for user authentication.
    """
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    user = relationship("User", back_populates="sessions")

    __table_args__ = (
        Index('ix_sessions_token', 'token'),
        Index('ix_sessions_user_id', 'user_id'),
    )
```

**Update User model:**
```python
# Add to User model
sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
```

**Create migration:**
```bash
alembic revision --autogenerate -m "Create sessions table for authentication"
alembic upgrade head
```

**Testing:**
- Test session creation with user_id
- Test token uniqueness
- Test cascade delete (deleting user deletes sessions)

**Acceptance Criteria:**
- [ ] Session model created
- [ ] Migration applied successfully
- [ ] Indexes created for token and user_id
- [ ] Cascade delete works (delete user → delete sessions)

---

### Task F1.3: Add user_id foreign key to generations table

**File:** `app/models/database.py`

**Changes to Generation model:**
```python
class Generation(Base):
    __tablename__ = "generations"

    # ... existing fields ...

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # NEW

    # ... existing fields ...

    # Relationship
    user = relationship("User", back_populates="generations")  # NEW
```

**Create migration:**
```bash
alembic revision --autogenerate -m "Add user_id foreign key to generations table"
alembic upgrade head
```

**Testing:**
- Test generation creation with user_id
- Test generation creation without user_id (nullable)
- Test foreign key constraint

**Acceptance Criteria:**
- [ ] user_id field added to Generation model
- [ ] Migration applied successfully
- [ ] Foreign key constraint works
- [ ] Relationship between User and Generation works

---

### Task F1.4: Update documentation

**File:** `docs/database-guide.md`

**Add new sections:**

1. **Sessions Table** (after users table section):
```markdown
### `sessions` Table

```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_sessions_token ON sessions(token);
CREATE INDEX ix_sessions_user_id ON sessions(user_id);
```

**Purpose:** Store authentication session tokens

**Key fields:**
- `token` - Secure random token (64 characters)
- `expires_at` - Session expiration (7 days from creation)
- `user_id` - Foreign key to users table
```

2. **Update Users Table** section to include new fields

3. **Update Generations Table** section to include user_id

**Acceptance Criteria:**
- [ ] Sessions table documented
- [ ] Users table documentation updated
- [ ] Generations table documentation updated
- [ ] Example queries added for sessions

---

## Stage F2: Backend Authentication Endpoints

### Task F2.1: Create password utility functions

**File:** `app/utils/auth.py` (NEW)

**Implementation:**
```python
"""
Authentication utilities for password hashing and session management.
"""
import secrets
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from sqlalchemy.orm import Session

from app.models.database import User, Session as DBSession


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a bcrypt hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt hashed password from database

    Returns:
        True if password matches, False otherwise
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_session_token() -> str:
    """
    Generate a secure random session token.

    Returns:
        64-character hexadecimal token
    """
    return secrets.token_hex(32)  # 32 bytes = 64 hex characters


def create_session(db: Session, user_id: str, expires_in_days: int = 7) -> DBSession:
    """
    Create a new session in the database.

    Args:
        db: Database session
        user_id: User UUID
        expires_in_days: Session expiration (default 7 days)

    Returns:
        Created Session object
    """
    token = create_session_token()
    expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

    session = DBSession(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


def verify_session_token(db: Session, token: str) -> Optional[User]:
    """
    Verify a session token and return the associated user.

    Args:
        db: Database session
        token: Session token to verify

    Returns:
        User object if valid, None if invalid or expired
    """
    session = db.query(DBSession).filter(DBSession.token == token).first()

    if not session:
        return None

    # Check if expired
    if session.expires_at < datetime.utcnow():
        # Delete expired session
        db.delete(session)
        db.commit()
        return None

    # Return associated user
    return session.user


def delete_session(db: Session, token: str) -> bool:
    """
    Delete a session from the database.

    Args:
        db: Database session
        token: Session token to delete

    Returns:
        True if session was deleted, False if not found
    """
    session = db.query(DBSession).filter(DBSession.token == token).first()

    if session:
        db.delete(session)
        db.commit()
        return True

    return False
```

**File:** `tests/unit/test_auth_utils.py` (NEW)

**Test implementation:**
```python
"""
Tests for authentication utilities.
"""
import pytest
from datetime import datetime, timedelta

from app.utils.auth import (
    hash_password,
    verify_password,
    create_session_token,
    create_session,
    verify_session_token,
    delete_session
)
from app.models.database import User, Session as DBSession


def test_hash_password():
    """Test password hashing."""
    password = "test_password_123"
    hashed = hash_password(password)

    assert hashed != password
    assert len(hashed) > 0
    assert isinstance(hashed, str)


def test_verify_password_correct():
    """Test password verification with correct password."""
    password = "test_password_123"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
    """Test password verification with incorrect password."""
    password = "test_password_123"
    wrong_password = "wrong_password"
    hashed = hash_password(password)

    assert verify_password(wrong_password, hashed) is False


def test_create_session_token():
    """Test session token generation."""
    token1 = create_session_token()
    token2 = create_session_token()

    assert len(token1) == 64  # 32 bytes hex = 64 chars
    assert len(token2) == 64
    assert token1 != token2  # Should be unique


def test_create_session(db_session):
    """Test session creation in database."""
    # Create a test user
    user = User(username="testuser", password_hash=hash_password("password"))
    db_session.add(user)
    db_session.commit()

    # Create session
    session = create_session(db_session, user.id)

    assert session.user_id == user.id
    assert len(session.token) == 64
    assert session.expires_at > datetime.utcnow()
    assert session.created_at is not None


def test_verify_session_token_valid(db_session):
    """Test session token verification with valid token."""
    # Create user and session
    user = User(username="testuser", password_hash=hash_password("password"))
    db_session.add(user)
    db_session.commit()

    session = create_session(db_session, user.id)

    # Verify token
    verified_user = verify_session_token(db_session, session.token)

    assert verified_user is not None
    assert verified_user.id == user.id


def test_verify_session_token_invalid(db_session):
    """Test session token verification with invalid token."""
    verified_user = verify_session_token(db_session, "invalid_token_12345")
    assert verified_user is None


def test_verify_session_token_expired(db_session):
    """Test session token verification with expired token."""
    # Create user and session
    user = User(username="testuser", password_hash=hash_password("password"))
    db_session.add(user)
    db_session.commit()

    # Create expired session
    token = create_session_token()
    expired_session = DBSession(
        user_id=user.id,
        token=token,
        expires_at=datetime.utcnow() - timedelta(days=1)  # Expired yesterday
    )
    db_session.add(expired_session)
    db_session.commit()

    # Verify token (should return None and delete session)
    verified_user = verify_session_token(db_session, token)

    assert verified_user is None
    # Check session was deleted
    session_in_db = db_session.query(DBSession).filter(DBSession.token == token).first()
    assert session_in_db is None


def test_delete_session(db_session):
    """Test session deletion."""
    # Create user and session
    user = User(username="testuser", password_hash=hash_password("password"))
    db_session.add(user)
    db_session.commit()

    session = create_session(db_session, user.id)
    token = session.token

    # Delete session
    result = delete_session(db_session, token)

    assert result is True
    # Check session was deleted
    session_in_db = db_session.query(DBSession).filter(DBSession.token == token).first()
    assert session_in_db is None


def test_delete_session_not_found(db_session):
    """Test deleting non-existent session."""
    result = delete_session(db_session, "nonexistent_token")
    assert result is False
```

**Dependencies to add:**
```bash
pip install bcrypt
# Update requirements.txt
```

**Acceptance Criteria:**
- [ ] app/utils/auth.py created with all functions
- [ ] bcrypt dependency added to requirements.txt
- [ ] All tests pass (test_auth_utils.py)
- [ ] Password hashing works correctly
- [ ] Session token generation is secure and unique
- [ ] Session verification handles expired tokens

---

### Task F2.2: Create auth dependencies

**File:** `app/api/dependencies.py` (NEW)

**Implementation:**
```python
"""
FastAPI dependencies for authentication and authorization.
"""
from typing import Optional
from fastapi import Cookie, HTTPException, Header, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.database import User
from app.utils.auth import verify_session_token


def get_current_user(
    session_token: Optional[str] = Cookie(None, alias="session_token"),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from session token.

    Checks for token in:
    1. Cookie (preferred): session_token
    2. Header: Authorization: Bearer <token>

    Args:
        session_token: Session token from cookie
        authorization: Authorization header
        db: Database session

    Returns:
        User object if authenticated

    Raises:
        HTTPException 401 if not authenticated
    """
    token = None

    # Try cookie first
    if session_token:
        token = session_token
    # Try Authorization header
    elif authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. Please log in."
        )

    # Verify token
    user = verify_session_token(db, token)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session. Please log in again."
        )

    return user


def get_current_user_optional(
    session_token: Optional[str] = Cookie(None, alias="session_token"),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get the current user if authenticated, otherwise return None.

    Used for endpoints that are optionally authenticated.

    Args:
        session_token: Session token from cookie
        authorization: Authorization header
        db: Database session

    Returns:
        User object if authenticated, None otherwise
    """
    try:
        return get_current_user(session_token, authorization, db)
    except HTTPException:
        return None
```

**File:** `tests/unit/test_dependencies.py` (NEW)

**Test implementation:**
```python
"""
Tests for FastAPI authentication dependencies.
"""
import pytest
from fastapi import HTTPException

from app.api.dependencies import get_current_user, get_current_user_optional
from app.models.database import User
from app.utils.auth import hash_password, create_session


def test_get_current_user_with_valid_cookie(db_session):
    """Test get_current_user with valid session cookie."""
    # Create user and session
    user = User(username="testuser", password_hash=hash_password("password"))
    db_session.add(user)
    db_session.commit()

    session = create_session(db_session, user.id)

    # Call dependency with cookie
    result = get_current_user(
        session_token=session.token,
        authorization=None,
        db=db_session
    )

    assert result.id == user.id
    assert result.username == user.username


def test_get_current_user_with_valid_header(db_session):
    """Test get_current_user with valid Authorization header."""
    # Create user and session
    user = User(username="testuser", password_hash=hash_password("password"))
    db_session.add(user)
    db_session.commit()

    session = create_session(db_session, user.id)

    # Call dependency with header
    result = get_current_user(
        session_token=None,
        authorization=f"Bearer {session.token}",
        db=db_session
    )

    assert result.id == user.id


def test_get_current_user_no_token(db_session):
    """Test get_current_user with no token."""
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(
            session_token=None,
            authorization=None,
            db=db_session
        )

    assert exc_info.value.status_code == 401
    assert "Not authenticated" in exc_info.value.detail


def test_get_current_user_invalid_token(db_session):
    """Test get_current_user with invalid token."""
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(
            session_token="invalid_token",
            authorization=None,
            db=db_session
        )

    assert exc_info.value.status_code == 401
    assert "Invalid or expired session" in exc_info.value.detail


def test_get_current_user_optional_with_token(db_session):
    """Test get_current_user_optional with valid token."""
    # Create user and session
    user = User(username="testuser", password_hash=hash_password("password"))
    db_session.add(user)
    db_session.commit()

    session = create_session(db_session, user.id)

    # Call dependency
    result = get_current_user_optional(
        session_token=session.token,
        authorization=None,
        db=db_session
    )

    assert result is not None
    assert result.id == user.id


def test_get_current_user_optional_without_token(db_session):
    """Test get_current_user_optional with no token."""
    result = get_current_user_optional(
        session_token=None,
        authorization=None,
        db=db_session
    )

    assert result is None
```

**Acceptance Criteria:**
- [ ] app/api/dependencies.py created
- [ ] get_current_user dependency works with cookies
- [ ] get_current_user dependency works with headers
- [ ] get_current_user raises 401 for invalid/missing tokens
- [ ] get_current_user_optional returns None gracefully
- [ ] All tests pass

---

### Task F2.3: Implement POST /auth/login endpoint

**File:** `app/api/auth.py` (NEW)

**Implementation:**
```python
"""
Authentication API routes.
"""
import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.models.database import User
from app.utils.auth import verify_password, create_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ============================================================================
# REQUEST/RESPONSE SCHEMAS
# ============================================================================

class LoginRequest(BaseModel):
    """Request schema for login."""
    username: str = Field(..., min_length=1, description="Username")
    password: str = Field(..., min_length=1, description="Password")


class LoginResponse(BaseModel):
    """Response schema for login."""
    success: bool = Field(..., description="Whether login was successful")
    token: str = Field(..., description="Session token")
    user: Dict[str, Any] = Field(..., description="User information")


class LogoutResponse(BaseModel):
    """Response schema for logout."""
    success: bool = Field(..., description="Whether logout was successful")


class MeResponse(BaseModel):
    """Response schema for /auth/me."""
    id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str | None = Field(None, description="Email address")
    created_at: str = Field(..., description="Account creation timestamp")


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """
    Authenticate user with username and password.

    Creates a session token valid for 7 days and sets it as an httpOnly cookie.

    Args:
        request: Login credentials (username, password)
        response: FastAPI response for setting cookies
        db: Database session

    Returns:
        LoginResponse with session token and user info

    Raises:
        HTTPException 401: Invalid credentials
    """
    logger.info(f"Login attempt for user: {request.username}")

    # Find user by username
    user = db.query(User).filter(User.username == request.username).first()

    if not user:
        logger.warning(f"Login failed: User not found - {request.username}")
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    # Verify password
    if not verify_password(request.password, user.password_hash):
        logger.warning(f"Login failed: Invalid password - {request.username}")
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    # Create session
    session = create_session(db, str(user.id), expires_in_days=7)

    # Set httpOnly cookie
    response.set_cookie(
        key="session_token",
        value=session.token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=7 * 24 * 60 * 60  # 7 days in seconds
    )

    logger.info(f"Login successful for user: {request.username}")

    return {
        "success": True,
        "token": session.token,
        "user": {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at.isoformat()
        }
    }
```

**Add to app/main.py:**
```python
from app.api import auth

# Register router
app.include_router(auth.router)
```

**Acceptance Criteria:**
- [ ] POST /auth/login endpoint created
- [ ] Validates username and password
- [ ] Creates session token
- [ ] Sets httpOnly cookie
- [ ] Returns user info
- [ ] Returns 401 for invalid credentials
- [ ] Logs login attempts

---

### Task F2.4: Implement POST /auth/logout endpoint

**Add to file:** `app/api/auth.py`

**Implementation:**
```python
@router.post("/logout", response_model=LogoutResponse)
def logout(
    response: Response,
    session_token: str = Cookie(None, alias="session_token"),
    db: Session = Depends(get_db)
):
    """
    Logout user by deleting session token.

    Clears the session cookie and deletes the session from database.

    Args:
        response: FastAPI response for clearing cookies
        session_token: Session token from cookie
        db: Database session

    Returns:
        LogoutResponse with success status
    """
    if session_token:
        # Delete session from database
        from app.utils.auth import delete_session
        deleted = delete_session(db, session_token)

        if deleted:
            logger.info(f"Session deleted successfully")
        else:
            logger.warning(f"Session not found during logout")

    # Clear cookie regardless
    response.delete_cookie(key="session_token")

    logger.info("User logged out successfully")

    return {"success": True}
```

**Don't forget import:**
```python
from fastapi import Cookie
```

**Acceptance Criteria:**
- [ ] POST /auth/logout endpoint created
- [ ] Deletes session from database
- [ ] Clears session cookie
- [ ] Works even if session not found
- [ ] Returns success status

---

### Task F2.5: Implement GET /auth/me endpoint

**Add to file:** `app/api/auth.py`

**Implementation:**
```python
from app.api.dependencies import get_current_user

@router.get("/me", response_model=MeResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.

    Requires valid session token in cookie or Authorization header.

    Args:
        current_user: Current user from auth dependency

    Returns:
        MeResponse with user information

    Raises:
        HTTPException 401: Not authenticated or invalid token
    """
    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "created_at": current_user.created_at.isoformat()
    }
```

**Acceptance Criteria:**
- [ ] GET /auth/me endpoint created
- [ ] Returns user info for valid session
- [ ] Returns 401 for invalid/missing token
- [ ] Works with cookie authentication
- [ ] Works with header authentication

---

### Task F2.6: Write integration tests for auth endpoints

**File:** `tests/integration/test_auth_endpoints.py` (NEW)

**Implementation:**
```python
"""
Integration tests for authentication endpoints.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.database import User
from app.utils.auth import hash_password, create_session


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        username="testuser",
        password_hash=hash_password("testpassword123"),
        email="test@example.com"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_login_success(client: TestClient, test_user):
    """Test successful login."""
    response = client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "testpassword123"
        }
    )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert "token" in data
    assert len(data["token"]) == 64
    assert data["user"]["username"] == "testuser"
    assert data["user"]["email"] == "test@example.com"

    # Check cookie was set
    assert "session_token" in response.cookies


def test_login_invalid_username(client: TestClient):
    """Test login with invalid username."""
    response = client.post(
        "/auth/login",
        json={
            "username": "nonexistent",
            "password": "anypassword"
        }
    )

    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]


def test_login_invalid_password(client: TestClient, test_user):
    """Test login with invalid password."""
    response = client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]


def test_logout(client: TestClient, test_user, db_session):
    """Test logout."""
    # First login
    login_response = client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "testpassword123"
        }
    )
    assert login_response.status_code == 200

    # Now logout
    logout_response = client.post("/auth/logout")

    assert logout_response.status_code == 200
    assert logout_response.json()["success"] is True

    # Check cookie was cleared
    # (TestClient doesn't perfectly simulate cookie clearing, but we can check the response)


def test_get_me_authenticated(client: TestClient, test_user, db_session):
    """Test GET /auth/me with valid session."""
    # Create session
    session = create_session(db_session, str(test_user.id))

    # Request with cookie
    response = client.get(
        "/auth/me",
        cookies={"session_token": session.token}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == str(test_user.id)
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"


def test_get_me_with_header(client: TestClient, test_user, db_session):
    """Test GET /auth/me with Authorization header."""
    # Create session
    session = create_session(db_session, str(test_user.id))

    # Request with header
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {session.token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"


def test_get_me_unauthenticated(client: TestClient):
    """Test GET /auth/me without session."""
    response = client.get("/auth/me")

    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


def test_get_me_invalid_token(client: TestClient):
    """Test GET /auth/me with invalid token."""
    response = client.get(
        "/auth/me",
        cookies={"session_token": "invalid_token_123"}
    )

    assert response.status_code == 401
    assert "Invalid or expired session" in response.json()["detail"]
```

**Run tests:**
```bash
pytest tests/integration/test_auth_endpoints.py -v
```

**Acceptance Criteria:**
- [ ] All login tests pass
- [ ] All logout tests pass
- [ ] All /auth/me tests pass
- [ ] Cookie authentication works
- [ ] Header authentication works
- [ ] Invalid credentials return 401

---

### Task F2.7: Update documentation

**File:** `docs/api-endpoints.md`

**Add new section (after /generate endpoint):**

```markdown
## Authentication Endpoints

### POST /auth/login

Authenticate user with username and password.

**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "token": "64-char-hex-token",
  "user": {
    "id": "uuid",
    "username": "string",
    "email": "string|null",
    "created_at": "ISO-8601-timestamp"
  }
}
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Invalid username or password"
}
```

**Cookies Set:**
- `session_token` (httpOnly, 7 days expiration)

**Example:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "myuser", "password": "mypassword"}' \
  -c cookies.txt
```

---

### POST /auth/logout

Logout user by deleting session.

**Request:** None (uses session cookie)

**Response (200 OK):**
```json
{
  "success": true
}
```

**Cookies Cleared:**
- `session_token`

**Example:**
```bash
curl -X POST http://localhost:8000/auth/logout \
  -b cookies.txt
```

---

### GET /auth/me

Get current authenticated user information.

**Authentication:** Required (cookie or header)

**Response (200 OK):**
```json
{
  "id": "uuid",
  "username": "string",
  "email": "string|null",
  "created_at": "ISO-8601-timestamp"
}
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Not authenticated. Please log in."
}
```

**Example (with cookie):**
```bash
curl http://localhost:8000/auth/me \
  -b cookies.txt
```

**Example (with header):**
```bash
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer <token>"
```
```

**Acceptance Criteria:**
- [ ] All auth endpoints documented
- [ ] Request/response examples included
- [ ] Authentication requirements noted
- [ ] Cookie behavior documented

---

## Stage F3: Backend Protected Routes

### Task F3.1: Protect POST /generate endpoint

**File:** `app/api/routes.py`

**Changes:**
```python
from app.api.dependencies import get_current_user
from app.models.database import User

@router.post("/generate", response_model=GenerateResponse)
async def generate(
    request: GenerateRequest,
    current_user: User = Depends(get_current_user),  # NEW: Require auth
    db: Session = Depends(get_db)
):
    """
    Generate cat image based on repository analysis.

    **Authentication Required:** Yes (session cookie or Bearer token)

    Takes a GitHub repository URL, analyzes the code quality, and generates
    a cat image reflecting the analysis results. The generation is associated
    with the authenticated user.

    Args:
        request: GenerateRequest with github_url
        current_user: Authenticated user (from dependency)
        db: Database session

    Returns:
        GenerateResponse with analysis results and image data

    Raises:
        HTTPException: 401 (not authenticated), 403 (private repo),
                      404 (not found), 500 (analysis failed)
    """
    generation_id = str(uuid.uuid4())

    logger.info(
        f"Starting generation {generation_id} for {request.github_url} "
        f"(user: {current_user.username})"
    )

    try:
        # Create and invoke LangGraph workflow
        workflow = create_workflow()
        result = workflow.invoke({
            "github_url": request.github_url,
            "generation_id": generation_id,
            "user_id": str(current_user.id)  # NEW: Pass user_id to workflow
        })

        # ... rest of existing code ...
```

**File:** `app/langgraph/workflow.py`

**Update WorkflowState:**
```python
class WorkflowState(TypedDict):
    # Input
    github_url: str
    generation_id: str
    user_id: NotRequired[str]  # NEW: User ID for association

    # ... rest of existing fields ...
```

**Update save_to_db node:**
```python
def save_to_db(state: WorkflowState) -> Dict[str, Any]:
    """
    Save generation to database.

    Stores all analysis results, cat attributes, and image metadata.
    """
    session = SessionLocal()

    try:
        generation = Generation(
            id=state["generation_id"],
            github_url=state["github_url"],
            user_id=state.get("user_id"),  # NEW: Save user_id
            # ... rest of existing fields ...
        )

        session.add(generation)
        session.commit()

        logger.info(f"Generation {state['generation_id']} saved to database")

        return {}

    except Exception as e:
        logger.error(f"Failed to save generation: {str(e)}")
        session.rollback()
        return {"error": f"Failed to save to database: {str(e)}"}

    finally:
        session.close()
```

**Acceptance Criteria:**
- [ ] POST /generate requires authentication
- [ ] Returns 401 if not authenticated
- [ ] user_id is passed to workflow
- [ ] user_id is saved in database
- [ ] Existing tests updated
- [ ] New test for protected endpoint

---

### Task F3.2: Update workflow to save user_id

(Covered in Task F3.1 above)

**Additional testing:**

**File:** `tests/integration/test_generate_protected.py` (NEW)

```python
"""
Tests for protected /generate endpoint.
"""
import pytest
from fastapi.testclient import TestClient

from app.models.database import User
from app.utils.auth import hash_password, create_session


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        username="testuser",
        password_hash=hash_password("password123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_generate_without_auth(client: TestClient):
    """Test /generate without authentication."""
    response = client.post(
        "/generate",
        json={"github_url": "https://github.com/torvalds/linux"}
    )

    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


def test_generate_with_auth(client: TestClient, test_user, db_session, monkeypatch):
    """Test /generate with valid authentication."""
    # Create session
    session = create_session(db_session, str(test_user.id))

    # Mock the workflow to avoid actual API calls
    def mock_workflow_invoke(state):
        return {
            "metadata": {"name": "test", "owner": "test", "size_kb": 100},
            "analysis": {"code_quality_score": 7.5, "files_analyzed": [], "metrics": {}},
            "cat_attrs": {"size": "small", "age": "young", "expression": "happy"},
            "image": {"url": "/test.png", "binary": "test", "prompt": "test"},
            "story": "Test story",
            "meme_text_top": "TEST",
            "meme_text_bottom": "MEME"
        }

    # Mock workflow
    from app.langgraph import workflow
    monkeypatch.setattr(workflow, "create_workflow", lambda: type('obj', (object,), {
        'invoke': mock_workflow_invoke
    })())

    # Make request
    response = client.post(
        "/generate",
        json={"github_url": "https://github.com/test/repo"},
        cookies={"session_token": session.token}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    # Check generation was saved with user_id
    from app.models.database import Generation
    gen = db_session.query(Generation).filter_by(
        id=data["generation_id"]
    ).first()
    assert gen is not None
    assert gen.user_id == test_user.id
```

**Acceptance Criteria:**
- [ ] Test for unauthenticated request passes
- [ ] Test for authenticated request passes
- [ ] user_id is correctly saved in database

---

### Task F3.3: Create GET /generations endpoint

**File:** `app/api/routes.py`

**Add new endpoint:**
```python
from typing import List

@router.get("/generations")
async def list_generations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """
    List generations for the current user.

    **Authentication Required:** Yes

    Returns a list of generations created by the authenticated user,
    ordered by most recent first.

    Args:
        current_user: Authenticated user
        db: Database session
        limit: Maximum number of results (default 50, max 100)
        offset: Number of results to skip (for pagination)

    Returns:
        List of generation objects
    """
    # Validate limit
    if limit > 100:
        limit = 100

    # Query user's generations
    generations = (
        db.query(Generation)
        .filter(Generation.user_id == current_user.id)
        .order_by(Generation.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )

    # Convert to dict for response
    result = []
    for gen in generations:
        result.append({
            "id": str(gen.id),
            "github_url": gen.github_url,
            "repo_owner": gen.repo_owner,
            "repo_name": gen.repo_name,
            "primary_language": gen.primary_language,
            "code_quality_score": float(gen.code_quality_score) if gen.code_quality_score else None,
            "image_path": gen.image_path,
            "created_at": gen.created_at.isoformat() if gen.created_at else None
        })

    return {
        "success": True,
        "count": len(result),
        "generations": result
    }
```

**File:** `app/api/schemas.py`

**Add response schema:**
```python
class GenerationListItem(BaseModel):
    """Single generation in list response."""
    id: str = Field(..., description="Generation ID")
    github_url: str = Field(..., description="GitHub repository URL")
    repo_owner: Optional[str] = Field(None, description="Repository owner")
    repo_name: Optional[str] = Field(None, description="Repository name")
    primary_language: Optional[str] = Field(None, description="Primary language")
    code_quality_score: Optional[float] = Field(None, description="Quality score")
    image_path: Optional[str] = Field(None, description="Path to generated image")
    created_at: Optional[str] = Field(None, description="Creation timestamp")


class GenerationListResponse(BaseModel):
    """Response for GET /generations."""
    success: bool = Field(..., description="Request success status")
    count: int = Field(..., description="Number of generations returned")
    generations: List[GenerationListItem] = Field(..., description="List of generations")
```

**Testing:**

**File:** `tests/integration/test_generations_list.py` (NEW)

```python
"""
Tests for GET /generations endpoint.
"""
import pytest
from fastapi.testclient import TestClient

from app.models.database import User, Generation
from app.utils.auth import hash_password, create_session


@pytest.fixture
def test_user(db_session):
    """Create a test user with some generations."""
    user = User(
        username="testuser",
        password_hash=hash_password("password123")
    )
    db_session.add(user)
    db_session.commit()

    # Create test generations
    for i in range(3):
        gen = Generation(
            github_url=f"https://github.com/test/repo{i}",
            repo_owner="test",
            repo_name=f"repo{i}",
            primary_language="Python",
            code_quality_score=7.5 + i,
            user_id=user.id
        )
        db_session.add(gen)

    db_session.commit()
    db_session.refresh(user)
    return user


def test_list_generations_authenticated(client: TestClient, test_user, db_session):
    """Test listing generations with authentication."""
    # Create session
    session = create_session(db_session, str(test_user.id))

    # Request generations
    response = client.get(
        "/generations",
        cookies={"session_token": session.token}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["count"] == 3
    assert len(data["generations"]) == 3

    # Check first generation
    gen = data["generations"][0]
    assert "id" in gen
    assert "github_url" in gen
    assert "repo_name" in gen
    assert "code_quality_score" in gen


def test_list_generations_unauthenticated(client: TestClient):
    """Test listing generations without authentication."""
    response = client.get("/generations")

    assert response.status_code == 401


def test_list_generations_pagination(client: TestClient, test_user, db_session):
    """Test pagination with limit and offset."""
    # Create session
    session = create_session(db_session, str(test_user.id))

    # Request with limit
    response = client.get(
        "/generations?limit=2&offset=0",
        cookies={"session_token": session.token}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2

    # Request with offset
    response = client.get(
        "/generations?limit=2&offset=2",
        cookies={"session_token": session.token}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1  # Only 1 remaining
```

**Acceptance Criteria:**
- [ ] GET /generations endpoint created
- [ ] Requires authentication
- [ ] Returns only current user's generations
- [ ] Ordered by created_at DESC
- [ ] Pagination works (limit, offset)
- [ ] All tests pass

---

### Task F3.4: Create GET /generation/:id endpoint

**File:** `app/api/routes.py`

**Add new endpoint:**
```python
@router.get("/generation/{generation_id}")
async def get_generation(
    generation_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a single generation by ID.

    **Authentication Required:** No (public endpoint for shareable links)

    Returns full generation details including image and analysis.
    If the generation is still processing, returns status "processing".

    Args:
        generation_id: Generation UUID
        db: Database session

    Returns:
        Generation object with full details

    Raises:
        HTTPException 404: Generation not found
    """
    # Query generation
    generation = db.query(Generation).filter(Generation.id == generation_id).first()

    if not generation:
        raise HTTPException(
            status_code=404,
            detail=f"Generation {generation_id} not found"
        )

    # Determine status
    status = "completed" if generation.image_path else "processing"

    # Build response
    return {
        "success": True,
        "status": status,
        "generation": {
            "id": str(generation.id),
            "github_url": generation.github_url,
            "repository": {
                "owner": generation.repo_owner,
                "name": generation.repo_name,
                "primary_language": generation.primary_language,
                "size_kb": generation.repo_size_kb
            },
            "analysis": {
                "code_quality_score": float(generation.code_quality_score) if generation.code_quality_score else None,
                "data": generation.analysis_data
            },
            "cat_attributes": generation.cat_attributes,
            "story": generation.story,
            "meme_text": {
                "top": generation.meme_text_top,
                "bottom": generation.meme_text_bottom
            } if generation.meme_text_top else None,
            "image": {
                "path": generation.image_path,
                "prompt": generation.image_prompt
            } if generation.image_path else None,
            "created_at": generation.created_at.isoformat() if generation.created_at else None
        }
    }
```

**File:** `app/api/schemas.py`

**Add response schema:**
```python
class GenerationDetailResponse(BaseModel):
    """Response for GET /generation/:id."""
    success: bool = Field(..., description="Request success")
    status: str = Field(..., description="Generation status: processing or completed")
    generation: Dict[str, Any] = Field(..., description="Full generation details")
```

**Testing:**

**File:** `tests/integration/test_generation_detail.py` (NEW)

```python
"""
Tests for GET /generation/:id endpoint.
"""
import pytest
from fastapi.testclient import TestClient

from app.models.database import Generation


@pytest.fixture
def test_generation(db_session):
    """Create a test generation."""
    gen = Generation(
        github_url="https://github.com/test/repo",
        repo_owner="test",
        repo_name="repo",
        primary_language="Python",
        code_quality_score=8.5,
        cat_attributes={"size": "small", "age": "young"},
        story="Test story",
        meme_text_top="TEST",
        meme_text_bottom="MEME",
        image_path="/test/image.png",
        image_prompt="Test prompt"
    )
    db_session.add(gen)
    db_session.commit()
    db_session.refresh(gen)
    return gen


def test_get_generation_found(client: TestClient, test_generation):
    """Test getting an existing generation."""
    response = client.get(f"/generation/{test_generation.id}")

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["status"] == "completed"
    assert data["generation"]["id"] == str(test_generation.id)
    assert data["generation"]["github_url"] == "https://github.com/test/repo"
    assert data["generation"]["story"] == "Test story"
    assert data["generation"]["meme_text"]["top"] == "TEST"


def test_get_generation_not_found(client: TestClient):
    """Test getting a non-existent generation."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/generation/{fake_id}")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_get_generation_processing(client: TestClient, db_session):
    """Test getting a generation that's still processing."""
    gen = Generation(
        github_url="https://github.com/test/processing",
        repo_owner="test",
        repo_name="processing",
        # No image_path = still processing
    )
    db_session.add(gen)
    db_session.commit()
    db_session.refresh(gen)

    response = client.get(f"/generation/{gen.id}")

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["status"] == "processing"
    assert data["generation"]["image"] is None
```

**Acceptance Criteria:**
- [ ] GET /generation/:id endpoint created
- [ ] Public endpoint (no auth required)
- [ ] Returns 404 for missing generation
- [ ] Returns "processing" status if image_path is null
- [ ] Returns "completed" status if image_path exists
- [ ] All tests pass

---

### Task F3.5: Write tests for protected routes

(Tests covered in tasks above)

**Run all tests:**
```bash
# Run all integration tests
pytest tests/integration/ -v

# Check coverage
pytest tests/integration/ -v --cov=app.api --cov-report=term
```

**Acceptance Criteria:**
- [ ] All auth endpoint tests pass
- [ ] All protected route tests pass
- [ ] All generation endpoint tests pass
- [ ] Coverage > 80%

---

### Task F3.6: Update documentation

**File:** `docs/api-endpoints.md`

**Add new sections:**

```markdown
## Protected Endpoints

The following endpoints require authentication via session cookie or Bearer token.

### POST /generate

**Authentication:** Required

(Update existing /generate documentation to note authentication requirement)

---

### GET /generations

List all generations for the authenticated user.

**Authentication:** Required

**Query Parameters:**
- `limit` (optional): Maximum results (default 50, max 100)
- `offset` (optional): Pagination offset (default 0)

**Response (200 OK):**
```json
{
  "success": true,
  "count": 3,
  "generations": [
    {
      "id": "uuid",
      "github_url": "https://github.com/owner/repo",
      "repo_owner": "owner",
      "repo_name": "repo",
      "primary_language": "Python",
      "code_quality_score": 8.5,
      "image_path": "/generated_images/uuid.png",
      "created_at": "2025-10-14T12:00:00Z"
    }
  ]
}
```

**Example:**
```bash
curl http://localhost:8000/generations \
  -H "Authorization: Bearer <token>"
```

---

## Public Endpoints

### GET /generation/:id

Get a single generation by ID.

**Authentication:** Not required (public shareable link)

**Path Parameters:**
- `generation_id`: Generation UUID

**Response (200 OK) - Completed:**
```json
{
  "success": true,
  "status": "completed",
  "generation": {
    "id": "uuid",
    "github_url": "https://github.com/owner/repo",
    "repository": { ... },
    "analysis": { ... },
    "cat_attributes": { ... },
    "story": "...",
    "meme_text": { "top": "...", "bottom": "..." },
    "image": { "path": "...", "prompt": "..." },
    "created_at": "..."
  }
}
```

**Response (200 OK) - Processing:**
```json
{
  "success": true,
  "status": "processing",
  "generation": {
    "id": "uuid",
    "github_url": "...",
    "image": null,
    ...
  }
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Generation <id> not found"
}
```

**Example:**
```bash
curl http://localhost:8000/generation/550e8400-e29b-41d4-a716-446655440000
```

**Use Case:** Share generation results publicly via direct link
```

**Acceptance Criteria:**
- [ ] All new endpoints documented
- [ ] Authentication requirements noted
- [ ] Query parameters documented
- [ ] Response examples included
- [ ] Use cases explained

---

## Stage F4: Astro Project Setup

### Task F4.1: Initialize Astro project

**Commands:**
```bash
# From project root
npm create astro@latest frontend -- --template minimal --typescript strict --no-git

# Answer prompts:
# - Where should we create your new project? → frontend
# - How would you like to start your new project? → Empty
# - Do you plan to write TypeScript? → Yes (strict)
# - Install dependencies? → Yes
# - Initialize a new git repository? → No (already in repo)

cd frontend

# Verify installation
npm run dev
# Should start on http://localhost:4321
```

**Verify structure:**
```
frontend/
├── src/
│   └── pages/
│       └── index.astro
├── public/
├── astro.config.mjs
├── package.json
├── tsconfig.json
└── README.md
```

**Acceptance Criteria:**
- [ ] Astro project created in frontend/ directory
- [ ] TypeScript configured (strict mode)
- [ ] Dev server runs successfully
- [ ] No errors in console

---

### Task F4.2: Install dependencies

**Commands:**
```bash
cd frontend

# Install SSR adapter
npm install @astrojs/node

# Install Tailwind
npm install @astrojs/tailwind tailwindcss

# Install cookie parsing (for session management)
npm install cookie

# Install development dependencies
npm install -D @types/cookie
```

**Update package.json scripts:**
```json
{
  "scripts": {
    "dev": "astro dev --port 4321",
    "build": "astro check && astro build",
    "preview": "astro preview",
    "astro": "astro"
  }
}
```

**Acceptance Criteria:**
- [ ] All dependencies installed
- [ ] No vulnerability warnings (or resolved)
- [ ] package.json updated
- [ ] node_modules populated

---

### Task F4.3: Configure SSR and Tailwind

**File:** `frontend/astro.config.mjs`

**Update configuration:**
```javascript
import { defineConfig } from 'astro/config';
import node from '@astrojs/node';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  output: 'server',  // Enable SSR
  adapter: node({
    mode: 'standalone'
  }),
  integrations: [tailwind()],
  server: {
    port: 4321,
    host: true
  },
  // API proxy (optional, for development)
  vite: {
    server: {
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, '')
        }
      }
    }
  }
});
```

**File:** `frontend/tailwind.config.mjs` (NEW)

**Create Tailwind config:**
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        'oxide-dark': '#0a0a0a',
        'oxide-darker': '#050505',
        'oxide-gray': '#1a1a1a',
        'oxide-gray-light': '#2a2a2a',
        'oxide-green': '#00ffa3',
        'oxide-green-dim': '#00cc82',
        'oxide-green-darker': '#009966',
        'oxide-text': '#e5e5e5',
        'oxide-text-dim': '#999999',
        'oxide-text-darker': '#666666',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      maxWidth: {
        'container': '1200px',
      }
    },
  },
  plugins: [],
}
```

**Test SSR:**
```bash
npm run dev
# Visit http://localhost:4321
# Should see default Astro page
```

**Acceptance Criteria:**
- [ ] astro.config.mjs configured for SSR
- [ ] Node adapter installed
- [ ] Tailwind configured with Oxide colors
- [ ] Dev server runs on port 4321
- [ ] SSR mode active (output: 'server')

---

### Task F4.4: Create project structure

**Commands:**
```bash
cd frontend/src

# Create directories
mkdir -p pages/generation
mkdir -p components
mkdir -p lib
mkdir -p styles

# Create placeholder files
touch components/Layout.astro
touch components/Header.astro
touch components/LoginForm.astro
touch components/GenerateForm.astro
touch components/GenerationCard.astro
touch components/GenerationList.astro
touch lib/api.ts
touch lib/auth.ts
touch styles/global.css
touch middleware.ts
```

**Final structure:**
```
frontend/src/
├── pages/
│   ├── index.astro
│   ├── login.astro
│   └── generation/
│       └── [id].astro
├── components/
│   ├── Layout.astro
│   ├── Header.astro
│   ├── LoginForm.astro
│   ├── GenerateForm.astro
│   ├── GenerationCard.astro
│   └── GenerationList.astro
├── lib/
│   ├── api.ts
│   └── auth.ts
├── styles/
│   └── global.css
└── middleware.ts
```

**Acceptance Criteria:**
- [ ] All directories created
- [ ] All placeholder files created
- [ ] Structure matches plan
- [ ] No errors in VS Code/IDE

---

### Task F4.5: Set up environment variables

**File:** `frontend/.env` (NEW)

**Create environment file:**
```bash
# API Configuration
PUBLIC_API_URL=http://localhost:8000
API_URL=http://localhost:8000

# Session Secret (generate with: openssl rand -hex 32)
SESSION_SECRET=your-secret-key-here-generate-with-openssl

# Environment
NODE_ENV=development
```

**File:** `frontend/.env.example` (NEW)

**Create example file:**
```bash
# API Configuration
PUBLIC_API_URL=http://localhost:8000
API_URL=http://localhost:8000

# Session Secret (generate with: openssl rand -hex 32)
SESSION_SECRET=generate-your-own-secret-key

# Environment
NODE_ENV=development
```

**Add to `.gitignore`:**
```bash
# In main .gitignore, add:
frontend/.env
frontend/node_modules/
frontend/dist/
frontend/.astro/
```

**Generate session secret:**
```bash
openssl rand -hex 32
# Copy output to .env SESSION_SECRET
```

**File:** `frontend/src/env.d.ts` (NEW)

**TypeScript environment types:**
```typescript
/// <reference types="astro/client" />

interface ImportMetaEnv {
  readonly PUBLIC_API_URL: string;
  readonly API_URL: string;
  readonly SESSION_SECRET: string;
  readonly NODE_ENV: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
```

**Acceptance Criteria:**
- [ ] .env file created with secrets
- [ ] .env.example created for reference
- [ ] .gitignore updated
- [ ] SESSION_SECRET generated
- [ ] TypeScript types defined

---

### Task F4.6: Create documentation

**File:** `docs/frontend-guide.md` (NEW)

**Create comprehensive guide:**
```markdown
# Frontend Development Guide

**Framework:** Astro 4.x with SSR
**Styling:** Tailwind CSS (Oxide-inspired)
**Port:** 4321
**Last Updated:** 2025-10-14

---

## Quick Start

### Installation

```bash
# From project root
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Visit: http://localhost:4321

---

## Project Structure

```
frontend/
├── src/
│   ├── pages/            # Routes (file-based routing)
│   │   ├── login.astro         # /login
│   │   ├── index.astro         # / (dashboard)
│   │   └── generation/
│   │       └── [id].astro      # /generation/:id
│   ├── components/       # Reusable components
│   │   ├── Layout.astro        # Base layout
│   │   ├── Header.astro        # Navigation header
│   │   ├── LoginForm.astro     # Login form
│   │   ├── GenerateForm.astro  # Generation form with polling
│   │   ├── GenerationCard.astro # Card for grid
│   │   └── GenerationList.astro # Grid of generations
│   ├── lib/              # Utility libraries
│   │   ├── api.ts              # API client
│   │   └── auth.ts             # Auth helpers
│   ├── styles/           # Global styles
│   │   └── global.css          # Oxide theme
│   └── middleware.ts     # Auth middleware
├── public/               # Static assets
├── astro.config.mjs      # Astro configuration
├── tailwind.config.mjs   # Tailwind configuration
├── .env                  # Environment variables (not committed)
└── package.json
```

---

## Development Commands

```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type check
npm run astro check
```

---

## Configuration

### Environment Variables

**File:** `frontend/.env`

```bash
PUBLIC_API_URL=http://localhost:8000  # Public API URL (client-side)
API_URL=http://localhost:8000          # Server-side API URL
SESSION_SECRET=<64-char-hex>           # Session encryption secret
NODE_ENV=development                   # Environment
```

**Generate SESSION_SECRET:**
```bash
openssl rand -hex 32
```

### API Proxy (Optional)

Configured in `astro.config.mjs`:

```javascript
vite: {
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
}
```

---

## Routing

Astro uses file-based routing:

| File | Route | Auth | Description |
|------|-------|------|-------------|
| `pages/login.astro` | `/login` | Public | Login page |
| `pages/index.astro` | `/` | Protected | Dashboard |
| `pages/generation/[id].astro` | `/generation/:id` | Public | Detail view |

**Dynamic routes:** Use `[param].astro` syntax

---

## Authentication

### Session Flow

1. User submits login form → POST `/auth/login` (FastAPI)
2. FastAPI validates credentials → returns session token
3. Astro sets httpOnly cookie with token
4. All requests include cookie automatically
5. Middleware validates session on protected routes

### Auth Middleware

**File:** `src/middleware.ts`

Runs on every request before page renders. Checks authentication for protected routes.

**Protected routes:**
- `/` (dashboard)
- Any route except `/login` and `/generation/:id`

**Public routes:**
- `/login`
- `/generation/:id` (shareable links)

### Auth Helpers

**File:** `src/lib/auth.ts`

- `getSession()` - Get current user from session
- `requireAuth()` - Throw redirect if not logged in
- `setSessionCookie()` - Set session cookie
- `clearSessionCookie()` - Clear session cookie

---

## API Integration

### API Client

**File:** `src/lib/api.ts`

Provides typed functions for all backend endpoints:

```typescript
// Authentication
await api.login(username, password)
await api.logout()
await api.getMe()

// Generations
await api.generate(githubUrl)
await api.getGenerations(limit, offset)
await api.getGeneration(id)
```

### Usage Example

```astro
---
import { api } from '../lib/api';

const generations = await api.getGenerations(50, 0);
---

<div>
  {generations.map(gen => (
    <div>{gen.repo_name}</div>
  ))}
</div>
```

---

## Styling

### Design System

**Inspiration:** [Oxide Computer](https://oxide.computer/)

**Colors:**
- Background: `#0a0a0a` (oxide-dark)
- Cards: `#1a1a1a` (oxide-gray)
- Accent: `#00ffa3` (oxide-green)
- Text: `#e5e5e5` (oxide-text)

**Typography:**
- Font: Inter
- Base size: 16px
- Headings: 24px, 32px, 48px

### Tailwind Classes

```html
<!-- Background -->
<div class="bg-oxide-dark">

<!-- Card -->
<div class="bg-oxide-gray rounded-lg p-6 hover:border-oxide-green">

<!-- Button -->
<button class="bg-oxide-green text-oxide-dark hover:bg-oxide-green-dim">

<!-- Text -->
<p class="text-oxide-text">
<p class="text-oxide-text-dim">
```

### Global Styles

**File:** `src/styles/global.css`

Applied in Layout component:
```astro
<style is:global>
  @import '../styles/global.css';
</style>
```

---

## Components

### Layout

**File:** `src/components/Layout.astro`

Base layout for all pages. Includes:
- HTML structure
- Global styles
- Header (if authenticated)
- Footer

### Header

**File:** `src/components/Header.astro`

Navigation header with:
- Logo/title
- User info
- Logout button

### GenerateForm

**File:** `src/components/GenerateForm.astro`

Form with client-side polling:
1. Submit GitHub URL
2. POST to `/generate`
3. Get generation_id
4. Poll `/generation/:id` every 2 seconds
5. Redirect when status = "completed"

### GenerationCard

**File:** `src/components/GenerationCard.astro`

Displays:
- Thumbnail image (150x150)
- Repo name + owner
- Quality score badge
- Link to detail page

### GenerationList

**File:** `src/components/GenerationList.astro`

Grid layout:
- 3 columns on desktop
- 2 columns on tablet
- 1 column on mobile

---

## Testing

### Manual Testing Checklist

**Authentication:**
- [ ] Can log in with valid credentials
- [ ] Cannot log in with invalid credentials
- [ ] Redirected to login when accessing dashboard without auth
- [ ] Can log out successfully
- [ ] Session persists across page reloads

**Generation:**
- [ ] Can submit GitHub URL
- [ ] Loading spinner shows during processing
- [ ] Redirected to detail page when complete
- [ ] Generation appears in list on dashboard

**Public Links:**
- [ ] Can access generation detail without auth
- [ ] Shareable links work

**Responsive Design:**
- [ ] Mobile layout works
- [ ] Tablet layout works
- [ ] Desktop layout works

---

## Troubleshooting

### Port Already in Use

```bash
# Kill process on port 4321
lsof -ti:4321 | xargs kill -9

# Or change port in astro.config.mjs
```

### API Connection Refused

Check:
1. FastAPI is running on port 8000
2. `API_URL` in `.env` is correct
3. CORS is configured in FastAPI

### Session Not Persisting

Check:
1. `SESSION_SECRET` is set in `.env`
2. Cookie is httpOnly
3. Cookie domain matches (localhost)

### TypeScript Errors

```bash
# Run type check
npm run astro check

# Restart TypeScript server in VS Code
Cmd+Shift+P → "TypeScript: Restart TS Server"
```

---

## Resources

- [Astro Documentation](https://docs.astro.build/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Oxide Computer (Design Inspiration)](https://oxide.computer/)
- Backend API: http://localhost:8000/docs

---

**Next Steps:** See [HANDOFF_FRONT.md](../HANDOFF_FRONT.md) for implementation checklist
```

**Acceptance Criteria:**
- [ ] docs/frontend-guide.md created
- [ ] All sections complete
- [ ] Examples included
- [ ] Troubleshooting section added
- [ ] Linked from HANDOFF_FRONT.md

---

## Manual Testing Checklist

Run these tests after each major stage:

### Authentication Tests
- [ ] Can create user in database manually (see below)
- [ ] Can log in with correct username/password
- [ ] Cannot log in with wrong password
- [ ] Cannot log in with non-existent username
- [ ] Session cookie is set after login
- [ ] Can access dashboard after login
- [ ] Cannot access dashboard without login
- [ ] Can log out successfully
- [ ] Session cookie is cleared after logout
- [ ] Session expires after 7 days (hard to test, check DB)

### Generation Tests
- [ ] Can submit GitHub URL from dashboard
- [ ] Loading spinner shows during generation
- [ ] Polling works (checks status every 2s)
- [ ] Redirected to detail page when complete
- [ ] Generation shows in list on dashboard
- [ ] Can click card to view detail
- [ ] Detail page shows full image
- [ ] Detail page shows story
- [ ] Detail page shows repo data

### Public Link Tests
- [ ] Can access /generation/:id without login
- [ ] Shareable link works in incognito mode
- [ ] Processing status shows if not complete

### Design Tests
- [ ] Dark theme matches Oxide style
- [ ] Green accents visible on hover
- [ ] Responsive on mobile (< 768px)
- [ ] Responsive on tablet (768-1024px)
- [ ] Responsive on desktop (> 1024px)
- [ ] Animations smooth
- [ ] No layout shift

---

## Creating Test User

**SQL command:**
```sql
-- Connect to database
psql postgresql://repo_user:repo_password@localhost:5434/repo_to_cat

-- Create user (run in Python first to hash password)
INSERT INTO users (id, username, password_hash, email, created_at, updated_at)
VALUES (
  gen_random_uuid(),
  'testuser',
  '<bcrypt-hash-here>',
  'test@example.com',
  NOW(),
  NOW()
);
```

**Or use Python:**
```python
from app.models.database import User
from app.utils.auth import hash_password
from app.core.database import SessionLocal

db = SessionLocal()

user = User(
    username="testuser",
    password_hash=hash_password("testpassword123"),
    email="test@example.com"
)

db.add(user)
db.commit()
db.close()

print(f"User created: {user.username}")
```

---

## Development Workflow

### Daily Workflow

1. **Start services:**
   ```bash
   # Terminal 1: Backend
   cd /path/to/repo-to-cat
   docker compose up -d postgres
   uvicorn app.main:app --reload --port 8000

   # Terminal 2: Frontend
   cd /path/to/repo-to-cat/frontend
   npm run dev
   ```

2. **Work on one task from HANDOFF_FRONT.md**
3. **Test changes manually**
4. **Write/update tests**
5. **Mark checkbox complete**
6. **Commit changes** (following LL-GIT-001)

### Before Each Stage

1. [ ] Check current stage in HANDOFF_FRONT.md
2. [ ] Read task descriptions
3. [ ] Review acceptance criteria
4. [ ] Plan implementation

### After Each Stage

1. [ ] Run all tests
2. [ ] Update documentation
3. [ ] Manual testing from checklist
4. [ ] Mark stage complete in HANDOFF_FRONT.md
5. [ ] Commit with clean message

---

## Notes

- **Work incrementally:** One checkbox at a time
- **Test frequently:** After each component
- **Document as you go:** Update docs after each stage
- **Ask for approval:** Before moving to next stage
- **Follow TDD:** Tests before/alongside implementation
- **Clean commits:** No AI branding (LL-GIT-001)

---

## Changelog

### 2025-10-14 - Stage F1 Complete ✅

**Commit:** `7d8648b` - Stage F1: Database schema for authentication

**Completed Tasks:**
- ✅ F1.1: Updated User model with password_hash and email fields
- ✅ F1.2: Created Session model for authentication tokens
- ✅ F1.3: Added user_id foreign key to Generation model
- ✅ F1.4: Created Alembic migration (1052d2e36053)
- ✅ F1.5: Wrote comprehensive unit tests (13/13 passing)
- ✅ F1.6: Updated docs/database-guide.md with auth schema
- ✅ F1.7: Committed all changes with clean message

**Database Changes:**
- `users` table: Added password_hash (NOT NULL), email (UNIQUE)
- `sessions` table: Created with user_id FK, token, expires_at
- `generations` table: Added user_id FK (nullable)
- All relationships configured (User ↔ Session, User ↔ Generation)
- Indexes created for performance

**Tests:** 13/13 passing ✅
- All database models tested
- Relationships verified
- Cascade delete confirmed

**Documentation:**
- Updated database-guide.md with complete auth schema
- Created HANDOFF_FRONT.md (4000+ lines implementation guide)
- Created INIT_FRONT_PROMPT.md (context restoration guide)

**Next:** Stage F2 - Backend Authentication Endpoints

---

**Last Updated:** 2025-10-14
**Status:** Stage F1 Complete ✅, Stage F2 Starting
**Next Task:** F2.1 - Create app/utils/auth.py (bcrypt utilities)
