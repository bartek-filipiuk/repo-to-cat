# LL-VALIDATION-001: Incomplete URL Segment Validation

**Tech**: Pydantic/FastAPI | **Severity**: high | **Date**: 2025-10-09

## The Mistake
GitHub URL validator only checked for minimum 2 parts after splitting, but didn't verify each part was non-empty. URLs like `https://github.com/owner/` or `https://github.com//repo` passed validation and would fail later at GitHub API call.

## Why It's Wrong
- Fails late (at API call) instead of early (at validation)
- Empty segments cause confusing errors downstream
- Violates "fail fast" principle

## The Fix
After splitting URL and checking length, verify each required segment is truthy.

```python
# ❌ Bad - only checks count
parts = url.replace("https://github.com/", "").split("/")
if len(parts) < 2:
    raise ValueError("GitHub URL must include owner and repository name")

# ✅ Good - checks count AND content
parts = url.replace("https://github.com/", "").split("/")
if len(parts) < 2:
    raise ValueError("GitHub URL must include owner and repository name")
if not parts[0] or not parts[1]:
    raise ValueError("GitHub URL must have non-empty owner and repository name")
```

## How to Detect
- Code review: Look for URL/path validation that splits strings
- Test edge cases: trailing slashes, double slashes, empty segments
- Check: Does validation verify segment content, not just count?

## Prevention
- **Always validate segment content after splitting strings**
- Test with malformed inputs: `value/`, `//value`, `value//`, etc.
- For path validation: check both `len(parts)` AND `all(parts)`
- Use Pydantic field validators with comprehensive edge case tests
