# 🚀 Repo-to-Cat: Project Initialization Prompt

Use this prompt to initialize or continue working on the Repo-to-Cat project in a new conversation (no history).

---

## 📋 Full Initialization Prompt

```
I'm working on "Repo-to-Cat" - a GitHub repository quality analyzer that generates unique cat images based on code quality.

PROJECT CONTEXT:
Read these files in order to understand the project:
1. @PRD.md - Complete product requirements and technical architecture
2. @HANDOFF.md - Development checklist with 150+ checkboxes (13 stages)
3. @PROJECT_STRUCTURE.md - Directory hierarchy and file organization
4. @FILE_SELECTION_STRATEGY.md - Algorithm for selecting 3-5 files to analyze
5. @DEVELOPMENT_RULES.md - Core development principles (TDD, incremental)
6. @CONVERSATION_FLOW.md or @init-flow.md - Previous session summary

TECH STACK:
- Backend: FastAPI + Python 3.11+
- AI: LangChain 0.3.0 + LangGraph 0.2.74
- LLM: OpenRouter (google/gemini-2.5-flash)
- Image: Together.ai (FLUX.1.1-pro, 768x432, 20 steps)
- GitHub: PyGithub + GitHub Contents API (no repo cloning)
- Database: PostgreSQL + SQLAlchemy + Alembic (Docker)
- Testing: pytest + pytest-asyncio (80% coverage target)

CURRENT STATUS:
Check @HANDOFF.md to see which checkboxes are completed (✅).
Report current stage and next checkbox to work on.

WORKFLOW:
1. Work on ONE checkbox at a time from HANDOFF.md
2. For logic/code: Write tests FIRST (TDD), then implement
3. For configs/docs: Create files, then manual verification
4. After each checkbox: Run tests, request review, mark complete
5. Commit with format: "Stage X.Y: Brief description\n\n- Changes\n✅ Tests pass"

MY REQUEST:
[Specify what you want to do, e.g.:]
- "Continue from where we left off" (I'll check HANDOFF.md and continue)
- "Start Stage 1.1: Basic Project Structure" (I'll work on first 5 checkboxes)
- "Implement Stage 3.1: GitHub Service" (I'll create github_service.py with tests)
- "Review and fix failing tests in [file]" (I'll debug and fix)
- "Add feature: [description]" (I'll update HANDOFF.md and implement)

IMPORTANT RULES:
- Always follow @DEVELOPMENT_RULES.md (TDD, incremental, 80% coverage)
- Use Context7 MCP for latest docs: langchain, langgraph, openrouter, together.ai
- Never skip tests for logic/code (only skip for dirs/configs/docs)
- One checkbox = one reviewable unit of work
- Update HANDOFF.md checkbox status after completion
```

---

## 🎯 Quick Start Variations

### Continue Work (Check Status First)
```
I'm working on Repo-to-Cat project.

Read: @PRD.md @HANDOFF.md @DEVELOPMENT_RULES.md

Check HANDOFF.md for completed checkboxes (✅), report current status, and continue from the next uncompleted checkbox. Follow TDD workflow from DEVELOPMENT_RULES.md.
```

### Start Fresh (Stage 1.1)
```
I'm starting Repo-to-Cat project implementation.

Read: @PRD.md @HANDOFF.md @PROJECT_STRUCTURE.md @DEVELOPMENT_RULES.md

Start Stage 1.1: Basic Project Structure (5 checkboxes). Work on one checkbox at a time, follow TDD where applicable, request review after each.

Tech stack: FastAPI, LangGraph, OpenRouter (gemini-2.5-flash), Together.ai (FLUX.1.1-pro)
```

### Specific Stage
```
I'm working on Repo-to-Cat - continue with Stage 3.1: GitHub Service Integration.

Read: @PRD.md @HANDOFF.md @FILE_SELECTION_STRATEGY.md @DEVELOPMENT_RULES.md

Implement GitHub service with TDD:
1. Write tests first for get_repository_metadata()
2. Implement with GitHub Contents API (no cloning)
3. Follow file selection strategy (5 priorities)

Request review after each checkpoint.
```

### Debug/Fix Issues
```
I'm working on Repo-to-Cat - need to debug/fix [describe issue].

Read: @PRD.md @HANDOFF.md @DEVELOPMENT_RULES.md

Current issue: [describe problem]
Affected files: [list files]

Help me:
1. Identify root cause
2. Write/fix tests
3. Implement fix
4. Verify all tests pass
```

### Add New Feature
```
I'm working on Repo-to-Cat - want to add new feature: [describe feature].

Read: @PRD.md @HANDOFF.md @DEVELOPMENT_RULES.md

Feature request: [detailed description]

Help me:
1. Update HANDOFF.md with new checkboxes
2. Design implementation approach
3. Write tests first (TDD)
4. Implement feature incrementally
5. Update documentation
```

---

## 📂 Essential Files Reference

**Planning & Architecture:**
- `PRD.md` - Product requirements, API specs, tech stack
- `HANDOFF.md` - Development checklist (150+ checkboxes, 13 stages)
- `PROJECT_STRUCTURE.md` - Directory layout, file descriptions
- `FILE_SELECTION_STRATEGY.md` - 5-priority file selection algorithm
- `DEVELOPMENT_RULES.md` - TDD, incremental dev, code review rules

**Progress Tracking:**
- `CONVERSATION_FLOW.md` - Detailed technical session log
- `init-flow.md` - Concise session summary
- `INIT_PROMPT.md` - This file (reusable init prompt)

**Configuration:**
- `.env.example` - Environment variables template
- `requirements.txt` - Python dependencies
- `docker-compose.yml` - Docker services (PostgreSQL)

**Code Structure:**
```
app/
├── api/          - FastAPI routes, Pydantic schemas
├── core/         - Config, database, exceptions
├── services/     - Business logic (github, analysis, image)
├── providers/    - External APIs (openrouter, together_ai)
├── langgraph/    - Workflow orchestration (10 nodes)
├── models/       - SQLAlchemy ORM models
└── utils/        - Helpers, validators

config/           - Cat attribute mappings
tests/            - Unit + integration tests
```

---

## 🔄 Workflow Checklist

When starting a new session:

1. ✅ Use initialization prompt above
2. ✅ I read all referenced files (@PRD.md, etc.)
3. ✅ I report current status from HANDOFF.md
4. ✅ I identify next uncompleted checkbox
5. ✅ I ask if you want to continue or work on something specific
6. ✅ Work begins following TDD workflow

---

## 🎯 Example Usage

### Morning Session Start:
```
Good morning! Continuing Repo-to-Cat project.

Read: @PRD.md @HANDOFF.md @DEVELOPMENT_RULES.md @init-flow.md

Check current progress in HANDOFF.md and continue from the next incomplete checkbox. Let's work on one checkbox at a time with TDD approach.
```

### Evening Continue:
```
Continuing Repo-to-Cat from this afternoon.

Read: @HANDOFF.md @CONVERSATION_FLOW.md

Resume from where we left off. Show me the last completed checkbox and next one to work on.
```

### Weekend Deep Dive:
```
Weekend session for Repo-to-Cat - want to make significant progress.

Read: @PRD.md @HANDOFF.md @DEVELOPMENT_RULES.md

Let's complete an entire stage today (e.g., Stage 3: GitHub Service Integration). Work through all checkboxes with TDD, run tests after each, and commit after each checkpoint.

I'll review and approve each checkpoint. Let's aim for high quality over speed.
```

---

## 🚨 Important Reminders

**Always:**
- ✅ Read context files before starting
- ✅ Follow TDD for all logic/code
- ✅ One checkbox at a time
- ✅ Run tests after each change
- ✅ Update HANDOFF.md status
- ✅ Commit with descriptive message

**Never:**
- ❌ Skip tests for logic/code
- ❌ Work on multiple checkboxes simultaneously
- ❌ Commit without running tests
- ❌ Move to next checkbox without review
- ❌ Modify files without updating documentation

**Tech Stack Specifics:**
- LLM Model: `google/gemini-2.5-flash` via OpenRouter
- Image Model: `black-forest-labs/FLUX.1.1-pro` (768x432, 20 steps)
- GitHub: Use Contents API, NO repo cloning
- File Selection: 5-priority algorithm (README → Entry → Core → Test → Config)
- Database: PostgreSQL with JSONB for analysis_data and cat_attributes

---

## 📊 Progress Tracking Template

After each session, update status:

```markdown
## Session [Date]
**Stage:** [e.g., 1.1 Basic Project Structure]
**Checkboxes Completed:** [e.g., 3/5]
**Status:** [e.g., ✅ On track / ⚠️ Blocked / ❌ Issues]

**Completed:**
- [x] Checkbox 1 description
- [x] Checkbox 2 description

**In Progress:**
- [ ] Checkbox 3 description

**Next Session:**
- Continue with Checkbox 3
- Then move to Checkbox 4-5

**Notes:**
- Any blockers, decisions, or important findings
```

---

## 💡 Pro Tips

1. **Use init-flow.md** for quick context (50 lines vs 500 in CONVERSATION_FLOW.md)
2. **Check HANDOFF.md first** - it's your single source of truth for progress
3. **Reference FILE_SELECTION_STRATEGY.md** when implementing GitHub file selection
4. **Use Context7 MCP** for latest library docs (langchain, langgraph, etc.)
5. **Commit format matters** - use the template from DEVELOPMENT_RULES.md
6. **80% test coverage** is the target - use `pytest --cov` to check
7. **One checkbox = one commit** - keeps git history clean and reviewable

---

## 🔗 Quick Links

**GitHub API Endpoints Used:**
- `GET /repos/{owner}/{repo}` - Metadata
- `GET /repos/{owner}/{repo}/languages` - Detect language
- `GET /repos/{owner}/{repo}/git/trees/{sha}?recursive=1` - File tree
- `GET /repos/{owner}/{repo}/contents/{path}` - Raw file content

**API Keys Needed (.env):**
```
GITHUB_TOKEN=ghp_xxxxx
OPENROUTER_API_KEY=sk-or-xxxxx
TOGETHER_API_KEY=xxxxx
DATABASE_URL=postgresql://user:pass@localhost:5432/repo_to_cat
```

**Development Commands:**
```bash
# Install dependencies
pip3 install -r requirements.txt

# Run tests
pytest tests/ -v --cov=app --cov-report=html

# Run specific test
pytest tests/unit/test_config.py -v

# Start FastAPI
uvicorn app.main:app --reload

# Database migrations
alembic upgrade head

# Docker
docker-compose up -d
```

---

**Version:** 1.0
**Last Updated:** 2025-10-07
**Project Status:** Planning Complete, Ready for Stage 1.1
