"""
Unit tests for OpenRouter provider.

Tests OpenRouter API integration including:
- Provider initialization
- Code quality analysis
- Error handling and retries
- Response parsing
"""

import pytest
import json
import httpx
from unittest.mock import Mock, patch, MagicMock
from openai import APIError, RateLimitError, AuthenticationError

from app.providers.openrouter import (
    OpenRouterProvider,
    CodeQualityAnalysis,
    CodeMetric,
)


def create_mock_response(status_code: int = 429):
    """Create a mock httpx.Response for testing exceptions."""
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = status_code
    mock_response.headers = {}
    mock_response.json.return_value = {"error": {"message": "Test error"}}
    return mock_response


def create_mock_request():
    """Create a mock httpx.Request for testing exceptions."""
    mock_request = Mock(spec=httpx.Request)
    mock_request.method = "POST"
    mock_request.url = "https://openrouter.ai/api/v1/chat/completions"
    return mock_request


class TestOpenRouterProviderInit:
    """Test OpenRouterProvider initialization."""

    def test_init_with_api_key(self):
        """Test initialization with provided API key."""
        provider = OpenRouterProvider(api_key="sk-or-test-key")
        assert provider.api_key == "sk-or-test-key"
        assert provider.client is not None

    @patch.dict('os.environ', {'OPENROUTER_API_KEY': 'sk-or-env-key'})
    def test_init_with_env_var(self):
        """Test initialization with environment variable."""
        provider = OpenRouterProvider()
        assert provider.api_key == "sk-or-env-key"

    @patch.dict('os.environ', {}, clear=True)
    def test_init_without_api_key(self):
        """Test initialization fails without API key."""
        with pytest.raises(ValueError, match="OPENROUTER_API_KEY not found"):
            OpenRouterProvider()


class TestAnalyzeCodeQuality:
    """Test analyze_code_quality() function."""

    @patch('app.providers.openrouter.OpenAI')
    def test_analyze_code_quality_success(self, mock_openai):
        """Test successful code quality analysis."""
        # Setup provider
        provider = OpenRouterProvider(api_key="sk-or-test-key")

        # Setup mock response
        mock_analysis = {
            "overall_quality_score": 8.5,
            "metrics": [
                {
                    "name": "Readability",
                    "score": 9.0,
                    "description": "Code is well-structured and easy to read"
                },
                {
                    "name": "Maintainability",
                    "score": 8.0,
                    "description": "Good modular design"
                }
            ],
            "strengths": ["Clear naming", "Good structure"],
            "weaknesses": ["Missing error handling"],
            "recommendations": ["Add try-except blocks"],
            "summary": "High quality code with minor improvements needed"
        }

        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content=json.dumps(mock_analysis)))]
        mock_response.usage = Mock(prompt_tokens=100, completion_tokens=200, total_tokens=300)

        mock_openai.return_value.chat.completions.create.return_value = mock_response

        # Execute
        code_files = [
            {
                "path": "test.py",
                "language": "python",
                "content": "def hello():\n    return 'world'"
            }
        ]

        result = provider.analyze_code_quality(code_files)

        # Assert
        assert isinstance(result, CodeQualityAnalysis)
        assert result.overall_quality_score == 8.5
        assert len(result.metrics) == 2
        assert result.metrics[0].name == "Readability"
        assert result.metrics[0].score == 9.0
        assert "Clear naming" in result.strengths
        assert "Missing error handling" in result.weaknesses
        assert len(result.recommendations) == 1

    @patch('app.providers.openrouter.OpenAI')
    def test_analyze_empty_files_raises_error(self, mock_openai):
        """Test that empty code_files raises ValueError."""
        provider = OpenRouterProvider(api_key="sk-or-test-key")

        with pytest.raises(ValueError, match="code_files cannot be empty"):
            provider.analyze_code_quality([])

    @patch('app.providers.openrouter.OpenAI')
    def test_analyze_with_multiple_files(self, mock_openai):
        """Test analysis with multiple code files."""
        provider = OpenRouterProvider(api_key="sk-or-test-key")

        mock_analysis = {
            "overall_quality_score": 7.5,
            "metrics": [{"name": "Overall", "score": 7.5, "description": "Good"}],
            "strengths": ["Multiple modules"],
            "weaknesses": [],
            "recommendations": [],
            "summary": "Multi-file project"
        }

        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content=json.dumps(mock_analysis)))]
        mock_response.usage = Mock(prompt_tokens=200, completion_tokens=150, total_tokens=350)

        mock_openai.return_value.chat.completions.create.return_value = mock_response

        code_files = [
            {"path": "main.py", "language": "python", "content": "# main file"},
            {"path": "utils.py", "language": "python", "content": "# utils file"},
            {"path": "test_main.py", "language": "python", "content": "# test file"}
        ]

        result = provider.analyze_code_quality(code_files)

        assert result.overall_quality_score == 7.5
        assert "Multiple modules" in result.strengths

    @patch('app.providers.openrouter.OpenAI')
    def test_analyze_custom_model(self, mock_openai):
        """Test analysis with custom model parameter."""
        provider = OpenRouterProvider(api_key="sk-or-test-key")

        mock_analysis = {
            "overall_quality_score": 9.0,
            "metrics": [],
            "strengths": [],
            "weaknesses": [],
            "recommendations": [],
            "summary": "Excellent"
        }

        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content=json.dumps(mock_analysis)))]
        mock_response.usage = Mock(prompt_tokens=50, completion_tokens=100, total_tokens=150)

        mock_openai.return_value.chat.completions.create.return_value = mock_response

        code_files = [{"path": "test.py", "language": "python", "content": "pass"}]

        result = provider.analyze_code_quality(
            code_files,
            model="google/gemini-2.5-flash:thinking"
        )

        # Verify the model was passed to the API call
        call_args = mock_openai.return_value.chat.completions.create.call_args
        assert call_args[1]["model"] == "google/gemini-2.5-flash:thinking"


class TestErrorHandling:
    """Test error handling and retry logic."""

    @patch('app.providers.openrouter.OpenAI')
    @patch('app.providers.openrouter.time.sleep')  # Mock sleep to speed up tests
    def test_rate_limit_retry_success(self, mock_sleep, mock_openai):
        """Test successful retry after rate limit error."""
        provider = OpenRouterProvider(api_key="sk-or-test-key")

        mock_analysis = {
            "overall_quality_score": 8.0,
            "metrics": [],
            "strengths": [],
            "weaknesses": [],
            "recommendations": [],
            "summary": "Good after retry"
        }

        # First call raises RateLimitError, second succeeds
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content=json.dumps(mock_analysis)))]
        mock_response.usage = Mock(prompt_tokens=100, completion_tokens=100, total_tokens=200)

        # Create proper RateLimitError
        rate_limit_error = RateLimitError(
            "Rate limit exceeded",
            response=create_mock_response(429),
            body={"error": {"message": "Rate limit exceeded"}}
        )

        mock_openai.return_value.chat.completions.create.side_effect = [
            rate_limit_error,
            mock_response
        ]

        code_files = [{"path": "test.py", "language": "python", "content": "pass"}]

        result = provider.analyze_code_quality(code_files)

        # Assert retry happened
        assert mock_openai.return_value.chat.completions.create.call_count == 2
        assert mock_sleep.call_count == 1
        assert mock_sleep.call_args[0][0] == 1  # First retry delay is 1 second
        assert result.overall_quality_score == 8.0

    @patch('app.providers.openrouter.OpenAI')
    @patch('app.providers.openrouter.time.sleep')
    def test_rate_limit_retry_exponential_backoff(self, mock_sleep, mock_openai):
        """Test exponential backoff in retry logic."""
        provider = OpenRouterProvider(api_key="sk-or-test-key")

        mock_analysis = {
            "overall_quality_score": 7.0,
            "metrics": [],
            "strengths": [],
            "weaknesses": [],
            "recommendations": [],
            "summary": "Success after multiple retries"
        }

        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content=json.dumps(mock_analysis)))]
        mock_response.usage = Mock(prompt_tokens=50, completion_tokens=50, total_tokens=100)

        # Create proper RateLimitErrors
        rate_limit_error_1 = RateLimitError(
            "Rate limit 1",
            response=create_mock_response(429),
            body={"error": {"message": "Rate limit 1"}}
        )
        rate_limit_error_2 = RateLimitError(
            "Rate limit 2",
            response=create_mock_response(429),
            body={"error": {"message": "Rate limit 2"}}
        )

        # Fail twice, succeed on third attempt
        mock_openai.return_value.chat.completions.create.side_effect = [
            rate_limit_error_1,
            rate_limit_error_2,
            mock_response
        ]

        code_files = [{"path": "test.py", "language": "python", "content": "pass"}]

        result = provider.analyze_code_quality(code_files)

        # Assert exponential backoff: 1s, 2s
        assert mock_sleep.call_count == 2
        assert mock_sleep.call_args_list[0][0][0] == 1  # First retry: 1s
        assert mock_sleep.call_args_list[1][0][0] == 2  # Second retry: 2s
        assert result.overall_quality_score == 7.0

    @patch('app.providers.openrouter.OpenAI')
    @patch('app.providers.openrouter.time.sleep')
    def test_rate_limit_max_retries_exceeded(self, mock_sleep, mock_openai):
        """Test that rate limit errors are raised after max retries."""
        provider = OpenRouterProvider(api_key="sk-or-test-key")

        # Create proper RateLimitError
        rate_limit_error = RateLimitError(
            "Rate limit exceeded",
            response=create_mock_response(429),
            body={"error": {"message": "Rate limit exceeded"}}
        )

        # All attempts fail with rate limit
        mock_openai.return_value.chat.completions.create.side_effect = rate_limit_error

        code_files = [{"path": "test.py", "language": "python", "content": "pass"}]

        with pytest.raises(RateLimitError):
            provider.analyze_code_quality(code_files)

        # Should retry 3 times (initial + 2 retries = 3 total calls)
        assert mock_openai.return_value.chat.completions.create.call_count == 3

    @patch('app.providers.openrouter.OpenAI')
    def test_authentication_error_no_retry(self, mock_openai):
        """Test that authentication errors are not retried."""
        provider = OpenRouterProvider(api_key="sk-or-test-key")

        # Create proper AuthenticationError
        auth_error = AuthenticationError(
            "Invalid API key",
            response=create_mock_response(401),
            body={"error": {"message": "Invalid API key"}}
        )

        mock_openai.return_value.chat.completions.create.side_effect = auth_error

        code_files = [{"path": "test.py", "language": "python", "content": "pass"}]

        with pytest.raises(AuthenticationError):
            provider.analyze_code_quality(code_files)

        # Should not retry authentication errors
        assert mock_openai.return_value.chat.completions.create.call_count == 1

    @patch('app.providers.openrouter.OpenAI')
    def test_api_error_not_retried(self, mock_openai):
        """Test that generic API errors are raised without retry."""
        provider = OpenRouterProvider(api_key="sk-or-test-key")

        # Create proper APIError
        api_error = APIError(
            "Internal server error",
            request=create_mock_request(),
            body={"error": {"message": "Internal server error"}}
        )

        mock_openai.return_value.chat.completions.create.side_effect = api_error

        code_files = [{"path": "test.py", "language": "python", "content": "pass"}]

        with pytest.raises(APIError):
            provider.analyze_code_quality(code_files)

        # Should not retry generic API errors
        assert mock_openai.return_value.chat.completions.create.call_count == 1


class TestResponseParsing:
    """Test response parsing and validation."""

    @patch('app.providers.openrouter.OpenAI')
    def test_invalid_json_response(self, mock_openai):
        """Test handling of invalid JSON in response."""
        provider = OpenRouterProvider(api_key="sk-or-test-key")

        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Not valid JSON{}"))]
        mock_response.usage = Mock(prompt_tokens=50, completion_tokens=50, total_tokens=100)

        mock_openai.return_value.chat.completions.create.return_value = mock_response

        code_files = [{"path": "test.py", "language": "python", "content": "pass"}]

        with pytest.raises(ValueError, match="Failed to parse JSON response"):
            provider.analyze_code_quality(code_files)

    @patch('app.providers.openrouter.OpenAI')
    def test_invalid_schema_response(self, mock_openai):
        """Test handling of response that doesn't match schema."""
        provider = OpenRouterProvider(api_key="sk-or-test-key")

        # Valid JSON but missing required fields
        invalid_analysis = {
            "overall_quality_score": 8.0
            # Missing: metrics, strengths, weaknesses, recommendations, summary
        }

        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content=json.dumps(invalid_analysis)))]
        mock_response.usage = Mock(prompt_tokens=50, completion_tokens=50, total_tokens=100)

        mock_openai.return_value.chat.completions.create.return_value = mock_response

        code_files = [{"path": "test.py", "language": "python", "content": "pass"}]

        with pytest.raises(ValueError, match="Failed to validate response structure"):
            provider.analyze_code_quality(code_files)


class TestPromptFormatting:
    """Test code file formatting for prompts."""

    @patch('app.providers.openrouter.OpenAI')
    def test_format_code_files_for_prompt(self, mock_openai):
        """Test that code files are properly formatted in the prompt."""
        provider = OpenRouterProvider(api_key="sk-or-test-key")

        mock_analysis = {
            "overall_quality_score": 8.0,
            "metrics": [],
            "strengths": [],
            "weaknesses": [],
            "recommendations": [],
            "summary": "Test"
        }

        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content=json.dumps(mock_analysis)))]
        mock_response.usage = Mock(prompt_tokens=100, completion_tokens=50, total_tokens=150)

        mock_openai.return_value.chat.completions.create.return_value = mock_response

        code_files = [
            {
                "path": "app/main.py",
                "language": "python",
                "content": "def main():\n    pass"
            },
            {
                "path": "app/utils.py",
                "language": "python",
                "content": "def helper():\n    pass"
            }
        ]

        provider.analyze_code_quality(code_files)

        # Verify the prompt contains formatted code
        call_args = mock_openai.return_value.chat.completions.create.call_args
        user_message = call_args[1]["messages"][1]["content"]

        assert "File: app/main.py" in user_message
        assert "```python" in user_message
        assert "def main():" in user_message
        assert "File: app/utils.py" in user_message
        assert "def helper():" in user_message
