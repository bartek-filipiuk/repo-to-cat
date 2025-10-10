# LL-TESTING-001: Missing Edge Case Tests in Heuristic Analysis

**Tech**: Python/pytest | **Severity**: high | **Date**: 2025-01-10

## The Mistake
Implemented heuristic analysis with basic tests but missed critical edge cases: (1) cumulative state tracking for brace-based languages, and (2) score boundary validation when perfect scores exceed limits.

## Why It's Wrong
- Line-by-line brace counting (`line.count('{')`) doesn't track cumulative nesting depth
- Scoring rubric totaled 11 points but claimed max was 10, causing validation errors
- Basic "happy path" tests passed (37/37) but didn't catch production bugs
- Both bugs would cause incorrect scores in production for common scenarios

## The Fix
Test edge cases explicitly: nested structures in multiple languages, boundary conditions (perfect scores), and validator constraints.

```python
# ❌ Bad: Only test happy path
def test_nesting_depth_basic():
    code = "if (x) { y(); }"
    assert depth > 0  # Passes but shallow

# ✅ Good: Test cumulative depth
def test_nesting_depth_nested():
    code = """if (x) {
        for (i=0; i<10; i++) {
            console.log(i);  // Should be depth=2
        }
    }"""
    assert result["nesting_depth_max"] >= 2
```

## How to Detect
- Code review: "Does this track state across lines?"
- Ask: "What happens with perfect/extreme input?"
- Check: Does validator max match scoring max?

## Prevention
- Test edge cases for stateful algorithms (cumulative tracking, state machines)
- Test boundary conditions: min (0), max (10), and out-of-bounds (11)
- Verify implementation matches spec (claimed "max 10" but code allowed 11)
- Test multiple languages when code is language-specific
