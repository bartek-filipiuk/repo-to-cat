# Frontend Development Guide

**Framework:** Astro 4.x with SSR
**Styling:** Tailwind CSS (Oxide-inspired)
**Port:** 4321
**Last Updated:** 2025-10-14

---

## Quick Start

### Installation

```bash
# From project root
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Visit: http://localhost:4321

---

## Project Structure

```
frontend/
├── src/
│   ├── pages/            # Routes (file-based routing)
│   │   ├── login.astro         # /login
│   │   ├── index.astro         # / (dashboard)
│   │   └── generation/
│   │       └── [id].astro      # /generation/:id
│   ├── components/       # Reusable components
│   │   ├── Layout.astro        # Base layout
│   │   ├── Header.astro        # Navigation header
│   │   ├── LoginForm.astro     # Login form
│   │   ├── GenerateForm.astro  # Generation form with polling
│   │   ├── GenerationCard.astro # Card for grid
│   │   └── GenerationList.astro # Grid of generations
│   ├── lib/              # Utility libraries
│   │   ├── api.ts              # API client
│   │   └── auth.ts             # Auth helpers
│   ├── styles/           # Global styles
│   │   └── global.css          # Oxide theme
│   └── middleware.ts     # Auth middleware
├── public/               # Static assets
├── astro.config.mjs      # Astro configuration
├── tailwind.config.mjs   # Tailwind configuration
├── .env                  # Environment variables (not committed)
└── package.json
```

---

## Development Commands

```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type check
npm run astro check
```

---

## Configuration

### Environment Variables

**File:** `frontend/.env`

```bash
PUBLIC_API_URL=http://localhost:8000  # Public API URL (client-side)
API_URL=http://localhost:8000          # Server-side API URL
SESSION_SECRET=<64-char-hex>           # Session encryption secret
NODE_ENV=development                   # Environment
```

**Generate SESSION_SECRET:**
```bash
openssl rand -hex 32
```

### API Proxy (Optional)

Configured in `astro.config.mjs`:

```javascript
vite: {
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
}
```

---

## Routing

Astro uses file-based routing:

| File | Route | Auth | Description |
|------|-------|------|-------------|
| `pages/login.astro` | `/login` | Public | Login page |
| `pages/index.astro` | `/` | Protected | Dashboard |
| `pages/generation/[id].astro` | `/generation/:id` | Public | Detail view |

**Dynamic routes:** Use `[param].astro` syntax

---

## Authentication

### Session Flow

1. User submits login form → POST `/auth/login` (FastAPI)
2. FastAPI validates credentials → returns session token
3. Astro sets httpOnly cookie with token
4. All requests include cookie automatically
5. Middleware validates session on protected routes

### Auth Middleware

**File:** `src/middleware.ts`

Runs on every request before page renders. Checks authentication for protected routes.

**Protected routes:**
- `/` (dashboard)
- Any route except `/login` and `/generation/:id`

**Public routes:**
- `/login`
- `/generation/:id` (shareable links)

### Auth Helpers

**File:** `src/lib/auth.ts`

- `getSession()` - Get current user from session
- `requireAuth()` - Throw redirect if not logged in
- `setSessionCookie()` - Set session cookie
- `clearSessionCookie()` - Clear session cookie

---

## API Integration

### API Client

**File:** `src/lib/api.ts`

Provides typed functions for all backend endpoints:

```typescript
// Authentication
await api.login(username, password)
await api.logout()
await api.getMe()

// Generations
await api.generate(githubUrl)
await api.getGenerations(limit, offset)
await api.getGeneration(id)
```

### Usage Example

```astro
---
import { api } from '../lib/api';

const generations = await api.getGenerations(50, 0);
---

<div>
  {generations.map(gen => (
    <div>{gen.repo_name}</div>
  ))}
</div>
```

---

## Styling

### Design System

**Inspiration:** [Oxide Computer](https://oxide.computer/)

**Colors:**
- Background: `#0a0a0a` (oxide-dark)
- Cards: `#1a1a1a` (oxide-gray)
- Accent: `#00ffa3` (oxide-green)
- Text: `#e5e5e5` (oxide-text)

**Typography:**
- Font: Inter
- Base size: 16px
- Headings: 24px, 32px, 48px

### Tailwind Classes

```html
<!-- Background -->
<div class="bg-oxide-dark">

<!-- Card -->
<div class="bg-oxide-gray rounded-lg p-6 hover:border-oxide-green">

<!-- Button -->
<button class="bg-oxide-green text-oxide-dark hover:bg-oxide-green-dim">

<!-- Text -->
<p class="text-oxide-text">
<p class="text-oxide-text-dim">
```

### Global Styles

**File:** `src/styles/global.css`

Applied in Layout component:
```astro
<style is:global>
  @import '../styles/global.css';
</style>
```

---

## Components

### Layout

**File:** `src/components/Layout.astro`

Base layout for all pages. Includes:
- HTML structure
- Global styles
- Header (if authenticated)
- Footer

### Header

**File:** `src/components/Header.astro`

Navigation header with:
- Logo/title
- User info
- Logout button

### GenerateForm

**File:** `src/components/GenerateForm.astro`

Form with client-side polling:
1. Submit GitHub URL
2. POST to `/generate`
3. Get generation_id
4. Poll `/generation/:id` every 2 seconds
5. Redirect when status = "completed"

### GenerationCard

**File:** `src/components/GenerationCard.astro`

Displays:
- Thumbnail image (150x150)
- Repo name + owner
- Quality score badge
- Link to detail page

### GenerationList

**File:** `src/components/GenerationList.astro`

Grid layout:
- 3 columns on desktop
- 2 columns on tablet
- 1 column on mobile

---

## Testing

### Manual Testing Checklist

**Authentication:**
- [ ] Can log in with valid credentials
- [ ] Cannot log in with invalid credentials
- [ ] Redirected to login when accessing dashboard without auth
- [ ] Can log out successfully
- [ ] Session persists across page reloads

**Generation:**
- [ ] Can submit GitHub URL
- [ ] Loading spinner shows during processing
- [ ] Redirected to detail page when complete
- [ ] Generation appears in list on dashboard

**Public Links:**
- [ ] Can access generation detail without auth
- [ ] Shareable links work

**Responsive Design:**
- [ ] Mobile layout works
- [ ] Tablet layout works
- [ ] Desktop layout works

---

## Troubleshooting

### Port Already in Use

```bash
# Kill process on port 4321
lsof -ti:4321 | xargs kill -9

# Or change port in astro.config.mjs
```

### API Connection Refused

Check:
1. FastAPI is running on port 8000
2. `API_URL` in `.env` is correct
3. CORS is configured in FastAPI

### Session Not Persisting

Check:
1. `SESSION_SECRET` is set in `.env`
2. Cookie is httpOnly
3. Cookie domain matches (localhost)

### TypeScript Errors

```bash
# Run type check
npm run astro check

# Restart TypeScript server in VS Code
Cmd+Shift+P → "TypeScript: Restart TS Server"
```

---

## Resources

- [Astro Documentation](https://docs.astro.build/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Oxide Computer (Design Inspiration)](https://oxide.computer/)
- Backend API: http://localhost:8000/docs

---

**Next Steps:** See [HANDOFF_FRONT.md](../PROJECT_FLOW_DOCS/HANDOFF_FRONT.md) for implementation checklist
