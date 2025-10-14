"""
FastAPI application entry point for Repo-to-Cat.

This module initializes the FastAPI app with basic configuration,
middleware, API routes, and static file serving.
"""
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.routes import router
from app.api.auth import router as auth_router

# Load environment variables from settings into os.environ
# This ensures that os.getenv() calls work correctly
os.environ["GITHUB_TOKEN"] = settings.GITHUB_TOKEN
os.environ["OPENROUTER_API_KEY"] = settings.OPENROUTER_API_KEY
os.environ["TOGETHER_API_KEY"] = settings.TOGETHER_API_KEY

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
        "http://localhost:4321",  # Astro dev server
        "http://localhost:8000",  # API itself
        "http://localhost:8080",  # Alternative frontend port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create generated_images directory if it doesn't exist
image_storage_path = Path(settings.IMAGE_STORAGE_PATH)
image_storage_path.mkdir(parents=True, exist_ok=True)

# Mount static files for serving generated images
app.mount(
    "/generated_images",
    StaticFiles(directory=str(image_storage_path)),
    name="generated_images"
)

# Include API routes
app.include_router(router)
app.include_router(auth_router)


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
        "health": "/health",
        "generate": "/generate"
    }
