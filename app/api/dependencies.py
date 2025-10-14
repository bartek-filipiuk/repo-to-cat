"""
FastAPI dependencies for authentication.

This module provides dependency functions for protected routes and optional
authentication in FastAPI endpoints.
"""
from typing import Optional

from fastapi import Cookie, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.database import User
from app.utils.auth import verify_session_token


def get_current_user(
    session_token: Optional[str] = Cookie(None, alias="session_token"),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the currently authenticated user.

    Reads the session token from the 'session_token' cookie, verifies it,
    and returns the associated user. Raises 401 if not authenticated.

    Args:
        session_token: Session token from cookie
        db: Database session (injected by FastAPI)

    Returns:
        User: The authenticated user

    Raises:
        HTTPException: 401 if token is missing, invalid, or expired

    Usage:
        @app.get("/protected")
        def protected_route(user: User = Depends(get_current_user)):
            return {"username": user.username}
    """
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please log in.",
            headers={"WWW-Authenticate": "Cookie"}
        )

    user = verify_session_token(db, session_token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session. Please log in again.",
            headers={"WWW-Authenticate": "Cookie"}
        )

    return user


def get_optional_user(
    session_token: Optional[str] = Cookie(None, alias="session_token"),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency to get the currently authenticated user (optional).

    Similar to get_current_user, but returns None if not authenticated
    instead of raising an exception. Useful for routes that behave
    differently based on authentication status.

    Args:
        session_token: Session token from cookie
        db: Database session (injected by FastAPI)

    Returns:
        User: The authenticated user if session is valid
        None: If not authenticated or session is invalid/expired

    Usage:
        @app.get("/public-or-private")
        def mixed_route(user: Optional[User] = Depends(get_optional_user)):
            if user:
                return {"message": f"Hello {user.username}"}
            else:
                return {"message": "Hello guest"}
    """
    if not session_token:
        return None

    user = verify_session_token(db, session_token)
    return user
