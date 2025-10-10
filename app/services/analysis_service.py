"""
Code analysis service for evaluating code quality.

Combines heuristic analysis (30% weight) with LLM-based analysis (70% weight)
to produce a comprehensive code quality score and metrics.
"""
import re
import logging
from typing import List, Dict, Optional, Any
from statistics import mean

from app.api.schemas import AnalysisResult
from app.providers.openrouter import OpenRouterProvider, CodeQualityAnalysis

logger = logging.getLogger(__name__)


# ============================================================================
# Language-Specific Patterns
# ============================================================================

# Function/method definition patterns for different languages
FUNCTION_PATTERNS = {
    "Python": r"^\s*(def|async def)\s+\w+",
    "JavaScript": r"^\s*(function\s+\w+|const\s+\w+\s*=\s*\([^)]*\)\s*=>|let\s+\w+\s*=\s*\([^)]*\)\s*=>)",
    "TypeScript": r"^\s*(function\s+\w+|const\s+\w+\s*=\s*\([^)]*\)\s*=>|let\s+\w+\s*=\s*\([^)]*\)\s*=>)",
    "Go": r"^\s*func\s+\w+",
    "Rust": r"^\s*fn\s+\w+",
    "Java": r"^\s*(public|private|protected|static).*\w+\s*\(",
    "C": r"^\w+\s+\w+\s*\(",
    "C++": r"^\w+\s+\w+\s*\(|^\w+::\w+\s*\(",
    "Ruby": r"^\s*def\s+\w+",
    "PHP": r"^\s*(public|private|protected)?\s*function\s+\w+",
}

# Comment patterns for different languages
COMMENT_PATTERNS = {
    "Python": [r"#.*$"],
    "JavaScript": [r"//.*$", r"/\*.*?\*/"],
    "TypeScript": [r"//.*$", r"/\*.*?\*/"],
    "Go": [r"//.*$", r"/\*.*?\*/"],
    "Rust": [r"//.*$", r"/\*.*?\*/"],
    "Java": [r"//.*$", r"/\*.*?\*/"],
    "C": [r"//.*$", r"/\*.*?\*/"],
    "C++": [r"//.*$", r"/\*.*?\*/"],
    "Ruby": [r"#.*$"],
    "PHP": [r"//.*$", r"/\*.*?\*/", r"#.*$"],
}

# Type hint patterns for languages that support optional typing
TYPE_HINT_PATTERNS = {
    "Python": r"\w+\s*:\s*\w+",  # x: int or x: List[int]
    "TypeScript": r"\w+\s*:\s*\w+",  # x: number
    "Go": None,  # Built-in (always typed)
    "Rust": None,  # Built-in (always typed)
    "Java": None,  # Built-in (always typed)
    "C": None,  # Built-in (always typed)
    "C++": None,  # Built-in (always typed)
    "Ruby": r"\w+\s*:\s*\w+",  # Ruby 3+ type signatures
    "PHP": r"\w+\s*:\s*\w+",  # PHP type hints
}

# Keywords that contribute to complexity
COMPLEXITY_KEYWORDS = [
    "if", "else", "elif", "for", "while", "switch", "case",
    "catch", "except", "&&", "||", "and", "or"
]


# ============================================================================
# Analysis Service
# ============================================================================

class AnalysisService:
    """
    Service for analyzing code quality using heuristics and LLM.

    Combines:
    - Heuristic analysis (30% weight): line length, function length, nesting,
      comments, type hints, complexity
    - LLM analysis (70% weight): readability, maintainability, best practices,
      error handling via OpenRouter
    """

    def __init__(self, openrouter_provider: Optional[OpenRouterProvider] = None):
        """
        Initialize analysis service.

        Args:
            openrouter_provider: Optional OpenRouter provider (for testing).
                                If None, creates a new provider instance.
        """
        self.openrouter_provider = openrouter_provider or OpenRouterProvider()

    # ========================================================================
    # Main Public Methods
    # ========================================================================

    def analyze_code_files(
        self,
        code_files: List[Dict[str, str]]
    ) -> AnalysisResult:
        """
        Main analysis function combining heuristics + LLM.

        Args:
            code_files: List of dicts with keys: path, language, content
                       Example: [{"path": "app.py", "language": "Python", "content": "..."}]

        Returns:
            AnalysisResult with:
                - code_quality_score: Final weighted score (0-10)
                - files_analyzed: List of file paths
                - metrics: Dict with heuristic + LLM metrics

        Raises:
            ValueError: If code_files is empty or invalid
        """
        if not code_files:
            raise ValueError("code_files cannot be empty")

        # 1. Run heuristics analysis (30% weight)
        heuristics_metrics = self.calculate_code_quality_score(code_files)
        heuristics_score = self._normalize_heuristics_to_10_scale(heuristics_metrics)

        # 2. Run LLM analysis (70% weight)
        llm_result = self.analyze_with_llm(code_files)
        llm_score = llm_result.overall_quality_score

        # 3. Weighted average: 30% heuristics + 70% LLM
        final_score = (heuristics_score * 0.3) + (llm_score * 0.7)

        # 4. Merge metrics dictionaries
        merged_metrics = self._merge_metrics(heuristics_metrics, llm_result)

        # 5. Return AnalysisResult schema
        return AnalysisResult(
            code_quality_score=round(final_score, 1),
            files_analyzed=[f["path"] for f in code_files],
            metrics=merged_metrics
        )

    def calculate_code_quality_score(
        self,
        code_files: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Calculate code quality metrics using heuristic analysis.

        Stage 5.1 implementation.

        Args:
            code_files: List of dicts with keys: path, language, content

        Returns:
            Dict with heuristic metrics:
                - line_length_avg, line_length_max, lines_too_long_pct
                - function_length_avg, function_length_max
                - nesting_depth_avg, nesting_depth_max
                - comment_ratio
                - has_tests
                - has_type_hints
                - complexity_avg, complexity_max
        """
        if not code_files:
            raise ValueError("code_files cannot be empty")

        # Aggregate metrics across all files
        all_line_lengths = []
        all_function_lengths = []
        all_nesting_depths = []
        all_comment_ratios = []
        all_complexities = []
        has_tests = False
        has_type_hints = False

        for file in code_files:
            path = file.get("path", "")
            language = file.get("language", "Python")
            content = file.get("content", "")

            if not content:
                continue

            # Check if this is a test file
            if "test" in path.lower() or "_test" in path.lower() or "spec" in path.lower():
                has_tests = True

            # Analyze each metric
            line_metrics = self._analyze_line_lengths(content, language)
            all_line_lengths.append(line_metrics)

            func_metrics = self._detect_function_lengths(content, language)
            all_function_lengths.append(func_metrics)

            nesting_metrics = self._calculate_nesting_depth(content, language)
            all_nesting_depths.append(nesting_metrics)

            comment_ratio = self._calculate_comment_ratio(content, language)
            all_comment_ratios.append(comment_ratio)

            type_hints = self._detect_type_hints(content, language)
            if type_hints:
                has_type_hints = True

            complexity_metrics = self._calculate_complexity(content, language)
            all_complexities.append(complexity_metrics)

        # Aggregate results (handle empty lists properly for mean)
        line_length_values = [m["line_length_avg"] for m in all_line_lengths if m["line_length_avg"] > 0]
        line_length_avg = mean(line_length_values) if line_length_values else 0
        line_length_max = max([m["line_length_max"] for m in all_line_lengths], default=0)

        lines_too_long_values = [m["lines_too_long_pct"] for m in all_line_lengths if m["lines_too_long_pct"] >= 0]
        lines_too_long_pct = mean(lines_too_long_values) if lines_too_long_values else 0

        function_length_values = [m["function_length_avg"] for m in all_function_lengths if m["function_length_avg"] > 0]
        function_length_avg = mean(function_length_values) if function_length_values else 0
        function_length_max = max([m["function_length_max"] for m in all_function_lengths], default=0)
        function_count = sum([m["function_count"] for m in all_function_lengths])

        nesting_depth_values = [m["nesting_depth_avg"] for m in all_nesting_depths if m["nesting_depth_avg"] >= 0]
        nesting_depth_avg = mean(nesting_depth_values) if nesting_depth_values else 0
        nesting_depth_max = max([m["nesting_depth_max"] for m in all_nesting_depths], default=0)

        comment_ratio_values = [r for r in all_comment_ratios if r >= 0]
        comment_ratio = mean(comment_ratio_values) if comment_ratio_values else 0.0

        complexity_values = [m["complexity_avg"] for m in all_complexities if m["complexity_avg"] > 0]
        complexity_avg = mean(complexity_values) if complexity_values else 0
        complexity_max = max([m["complexity_max"] for m in all_complexities], default=0)
        complexity_total = sum([m["complexity_total"] for m in all_complexities])

        return {
            "line_length_avg": round(line_length_avg, 1) if line_length_avg else 0,
            "line_length_max": line_length_max,
            "lines_too_long_pct": round(lines_too_long_pct, 1) if lines_too_long_pct else 0.0,
            "function_length_avg": round(function_length_avg, 1) if function_length_avg else 0,
            "function_length_max": function_length_max,
            "function_count": function_count,
            "nesting_depth_avg": round(nesting_depth_avg, 1) if nesting_depth_avg else 0,
            "nesting_depth_max": nesting_depth_max,
            "comment_ratio": round(comment_ratio, 2),
            "has_tests": has_tests,
            "has_type_hints": has_type_hints,
            "complexity_avg": round(complexity_avg, 1) if complexity_avg else 0,
            "complexity_max": complexity_max,
            "complexity_total": complexity_total
        }

    def analyze_with_llm(
        self,
        code_files: List[Dict[str, str]]
    ) -> CodeQualityAnalysis:
        """
        Analyze code quality using LLM via OpenRouter.

        Stage 5.2 implementation.

        Args:
            code_files: List of dicts with keys: path, language, content

        Returns:
            CodeQualityAnalysis with:
                - overall_quality_score (0-10)
                - metrics (readability, maintainability, etc.)
                - strengths, weaknesses, recommendations

        Raises:
            ValueError: If code_files is empty
            APIError: If OpenRouter API call fails
        """
        if not code_files:
            raise ValueError("code_files cannot be empty")

        # Use OpenRouter provider to analyze code
        logger.info(f"Analyzing {len(code_files)} files with LLM...")
        result = self.openrouter_provider.analyze_code_quality(code_files)
        logger.info(f"LLM analysis complete. Score: {result.overall_quality_score}")

        return result

    # ========================================================================
    # Heuristic Analysis Methods (Stage 5.1)
    # ========================================================================

    def _analyze_line_lengths(
        self,
        code: str,
        language: str
    ) -> Dict[str, Any]:
        """
        Analyze line length metrics.

        Args:
            code: Source code string
            language: Programming language

        Returns:
            Dict with: line_length_avg, line_length_max, lines_too_long_pct
        """
        if not code or not code.strip():
            return {
                "line_length_avg": 0,
                "line_length_max": 0,
                "lines_too_long_pct": 0.0
            }

        lines = code.splitlines()
        if not lines:
            return {
                "line_length_avg": 0,
                "line_length_max": 0,
                "lines_too_long_pct": 0.0
            }

        # Calculate line lengths
        lengths = [len(line) for line in lines]

        # Count lines that are too long (>120 chars)
        too_long_count = sum(1 for length in lengths if length > 120)

        return {
            "line_length_avg": round(mean(lengths), 1) if lengths else 0,
            "line_length_max": max(lengths) if lengths else 0,
            "lines_too_long_pct": round((too_long_count / len(lines)) * 100, 1) if lines else 0.0
        }

    def _detect_function_lengths(
        self,
        code: str,
        language: str
    ) -> Dict[str, Any]:
        """
        Detect function/method lengths using language-specific patterns.

        Args:
            code: Source code string
            language: Programming language

        Returns:
            Dict with: function_length_avg, function_length_max, function_count
        """
        if not code or not code.strip():
            return {
                "function_length_avg": 0,
                "function_length_max": 0,
                "function_count": 0
            }

        # Get language-specific pattern
        pattern = FUNCTION_PATTERNS.get(language)
        if not pattern:
            # Unknown language, return zeros
            return {
                "function_length_avg": 0,
                "function_length_max": 0,
                "function_count": 0
            }

        lines = code.splitlines()
        function_lengths = []
        current_function_start = None
        current_function_indent = None

        for i, line in enumerate(lines):
            # Check if this is a function definition
            if re.match(pattern, line):
                # Save previous function length if any
                if current_function_start is not None:
                    length = i - current_function_start
                    if length > 0:
                        function_lengths.append(length)

                # Start new function
                current_function_start = i
                current_function_indent = len(line) - len(line.lstrip())

            # For Python-like languages, detect function end by indentation
            elif current_function_start is not None and language in ["Python", "Ruby"]:
                if line.strip():  # Non-empty line
                    indent = len(line) - len(line.lstrip())
                    # Function ends when we see code at same or lower indentation
                    if indent <= current_function_indent:
                        length = i - current_function_start
                        if length > 0:
                            function_lengths.append(length)
                        current_function_start = None
                        current_function_indent = None

        # Handle last function if code ends while still in function
        if current_function_start is not None:
            length = len(lines) - current_function_start
            if length > 0:
                function_lengths.append(length)

        if not function_lengths:
            return {
                "function_length_avg": 0,
                "function_length_max": 0,
                "function_count": 0
            }

        return {
            "function_length_avg": round(mean(function_lengths), 1),
            "function_length_max": max(function_lengths),
            "function_count": len(function_lengths)
        }

    def _calculate_nesting_depth(
        self,
        code: str,
        language: str
    ) -> Dict[str, Any]:
        """
        Calculate nesting depth (indentation levels or brace depth).

        Args:
            code: Source code string
            language: Programming language

        Returns:
            Dict with: nesting_depth_avg, nesting_depth_max
        """
        if not code or not code.strip():
            return {
                "nesting_depth_avg": 0,
                "nesting_depth_max": 0
            }

        lines = code.splitlines()
        depths = []

        if language == "Python" or language == "Ruby":
            # For Python/Ruby: use indentation levels
            for line in lines:
                if not line.strip():  # Skip empty lines
                    continue

                # Count indentation levels (4 spaces or 1 tab = 1 level)
                stripped = line.lstrip()
                indent_chars = len(line) - len(stripped)
                # Assume 4 spaces per indent level
                depth = indent_chars // 4
                depths.append(depth)
        else:
            # For brace-based languages: track cumulative brace depth
            brace_depth = 0
            for line in lines:
                if not line.strip():  # Skip empty lines
                    continue

                # Record depth BEFORE processing this line's braces
                depths.append(max(0, brace_depth))

                # Update brace depth for next lines
                opening = line.count('{')
                closing = line.count('}')
                brace_depth += opening - closing
                brace_depth = max(0, brace_depth)  # Don't go negative

        if not depths:
            return {
                "nesting_depth_avg": 0,
                "nesting_depth_max": 0
            }

        return {
            "nesting_depth_avg": round(mean(depths), 1),
            "nesting_depth_max": max(depths)
        }

    def _calculate_comment_ratio(
        self,
        code: str,
        language: str
    ) -> float:
        """
        Calculate ratio of comment lines to total lines.

        Args:
            code: Source code string
            language: Programming language

        Returns:
            Float: Comment ratio (0.0 to 1.0)
        """
        if not code or not code.strip():
            return 0.0

        patterns = COMMENT_PATTERNS.get(language, [])
        if not patterns:
            return 0.0

        lines = code.splitlines()
        if not lines:
            return 0.0

        comment_count = 0
        for line in lines:
            # Check if line contains a comment
            for pattern in patterns:
                if re.search(pattern, line):
                    comment_count += 1
                    break  # Count each line only once

        return round(comment_count / len(lines), 2)

    def _detect_type_hints(
        self,
        code: str,
        language: str
    ) -> bool:
        """
        Detect presence of type hints/annotations.

        Args:
            code: Source code string
            language: Programming language

        Returns:
            Bool: True if type hints detected, False otherwise
        """
        if not code or not code.strip():
            return False

        pattern = TYPE_HINT_PATTERNS.get(language)

        # Languages with built-in typing (always considered typed)
        if pattern is None:
            return language in ["Go", "Rust", "Java", "C", "C++"]

        # Check if pattern matches
        return bool(re.search(pattern, code))

    def _calculate_complexity(
        self,
        code: str,
        language: str
    ) -> Dict[str, Any]:
        """
        Calculate simplified cyclomatic complexity.

        Counts control flow keywords (if, for, while, etc.).

        Args:
            code: Source code string
            language: Programming language

        Returns:
            Dict with: complexity_avg, complexity_max, complexity_total
        """
        if not code or not code.strip():
            return {
                "complexity_avg": 0,
                "complexity_max": 0,
                "complexity_total": 0
            }

        # Count complexity keywords per line
        lines = code.splitlines()
        line_complexities = []
        total_complexity = 0

        for line in lines:
            line_lower = line.lower()
            complexity = 0

            for keyword in COMPLEXITY_KEYWORDS:
                complexity += line_lower.count(keyword)

            if complexity > 0:
                line_complexities.append(complexity)
            total_complexity += complexity

        if not line_complexities:
            return {
                "complexity_avg": 0,
                "complexity_max": 0,
                "complexity_total": 0
            }

        return {
            "complexity_avg": round(mean(line_complexities), 1),
            "complexity_max": max(line_complexities),
            "complexity_total": total_complexity
        }

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _normalize_heuristics_to_10_scale(
        self,
        metrics: Dict[str, Any]
    ) -> float:
        """
        Normalize heuristic metrics to 0-10 scale.

        Scoring rules:
        - Line length: +2 if avg < 100, +1 if avg < 120, 0 otherwise
        - Function length: +2 if avg < 30, +1 if avg < 50, 0 otherwise
        - Nesting depth: +2 if avg < 3, +1 if avg < 4, 0 otherwise
        - Comment ratio: +1 if ratio > 0.1, 0 otherwise
        - Type hints: +1 if detected
        - Complexity: +2 if avg < 5, +1 if avg < 8, 0 otherwise
        - Tests: +1 if has_tests

        Note: Maximum raw total is 11 points, but score is capped at 10.0

        Args:
            metrics: Dict with heuristic metrics

        Returns:
            Float: Normalized score (0-10), capped at 10.0
        """
        score = 0.0

        # Line length (max 2 points)
        line_avg = metrics.get("line_length_avg", 0)
        if line_avg < 100:
            score += 2
        elif line_avg < 120:
            score += 1

        # Function length (max 2 points)
        func_avg = metrics.get("function_length_avg", 0)
        if func_avg == 0:  # No functions found
            score += 1  # Neutral score
        elif func_avg < 30:
            score += 2
        elif func_avg < 50:
            score += 1

        # Nesting depth (max 2 points)
        nesting_avg = metrics.get("nesting_depth_avg", 0)
        if nesting_avg < 3:
            score += 2
        elif nesting_avg < 4:
            score += 1

        # Comment ratio (max 1 point)
        comment_ratio = metrics.get("comment_ratio", 0)
        if comment_ratio > 0.1:
            score += 1

        # Type hints (max 1 point)
        if metrics.get("has_type_hints", False):
            score += 1

        # Complexity (max 2 points)
        complexity_avg = metrics.get("complexity_avg", 0)
        if complexity_avg == 0:  # No complexity
            score += 2
        elif complexity_avg < 5:
            score += 2
        elif complexity_avg < 8:
            score += 1

        # Tests (max 1 point)
        if metrics.get("has_tests", False):
            score += 1

        # Cap at 10.0 to prevent AnalysisResult validation errors
        return min(round(score, 1), 10.0)

    def _merge_metrics(
        self,
        heuristics: Dict[str, Any],
        llm_result: CodeQualityAnalysis
    ) -> Dict[str, Any]:
        """
        Merge heuristic and LLM metrics into single dictionary.

        Args:
            heuristics: Heuristic metrics dict
            llm_result: LLM analysis result

        Returns:
            Dict with all metrics combined
        """
        # Start with all heuristic metrics
        merged = {**heuristics}

        # Extract LLM metric scores
        llm_metric_dict = {}
        for metric in llm_result.metrics:
            metric_name = metric.name.lower().replace(" ", "_") + "_score"
            llm_metric_dict[metric_name] = metric.score

        # Add LLM scores
        merged.update(llm_metric_dict)

        # Add LLM insights
        merged["strengths"] = llm_result.strengths
        merged["weaknesses"] = llm_result.weaknesses
        merged["recommendations"] = llm_result.recommendations
        merged["summary"] = llm_result.summary

        return merged
