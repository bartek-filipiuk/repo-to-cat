"""
Together.ai API provider for cat image generation.

Uses FLUX.1.1-pro model for generating cat images based on code quality.
"""
import os
import base64
import time
import logging
from typing import Tuple, Optional
import requests
from together import Together

logger = logging.getLogger(__name__)


class ImageGenerationError(Exception):
    """Custom exception for image generation failures."""
    pass


class TogetherProvider:
    """Provider for Together.ai FLUX.1.1-pro image generation."""

    DEFAULT_MODEL = "black-forest-labs/FLUX.1.1-pro"
    DEFAULT_WIDTH = 768
    DEFAULT_HEIGHT = 432
    DEFAULT_STEPS = 20
    MAX_RETRIES = 3
    BASE_RETRY_DELAY = 1  # seconds
    DOWNLOAD_TIMEOUT = 30  # seconds

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Together.ai client.

        Args:
            api_key: Together.ai API key (defaults to TOGETHER_API_KEY env var)

        Raises:
            ValueError: If API key is not provided or found in environment
        """
        self.api_key = api_key or os.environ.get("TOGETHER_API_KEY")
        if not self.api_key:
            raise ValueError("TOGETHER_API_KEY not found in environment variables")

        self.client = Together(api_key=self.api_key)

    def _download_and_encode_image(self, image_url: str) -> str:
        """
        Download image from URL and encode as base64.

        Args:
            image_url: URL of the image to download

        Returns:
            Base64-encoded image string

        Raises:
            ImageGenerationError: If download fails
        """
        try:
            response = requests.get(image_url, timeout=self.DOWNLOAD_TIMEOUT)
            response.raise_for_status()

            # Get image bytes
            image_bytes = response.content

            # Encode to base64
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')

            return image_base64

        except requests.exceptions.Timeout:
            raise ImageGenerationError(f"Image download timed out after {self.DOWNLOAD_TIMEOUT}s")
        except requests.exceptions.RequestException as e:
            raise ImageGenerationError(f"Failed to download image: {str(e)}")

    def generate_cat_image(
        self,
        prompt: str,
        width: int = DEFAULT_WIDTH,
        height: int = DEFAULT_HEIGHT,
        steps: int = DEFAULT_STEPS,
        model: str = DEFAULT_MODEL
    ) -> Tuple[str, str]:
        """
        Generate a cat image using FLUX.1.1-pro model.

        Args:
            prompt: Detailed text description of the cat image
            width: Image width in pixels (default: 768)
            height: Image height in pixels (default: 432)
            steps: Number of diffusion steps (default: 20)
            model: Model to use (default: black-forest-labs/FLUX.1.1-pro)

        Returns:
            Tuple of (image_url, base64_encoded_image)

        Raises:
            ValueError: If prompt is empty
            ImageGenerationError: If image generation fails after all retries
        """
        # Validation
        if not prompt or not prompt.strip():
            raise ValueError("prompt cannot be empty")

        # Retry logic with exponential backoff
        last_exception = None
        for attempt in range(self.MAX_RETRIES):
            try:
                logger.info(
                    f"Generating image (attempt {attempt + 1}/{self.MAX_RETRIES}): "
                    f"{prompt[:50]}..."
                )

                # Generate image
                response = self.client.images.generate(
                    model=model,
                    width=width,
                    height=height,
                    steps=steps,
                    prompt=prompt,
                    n=1,
                    response_format="url"
                )

                # Extract image URL
                image_url = response.data[0].url
                logger.info(f"Image generated successfully: {image_url}")

                # Download image and convert to base64
                try:
                    image_base64 = self._download_and_encode_image(image_url)
                    logger.info(
                        f"Image downloaded and encoded (size: {len(image_base64)} chars)"
                    )

                    return image_url, image_base64

                except ImageGenerationError as e:
                    # Download failed - raise immediately
                    logger.error(f"Failed to download image: {e}")
                    raise

            except Exception as e:
                last_exception = e
                logger.warning(
                    f"Attempt {attempt + 1} failed: {type(e).__name__}: {str(e)}"
                )

                # Don't retry authentication-related errors
                if "authentication" in str(e).lower() or "api key" in str(e).lower():
                    raise ImageGenerationError(f"Authentication failed: {str(e)}")

                # Last attempt - raise exception
                if attempt == self.MAX_RETRIES - 1:
                    logger.error(f"All {self.MAX_RETRIES} attempts failed")
                    raise ImageGenerationError(
                        f"Image generation failed after {self.MAX_RETRIES} attempts: "
                        f"{str(last_exception)}"
                    )

                # Exponential backoff: 1s, 2s, 4s
                wait_time = self.BASE_RETRY_DELAY * (2 ** attempt)
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

        # Should never reach here, but just in case
        raise ImageGenerationError(f"Unexpected error: {str(last_exception)}")
