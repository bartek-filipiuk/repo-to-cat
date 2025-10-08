# 🚀 Repo-to-Cat: Init Prompt

Use this to start/continue work on Repo-to-Cat in a new conversation.

---

## 📋 Main Initialization Prompt

```
I'm working on "Repo-to-Cat" - GitHub repository analyzer that generates cat images based on code quality.

CONTEXT FILES (read in order):
1. @HANDOFF.md - Development checklist (150+ checkboxes, 13 stages) - CHECK THIS FIRST
2. @DEVELOPMENT_RULES.md - TDD workflow, commit format, testing rules
3. @PRD.md - Product requirements, API specs, tech stack (reference only)
4. @01-setup.md or latest session file - Previous session summary

TECH STACK:
- Backend: FastAPI, Python 3.11+, PostgreSQL
- AI: LangChain 0.3.0 + LangGraph 0.2.74
- LLM: OpenRouter (google/gemini-2.5-flash)
- Image: Together.ai (FLUX.1.1-pro, 768x432)
- GitHub: PyGithub + Contents API (no cloning)
- Testing: pytest + pytest-asyncio (80% coverage)

WORKFLOW:
1. Check @HANDOFF.md for current stage and next checkbox
2. Work on ONE checkbox at a time
3. For code: TDD (tests first, then implement)
4. After each checkbox: run tests, request review, mark ✅
5. Follow stage completion checklist before creating PR

MY REQUEST:
[Your instruction here - examples below]
```

---

## 🎯 Quick Start Variations

### Continue Work
```
Continuing Repo-to-Cat project.

Read: @HANDOFF.md @DEVELOPMENT_RULES.md @01-setup.md

Check HANDOFF.md for completed checkboxes (✅), report current stage and next checkbox, then continue with TDD workflow.
```

### Start Specific Stage
```
Repo-to-Cat - start Stage X.Y: [Stage Name]

Read: @HANDOFF.md @DEVELOPMENT_RULES.md @PRD.md

Work on Stage X.Y checkboxes one at a time. Follow TDD, run tests after each, request review before moving forward.
```

### Debug/Fix
```
Repo-to-Cat - fix issue: [describe problem]

Read: @HANDOFF.md @DEVELOPMENT_RULES.md

Issue: [description]
Files: [list]

Help: identify root cause, write/fix tests, implement fix, verify tests pass.
```

---

## 📂 Context Files Reference

**Essential (always read):**
- `HANDOFF.md` - Development checklist with stage completion checklists
- `DEVELOPMENT_RULES.md` - TDD workflow, commit format, PR process

**Reference (read as needed):**
- `PRD.md` - Product requirements, API specs, architecture
- `PROJECT_STRUCTURE.md` - Directory layout and file organization
- `FILE_SELECTION_STRATEGY.md` - Algorithm for selecting files to analyze
- `01-setup.md` (or latest) - Previous session summary

**Config:**
- `.env.example` - Environment variables template
- `requirements.txt` - Python dependencies
- `docker-compose.yml` - PostgreSQL service

---

## 🔄 Stage Completion Process

Before creating PR for each stage:

1. ✅ All stage checkboxes marked complete
2. ✅ Run: `pytest tests/ -v --cov=app --cov-report=term`
3. ✅ Coverage ≥ 80% for new code
4. ✅ Stage-specific verification (see HANDOFF.md completion checklist)
5. ✅ All tests passing
6. ✅ Committed on feature branch: `feature/stage-X.Y-description`
7. ✅ Create PR to `main` with `gh pr create`
