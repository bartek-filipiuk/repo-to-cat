"""
Unit tests for Together.ai provider.

Tests Together.ai API integration including:
- Provider initialization
- Cat image generation
- Image download and encoding
- Error handling and retries
"""

import pytest
import base64
from unittest.mock import Mock, patch
import requests

from app.providers.together_ai import (
    TogetherProvider,
    ImageGenerationError,
)


class TestTogetherProviderInit:
    """Test TogetherProvider initialization."""

    def test_init_with_api_key(self):
        """Test initialization with provided API key."""
        provider = TogetherProvider(api_key="test-together-key")
        assert provider.api_key == "test-together-key"

    @patch.dict('os.environ', {'TOGETHER_API_KEY': 'env-together-key'})
    def test_init_with_env_var(self):
        """Test initialization with environment variable."""
        provider = TogetherProvider()
        assert provider.api_key == "env-together-key"

    @patch.dict('os.environ', {}, clear=True)
    def test_init_without_api_key(self):
        """Test initialization fails without API key."""
        with pytest.raises(ValueError, match="TOGETHER_API_KEY not found"):
            TogetherProvider()


class TestGenerateCatImage:
    """Test generate_cat_image() function."""

    @patch('app.providers.together_ai.requests.post')
    @patch('app.providers.together_ai.requests.get')
    def test_generate_cat_image_success(self, mock_get, mock_post):
        """Test successful cat image generation."""
        provider = TogetherProvider(api_key="test-key")

        # Setup mock response for image generation API
        mock_api_response = Mock()
        mock_api_response.json.return_value = {
            "data": [{
                "url": "https://together.ai/images/test123.png"
            }]
        }
        mock_api_response.raise_for_status = Mock()
        mock_post.return_value = mock_api_response

        # Setup mock response for image download
        fake_image_bytes = b"fake_image_data_123"
        mock_download_response = Mock()
        mock_download_response.content = fake_image_bytes
        mock_download_response.raise_for_status = Mock()
        mock_get.return_value = mock_download_response

        # Execute
        prompt = "A beautiful fluffy cat with green eyes"
        image_url, image_base64 = provider.generate_cat_image(prompt)

        # Assert
        assert image_url == "https://together.ai/images/test123.png"
        assert image_base64 == base64.b64encode(fake_image_bytes).decode('utf-8')

        # Verify API was called with correct parameters
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://api.together.xyz/v1/images/generations"
        payload = call_args[1]["json"]
        assert payload["model"] == "black-forest-labs/FLUX.1.1-pro"
        assert payload["width"] == 768
        assert payload["height"] == 448
        assert payload["steps"] == 20
        assert payload["prompt"] == prompt

    def test_generate_empty_prompt_raises_error(self):
        """Test that empty prompt raises ValueError."""
        provider = TogetherProvider(api_key="test-key")

        with pytest.raises(ValueError, match="prompt cannot be empty"):
            provider.generate_cat_image("")

        with pytest.raises(ValueError, match="prompt cannot be empty"):
            provider.generate_cat_image("   ")  # Whitespace only

    @patch('app.providers.together_ai.requests.post')
    @patch('app.providers.together_ai.requests.get')
    def test_generate_with_custom_parameters(self, mock_get, mock_post):
        """Test generation with custom width, height, steps."""
        provider = TogetherProvider(api_key="test-key")

        # Setup mocks
        mock_api_response = Mock()
        mock_api_response.json.return_value = {
            "data": [{"url": "https://together.ai/images/custom.png"}]
        }
        mock_api_response.raise_for_status = Mock()
        mock_post.return_value = mock_api_response

        mock_download_response = Mock()
        mock_download_response.content = b"test"
        mock_download_response.raise_for_status = Mock()
        mock_get.return_value = mock_download_response

        # Execute with custom parameters
        image_url, _ = provider.generate_cat_image(
            prompt="Custom cat",
            width=1024,
            height=768,
            steps=30
        )

        # Verify custom parameters were used
        payload = mock_post.call_args[1]["json"]
        assert payload["width"] == 1024
        assert payload["height"] == 768
        assert payload["steps"] == 30


class TestErrorHandling:
    """Test error handling and retry logic."""

    @patch('app.providers.together_ai.requests.post')
    @patch('app.providers.together_ai.requests.get')
    @patch('app.providers.together_ai.time.sleep')
    def test_retry_on_generation_failure(self, mock_sleep, mock_get, mock_post):
        """Test successful retry after generation failure."""
        provider = TogetherProvider(api_key="test-key")

        # Setup mocks - fail once, then succeed
        mock_success_response = Mock()
        mock_success_response.json.return_value = {
            "data": [{"url": "https://together.ai/images/success.png"}]
        }
        mock_success_response.raise_for_status = Mock()

        mock_post.side_effect = [
            requests.exceptions.RequestException("Temporary failure"),
            mock_success_response
        ]

        # Mock successful download
        mock_download_response = Mock()
        mock_download_response.content = b"test"
        mock_download_response.raise_for_status = Mock()
        mock_get.return_value = mock_download_response

        # Execute
        image_url, _ = provider.generate_cat_image("Test cat")

        # Assert retry happened
        assert mock_post.call_count == 2
        assert mock_sleep.call_count == 1
        assert image_url == "https://together.ai/images/success.png"

    @patch('app.providers.together_ai.requests.post')
    @patch('app.providers.together_ai.time.sleep')
    def test_max_retries_exceeded(self, mock_sleep, mock_post):
        """Test that errors are raised after max retries."""
        provider = TogetherProvider(api_key="test-key")

        # All attempts fail
        mock_post.side_effect = requests.exceptions.RequestException("Persistent failure")

        # Execute and assert
        with pytest.raises(ImageGenerationError, match="Image generation failed after 3 attempts"):
            provider.generate_cat_image("Test cat")

        # Should retry 3 times total
        assert mock_post.call_count == 3


class TestPromptHandling:
    """Test prompt handling and formatting."""

    @patch('app.providers.together_ai.requests.post')
    @patch('app.providers.together_ai.requests.get')
    def test_long_prompt(self, mock_get, mock_post):
        """Test handling of long detailed prompts."""
        provider = TogetherProvider(api_key="test-key")

        # Setup mocks
        mock_api_response = Mock()
        mock_api_response.json.return_value = {
            "data": [{"url": "https://together.ai/images/test.png"}]
        }
        mock_api_response.raise_for_status = Mock()
        mock_post.return_value = mock_api_response

        mock_download_response = Mock()
        mock_download_response.content = b"test"
        mock_download_response.raise_for_status = Mock()
        mock_get.return_value = mock_download_response

        # Very long prompt
        long_prompt = " ".join([
            "A beautiful fluffy Persian cat with golden fur,",
            "sitting regally on a velvet cushion,",
            "professional studio lighting, highly detailed,",
            "8k resolution, photorealistic, soft background,",
            "elegant pose, green eyes, whiskers visible"
        ])

        # Execute
        image_url, _ = provider.generate_cat_image(long_prompt)

        # Verify prompt was passed correctly
        payload = mock_post.call_args[1]["json"]
        assert payload["prompt"] == long_prompt
