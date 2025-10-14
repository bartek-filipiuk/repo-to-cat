"""
Authentication API endpoints.

Implements login, logout, and user session management.
"""
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Depends, Response, Cookie
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.database import User
from app.api.schemas import (
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    UserResponse,
    ErrorResponse
)
from app.api.dependencies import get_current_user, get_optional_user
from app.utils.auth import (
    verify_password,
    create_session,
    delete_session
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Login successful, session cookie set"},
        401: {
            "description": "Authentication failed",
            "model": ErrorResponse
        }
    }
)
def login(
    credentials: LoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Login endpoint - authenticate user and create session.

    Validates username/password, creates a session, and sets an httpOnly
    cookie with the session token.

    **Cookie Details:**
    - Name: `session_token`
    - httpOnly: true (prevents XSS attacks)
    - secure: false (development), true (production)
    - sameSite: "lax" (CSRF protection)
    - maxAge: 604800 seconds (7 days)

    **Args:**
    - `username`: User's username
    - `password`: User's password

    **Returns:**
    - User information
    - Sets `session_token` cookie

    **Errors:**
    - 401: Invalid username or password
    """
    # Find user by username
    user = db.query(User).filter(User.username == credentials.username).first()

    if not user:
        logger.warning(f"Login attempt with non-existent username: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        logger.warning(f"Failed login attempt for user: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Create session (7-day expiration)
    session = create_session(db, str(user.id), expires_in_days=7)

    # Set httpOnly cookie with session token
    response.set_cookie(
        key="session_token",
        value=session.token,
        httponly=True,  # Prevent XSS
        secure=False,   # Set to True in production with HTTPS
        samesite="lax", # CSRF protection
        max_age=604800  # 7 days in seconds
    )

    logger.info(f"User logged in successfully: {user.username}")

    # Return user data (no sensitive fields)
    return LoginResponse(
        success=True,
        message="Login successful",
        user=UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            created_at=user.created_at
        )
    )


@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Logout successful"}
    }
)
def logout(
    response: Response,
    session_token: Optional[str] = Cookie(None, alias="session_token"),
    db: Session = Depends(get_db)
):
    """
    Logout endpoint - delete session and clear cookie.

    Removes the session from the database and clears the session cookie.
    This endpoint is idempotent - it always succeeds even if no session exists.

    **Returns:**
    - Success message
    - Clears `session_token` cookie

    **Note:**
    - Always returns 200, even if not authenticated
    - Logout is an idempotent operation
    """
    # Clear cookie regardless of session existence
    response.delete_cookie(key="session_token")

    # Delete session from database if token provided
    if session_token:
        deleted = delete_session(db, session_token)
        if deleted:
            logger.info("User logged out successfully")
        else:
            logger.info("Logout attempted with invalid/expired session")
    else:
        logger.info("Logout attempted with no session token")

    return LogoutResponse(
        success=True,
        message="Logged out successfully"
    )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Current user information"},
        401: {
            "description": "Not authenticated",
            "model": ErrorResponse
        }
    }
)
def get_current_user_info(
    user: User = Depends(get_current_user)
):
    """
    Get current user information.

    Returns the authenticated user's information based on the session cookie.

    **Returns:**
    - Current user information (id, username, email, created_at)

    **Errors:**
    - 401: Not authenticated or session expired

    **Note:**
    - This endpoint requires authentication (session cookie must be present and valid)
    """
    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        created_at=user.created_at
    )


# ============================================================================
# OPTIONAL: Test endpoint to check session status without requiring auth
# ============================================================================

@router.get(
    "/status",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    include_in_schema=True
)
def check_auth_status(
    user: Optional[User] = Depends(get_optional_user)
):
    """
    Check authentication status (optional auth).

    Returns whether the user is authenticated and their username if logged in.
    This endpoint does not require authentication.

    **Returns:**
    - `authenticated`: boolean
    - `username`: string (if authenticated) or null

    **Example Response (authenticated):**
    ```json
    {
        "authenticated": true,
        "username": "testuser"
    }
    ```

    **Example Response (not authenticated):**
    ```json
    {
        "authenticated": false,
        "username": null
    }
    ```
    """
    if user:
        return {
            "authenticated": True,
            "username": user.username
        }
    else:
        return {
            "authenticated": False,
            "username": None
        }
