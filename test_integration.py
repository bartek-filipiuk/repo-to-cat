#!/usr/bin/env python3
"""
Integration test for OpenRouter and Together.ai providers with real API keys.
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

from app.providers.openrouter import OpenRouterProvider
from app.providers.together_ai import TogetherProvider

print("=" * 80)
print("🧪 INTEGRATION TEST: AI Providers (Real API Keys)")
print("=" * 80)

# Test 1: OpenRouter Provider
print("\n" + "=" * 80)
print("TEST 1: OpenRouter - Code Quality Analysis")
print("=" * 80)

try:
    print("\n✓ Initializing OpenRouter provider...")
    openrouter = OpenRouterProvider()
    print(f"✓ API Key loaded: {openrouter.api_key[:10]}...")

    # Sample code files for analysis
    code_files = [
        {
            "path": "example.py",
            "language": "python",
            "content": """
def calculate_average(numbers):
    \"\"\"Calculate average of a list of numbers.\"\"\"
    if not numbers:
        return 0
    total = sum(numbers)
    return total / len(numbers)

class DataProcessor:
    def __init__(self, data):
        self.data = data

    def process(self):
        \"\"\"Process data and return filtered results.\"\"\"
        return [item * 2 for item in self.data if item > 0]
"""
        }
    ]

    print(f"\n✓ Analyzing {len(code_files)} code file(s)...")
    print(f"  - File: {code_files[0]['path']}")
    print(f"  - Language: {code_files[0]['language']}")
    print(f"  - Size: {len(code_files[0]['content'])} bytes")

    result = openrouter.analyze_code_quality(code_files)

    print("\n" + "=" * 80)
    print("✅ OPENROUTER TEST PASSED!")
    print("=" * 80)
    print(f"\n📊 Overall Quality Score: {result.overall_quality_score}/10")
    print(f"\n📝 Summary: {result.summary}")

    print(f"\n🎯 Metrics ({len(result.metrics)}):")
    for metric in result.metrics:
        print(f"  • {metric.name}: {metric.score}/10")
        print(f"    └─ {metric.description}")

    print(f"\n💪 Strengths ({len(result.strengths)}):")
    for strength in result.strengths:
        print(f"  + {strength}")

    print(f"\n⚠️  Weaknesses ({len(result.weaknesses)}):")
    for weakness in result.weaknesses:
        print(f"  - {weakness}")

    print(f"\n💡 Recommendations ({len(result.recommendations)}):")
    for i, rec in enumerate(result.recommendations, 1):
        print(f"  {i}. {rec}")

except Exception as e:
    print(f"\n❌ OPENROUTER TEST FAILED: {type(e).__name__}: {str(e)}")
    sys.exit(1)

# Test 2: Together.ai Provider
print("\n\n" + "=" * 80)
print("TEST 2: Together.ai - Cat Image Generation")
print("=" * 80)

try:
    print("\n✓ Initializing Together.ai provider...")
    together = TogetherProvider()
    print(f"✓ API Key loaded: {together.api_key[:10]}...")

    # Simple test prompt
    prompt = """
    A small fluffy kitten with bright blue eyes, sitting on a windowsill,
    soft natural lighting, highly detailed fur texture, photorealistic
    """

    print(f"\n✓ Generating cat image...")
    print(f"  - Model: {together.DEFAULT_MODEL}")
    print(f"  - Dimensions: {together.DEFAULT_WIDTH}x{together.DEFAULT_HEIGHT}")
    print(f"  - Steps: {together.DEFAULT_STEPS}")
    print(f"  - Prompt: {prompt.strip()[:60]}...")

    image_url, image_base64 = together.generate_cat_image(prompt.strip())

    print("\n" + "=" * 80)
    print("✅ TOGETHER.AI TEST PASSED!")
    print("=" * 80)
    print(f"\n🖼️  Image URL: {image_url}")
    print(f"📦 Base64 size: {len(image_base64)} characters")
    print(f"📊 Estimated image size: ~{len(image_base64) * 3 // 4 // 1024} KB")

except Exception as e:
    print(f"\n❌ TOGETHER.AI TEST FAILED: {type(e).__name__}: {str(e)}")
    sys.exit(1)

# All tests passed
print("\n\n" + "=" * 80)
print("🎉 ALL INTEGRATION TESTS PASSED!")
print("=" * 80)
print("\n✅ OpenRouter: Code quality analysis working")
print("✅ Together.ai: Cat image generation working")
print("\nBoth providers are ready for production use! 🚀")
print("=" * 80)
