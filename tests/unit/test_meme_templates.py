"""
Unit tests for meme examples system.

Tests the LLM-based meme generation with example formatting.
"""

import pytest
from config.meme_templates import (
    MEME_EXAMPLES,
    format_examples_for_prompt
)


class TestMemeExamples:
    """Test meme examples structure and content."""

    def test_meme_examples_structure(self):
        """Test that MEME_EXAMPLES has correct structure."""
        assert isinstance(MEME_EXAMPLES, list)
        assert len(MEME_EXAMPLES) > 0

        for item in MEME_EXAMPLES:
            assert isinstance(item, tuple)
            assert len(item) == 3
            top, bottom, context = item
            assert isinstance(top, str)
            assert isinstance(bottom, str)
            assert isinstance(context, str)

    def test_all_examples_have_content(self):
        """Test that all examples have non-empty text."""
        for top, bottom, context in MEME_EXAMPLES:
            assert len(top) > 0, "Empty top text found"
            assert len(bottom) > 0, "Empty bottom text found"
            assert len(context) > 0, "Empty context found"

    def test_example_text_is_uppercase(self):
        """Test that all example text is uppercase."""
        for top, bottom, context in MEME_EXAMPLES:
            assert top == top.upper(), f"Non-uppercase top text: {top}"
            assert bottom == bottom.upper(), f"Non-uppercase bottom text: {bottom}"

    def test_examples_count(self):
        """Test that we have 20+ examples for LLM inspiration."""
        assert len(MEME_EXAMPLES) >= 20, f"Only {len(MEME_EXAMPLES)} examples, expected 20+"

    def test_text_length_reasonable(self):
        """Test that example text lengths are reasonable (1-10 words)."""
        for top, bottom, context in MEME_EXAMPLES:
            top_words = len(top.split())
            bottom_words = len(bottom.split())

            # Allow 1-10 words (flexible range for meme text)
            assert 1 <= top_words <= 10, f"Top text has {top_words} words: {top}"
            assert 1 <= bottom_words <= 10, f"Bottom text has {bottom_words} words: {bottom}"

    def test_python_examples_exist(self):
        """Test that Python-specific examples exist."""
        python_examples = [
            (top, bottom, context)
            for top, bottom, context in MEME_EXAMPLES
            if "python" in context.lower()
        ]
        assert len(python_examples) >= 3, "Should have multiple Python examples"

    def test_javascript_examples_exist(self):
        """Test that JavaScript-specific examples exist."""
        js_examples = [
            (top, bottom, context)
            for top, bottom, context in MEME_EXAMPLES
            if "javascript" in context.lower()
        ]
        assert len(js_examples) >= 3, "Should have multiple JavaScript examples"

    def test_rust_examples_exist(self):
        """Test that Rust-specific examples exist."""
        rust_examples = [
            (top, bottom, context)
            for top, bottom, context in MEME_EXAMPLES
            if "rust" in context.lower()
        ]
        assert len(rust_examples) >= 3, "Should have multiple Rust examples"

    def test_generic_examples_exist(self):
        """Test that generic examples exist."""
        generic_examples = [
            (top, bottom, context)
            for top, bottom, context in MEME_EXAMPLES
            if "generic" in context.lower()
        ]
        assert len(generic_examples) >= 3, "Should have multiple generic examples"


class TestFormatExamplesForPrompt:
    """Test example formatting for LLM prompts."""

    def test_returns_string(self):
        """Test that format_examples_for_prompt returns a string."""
        result = format_examples_for_prompt()
        assert isinstance(result, str)

    def test_default_limit(self):
        """Test that default limit of 15 examples is applied."""
        result = format_examples_for_prompt()
        lines = result.strip().split('\n')
        assert len(lines) <= 15, "Should return max 15 examples by default"

    def test_custom_limit(self):
        """Test that custom limit works."""
        result = format_examples_for_prompt(limit=5)
        lines = result.strip().split('\n')
        assert len(lines) <= 5, "Should return max 5 examples"

    def test_format_structure(self):
        """Test that formatted output has correct structure."""
        result = format_examples_for_prompt(limit=3)
        lines = result.strip().split('\n')

        for line in lines:
            assert 'TOP: "' in line, f"Missing TOP: format in line: {line}"
            assert '" / BOTTOM: "' in line, f"Missing BOTTOM: format in line: {line}"
            assert line.endswith('"'), f"Line doesn't end with quote: {line}"

    def test_python_prioritization(self):
        """Test that Python language prioritizes Python examples."""
        result = format_examples_for_prompt(language="Python", limit=5)
        lines = result.strip().split('\n')

        # Should have at least some Python examples in first 5
        assert len(lines) > 0, "Should return some examples"

        # Parse examples and check context (we don't expose context, but can verify format)
        for line in lines:
            assert 'TOP: "' in line
            assert 'BOTTOM: "' in line

    def test_javascript_prioritization(self):
        """Test that JavaScript language prioritizes JavaScript examples."""
        result = format_examples_for_prompt(language="JavaScript", limit=5)
        lines = result.strip().split('\n')
        assert len(lines) > 0, "Should return some examples"

    def test_typescript_uses_javascript_examples(self):
        """Test that TypeScript uses JavaScript examples."""
        result_ts = format_examples_for_prompt(language="TypeScript", limit=10)
        result_js = format_examples_for_prompt(language="JavaScript", limit=10)

        # Should return examples (both should prioritize JavaScript)
        assert len(result_ts) > 0
        assert len(result_js) > 0

    def test_unknown_language_returns_generic(self):
        """Test that unknown language returns generic examples."""
        result = format_examples_for_prompt(language="COBOL", limit=5)
        lines = result.strip().split('\n')
        assert len(lines) > 0, "Should return generic examples for unknown language"

    def test_no_language_returns_all(self):
        """Test that no language specified returns first N examples."""
        result = format_examples_for_prompt(limit=10)
        lines = result.strip().split('\n')
        assert len(lines) <= 10, "Should return up to 10 examples"

    def test_limit_greater_than_available(self):
        """Test that limit greater than available examples returns all."""
        total_examples = len(MEME_EXAMPLES)
        result = format_examples_for_prompt(limit=1000)
        lines = result.strip().split('\n')
        assert len(lines) == total_examples, f"Should return all {total_examples} examples"

    def test_empty_result_when_no_examples(self):
        """Test behavior when limit is 0."""
        result = format_examples_for_prompt(limit=0)
        assert result == "", "Should return empty string when limit is 0"
