"""
OpenRouter API provider for code quality analysis.

Uses Google Gemini 2.5 Flash via OpenRouter for analyzing code quality.
"""
import os
import json
import time
import logging
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from openai import OpenAI, APIError, RateLimitError, AuthenticationError

logger = logging.getLogger(__name__)


# ============================================================================
# Data Models
# ============================================================================

class CodeMetric(BaseModel):
    """Individual code quality metric."""
    name: str = Field(description="Metric name")
    score: float = Field(ge=0, le=10, description="Score from 0-10")
    description: str = Field(description="Explanation of the score")


class CodeQualityAnalysis(BaseModel):
    """Structured code quality analysis result."""
    overall_quality_score: float = Field(ge=0, le=10, description="Overall quality score 0-10")
    metrics: List[CodeMetric] = Field(description="Individual quality metrics")
    strengths: List[str] = Field(description="Code strengths")
    weaknesses: List[str] = Field(description="Code weaknesses")
    recommendations: List[str] = Field(description="Improvement recommendations")
    summary: str = Field(description="Brief summary")


# ============================================================================
# OpenRouter Provider
# ============================================================================

class OpenRouterProvider:
    """Provider for OpenRouter API with Google Gemini 2.5 Flash."""

    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    DEFAULT_MODEL = "google/gemini-2.5-flash"
    MAX_RETRIES = 3
    BASE_RETRY_DELAY = 1  # seconds

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenRouter client.

        Args:
            api_key: OpenRouter API key (defaults to OPENROUTER_API_KEY env var)

        Raises:
            ValueError: If API key is not provided or found in environment
        """
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")

        self.client = OpenAI(
            base_url=self.OPENROUTER_BASE_URL,
            api_key=self.api_key
        )

    def _format_code_files_for_prompt(self, code_files: List[Dict[str, str]]) -> str:
        """Format code files into a structured prompt."""
        formatted = []
        for file in code_files:
            path = file.get("path", "unknown")
            language = file.get("language", "")
            content = file.get("content", "")

            formatted.append(
                f"File: {path}\n"
                f"```{language}\n"
                f"{content}\n"
                f"```"
            )

        return "\n\n".join(formatted)

    def _exponential_backoff_retry(self, func, max_retries: int = MAX_RETRIES):
        """Retry function with exponential backoff for rate limits."""
        for attempt in range(max_retries):
            try:
                return func()
            except RateLimitError as e:
                if attempt == max_retries - 1:
                    raise

                delay = self.BASE_RETRY_DELAY * (2 ** attempt)
                logger.warning(
                    f"Rate limit hit. Retrying in {delay}s... (attempt {attempt + 1}/{max_retries})"
                )
                time.sleep(delay)
            except AuthenticationError:
                # Don't retry authentication errors
                logger.error("Authentication failed - not retrying")
                raise
            except APIError as e:
                # Log and raise other API errors
                logger.error(f"API error: {e}")
                raise

    def analyze_code_quality(
        self,
        code_files: List[Dict[str, str]],
        model: str = DEFAULT_MODEL,
        temperature: float = 0.3
    ) -> CodeQualityAnalysis:
        """
        Analyze code quality using OpenRouter and Gemini 2.5 Flash.

        Args:
            code_files: List of dicts with keys: path, language, content
                       Example: [{"path": "app.py", "language": "python", "content": "..."}]
            model: Model to use (default: google/gemini-2.5-flash)
            temperature: Sampling temperature (0.0-1.0, lower = more deterministic)

        Returns:
            CodeQualityAnalysis object with structured analysis

        Raises:
            ValueError: If code_files is empty or invalid
            APIError: If API call fails after retries
            AuthenticationError: If authentication fails
        """
        # Validation
        if not code_files:
            raise ValueError("code_files cannot be empty")

        # Format code for prompt
        code_context = self._format_code_files_for_prompt(code_files)

        # Define system prompt
        system_prompt = """You are an expert code quality analyst. Analyze the provided code files and assess:

1. Code Quality Metrics (score each 0-10):
   - Readability: How easy is the code to understand?
   - Maintainability: How easy is it to modify and extend?
   - Complexity: Are there overly complex sections?
   - Best Practices: Does it follow language/framework conventions?
   - Error Handling: How robust is error management?

2. Identify specific strengths and weaknesses
3. Provide actionable recommendations for improvement
4. Generate an overall quality score (weighted average)

Return your analysis in the specified JSON schema."""

        # Define user prompt
        user_prompt = f"""Analyze the following code files for quality:

{code_context}

Provide a comprehensive code quality analysis."""

        # Prepare request
        def make_request():
            request_params = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": temperature,
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "code_quality_analysis",
                        "strict": True,
                        "schema": CodeQualityAnalysis.model_json_schema()
                    }
                }
            }

            return self.client.chat.completions.create(**request_params)

        # Execute request with retry logic
        response = self._exponential_backoff_retry(make_request)

        # Log usage statistics
        usage = response.usage
        logger.info(
            f"Token usage - Prompt: {usage.prompt_tokens}, "
            f"Completion: {usage.completion_tokens}, "
            f"Total: {usage.total_tokens}"
        )

        # Parse and validate response
        try:
            result_json = json.loads(response.choices[0].message.content)
            analysis = CodeQualityAnalysis(**result_json)
            return analysis

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}")
        except Exception as e:
            raise ValueError(f"Failed to validate response structure: {e}")

    def generate_text(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> str:
        """
        Generate text using OpenRouter.

        Args:
            prompt: The prompt to generate text from
            system_message: Optional system message to set context
            model: Model to use (default: google/gemini-2.5-flash)
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text string

        Raises:
            APIError: If API call fails after retries
        """
        def make_request():
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})

            return self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

        response = self._exponential_backoff_retry(make_request)
        return response.choices[0].message.content.strip()
