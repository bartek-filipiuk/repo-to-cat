# LL-GIT-001: No AI Branding in Commit Messages

**Tech**: git | **Severity**: low | **Date**: 2025-10-08

## The Mistake
Including AI tool branding and co-authorship attribution in git commit messages without user consent.

## Why It's Wrong
- Clutters git history with unnecessary metadata
- User may not want to disclose AI usage in commits
- Not all projects/teams allow AI attribution
- Makes commits less professional

## The Fix
Never add AI branding or co-authorship lines to commits unless explicitly requested by the user.

**Bad:**
```bash
git commit -m "Stage 1.2: Docker & Database Setup

...commit message...

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Good:**
```bash
git commit -m "Stage 1.2: Docker & Database Setup

...commit message...

All Stage 1.2 checkboxes completed."
```

## How to Detect
- Review commit messages before pushing
- Check if user rejected the commit tool use
- User explicitly says "don't add"

## Prevention
- Default to clean commits (no AI attribution)
- Only add branding if user explicitly asks
- When user rejects commit, check the content they rejected
- Remember user preferences across sessions