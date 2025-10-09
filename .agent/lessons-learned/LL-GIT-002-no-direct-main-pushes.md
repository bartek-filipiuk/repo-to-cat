# LL-GIT-002: No Direct Pushes to Main Branch

**Tech**: Git | **Severity**: high | **Date**: 2025-10-09

## The Mistake
Pushed lesson learned documentation directly to `main` branch instead of creating a PR, bypassing code review process even for markdown files.

## Why It's Wrong
- Bypasses mandatory code review (violates project rule #2)
- No visibility for team on what changed
- Can't be easily rolled back if mistake found
- Sets bad precedent that "small changes" can skip process
- ALL changes need review - code, docs, config, etc.

## The Fix
**ALWAYS use PR workflow, even for documentation:**

```bash
# ❌ Bad - direct to main
git checkout main
git add .agent/lessons-learned/LL-XXX.md
git commit -m "docs: add lesson learned"
git push origin main  # NEVER DO THIS!

# ✅ Good - via PR
git checkout -b docs/add-lesson-learned-xxx
git add .agent/lessons-learned/LL-XXX.md
git commit -m "docs: Add LL-XXX lesson learned"
git push origin docs/add-lesson-learned-xxx
gh pr create --title "docs: Add LL-XXX" --body "..." --base main
```

## How to Detect
- Check git history: `git log --oneline --graph main`
- If you see direct commits without PR merge, that's a red flag
- Set up branch protection on `main` to prevent this

## Prevention
- **Enable branch protection** on `main` in GitHub settings
- Require PR reviews before merging
- Add rule to DEVELOPMENT_RULES.md (already done)
- Add reminder to INIT_PROMPT.md (already done)
- Create git pre-push hook to warn when pushing to main
- Make it muscle memory: branch → commit → push → PR → review → merge
