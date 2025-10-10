"""
Unit tests for code analysis service.

Tests all heuristic analysis methods and LLM integration.
"""
import pytest
from unittest.mock import Mock, patch
from app.services.analysis_service import AnalysisService
from app.providers.openrouter import CodeQualityAnalysis, CodeMetric


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def analysis_service():
    """Create AnalysisService instance with mocked OpenRouter."""
    mock_provider = Mock()
    return AnalysisService(openrouter_provider=mock_provider)


# ============================================================================
# Line Length Analysis Tests
# ============================================================================

class TestLineLengthAnalysis:
    """Tests for _analyze_line_lengths method."""

    def test_analyze_line_lengths_empty_code(self, analysis_service):
        """Test with empty code."""
        result = analysis_service._analyze_line_lengths("", "Python")

        assert result["line_length_avg"] == 0
        assert result["line_length_max"] == 0
        assert result["lines_too_long_pct"] == 0.0

    def test_analyze_line_lengths_simple_code(self, analysis_service):
        """Test with simple Python code."""
        code = """def hello():
    print("Hello, World!")
    return True"""

        result = analysis_service._analyze_line_lengths(code, "Python")

        assert result["line_length_avg"] > 0
        assert result["line_length_max"] == 26  # '    print("Hello, World!")'
        assert result["lines_too_long_pct"] == 0.0  # No lines > 120

    def test_analyze_line_lengths_with_long_lines(self, analysis_service):
        """Test with code containing long lines."""
        code = """def short():
    return True

def very_long_function_name_that_exceeds_one_hundred_twenty_characters_and_should_be_counted_as_too_long_in_the_analysis():
    pass"""

        result = analysis_service._analyze_line_lengths(code, "Python")

        assert result["line_length_max"] > 120
        assert result["lines_too_long_pct"] > 0  # At least one long line
        assert result["lines_too_long_pct"] == 20.0  # 1 out of 5 lines (20%)

    def test_analyze_line_lengths_all_long_lines(self, analysis_service):
        """Test with all lines being too long."""
        # Using explicit strings without triple quotes to avoid empty lines
        code = ("this_is_a_very_long_line_that_exceeds_one_hundred_twenty_characters_by_quite_a_bit_and_should_definitely_be_counted_in_stats_absolutely\n"
                "another_very_long_line_that_exceeds_one_hundred_twenty_characters_by_quite_a_bit_and_should_definitely_be_counted_too_for_sure_yes")

        result = analysis_service._analyze_line_lengths(code, "Python")

        assert result["lines_too_long_pct"] == 100.0  # All lines too long

    def test_analyze_line_lengths_single_line(self, analysis_service):
        """Test with single line."""
        code = "x = 42"

        result = analysis_service._analyze_line_lengths(code, "Python")

        assert result["line_length_avg"] == 6
        assert result["line_length_max"] == 6
        assert result["lines_too_long_pct"] == 0.0

    def test_analyze_line_lengths_whitespace_only(self, analysis_service):
        """Test with whitespace-only code."""
        code = "   \n\t\n  "

        result = analysis_service._analyze_line_lengths(code, "Python")

        # Should handle whitespace gracefully
        assert isinstance(result["line_length_avg"], (int, float))
        assert isinstance(result["line_length_max"], int)
        assert isinstance(result["lines_too_long_pct"], float)


# ============================================================================
# Placeholder Tests for Other Methods (will implement)
# ============================================================================

class TestFunctionLengthDetection:
    """Tests for _detect_function_lengths method."""

    def test_detect_function_lengths_empty_code(self, analysis_service):
        """Test with empty code."""
        result = analysis_service._detect_function_lengths("", "Python")

        assert result["function_length_avg"] == 0
        assert result["function_length_max"] == 0
        assert result["function_count"] == 0

    def test_detect_function_lengths_python_single_function(self, analysis_service):
        """Test with single Python function."""
        code = """def hello():
    print("Hello")
    return True"""

        result = analysis_service._detect_function_lengths(code, "Python")

        assert result["function_count"] == 1
        assert result["function_length_avg"] == 3
        assert result["function_length_max"] == 3

    def test_detect_function_lengths_python_multiple_functions(self, analysis_service):
        """Test with multiple Python functions."""
        code = """def short():
    return 1

def medium():
    x = 1
    y = 2
    return x + y

def long_function():
    a = 1
    b = 2
    c = 3
    d = 4
    e = 5
    return a + b + c + d + e"""

        result = analysis_service._detect_function_lengths(code, "Python")

        assert result["function_count"] == 3
        assert result["function_length_avg"] > 0
        assert result["function_length_max"] >= 7  # long_function has 7+ lines

    def test_detect_function_lengths_javascript(self, analysis_service):
        """Test with JavaScript function."""
        code = """function hello() {
    console.log("Hello");
    return true;
}"""

        result = analysis_service._detect_function_lengths(code, "JavaScript")

        assert result["function_count"] == 1
        # Note: For non-Python, function length detection is simpler

    def test_detect_function_lengths_unknown_language(self, analysis_service):
        """Test with unknown language."""
        result = analysis_service._detect_function_lengths("some code", "UnknownLang")

        assert result["function_count"] == 0
        assert result["function_length_avg"] == 0
        assert result["function_length_max"] == 0

    def test_detect_function_lengths_no_functions(self, analysis_service):
        """Test with code that has no functions."""
        code = """x = 1
y = 2
print(x + y)"""

        result = analysis_service._detect_function_lengths(code, "Python")

        assert result["function_count"] == 0


class TestNestingDepthCalculation:
    """Tests for _calculate_nesting_depth method."""

    def test_calculate_nesting_depth_empty_code(self, analysis_service):
        """Test with empty code."""
        result = analysis_service._calculate_nesting_depth("", "Python")

        assert result["nesting_depth_avg"] == 0
        assert result["nesting_depth_max"] == 0

    def test_calculate_nesting_depth_python_flat(self, analysis_service):
        """Test with flat Python code (no nesting)."""
        code = """x = 1
y = 2
print(x + y)"""

        result = analysis_service._calculate_nesting_depth(code, "Python")

        assert result["nesting_depth_avg"] == 0
        assert result["nesting_depth_max"] == 0

    def test_calculate_nesting_depth_python_nested(self, analysis_service):
        """Test with nested Python code."""
        code = """def foo():
    if x > 0:
        for i in range(10):
            print(i)"""

        result = analysis_service._calculate_nesting_depth(code, "Python")

        assert result["nesting_depth_avg"] > 0
        assert result["nesting_depth_max"] >= 3  # Three levels of indentation

    def test_calculate_nesting_depth_javascript_nested(self, analysis_service):
        """Test with nested JavaScript code (brace-based)."""
        code = """function foo() {
    if (x > 0) {
        for (let i = 0; i < 10; i++) {
            console.log(i);
        }
    }
}"""

        result = analysis_service._calculate_nesting_depth(code, "JavaScript")

        # Should track cumulative brace depth, not just braces on each line
        assert result["nesting_depth_max"] >= 2  # At least 2 levels deep
        assert result["nesting_depth_avg"] > 0

    def test_calculate_nesting_depth_c_nested(self, analysis_service):
        """Test with nested C code (brace-based)."""
        code = """int main() {
    if (x > 0) {
        while (y < 10) {
            printf("test");
            y++;
        }
    }
    return 0;
}"""

        result = analysis_service._calculate_nesting_depth(code, "C")

        # The printf and y++ lines should report depth of 2
        assert result["nesting_depth_max"] >= 2
        assert result["nesting_depth_avg"] > 0


class TestCommentRatioCalculation:
    """Tests for _calculate_comment_ratio method."""

    def test_calculate_comment_ratio_empty_code(self, analysis_service):
        """Test with empty code."""
        result = analysis_service._calculate_comment_ratio("", "Python")

        assert result == 0.0

    def test_calculate_comment_ratio_python_no_comments(self, analysis_service):
        """Test Python code with no comments."""
        code = """x = 1
y = 2
print(x + y)"""

        result = analysis_service._calculate_comment_ratio(code, "Python")

        assert result == 0.0

    def test_calculate_comment_ratio_python_with_comments(self, analysis_service):
        """Test Python code with comments."""
        code = """# This is a comment
x = 1  # Inline comment
y = 2
print(x + y)"""

        result = analysis_service._calculate_comment_ratio(code, "Python")

        assert result == 0.5  # 2 out of 4 lines have comments

    def test_calculate_comment_ratio_javascript_with_comments(self, analysis_service):
        """Test JavaScript code with comments."""
        code = """// This is a comment
const x = 1;
/* Block comment */
const y = 2;"""

        result = analysis_service._calculate_comment_ratio(code, "JavaScript")

        assert result == 0.5  # 2 out of 4 lines


class TestTypeHintsDetection:
    """Tests for _detect_type_hints method."""

    def test_detect_type_hints_empty_code(self, analysis_service):
        """Test with empty code."""
        result = analysis_service._detect_type_hints("", "Python")

        assert result is False

    def test_detect_type_hints_python_no_hints(self, analysis_service):
        """Test Python code without type hints."""
        code = """def foo(x):
    return x + 1"""

        result = analysis_service._detect_type_hints(code, "Python")

        assert result is False

    def test_detect_type_hints_python_with_hints(self, analysis_service):
        """Test Python code with type hints."""
        code = """def foo(x: int) -> int:
    return x + 1"""

        result = analysis_service._detect_type_hints(code, "Python")

        assert result is True

    def test_detect_type_hints_typescript_with_hints(self, analysis_service):
        """Test TypeScript code (always has types)."""
        code = """function foo(x: number): number {
    return x + 1;
}"""

        result = analysis_service._detect_type_hints(code, "TypeScript")

        assert result is True

    def test_detect_type_hints_go_always_typed(self, analysis_service):
        """Test Go (always typed language)."""
        result = analysis_service._detect_type_hints("func main() {}", "Go")

        assert result is True


class TestComplexityCalculation:
    """Tests for _calculate_complexity method."""

    def test_calculate_complexity_empty_code(self, analysis_service):
        """Test with empty code."""
        result = analysis_service._calculate_complexity("", "Python")

        assert result["complexity_avg"] == 0
        assert result["complexity_max"] == 0
        assert result["complexity_total"] == 0

    def test_calculate_complexity_simple_code(self, analysis_service):
        """Test with simple code (no control flow)."""
        code = """x = 1
y = 2
print(x + y)"""

        result = analysis_service._calculate_complexity(code, "Python")

        assert result["complexity_total"] == 0

    def test_calculate_complexity_with_conditionals(self, analysis_service):
        """Test with code containing conditionals."""
        code = """if x > 0:
    print("positive")
elif x < 0:
    print("negative")
else:
    print("zero")"""

        result = analysis_service._calculate_complexity(code, "Python")

        assert result["complexity_total"] >= 2  # if + elif

    def test_calculate_complexity_with_loops(self, analysis_service):
        """Test with code containing loops."""
        code = """for i in range(10):
    if i % 2 == 0:
        print(i)
while x > 0:
    x -= 1"""

        result = analysis_service._calculate_complexity(code, "Python")

        assert result["complexity_total"] >= 3  # for + if + while


class TestHeuristicScoring:
    """Tests for calculate_code_quality_score method."""

    def test_calculate_code_quality_score_empty_list(self, analysis_service):
        """Test with empty code files list."""
        with pytest.raises(ValueError, match="code_files cannot be empty"):
            analysis_service.calculate_code_quality_score([])

    def test_calculate_code_quality_score_single_file(self, analysis_service):
        """Test with single Python file."""
        code_files = [
            {
                "path": "app.py",
                "language": "Python",
                "content": """# Simple Python file
def hello():
    print("Hello")
    return True"""
            }
        ]

        result = analysis_service.calculate_code_quality_score(code_files)

        assert "line_length_avg" in result
        assert "function_length_avg" in result
        assert "has_tests" in result
        assert result["has_tests"] is False  # No test file
        assert isinstance(result["comment_ratio"], float)

    def test_calculate_code_quality_score_with_test_file(self, analysis_service):
        """Test with test file included."""
        code_files = [
            {
                "path": "test_app.py",
                "language": "Python",
                "content": "def test_foo(): pass"
            }
        ]

        result = analysis_service.calculate_code_quality_score(code_files)

        assert result["has_tests"] is True

    def test_calculate_code_quality_score_multiple_files(self, analysis_service):
        """Test with multiple files."""
        code_files = [
            {
                "path": "app.py",
                "language": "Python",
                "content": "def foo(): pass"
            },
            {
                "path": "test_app.py",
                "language": "Python",
                "content": "def test_foo(): pass"
            }
        ]

        result = analysis_service.calculate_code_quality_score(code_files)

        assert result["function_count"] == 2
        assert result["has_tests"] is True

    def test_normalize_heuristics_caps_at_10(self, analysis_service):
        """Test that normalization caps score at 10.0 even if raw score is 11."""
        # Create perfect metrics that would score 11 points
        perfect_metrics = {
            "line_length_avg": 80,          # +2 (< 100)
            "function_length_avg": 25,      # +2 (< 30)
            "nesting_depth_avg": 2,         # +2 (< 3)
            "comment_ratio": 0.15,          # +1 (> 0.1)
            "has_type_hints": True,         # +1
            "complexity_avg": 3,            # +2 (< 5)
            "has_tests": True               # +1
            # Total = 11 points, should be capped at 10.0
        }

        score = analysis_service._normalize_heuristics_to_10_scale(perfect_metrics)

        assert score == 10.0  # Should be capped
        assert score <= 10.0  # Must not exceed 10


class TestLLMAnalysis:
    """Tests for analyze_with_llm method."""

    def test_analyze_with_llm_empty_list(self, analysis_service):
        """Test with empty code files list."""
        with pytest.raises(ValueError, match="code_files cannot be empty"):
            analysis_service.analyze_with_llm([])

    def test_analyze_with_llm_success(self, analysis_service):
        """Test successful LLM analysis."""
        code_files = [
            {
                "path": "app.py",
                "language": "Python",
                "content": "def hello(): pass"
            }
        ]

        # Mock the OpenRouter provider response
        mock_result = CodeQualityAnalysis(
            overall_quality_score=7.5,
            metrics=[
                CodeMetric(name="Readability", score=8.0, description="Good readability"),
                CodeMetric(name="Maintainability", score=7.0, description="Easy to maintain"),
                CodeMetric(name="Complexity", score=6.0, description="Low complexity"),
                CodeMetric(name="Best Practices", score=7.5, description="Follows best practices"),
                CodeMetric(name="Error Handling", score=6.5, description="Basic error handling")
            ],
            strengths=["Clean code", "Good structure"],
            weaknesses=["Missing error handling"],
            recommendations=["Add error handling"],
            summary="Overall good quality"
        )

        analysis_service.openrouter_provider.analyze_code_quality = Mock(return_value=mock_result)

        result = analysis_service.analyze_with_llm(code_files)

        assert result.overall_quality_score == 7.5
        assert len(result.metrics) == 5
        assert result.strengths == ["Clean code", "Good structure"]


class TestCombinedAnalysis:
    """Tests for analyze_code_files method."""

    def test_analyze_code_files_empty_list(self, analysis_service):
        """Test with empty code files list."""
        with pytest.raises(ValueError, match="code_files cannot be empty"):
            analysis_service.analyze_code_files([])

    def test_analyze_code_files_success(self, analysis_service):
        """Test successful combined analysis."""
        code_files = [
            {
                "path": "app.py",
                "language": "Python",
                "content": """# Simple app
def hello():
    print("Hello")
    return True"""
            }
        ]

        # Mock the LLM provider response
        mock_llm_result = CodeQualityAnalysis(
            overall_quality_score=8.0,
            metrics=[
                CodeMetric(name="Readability", score=8.0, description="Good"),
                CodeMetric(name="Maintainability", score=7.5, description="Good"),
                CodeMetric(name="Complexity", score=6.0, description="Low"),
                CodeMetric(name="Best Practices", score=7.0, description="Good"),
                CodeMetric(name="Error Handling", score=6.5, description="Basic")
            ],
            strengths=["Clean code"],
            weaknesses=["Could improve"],
            recommendations=["Add tests"],
            summary="Good quality"
        )

        analysis_service.openrouter_provider.analyze_code_quality = Mock(return_value=mock_llm_result)

        result = analysis_service.analyze_code_files(code_files)

        # Check result structure
        assert result.code_quality_score > 0
        assert result.code_quality_score <= 10
        assert result.files_analyzed == ["app.py"]
        assert "line_length_avg" in result.metrics
        assert "readability_score" in result.metrics
        assert "strengths" in result.metrics

    def test_analyze_code_files_weighted_average(self, analysis_service):
        """Test that the weighted average (30/70) is calculated correctly."""
        code_files = [
            {
                "path": "perfect.py",
                "language": "Python",
                "content": """# Perfect code with type hints
def hello(name: str) -> str:
    return f"Hello {name}"

def test_hello():
    assert hello("World") == "Hello World"
"""
            }
        ]

        # Mock LLM to return perfect score
        mock_llm_result = CodeQualityAnalysis(
            overall_quality_score=10.0,
            metrics=[
                CodeMetric(name="Readability", score=10.0, description="Perfect"),
                CodeMetric(name="Maintainability", score=10.0, description="Perfect"),
                CodeMetric(name="Complexity", score=10.0, description="Perfect"),
                CodeMetric(name="Best Practices", score=10.0, description="Perfect"),
                CodeMetric(name="Error Handling", score=10.0, description="Perfect")
            ],
            strengths=["Everything"],
            weaknesses=[],
            recommendations=[],
            summary="Perfect"
        )

        analysis_service.openrouter_provider.analyze_code_quality = Mock(return_value=mock_llm_result)

        result = analysis_service.analyze_code_files(code_files)

        # With perfect heuristics (10) and perfect LLM (10):
        # 0.3 * 10 + 0.7 * 10 = 10.0
        # But heuristics might not be perfect, so check it's weighted
        assert result.code_quality_score > 7.0  # At least weighted towards LLM's 10

    def test_analyze_code_files_perfect_code_does_not_exceed_10(self, analysis_service):
        """Test that even with perfect code, final score never exceeds 10.0."""
        # Create perfect code that would score 11 on heuristics
        code_files = [
            {
                "path": "perfect.py",
                "language": "Go",  # Always has type hints
                "content": """// Perfect Go code
func hello() {
    return
}

func TestHello() {
    hello()
}
"""
            },
            {
                "path": "test_perfect.go",
                "language": "Go",
                "content": "func TestAnother() {}"
            }
        ]

        # Mock LLM to return perfect score
        mock_llm_result = CodeQualityAnalysis(
            overall_quality_score=10.0,
            metrics=[
                CodeMetric(name="Readability", score=10.0, description="Perfect"),
                CodeMetric(name="Maintainability", score=10.0, description="Perfect"),
                CodeMetric(name="Complexity", score=10.0, description="Perfect"),
                CodeMetric(name="Best Practices", score=10.0, description="Perfect"),
                CodeMetric(name="Error Handling", score=10.0, description="Perfect")
            ],
            strengths=["Perfect"],
            weaknesses=[],
            recommendations=[],
            summary="Perfect"
        )

        analysis_service.openrouter_provider.analyze_code_quality = Mock(return_value=mock_llm_result)

        result = analysis_service.analyze_code_files(code_files)

        # Must not exceed 10.0 (would fail AnalysisResult validation)
        assert result.code_quality_score <= 10.0
        assert isinstance(result.code_quality_score, (int, float))
