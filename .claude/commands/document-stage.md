---
description: Generate comprehensive documentation for a completed development stage
---

You are helping document a completed development stage for the Repo-to-Cat project.

## Your Task

Create **multiple focused documentation files** based on what was accomplished in a development stage, using a **hybrid approach** that auto-detects changes but asks the user for narrative and purpose.

---

## Process

### Step 1: Detect Stage Information

**Auto-detect from branch name:**
```bash
git branch --show-current
# Example: feature/stage-1.3-fastapi-skeleton
```

**If unable to detect, ask user:**
- What stage number is this? (e.g., 1.3)
- What's the stage name? (e.g., "FastAPI Skeleton")
- What branch are you on?

### Step 2: Analyze What Changed

**Auto-detect files changed:**
```bash
# Get files changed in this branch vs main
git diff --name-status main...HEAD

# Get new files
git diff --name-status --diff-filter=A main...HEAD

# Get modified files
git diff --name-status --diff-filter=M main...HEAD
```

**Auto-detect tests added:**
```bash
# Find new test files
git diff --name-status main...HEAD | grep "test_"

# Count tests
grep -r "def test_" tests/ --include="*.py" | wc -l
```

**Auto-detect Docker/Database changes:**
```bash
# Check if Docker files changed
git diff --name-status main...HEAD | grep -E "(Dockerfile|docker-compose)"

# Check if migrations added
ls alembic/versions/ | wc -l
```

**Present findings to user:**
```
I detected the following changes:
- 15 files created
- 8 files modified
- 3 new test files (12 tests total)
- Docker configuration added
- 1 new Alembic migration
```

### Step 3: Ask User Key Questions

**About Purpose & Capabilities:**
1. **What's the main purpose of this stage?**
   - Example: "Set up Docker and PostgreSQL database infrastructure"

2. **What can users DO now that they couldn't before?**
   - Example: "Run PostgreSQL in Docker, connect from host, apply migrations"

3. **What are the key features or components added?**
   - Example: "Docker Compose, Alembic migrations, SQLAlchemy models, database tests"

**About Usage:**
4. **What are the key setup/startup commands?**
   - Example: "docker compose up -d, alembic upgrade head"

5. **How do users verify it's working?**
   - Example: "docker compose ps, pytest tests/unit/test_database.py"

6. **What's the typical development workflow for this stage?**
   - Example: "Start DB → Apply migrations → Run tests → Make changes"

**About Troubleshooting:**
7. **What common issues did you encounter during development?**
   - Example: "Port conflicts with local PostgreSQL, connection timeouts"

8. **How did you solve them?**
   - Example: "Changed port to 5434, added health checks"

**About Next Steps:**
9. **What comes next in the development process?**
   - Example: "Stage 1.3: FastAPI Skeleton"

### Step 4: Determine Documentation Structure

**Ask user which guides to create/update:**

Based on the changes detected, I recommend creating:
- [x] `docs/docker-setup.md` (Docker detected)
- [x] `docs/database-guide.md` (Database detected)
- [x] `docs/testing-guide.md` (Tests detected)
- [ ] `docs/api-guide.md` (No API changes)
- [x] `docs/stages/stage-X.Y-summary.md`

**Should I:**
- A) Create all recommended guides
- B) Create only the stage summary (you'll write guides manually)
- C) Let me customize which guides to create

### Step 5: Generate Documentation

**For each focused guide:**

#### Docker Setup Guide Template
- Overview (what Docker is used for)
- Prerequisites
- Quick Start (essential commands)
- Configuration (docker-compose.yml explanation)
- Common commands (start, stop, logs, build)
- Troubleshooting (port conflicts, connection issues)
- Best practices
- Links to related docs

#### Database Guide Template
- Overview (database schema, tools)
- Quick Start (connection string)
- Schema reference (tables, fields)
- psql commands
- Alembic migrations (create, apply, rollback)
- CRUD operations from Python
- Backup & restore
- Troubleshooting
- GUI tools recommendation

#### Testing Guide Template
- Overview (test framework, coverage target)
- Quick Start (run tests command)
- Test organization (directory structure)
- Running tests (specific files, patterns, output control)
- Code coverage (generate reports)
- Test descriptions (what each test does)
- Writing new tests (examples)
- Best practices
- Troubleshooting

#### API Guide Template
- Overview (endpoints, authentication)
- Quick Start (server startup, test request)
- Endpoint reference (method, path, request/response)
- Authentication
- Error handling
- Testing API (curl examples)
- Swagger UI usage
- Troubleshooting

#### Stage Summary Template
- Status & metadata (PR link, branch, date)
- Overview (what was built, what you can do now)
- What Was Built (numbered sections for each component)
- Quick Start (step-by-step getting started)
- File Reference (new files, modified files)
- Verification Checklist
- Common Tasks
- Troubleshooting (top 3-5 issues)
- Dependencies Added
- What's Next
- Related Documentation (links to guides)
- Key Learnings
- Metrics (files changed, tests added, coverage)

### Step 6: Create/Update Files

**Write documentation files:**
1. Create `docs/stages/` directory if needed
2. Write focused guide files to `docs/`
3. Write stage summary to `docs/stages/stage-X.Y-summary.md`
4. Overwrite existing files (always latest version)

**Update README.md:**
Add link to new stage documentation in main README if relevant.

### Step 7: Provide Summary

Give the user:
```
✅ Documentation created for Stage X.Y!

Files created:
- docs/docker-setup.md (2.5 KB)
- docs/database-guide.md (4.1 KB)
- docs/testing-guide.md (3.2 KB)
- docs/stages/stage-X.Y-summary.md (5.8 KB)

Quick access:
- Stage summary: docs/stages/stage-X.Y-summary.md
- Docker guide: docs/docker-setup.md

Next steps:
1. Review generated docs for accuracy
2. Commit docs with stage code: git add docs/
3. Continue to Stage X.Z
```

---

## Documentation Principles

### Content Guidelines

1. **Be practical** - Focus on "how to" not "what is"
2. **Include examples** - Show actual commands and expected output
3. **Be comprehensive** - Cover setup, usage, troubleshooting
4. **Link related docs** - Cross-reference other guides
5. **Keep updated** - Overwrite old docs with latest info

### Structure Guidelines

1. **Start with Quick Start** - Get users running ASAP
2. **Organize by task** - Group related commands together
3. **Use consistent formatting** - Same structure across all guides
4. **Add troubleshooting** - Address common pain points
5. **Include next steps** - Link to what comes after

### Writing Style

1. **Use imperative voice** - "Run the command" not "You should run"
2. **Short paragraphs** - Max 3-4 sentences
3. **Code blocks for commands** - Always use ```bash
4. **Headers for scanning** - Make docs skimmable
5. **Concrete examples** - Real repos, realistic data

---

## Auto-Detection Capabilities

### What Gets Auto-Detected

✅ Stage number (from branch name)
✅ Files created/modified (git diff)
✅ Tests added (grep for test_ functions)
✅ Docker changes (Dockerfile, docker-compose.yml)
✅ Database changes (Alembic migrations, models)
✅ API changes (routes, schemas, main.py)
✅ Dependencies added (requirements.txt diff)

### What Requires User Input

❓ Purpose and "why" (user's intent)
❓ Key capabilities unlocked
❓ Setup steps and workflow
❓ Common issues encountered
❓ Solutions to problems
❓ Best practices learned
❓ What comes next

---

## Example Interaction

```
Assistant: I'll help document Stage 1.3. Let me analyze what changed...

[Runs git diff, finds files]

I detected:
- 12 files created
- 5 files modified
- 2 new test files (8 tests)
- FastAPI main.py created
- New API routes added

Great! Now some questions:

1. What's the main purpose of Stage 1.3?
User: Set up FastAPI skeleton with basic server and health check endpoint

2. What can users do now?
User: Start FastAPI server, access Swagger UI, call health endpoint

3. Key setup commands?
User: uvicorn app.main:app --reload

4. How to verify it works?
User: curl http://localhost:8000/health and open /docs

5. Common issues?
User: Import errors if dependencies not installed, port 8000 conflicts

6. How did you fix them?
User: pip install -r requirements.txt, change port in config

[Generates docs...]

✅ Documentation created!
- docs/api-guide.md
- docs/stages/stage-1.3-summary.md

Ready to commit!
```

---

## Special Cases

### Stage Has No Tests Yet
- Skip testing-guide.md
- Note in summary: "Tests will be added in future stage"

### Stage Modifies Existing Infrastructure
- Update existing guide files
- Note "Updated: YYYY-MM-DD" at top
- Add changelog section

### Stage Is Bug Fix or Refactor
- Create brief summary only
- No need for new guides
- Link to original stage docs

### Stage Adds New Tool/Service
- Create dedicated guide (e.g., `docs/redis-guide.md`)
- Update stage summary with link

---

## Output Format

**All documentation files:**
- Markdown (.md)
- UTF-8 encoding
- Unix line endings (LF)
- Last Updated date at top
- Clear section headers
- Code blocks with language hints
- Links to related docs at bottom

**Naming conventions:**
- Guides: `docs/{topic}-guide.md` (lowercase, hyphenated)
- Summaries: `docs/stages/stage-{X.Y}-{name}.md`
- Keep filenames short and descriptive

---

## Best Practices

### Before Generating

1. ✅ Ensure stage is complete (all tests passing)
2. ✅ Code is committed to feature branch
3. ✅ PR is created (include link in summary)
4. ✅ Run through stage manually to verify steps

### During Generation

1. ✅ Review auto-detected changes for accuracy
2. ✅ Provide detailed answers to questions
3. ✅ Include actual error messages seen
4. ✅ Note any gotchas or surprises

### After Generation

1. ✅ Review generated docs for accuracy
2. ✅ Test commands actually work
3. ✅ Fix any errors or omissions
4. ✅ Commit docs with stage code
5. ✅ Link from main README if needed

---

Now, let's document the stage! What stage number are we documenting?
