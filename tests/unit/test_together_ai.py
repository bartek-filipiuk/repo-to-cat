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
from unittest.mock import Mock, patch, MagicMock
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
        assert provider.client is not None

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

    @patch('app.providers.together_ai.requests.get')
    @patch('app.providers.together_ai.Together')
    def test_generate_cat_image_success(self, mock_together, mock_requests):
        """Test successful cat image generation."""
        provider = TogetherProvider(api_key="test-key")

        # Setup mock response for image generation
        mock_image_data = Mock()
        mock_image_data.url = "https://together.ai/images/test123.png"

        mock_response = Mock()
        mock_response.data = [mock_image_data]

        mock_together.return_value.images.generate.return_value = mock_response

        # Setup mock response for image download
        fake_image_bytes = b"fake_image_data_123"
        mock_download_response = Mock()
        mock_download_response.content = fake_image_bytes
        mock_download_response.raise_for_status = Mock()

        mock_requests.return_value = mock_download_response

        # Execute
        prompt = "A beautiful fluffy cat with green eyes"
        image_url, image_base64 = provider.generate_cat_image(prompt)

        # Assert
        assert image_url == "https://together.ai/images/test123.png"
        assert image_base64 == base64.b64encode(fake_image_bytes).decode('utf-8')

        # Verify API was called with correct parameters
        call_args = mock_together.return_value.images.generate.call_args
        assert call_args[1]["model"] == "black-forest-labs/FLUX.1.1-pro"
        assert call_args[1]["width"] == 768
        assert call_args[1]["height"] == 432
        assert call_args[1]["steps"] == 20
        assert call_args[1]["prompt"] == prompt
        assert call_args[1]["response_format"] == "url"

    @patch('app.providers.together_ai.Together')
    def test_generate_empty_prompt_raises_error(self, mock_together):
        """Test that empty prompt raises ValueError."""
        provider = TogetherProvider(api_key="test-key")

        with pytest.raises(ValueError, match="prompt cannot be empty"):
            provider.generate_cat_image("")

        with pytest.raises(ValueError, match="prompt cannot be empty"):
            provider.generate_cat_image("   ")  # Whitespace only

    @patch('app.providers.together_ai.requests.get')
    @patch('app.providers.together_ai.Together')
    def test_generate_with_custom_parameters(self, mock_together, mock_requests):
        """Test generation with custom width, height, steps."""
        provider = TogetherProvider(api_key="test-key")

        # Setup mocks
        mock_image_data = Mock()
        mock_image_data.url = "https://together.ai/images/custom.png"

        mock_response = Mock()
        mock_response.data = [mock_image_data]

        mock_together.return_value.images.generate.return_value = mock_response

        mock_download_response = Mock()
        mock_download_response.content = b"test"
        mock_download_response.raise_for_status = Mock()
        mock_requests.return_value = mock_download_response

        # Execute with custom parameters
        image_url, _ = provider.generate_cat_image(
            prompt="Custom cat",
            width=1024,
            height=768,
            steps=30
        )

        # Verify custom parameters were used
        call_args = mock_together.return_value.images.generate.call_args
        assert call_args[1]["width"] == 1024
        assert call_args[1]["height"] == 768
        assert call_args[1]["steps"] == 30

    @patch('app.providers.together_ai.requests.get')
    @patch('app.providers.together_ai.Together')
    def test_generate_with_custom_model(self, mock_together, mock_requests):
        """Test generation with custom model."""
        provider = TogetherProvider(api_key="test-key")

        # Setup mocks
        mock_image_data = Mock()
        mock_image_data.url = "https://together.ai/images/test.png"

        mock_response = Mock()
        mock_response.data = [mock_image_data]

        mock_together.return_value.images.generate.return_value = mock_response

        mock_download_response = Mock()
        mock_download_response.content = b"test"
        mock_download_response.raise_for_status = Mock()
        mock_requests.return_value = mock_download_response

        # Execute with custom model
        image_url, _ = provider.generate_cat_image(
            prompt="Test cat",
            model="custom-model"
        )

        # Verify custom model was used
        call_args = mock_together.return_value.images.generate.call_args
        assert call_args[1]["model"] == "custom-model"


class TestImageDownload:
    """Test image download and encoding functionality."""

    @patch('app.providers.together_ai.requests.get')
    @patch('app.providers.together_ai.Together')
    def test_download_and_encode_image(self, mock_together, mock_requests):
        """Test successful image download and base64 encoding."""
        provider = TogetherProvider(api_key="test-key")

        # Setup mocks
        mock_image_data = Mock()
        mock_image_data.url = "https://together.ai/images/test.png"

        mock_response = Mock()
        mock_response.data = [mock_image_data]

        mock_together.return_value.images.generate.return_value = mock_response

        # Test image bytes
        test_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR..."
        mock_download_response = Mock()
        mock_download_response.content = test_bytes
        mock_download_response.raise_for_status = Mock()
        mock_requests.return_value = mock_download_response

        # Execute
        _, image_base64 = provider.generate_cat_image("Test")

        # Verify encoding
        expected_base64 = base64.b64encode(test_bytes).decode('utf-8')
        assert image_base64 == expected_base64

        # Verify download was called with correct URL
        mock_requests.assert_called_once_with(
            "https://together.ai/images/test.png",
            timeout=30
        )

    @patch('app.providers.together_ai.requests.get')
    @patch('app.providers.together_ai.Together')
    def test_download_timeout_error(self, mock_together, mock_requests):
        """Test handling of image download timeout."""
        provider = TogetherProvider(api_key="test-key")

        # Setup generation mock
        mock_image_data = Mock()
        mock_image_data.url = "https://together.ai/images/test.png"

        mock_response = Mock()
        mock_response.data = [mock_image_data]

        mock_together.return_value.images.generate.return_value = mock_response

        # Mock download timeout
        mock_requests.side_effect = requests.exceptions.Timeout("Download timeout")

        # Execute and assert
        with pytest.raises(ImageGenerationError, match="Image download timed out"):
            provider.generate_cat_image("Test")

    @patch('app.providers.together_ai.requests.get')
    @patch('app.providers.together_ai.Together')
    def test_download_request_exception(self, mock_together, mock_requests):
        """Test handling of image download request exception."""
        provider = TogetherProvider(api_key="test-key")

        # Setup generation mock
        mock_image_data = Mock()
        mock_image_data.url = "https://together.ai/images/test.png"

        mock_response = Mock()
        mock_response.data = [mock_image_data]

        mock_together.return_value.images.generate.return_value = mock_response

        # Mock download failure
        mock_requests.side_effect = requests.exceptions.RequestException("Network error")

        # Execute and assert
        with pytest.raises(ImageGenerationError, match="Failed to download image"):
            provider.generate_cat_image("Test")

    @patch('app.providers.together_ai.requests.get')
    @patch('app.providers.together_ai.Together')
    def test_download_http_error(self, mock_together, mock_requests):
        """Test handling of HTTP errors during download."""
        provider = TogetherProvider(api_key="test-key")

        # Setup generation mock
        mock_image_data = Mock()
        mock_image_data.url = "https://together.ai/images/test.png"

        mock_response = Mock()
        mock_response.data = [mock_image_data]

        mock_together.return_value.images.generate.return_value = mock_response

        # Mock HTTP error
        mock_download_response = Mock()
        mock_download_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_requests.return_value = mock_download_response

        # Execute and assert
        with pytest.raises(ImageGenerationError, match="Failed to download image"):
            provider.generate_cat_image("Test")


class TestErrorHandling:
    """Test error handling and retry logic."""

    @patch('app.providers.together_ai.requests.get')
    @patch('app.providers.together_ai.Together')
    @patch('app.providers.together_ai.time.sleep')  # Mock sleep
    def test_retry_on_generation_failure(self, mock_sleep, mock_together, mock_requests):
        """Test successful retry after generation failure."""
        provider = TogetherProvider(api_key="test-key")

        # Setup mocks - fail once, then succeed
        mock_image_data = Mock()
        mock_image_data.url = "https://together.ai/images/success.png"

        mock_success_response = Mock()
        mock_success_response.data = [mock_image_data]

        mock_together.return_value.images.generate.side_effect = [
            Exception("Temporary failure"),
            mock_success_response
        ]

        # Mock successful download
        mock_download_response = Mock()
        mock_download_response.content = b"test"
        mock_download_response.raise_for_status = Mock()
        mock_requests.return_value = mock_download_response

        # Execute
        image_url, _ = provider.generate_cat_image("Test cat")

        # Assert retry happened
        assert mock_together.return_value.images.generate.call_count == 2
        assert mock_sleep.call_count == 1
        assert mock_sleep.call_args[0][0] == 1  # First retry delay: 1s
        assert image_url == "https://together.ai/images/success.png"

    @patch('app.providers.together_ai.requests.get')
    @patch('app.providers.together_ai.Together')
    @patch('app.providers.together_ai.time.sleep')
    def test_exponential_backoff(self, mock_sleep, mock_together, mock_requests):
        """Test exponential backoff in retry logic."""
        provider = TogetherProvider(api_key="test-key")

        # Setup mocks - fail twice, succeed on third attempt
        mock_image_data = Mock()
        mock_image_data.url = "https://together.ai/images/success.png"

        mock_success_response = Mock()
        mock_success_response.data = [mock_image_data]

        mock_together.return_value.images.generate.side_effect = [
            Exception("Failure 1"),
            Exception("Failure 2"),
            mock_success_response
        ]

        # Mock successful download
        mock_download_response = Mock()
        mock_download_response.content = b"test"
        mock_download_response.raise_for_status = Mock()
        mock_requests.return_value = mock_download_response

        # Execute
        image_url, _ = provider.generate_cat_image("Test cat")

        # Assert exponential backoff: 1s, 2s
        assert mock_sleep.call_count == 2
        assert mock_sleep.call_args_list[0][0][0] == 1  # First retry: 1s
        assert mock_sleep.call_args_list[1][0][0] == 2  # Second retry: 2s

    @patch('app.providers.together_ai.Together')
    @patch('app.providers.together_ai.time.sleep')
    def test_max_retries_exceeded(self, mock_sleep, mock_together):
        """Test that errors are raised after max retries."""
        provider = TogetherProvider(api_key="test-key")

        # All attempts fail
        mock_together.return_value.images.generate.side_effect = Exception("Persistent failure")

        # Execute and assert
        with pytest.raises(ImageGenerationError, match="Image generation failed after 3 attempts"):
            provider.generate_cat_image("Test cat")

        # Should retry 3 times total
        assert mock_together.return_value.images.generate.call_count == 3

    @patch('app.providers.together_ai.Together')
    def test_authentication_error_no_retry(self, mock_together):
        """Test that authentication errors are not retried."""
        provider = TogetherProvider(api_key="test-key")

        # Simulate authentication error
        mock_together.return_value.images.generate.side_effect = Exception("Invalid API key")

        # Execute and assert
        with pytest.raises(ImageGenerationError, match="Authentication failed"):
            provider.generate_cat_image("Test cat")

        # Should not retry authentication errors
        assert mock_together.return_value.images.generate.call_count == 1


class TestPromptHandling:
    """Test prompt handling and formatting."""

    @patch('app.providers.together_ai.requests.get')
    @patch('app.providers.together_ai.Together')
    def test_long_prompt(self, mock_together, mock_requests):
        """Test handling of long detailed prompts."""
        provider = TogetherProvider(api_key="test-key")

        # Setup mocks
        mock_image_data = Mock()
        mock_image_data.url = "https://together.ai/images/test.png"

        mock_response = Mock()
        mock_response.data = [mock_image_data]

        mock_together.return_value.images.generate.return_value = mock_response

        mock_download_response = Mock()
        mock_download_response.content = b"test"
        mock_download_response.raise_for_status = Mock()
        mock_requests.return_value = mock_download_response

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
        call_args = mock_together.return_value.images.generate.call_args
        assert call_args[1]["prompt"] == long_prompt

    @patch('app.providers.together_ai.requests.get')
    @patch('app.providers.together_ai.Together')
    def test_prompt_with_special_characters(self, mock_together, mock_requests):
        """Test handling of prompts with special characters."""
        provider = TogetherProvider(api_key="test-key")

        # Setup mocks
        mock_image_data = Mock()
        mock_image_data.url = "https://together.ai/images/test.png"

        mock_response = Mock()
        mock_response.data = [mock_image_data]

        mock_together.return_value.images.generate.return_value = mock_response

        mock_download_response = Mock()
        mock_download_response.content = b"test"
        mock_download_response.raise_for_status = Mock()
        mock_requests.return_value = mock_download_response

        # Prompt with special characters
        special_prompt = "A cat with \"quotes\", 'apostrophes', & symbols, #hashtags"

        # Execute
        image_url, _ = provider.generate_cat_image(special_prompt)

        # Verify prompt was passed correctly
        call_args = mock_together.return_value.images.generate.call_args
        assert call_args[1]["prompt"] == special_prompt
