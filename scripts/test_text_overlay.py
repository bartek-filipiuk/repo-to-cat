#!/usr/bin/env python3
"""
Standalone test script for testing meme text overlay on images.

This script allows testing the text overlay feature independently
without running the full workflow. Useful for iterating on:
- Font size
- Text positioning
- Stroke width
- Font selection

Usage:
    python scripts/test_text_overlay.py --image path/to/image.png --top "TOP TEXT" --bottom "BOTTOM TEXT"
    python scripts/test_text_overlay.py --image generated_images/uuid.png --top "PYTHON CODE" --bottom "SUCH QUALITY"
"""
import argparse
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def find_font(font_name="impact.ttf", font_size=60):
    """
    Find and load a font, trying multiple common locations.

    Args:
        font_name: Font filename to search for
        font_size: Size of the font

    Returns:
        ImageFont object
    """
    # Common font locations on Linux
    font_paths = [
        f"/usr/share/fonts/truetype/msttcorefonts/{font_name}",
        f"/usr/share/fonts/TTF/{font_name}",
        f"/usr/share/fonts/truetype/{font_name}",
        f"/System/Library/Fonts/{font_name}",  # macOS
        f"C:\\Windows\\Fonts\\{font_name}",     # Windows
    ]

    # Try each path
    for font_path in font_paths:
        try:
            return ImageFont.truetype(font_path, font_size)
        except (OSError, IOError):
            continue

    # Try loading Impact without full path (might work on some systems)
    try:
        return ImageFont.truetype(font_name, font_size)
    except (OSError, IOError):
        pass

    # Fallback to DejaVu Sans Bold (widely available, supports sizing)
    fallback_fonts = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",  # macOS
        "C:\\Windows\\Fonts\\arialbd.ttf",      # Windows Arial Bold
    ]

    for fallback in fallback_fonts:
        try:
            print(f"⚠ Warning: Could not find {font_name}, using fallback: {fallback}")
            return ImageFont.truetype(fallback, font_size)
        except (OSError, IOError):
            continue

    # Last resort: default font (fixed size, doesn't respect font_size)
    print(f"❌ Error: No TrueType fonts found, using fixed-size default font")
    return ImageFont.load_default()


def add_text_to_image(
    image_path: str,
    top_text: str,
    bottom_text: str,
    output_path: str = "test_overlay_output.png",
    font_size: int = 60,
    stroke_width: int = 4
):
    """
    Add meme-style text overlay to an image.

    Args:
        image_path: Path to input image
        top_text: Text for top of image (uppercase recommended)
        bottom_text: Text for bottom of image (uppercase recommended)
        output_path: Path to save output image
        font_size: Font size in points
        stroke_width: Width of black stroke around text
    """
    # Load image
    print(f"📷 Loading image: {image_path}")
    img = Image.open(image_path)
    width, height = img.size

    # Create drawing context
    draw = ImageDraw.Draw(img)

    # Load font
    print(f"🔤 Loading font (size={font_size})...")
    font = find_font("impact.ttf", font_size)

    # Convert text to uppercase (meme style)
    top_text = top_text.upper()
    bottom_text = bottom_text.upper()

    # Calculate text positions
    # Top text: centered horizontally, 10% from top
    if top_text:
        # Get text bounding box
        bbox = draw.textbbox((0, 0), top_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        top_x = (width - text_width) // 2
        top_y = int(height * 0.05)  # 5% from top

        # Draw text with black outline (stroke)
        print(f"✍ Drawing top text: '{top_text}'")
        draw.text(
            (top_x, top_y),
            top_text,
            font=font,
            fill="white",
            stroke_width=stroke_width,
            stroke_fill="black"
        )

    # Bottom text: centered horizontally, 10% from bottom
    if bottom_text:
        bbox = draw.textbbox((0, 0), bottom_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        bottom_x = (width - text_width) // 2
        bottom_y = height - text_height - int(height * 0.08)  # 8% from bottom

        # Draw text with black outline
        print(f"✍ Drawing bottom text: '{bottom_text}'")
        draw.text(
            (bottom_x, bottom_y),
            bottom_text,
            font=font,
            fill="white",
            stroke_width=stroke_width,
            stroke_fill="black"
        )

    # Save result
    print(f"💾 Saving to: {output_path}")
    img.save(output_path)
    print(f"✅ Done! Open {output_path} to see the result")


def main():
    parser = argparse.ArgumentParser(
        description="Test meme text overlay on images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python scripts/test_text_overlay.py --image test.png --top "TOP TEXT" --bottom "BOTTOM TEXT"

  # Use existing generated image
  python scripts/test_text_overlay.py \\
    --image generated_images/8ddcf860-8095-4f62-8beb-cefef53077cc.png \\
    --top "HELLO WORLD" \\
    --bottom "NO TESTS FOUND"

  # Custom font size and output
  python scripts/test_text_overlay.py \\
    --image test.png \\
    --top "PYTHON CODE" \\
    --bottom "SUCH QUALITY" \\
    --font-size 70 \\
    --output my_meme.png
        """
    )

    parser.add_argument(
        "--image",
        required=True,
        help="Path to input image file"
    )
    parser.add_argument(
        "--top",
        default="",
        help="Top text (will be uppercased)"
    )
    parser.add_argument(
        "--bottom",
        default="",
        help="Bottom text (will be uppercased)"
    )
    parser.add_argument(
        "--output",
        default="test_overlay_output.png",
        help="Output filename (default: test_overlay_output.png)"
    )
    parser.add_argument(
        "--font-size",
        type=int,
        default=60,
        help="Font size in points (default: 60)"
    )
    parser.add_argument(
        "--stroke-width",
        type=int,
        default=4,
        help="Width of black outline around text (default: 4)"
    )

    args = parser.parse_args()

    # Validate input
    if not Path(args.image).exists():
        print(f"❌ Error: Image file not found: {args.image}")
        sys.exit(1)

    if not args.top and not args.bottom:
        print("❌ Error: At least one of --top or --bottom must be provided")
        sys.exit(1)

    # Run overlay
    try:
        add_text_to_image(
            image_path=args.image,
            top_text=args.top,
            bottom_text=args.bottom,
            output_path=args.output,
            font_size=args.font_size,
            stroke_width=args.stroke_width
        )
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
