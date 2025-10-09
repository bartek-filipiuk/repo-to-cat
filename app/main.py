"""
FastAPI application entry point for Repo-to-Cat.

This module initializes the FastAPI app with basic configuration,
middleware, and health check endpoint.
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.core.config import settings
from app.core.database import get_db

# Initialize FastAPI app
app = FastAPI(
    title="Repo-to-Cat API",
    description="GitHub Repository Quality Visualizer - Generates cat images based on code quality",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:8000",  # API itself
        "http://localhost:8080",  # Alternative frontend port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint.

    Checks the status of the application and database connectivity.
    Returns health status, database status, and timestamp.

    Args:
        db: Database session dependency

    Returns:
        dict: Health status information including:
            - status: Overall health status ("healthy" or "unhealthy")
            - database: Database connectivity status
            - timestamp: Current ISO timestamp
    """
    # Check database connectivity
    database_status = {"status": "down"}
    try:
        # Try to execute a simple query
        db.execute(text("SELECT 1"))
        database_status = {"status": "up"}
    except Exception as e:
        database_status = {"status": "down", "error": str(e)}

    # Determine overall health status
    overall_status = "healthy" if database_status["status"] == "up" else "unhealthy"

    return {
        "status": overall_status,
        "database": database_status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/")
async def root():
    """
    Root endpoint.

    Returns basic API information and links to documentation.

    Returns:
        dict: API information with links to docs
    """
    return {
        "message": "Welcome to Repo-to-Cat API",
        "description": "GitHub Repository Quality Visualizer",
        "version": app.version,
        "docs": "/docs",
        "health": "/health"
    }
