# 🎨 Repo-to-Cat Frontend: Init Prompt

Use this to start/continue frontend work on Repo-to-Cat in a new conversation.

---

## 📋 Main Initialization Prompt for Frontend

```
I'm working on the FRONTEND for "Repo-to-Cat" - an Astro SSR application with authentication that allows users to generate cat images from GitHub repositories.

CONTEXT FILES (read in order):
1. @HANDOFF_FRONT.md - Frontend development checklist (70+ tasks, 10 stages F1-F10) - CHECK THIS FIRST
2. @docs/frontend-guide.md - Comprehensive frontend development guide
3. @docs/workflow-guide.md - Backend workflow (understand the API)
4. @docs/api-endpoints.md - API reference (all endpoints we'll call)
5. @CLAUDE.md - Project instructions and rules

TECH STACK - FRONTEND:
- Framework: Astro 4.x with SSR (Node adapter)
- Styling: Tailwind CSS (Oxide-inspired: dark #0a0a0a, green #00ffa3)
- Auth: Session-based (httpOnly cookies, 7-day expiration)
- API Client: TypeScript fetch wrappers
- Port: 4321 (Backend on 8000)

TECH STACK - BACKEND (what we're consuming):
- Backend: FastAPI (Python 3.11+)
- Database: PostgreSQL (users, sessions, generations tables)
- Auth Endpoints: /auth/login, /auth/logout, /auth/me
- Generation Endpoints: POST /generate, GET /generations, GET /generation/:id
- Processing Time: 15-25 seconds (requires polling)

PROJECT STATUS:
- Backend: ✅ Stage 8 complete - API ready with stories & memes
- Frontend: 🚧 In progress - See HANDOFF_FRONT.md for current stage

DESIGN INSPIRATION:
- Oxide Computer: https://oxide.computer/
- Dark theme (#0a0a0a) with green accents (#00ffa3)
- Minimalist, technical aesthetic
- Clean typography (Inter font)

WORKFLOW:
1. Check @HANDOFF_FRONT.md for current stage (F1-F10) and next checkbox
2. Work on ONE checkbox at a time (incremental development)
3. For backend (F1-F3): Write tests first, then implement (TDD)
4. For frontend (F4-F8): Build component, test manually, update docs
5. After each checkbox: test thoroughly, mark ✅
6. After each stage: Update documentation as specified in task
7. **IMPORTANT:** Clean commits (no AI branding - see LL-GIT-001)

AUTHENTICATION FLOW:
1. User enters username/password (accounts created manually in DB)
2. POST /auth/login → FastAPI validates → returns session token
3. Astro sets httpOnly cookie with token
4. Middleware validates session on protected routes
5. Session expires after 7 days

GENERATION FLOW:
1. User submits GitHub URL on dashboard
2. POST /generate → get generation_id (immediate response)
3. Poll GET /generation/:id every 2 seconds
4. Check status: "processing" or "completed"
5. Redirect to detail page when completed

MY REQUEST:
[Your instruction here - examples below]
```

---

## 🎯 Quick Start Variations

### Continue Frontend Work
```
Continuing Repo-to-Cat FRONTEND project.

Read: @HANDOFF_FRONT.md @docs/frontend-guide.md @CLAUDE.md

Check HANDOFF_FRONT.md for completed checkboxes (✅), identify current stage (F1-F10), report next task, then continue with incremental workflow.
```

### Start Specific Frontend Stage
```
Repo-to-Cat FRONTEND - start Stage FX: [Stage Name]

Read: @HANDOFF_FRONT.md @docs/frontend-guide.md @docs/api-endpoints.md

Work on Stage FX checkboxes one at a time. For backend tasks (F1-F3): use TDD. For frontend tasks (F4-F8): build + test manually. Update docs after stage complete.
```

### Backend Auth Work (Stages F1-F3)
```
Repo-to-Cat FRONTEND - Backend auth implementation

Read: @HANDOFF_FRONT.md (Stage F1/F2/F3) @docs/database-guide.md @docs/api-endpoints.md

Working on backend authentication system:
- Database migrations (add password_hash, sessions table, user_id FK)
- Auth utilities (bcrypt, session management)
- Auth endpoints (/auth/login, /auth/logout, /auth/me)
- Protect /generate endpoint

Follow TDD: write tests first, implement, run tests, mark complete.
```

### Frontend UI Work (Stages F4-F8)
```
Repo-to-Cat FRONTEND - Astro UI implementation

Read: @HANDOFF_FRONT.md (Stage F4/F5/F6/F7/F8) @docs/frontend-guide.md

Working on Astro frontend:
- Setup: SSR, Tailwind, project structure
- Auth UI: Login page, middleware, session helpers
- Dashboard: Generate form with polling, generation list/cards
- Detail: Full-width image, story, repo data
- Design: Oxide-inspired (dark bg, green accents)

Test manually after each component. Update docs after each stage.
```

### Debug Frontend Issue
```
Repo-to-Cat FRONTEND - fix issue: [describe problem]

Read: @HANDOFF_FRONT.md @docs/frontend-guide.md

Issue: [description]
Component/File: [path]
Expected: [behavior]
Actual: [behavior]

Help: identify root cause, implement fix, test manually, verify working.
```

### Design Implementation
```
Repo-to-Cat FRONTEND - Implement Oxide-inspired design

Read: @HANDOFF_FRONT.md (Stage F8) @docs/frontend-guide.md

Design reference: https://oxide.computer/
Colors: dark #0a0a0a, green #00ffa3, text #e5e5e5
Requirements: Minimalist, technical, responsive, smooth hover effects

Implement design system in Tailwind config + global styles, apply to all components.
```

---

## 📂 Context Files Reference

**Essential (always read):**
- `HANDOFF_FRONT.md` - Frontend development checklist (F1-F10 stages, 70+ tasks)
- `docs/frontend-guide.md` - Complete frontend development guide
- `CLAUDE.md` - Project instructions and commit rules

**Backend Understanding (read as needed):**
- `docs/api-endpoints.md` - All API endpoints with examples
- `docs/workflow-guide.md` - How backend processes requests (11-node pipeline)
- `docs/response-examples.md` - JSON response structures
- `docs/database-guide.md` - Database schema and migrations

**Design Reference:**
- Oxide Computer: https://oxide.computer/ (for design inspiration)
- Screenshot in project: Shows dark theme with green accents

**Project Structure:**
```
repo-to-cat/
├── app/                    # Backend (FastAPI)
│   ├── api/               # Routes, schemas, auth
│   ├── models/            # SQLAlchemy models
│   ├── utils/             # Auth utilities
│   └── langgraph/         # Workflow
├── frontend/              # Frontend (Astro) - OUR WORK
│   ├── src/
│   │   ├── pages/         # Routes (login, dashboard, detail)
│   │   ├── components/    # Reusable components
│   │   ├── lib/           # API client, auth helpers
│   │   ├── styles/        # Global styles
│   │   └── middleware.ts  # Auth middleware
│   ├── astro.config.mjs   # Astro SSR config
│   └── tailwind.config.mjs # Tailwind with Oxide colors
├── docs/                  # Documentation
├── HANDOFF_FRONT.md       # Frontend checklist
└── CLAUDE.md              # Project instructions
```

---

## 🔄 Stage Completion Process

Before marking each frontend stage complete:

### Backend Stages (F1-F3)

1. ✅ All stage checkboxes marked complete in HANDOFF_FRONT.md
2. ✅ Database migrations created and applied
3. ✅ Run: `pytest tests/ -v --cov=app --cov-report=term`
4. ✅ Coverage ≥ 80% for new code
5. ✅ All integration tests passing
6. ✅ Manual test with curl/httpie (test auth endpoints)
7. ✅ Documentation updated (docs/api-endpoints.md, docs/database-guide.md)
8. ✅ Commit with clean message (no AI branding)

### Frontend Stages (F4-F8)

1. ✅ All stage checkboxes marked complete in HANDOFF_FRONT.md
2. ✅ Run: `npm run build` (no errors)
3. ✅ Run: `npm run astro check` (TypeScript validation)
4. ✅ Manual testing checklist passed (see HANDOFF_FRONT.md)
5. ✅ Test on mobile, tablet, desktop (responsive)
6. ✅ Test in Chrome, Firefox, Safari (cross-browser)
7. ✅ Documentation updated (docs/frontend-guide.md)
8. ✅ Commit with clean message (no AI branding)

### Testing Stages (F9-F10)

1. ✅ All manual tests pass (27-item checklist)
2. ✅ All backend tests pass
3. ✅ Frontend builds without errors
4. ✅ No console errors in browser
5. ✅ Performance acceptable (< 3s page load)
6. ✅ Accessibility audit passed (basic WCAG)
7. ✅ Documentation complete and reviewed
8. ✅ Ready for PR

---

## 🎨 Design System Quick Reference

**Colors (Tailwind):**
```javascript
colors: {
  'oxide-dark': '#0a0a0a',          // Main background
  'oxide-darker': '#050505',         // Deeper sections
  'oxide-gray': '#1a1a1a',           // Cards, panels
  'oxide-gray-light': '#2a2a2a',     // Hover states
  'oxide-green': '#00ffa3',          // Primary accent
  'oxide-green-dim': '#00cc82',      // Hover accent
  'oxide-green-darker': '#009966',   // Active state
  'oxide-text': '#e5e5e5',           // Main text
  'oxide-text-dim': '#999999',       // Secondary text
  'oxide-text-darker': '#666666',    // Disabled text
}
```

**Typography:**
- Font: Inter (or system-ui fallback)
- Base: 16px
- Headings: 24px, 32px, 48px
- Line height: 1.5 (body), 1.2 (headings)

**Components:**
- Cards: `bg-oxide-gray rounded-lg p-6 hover:border-oxide-green`
- Buttons: `bg-oxide-green text-oxide-dark px-6 py-3 rounded hover:bg-oxide-green-dim`
- Inputs: `bg-oxide-gray border-oxide-gray-light focus:border-oxide-green`

**Layout:**
- Max width: 1200px
- Grid: 3 columns (desktop), 2 (tablet), 1 (mobile)
- Spacing: 1rem, 1.5rem, 2rem, 3rem

---

## 🔐 Authentication Implementation Details

### Backend (Stages F1-F3)

**Database Schema:**
```sql
-- Users table (updated)
ALTER TABLE users
ADD COLUMN password_hash VARCHAR(255) NOT NULL,
ADD COLUMN email VARCHAR(255) UNIQUE;

-- Sessions table (new)
CREATE TABLE sessions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Generations table (updated)
ALTER TABLE generations
ADD COLUMN user_id UUID REFERENCES users(id);
```

**Auth Endpoints:**
- `POST /auth/login` - Returns token + user info
- `POST /auth/logout` - Deletes session
- `GET /auth/me` - Returns current user

**Protected Endpoints:**
- `POST /generate` - Requires auth, saves user_id
- `GET /generations` - Requires auth, filters by user_id

**Public Endpoints:**
- `GET /generation/:id` - No auth, shareable links

### Frontend (Stages F4-F8)

**Pages:**
- `/login` - Public, redirects if logged in
- `/` (dashboard) - Protected, shows form + list
- `/generation/:id` - Public, shows full detail

**Auth Flow:**
1. Login form → POST /auth/login
2. Store token in httpOnly cookie
3. Middleware checks cookie on each request
4. Validate with GET /auth/me
5. Redirect to /login if invalid

**Polling Flow:**
1. Submit form → POST /generate → get generation_id
2. Start interval: every 2 seconds
3. GET /generation/:id → check status
4. If "completed" → stop polling, redirect to detail
5. If "processing" → continue polling
6. Timeout after 60 seconds → show error

---

## 🚀 Development Commands

**Backend (Terminal 1):**
```bash
# Start database
docker compose up -d postgres

# Start FastAPI
uvicorn app.main:app --reload --port 8000

# Run tests
pytest tests/ -v --cov=app

# Create migration
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

**Frontend (Terminal 2):**
```bash
cd frontend

# Start dev server
npm run dev

# Build production
npm run build

# Type check
npm run astro check

# Preview production
npm run preview
```

---

## 📊 Current Stage Reference

**Completed:**
- Backend: Stage 8 ✅ (API with stories & memes)

**In Progress:**
- Frontend: See HANDOFF_FRONT.md for current stage

**Stage Breakdown:**
- **F1**: Database schema (password_hash, sessions, user_id FK)
- **F2**: Backend auth endpoints (/auth/login, /logout, /me)
- **F3**: Protected routes (/generate requires auth, GET /generations)
- **F4**: Astro project setup (SSR, Tailwind, structure)
- **F5**: Auth UI (login page, middleware, session helpers)
- **F6**: Dashboard (generate form with polling, card grid)
- **F7**: Detail page (full image, story, repo data)
- **F8**: Design system (Oxide theme, responsive)
- **F9**: Testing (manual + automated)
- **F10**: Deployment prep (docs, PR, demo)

---

## 🐛 Common Issues & Solutions

**Issue: Port 4321 in use**
```bash
lsof -ti:4321 | xargs kill -9
```

**Issue: API connection refused**
- Check FastAPI running on port 8000
- Check API_URL in frontend/.env
- Test: `curl http://localhost:8000/health`

**Issue: Session not persisting**
- Check SESSION_SECRET in frontend/.env (64 chars)
- Check cookie httpOnly=true
- Check cookie domain (localhost)

**Issue: TypeScript errors**
```bash
npm run astro check
# Restart TS server in VS Code: Cmd+Shift+P → "Restart TS Server"
```

**Issue: Tailwind not working**
- Check tailwind.config.mjs content paths
- Restart dev server
- Check global.css imported in Layout

**Issue: Migration fails**
```bash
alembic current  # Check current version
alembic history  # Check available migrations
alembic stamp head  # Force stamp if needed
```

---

## 🎯 Key Requirements

**Authentication:**
- [x] Username/password only (no registration UI)
- [x] Accounts created manually in database
- [x] bcrypt for password hashing
- [x] Session-based auth (7-day expiration)
- [x] httpOnly cookies

**Design:**
- [x] Oxide Computer inspired
- [x] Dark theme (#0a0a0a)
- [x] Green accents (#00ffa3)
- [x] Minimalist, technical aesthetic
- [x] Responsive (mobile, tablet, desktop)

**Pages:**
- [x] Login page (public)
- [x] Dashboard (protected) - form + list grid
- [x] Detail page (public) - full image + story + data

**Functionality:**
- [x] Generate form with polling (2s interval)
- [x] Generation list (card grid, 3 columns)
- [x] Generation detail (full-width, shareable)
- [x] Loading states
- [x] Error handling

---

## 📝 Commit Message Format

**Follow LL-GIT-001 (no AI branding):**

✅ **Good:**
```
Stage F2: Authentication endpoints

Implemented login, logout, and me endpoints with session management.

Changes:
- Created app/api/auth.py with auth router
- Added bcrypt password hashing
- Implemented session creation and validation
- Added integration tests

All Stage F2 checkboxes completed.
```

❌ **Bad (no AI branding):**
```
Stage F2: Authentication endpoints

...

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## 🔗 Quick Links

- Backend API docs: http://localhost:8000/docs
- Frontend dev: http://localhost:4321
- Design inspiration: https://oxide.computer/
- Astro docs: https://docs.astro.build/
- Tailwind docs: https://tailwindcss.com/docs

---

**Last Updated:** 2025-10-14
**Current Branch:** `feature/frontend-astro-auth` (to be created)
**Next Task:** Check HANDOFF_FRONT.md for current stage
