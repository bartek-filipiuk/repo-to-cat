"""
Authentication utilities for password hashing and session management.

This module provides bcrypt password hashing, session token generation,
and session validation functions for the authentication system.
"""
import secrets
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from sqlalchemy.orm import Session as DBSession

from app.models.database import User, Session


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        str: Bcrypt hashed password (60 characters)

    Example:
        >>> hashed = hash_password("my_secure_password")
        >>> len(hashed)
        60
    """
    # Generate salt and hash password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a bcrypt hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt hash to compare against

    Returns:
        bool: True if password matches, False otherwise

    Example:
        >>> hashed = hash_password("my_password")
        >>> verify_password("my_password", hashed)
        True
        >>> verify_password("wrong_password", hashed)
        False
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except (ValueError, AttributeError):
        return False


def create_session_token() -> str:
    """
    Generate a secure random session token.

    Returns:
        str: 64-character hexadecimal token

    Example:
        >>> token = create_session_token()
        >>> len(token)
        64
        >>> all(c in '0123456789abcdef' for c in token)
        True
    """
    return secrets.token_hex(32)  # 32 bytes = 64 hex characters


def create_session(
    db: DBSession,
    user_id: str,
    expires_in_days: int = 7
) -> Session:
    """
    Create a new session in the database.

    Args:
        db: Database session
        user_id: UUID of the user
        expires_in_days: Number of days until session expires (default: 7)

    Returns:
        Session: Created session object with token and expiration

    Raises:
        ValueError: If user_id is invalid or user doesn't exist

    Example:
        >>> session = create_session(db, user.id)
        >>> session.token  # 64-char hex token
        >>> session.expires_at  # 7 days from now
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"User with id {user_id} not found")

    # Generate token and expiration
    token = create_session_token()
    expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

    # Create session
    session = Session(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


def verify_session_token(db: DBSession, token: str) -> Optional[User]:
    """
    Verify a session token and return the associated user.

    Args:
        db: Database session
        token: Session token to verify

    Returns:
        User: User object if token is valid and not expired
        None: If token is invalid or expired

    Example:
        >>> user = verify_session_token(db, "abc123...")
        >>> if user:
        ...     print(f"Valid session for {user.username}")
        ... else:
        ...     print("Invalid or expired session")
    """
    # Find session by token
    session = db.query(Session).filter(Session.token == token).first()

    if not session:
        return None

    # Check if session is expired
    if session.expires_at < datetime.utcnow():
        # Delete expired session
        db.delete(session)
        db.commit()
        return None

    # Return associated user
    return session.user


def delete_session(db: DBSession, token: str) -> bool:
    """
    Delete a session from the database (logout).

    Args:
        db: Database session
        token: Session token to delete

    Returns:
        bool: True if session was deleted, False if not found

    Example:
        >>> success = delete_session(db, "abc123...")
        >>> if success:
        ...     print("Logged out successfully")
    """
    session = db.query(Session).filter(Session.token == token).first()

    if not session:
        return False

    db.delete(session)
    db.commit()
    return True


def cleanup_expired_sessions(db: DBSession) -> int:
    """
    Delete all expired sessions from the database.

    This is a maintenance function that should be run periodically
    (e.g., via cron job or scheduled task).

    Args:
        db: Database session

    Returns:
        int: Number of sessions deleted

    Example:
        >>> deleted = cleanup_expired_sessions(db)
        >>> print(f"Cleaned up {deleted} expired sessions")
    """
    expired_sessions = db.query(Session).filter(
        Session.expires_at < datetime.utcnow()
    ).all()

    count = len(expired_sessions)

    for session in expired_sessions:
        db.delete(session)

    db.commit()
    return count
