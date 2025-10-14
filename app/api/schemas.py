"""
Pydantic schemas for API request/response models.

Defines all API schemas matching the specifications in PRD.md.
These models handle validation, serialization, and API documentation.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class GenerateRequest(BaseModel):
    """
    Request schema for POST /generate endpoint.

    Validates GitHub repository URL format.
    """
    github_url: str = Field(
        ...,
        description="GitHub repository URL (e.g., https://github.com/owner/repo)",
        examples=["https://github.com/python/cpython"]
    )

    @field_validator('github_url')
    @classmethod
    def validate_github_url(cls, v: str) -> str:
        """Validate that the URL is a valid GitHub repository URL."""
        if not v:
            raise ValueError("GitHub URL cannot be empty")

        if not v.startswith("https://github.com/"):
            raise ValueError("URL must be a GitHub repository (https://github.com/...)")

        # Basic validation: should have owner/repo format
        parts = v.replace("https://github.com/", "").split("/")
        if len(parts) < 2:
            raise ValueError("GitHub URL must include owner and repository name")

        # Ensure both owner and repo are non-empty
        if not parts[0] or not parts[1]:
            raise ValueError("GitHub URL must have non-empty owner and repository name")

        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "github_url": "https://github.com/python/cpython"
            }
        }
    )


# ============================================================================
# RESPONSE COMPONENT SCHEMAS
# ============================================================================

class RepositoryInfo(BaseModel):
    """
    Repository metadata from GitHub API.

    Contains basic information about the analyzed repository.
    """
    url: str = Field(..., description="Full GitHub repository URL")
    name: str = Field(..., description="Repository name")
    owner: str = Field(..., description="Repository owner/organization")
    primary_language: str = Field(..., description="Primary programming language")
    size_kb: int = Field(..., description="Repository size in kilobytes")
    stars: Optional[int] = Field(None, description="Number of GitHub stars")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "url": "https://github.com/python/cpython",
                "name": "cpython",
                "owner": "python",
                "primary_language": "Python",
                "size_kb": 150000,
                "stars": 50000
            }
        }
    )


class AnalysisResult(BaseModel):
    """
    Code quality analysis results.

    Contains quality score, analyzed files, and detailed metrics.
    """
    code_quality_score: float = Field(
        ...,
        ge=0.0,
        le=10.0,
        description="Overall code quality score (0-10)"
    )
    files_analyzed: List[str] = Field(
        ...,
        description="List of files that were analyzed"
    )
    metrics: Dict[str, Any] = Field(
        ...,
        description="Detailed code metrics (line length, tests, etc.)"
    )

    @field_validator('code_quality_score')
    @classmethod
    def validate_score_range(cls, v: float) -> float:
        """Ensure score is within valid range."""
        if v < 0.0 or v > 10.0:
            raise ValueError("Code quality score must be between 0.0 and 10.0")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code_quality_score": 7.5,
                "files_analyzed": ["README.md", "src/main.py", "tests/test_main.py"],
                "metrics": {
                    "line_length_avg": 85,
                    "function_length_avg": 25,
                    "has_tests": True,
                    "has_type_hints": True,
                    "has_documentation": True
                }
            }
        }
    )


class CatAttributes(BaseModel):
    """
    Cat visualization attributes derived from code analysis.

    Maps code quality metrics to cat characteristics for image generation.
    """
    size: str = Field(..., description="Cat size (kitten, small, medium, large, chonky)")
    age: str = Field(..., description="Cat age (kitten, young, adult, senior)")
    beauty_score: float = Field(..., ge=0.0, le=10.0, description="Beauty/quality score (0-10)")
    expression: str = Field(..., description="Cat expression (happy, neutral, grumpy, concerned)")
    background: str = Field(..., description="Background theme based on language")
    accessories: Optional[List[str]] = Field(None, description="Optional accessories (bow tie, collar, etc.)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "size": "medium",
                "age": "young",
                "beauty_score": 7.5,
                "expression": "happy",
                "background": "snakes and code snippets",
                "accessories": ["bow tie", "collar"]
            }
        }
    )


class ImageData(BaseModel):
    """
    Generated cat image data.

    Contains image URL, base64 binary, and the prompt used for generation.
    """
    url: str = Field(..., description="Relative URL to the generated image")
    binary: str = Field(..., description="Base64-encoded image data")
    prompt: str = Field(..., description="Image generation prompt used")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "url": "/generated_images/uuid-here.png",
                "binary": "base64-encoded-image-data...",
                "prompt": "A young, beautiful medium-sized cat with a happy expression..."
            }
        }
    )


# ============================================================================
# MAIN RESPONSE SCHEMAS
# ============================================================================

class MemeText(BaseModel):
    """
    Meme text overlay for image (top and bottom).
    """
    top: str = Field(..., description="Top meme text (uppercase)")
    bottom: str = Field(..., description="Bottom meme text (uppercase)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "top": "PYTHON CODE",
                "bottom": "SUCH QUALITY"
            }
        }
    )


class GenerateResponse(BaseModel):
    """
    Complete response for POST /generate endpoint.

    Contains all analysis results, cat attributes, generated image,
    funny story, and meme text overlay.
    Matches the exact structure defined in PRD.md section 3.1.
    """
    success: bool = Field(..., description="Whether generation was successful")
    generation_id: str = Field(..., description="Unique ID for this generation (UUID)")
    repository: RepositoryInfo = Field(..., description="Repository metadata")
    analysis: AnalysisResult = Field(..., description="Code quality analysis")
    cat_attributes: CatAttributes = Field(..., description="Derived cat attributes")
    story: Optional[str] = Field(None, description="Funny story about the repository (3-5 sentences)")
    meme_text: Optional[MemeText] = Field(None, description="Meme text overlay for image")
    image: ImageData = Field(..., description="Generated image data")
    timestamp: datetime = Field(..., description="Generation timestamp (ISO 8601)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "generation_id": "550e8400-e29b-41d4-a716-446655440000",
                "repository": {
                    "url": "https://github.com/python/cpython",
                    "name": "cpython",
                    "owner": "python",
                    "primary_language": "Python",
                    "size_kb": 150000,
                    "stars": 50000
                },
                "analysis": {
                    "code_quality_score": 9.5,
                    "files_analyzed": ["README.md", "Python/main.c"],
                    "metrics": {
                        "has_tests": True,
                        "has_type_hints": True,
                        "has_documentation": True
                    }
                },
                "cat_attributes": {
                    "size": "large",
                    "age": "senior",
                    "beauty_score": 9.5,
                    "expression": "happy",
                    "background": "snakes and code snippets",
                    "accessories": ["bow tie"]
                },
                "image": {
                    "url": "/generated_images/550e8400.png",
                    "binary": "iVBORw0KGgo...",
                    "prompt": "A wise senior large cat with happy expression..."
                },
                "timestamp": "2025-10-07T12:34:56Z"
            }
        }
    )


class HealthCheckResponse(BaseModel):
    """
    Response for GET /health endpoint.

    Contains service health status and database connectivity check.
    """
    status: str = Field(..., description="Overall health status (healthy/unhealthy)")
    database: Dict[str, str] = Field(..., description="Database connection status")
    services: Optional[Dict[str, Dict[str, Any]]] = Field(
        None,
        description="Optional detailed service status (GitHub API, OpenRouter, Together.ai)"
    )
    timestamp: datetime = Field(..., description="Health check timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "database": {
                    "status": "up"
                },
                "services": {
                    "github_api": {
                        "status": "up",
                        "response_time_ms": 145
                    },
                    "openrouter": {
                        "status": "up",
                        "response_time_ms": 320
                    },
                    "together_ai": {
                        "status": "up",
                        "response_time_ms": 280
                    }
                },
                "timestamp": "2025-10-07T12:34:56Z"
            }
        }
    )


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    "GenerateRequest",
    "GenerateResponse",
    "RepositoryInfo",
    "AnalysisResult",
    "CatAttributes",
    "ImageData",
    "MemeText",
    "HealthCheckResponse",
]
