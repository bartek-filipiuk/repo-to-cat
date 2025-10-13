"""
API route handlers for Repo-to-Cat.

Implements /health and /generate endpoints.
"""
import logging
import time
import uuid
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.core.database import get_db
from app.api.schemas import GenerateRequest, GenerateResponse
from app.langgraph.workflow import create_workflow

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# HEALTH CHECK HELPERS
# ============================================================================

def check_github_api() -> Dict[str, Any]:
    """
    Check GitHub API connectivity.

    Returns:
        Dict with status, response_time_ms, and optional error
    """
    start_time = time.time()
    try:
        response = httpx.get(
            "https://api.github.com/user",
            headers={"Authorization": f"token {settings.GITHUB_TOKEN}"},
            timeout=5.0
        )
        response_time_ms = int((time.time() - start_time) * 1000)

        if response.status_code in [200, 401]:  # 401 means API is up, just bad token
            return {"status": "up", "response_time_ms": response_time_ms}
        else:
            return {
                "status": "down",
                "error": f"HTTP {response.status_code}",
                "response_time_ms": response_time_ms
            }
    except Exception as e:
        response_time_ms = int((time.time() - start_time) * 1000)
        return {
            "status": "down",
            "error": str(e),
            "response_time_ms": response_time_ms
        }


def check_openrouter_api() -> Dict[str, Any]:
    """
    Check OpenRouter API connectivity.

    Returns:
        Dict with status, response_time_ms, and optional error
    """
    start_time = time.time()
    try:
        # Check if API key is configured
        if not settings.OPENROUTER_API_KEY or len(settings.OPENROUTER_API_KEY) < 10:
            return {
                "status": "down",
                "error": "API key not configured",
                "response_time_ms": 0
            }

        # Simple check - validate API key format and try to reach the endpoint
        response = httpx.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}"},
            timeout=5.0
        )
        response_time_ms = int((time.time() - start_time) * 1000)

        if response.status_code in [200, 401]:
            return {"status": "up", "response_time_ms": response_time_ms}
        else:
            return {
                "status": "down",
                "error": f"HTTP {response.status_code}",
                "response_time_ms": response_time_ms
            }
    except Exception as e:
        response_time_ms = int((time.time() - start_time) * 1000)
        return {
            "status": "down",
            "error": str(e),
            "response_time_ms": response_time_ms
        }


def check_together_api() -> Dict[str, Any]:
    """
    Check Together.ai API connectivity.

    Returns:
        Dict with status, response_time_ms, and optional error
    """
    start_time = time.time()
    try:
        # Check if API key is configured
        if not settings.TOGETHER_API_KEY or len(settings.TOGETHER_API_KEY) < 10:
            return {
                "status": "down",
                "error": "API key not configured",
                "response_time_ms": 0
            }

        # Simple check - validate API key format and try to reach the endpoint
        response = httpx.get(
            "https://api.together.xyz/v1/models",
            headers={"Authorization": f"Bearer {settings.TOGETHER_API_KEY}"},
            timeout=5.0
        )
        response_time_ms = int((time.time() - start_time) * 1000)

        if response.status_code in [200, 401]:
            return {"status": "up", "response_time_ms": response_time_ms}
        else:
            return {
                "status": "down",
                "error": f"HTTP {response.status_code}",
                "response_time_ms": response_time_ms
            }
    except Exception as e:
        response_time_ms = int((time.time() - start_time) * 1000)
        return {
            "status": "down",
            "error": str(e),
            "response_time_ms": response_time_ms
        }


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint.

    Checks the status of all external services:
    - GitHub API
    - OpenRouter API
    - Together.ai API
    - PostgreSQL Database

    Returns:
        JSON with overall status and individual service statuses
    """
    # Check database connectivity
    database_status = {"status": "down"}
    try:
        db.execute(text("SELECT 1"))
        database_status = {"status": "up", "response_time_ms": 0}
    except Exception as e:
        database_status = {"status": "down", "error": str(e)}

    # Check external APIs in parallel using thread pool
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_github = executor.submit(check_github_api)
        future_openrouter = executor.submit(check_openrouter_api)
        future_together = executor.submit(check_together_api)

        github_status = future_github.result()
        openrouter_status = future_openrouter.result()
        together_status = future_together.result()

    # Determine overall health status
    all_services_up = (
        database_status["status"] == "up" and
        github_status["status"] == "up" and
        openrouter_status["status"] == "up" and
        together_status["status"] == "up"
    )

    overall_status = "healthy" if all_services_up else "degraded"

    return {
        "status": overall_status,
        "services": {
            "github_api": github_status,
            "openrouter": openrouter_status,
            "together_ai": together_status,
            "database": database_status
        }
    }


# ============================================================================
# GENERATE ENDPOINT
# ============================================================================

@router.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest, db: Session = Depends(get_db)):
    """
    Generate cat image based on repository analysis.

    Takes a GitHub repository URL, analyzes the code quality, and generates
    a cat image reflecting the analysis results.

    Args:
        request: GenerateRequest with github_url
        db: Database session

    Returns:
        GenerateResponse with analysis results and image data

    Raises:
        HTTPException: 403 (private repo), 404 (not found), 500 (analysis failed)
    """
    generation_id = str(uuid.uuid4())

    logger.info(f"Starting generation {generation_id} for {request.github_url}")

    try:
        # Create and invoke LangGraph workflow
        workflow = create_workflow()
        result = workflow.invoke({
            "github_url": request.github_url,
            "generation_id": generation_id
        })

        # Check for errors in workflow result
        if result.get("error"):
            error_msg = result["error"]
            logger.error(f"Workflow error for {generation_id}: {error_msg}")

            # Determine appropriate HTTP status code based on error
            if "404" in error_msg or "not found" in error_msg.lower():
                raise HTTPException(
                    status_code=404,
                    detail=error_msg
                )
            elif "403" in error_msg or "forbidden" in error_msg.lower():
                raise HTTPException(
                    status_code=403,
                    detail=error_msg
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=error_msg
                )

        # Extract data from workflow result
        metadata = result.get("metadata", {})
        analysis = result.get("analysis", {})
        cat_attrs = result.get("cat_attrs", {})
        image = result.get("image", {})

        # Build response
        response_data = {
            "success": True,
            "generation_id": generation_id,
            "repository": {
                "url": request.github_url,
                "name": metadata.get("name", ""),
                "owner": metadata.get("owner", ""),
                "primary_language": metadata.get("primary_language") or "Unknown",
                "size_kb": metadata.get("size_kb", 0),
                "stars": metadata.get("stars")
            },
            "analysis": {
                "code_quality_score": analysis.get("code_quality_score", 0.0),
                "files_analyzed": analysis.get("files_analyzed", []),
                "metrics": analysis.get("metrics", {})
            },
            "cat_attributes": {
                "size": cat_attrs.get("size", "medium"),
                "age": cat_attrs.get("age", "adult cat"),
                "beauty_score": cat_attrs.get("beauty_score", analysis.get("code_quality_score", 5.0)),
                "expression": cat_attrs.get("expression", "neutral"),
                "background": cat_attrs.get("background", "neutral background"),
                "accessories": cat_attrs.get("accessories")
            },
            "image": {
                "url": image.get("url", ""),
                "binary": image.get("binary", ""),
                "prompt": image.get("prompt", "")
            },
            "timestamp": datetime.now(timezone.utc)
        }

        logger.info(f"Successfully completed generation {generation_id}")
        return response_data

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        # Catch-all for unexpected errors
        logger.error(f"Unexpected error for {generation_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
