# AI Events Tracker

## Spec-driven development with OpenSpec

This project uses OpenSpec for spec-driven development. Before implementing changes, define what you're building:

1. **Propose a change:**
   ```
   /opsx:propose "your idea"
   ```
   This creates a spec in `openspec/specs/` that defines the requirements, acceptance criteria, and implementation plan.

2. **Review the spec** before writing any code — ensure alignment on what's being built.

3. **Implement against the spec** — the spec serves as the source of truth for what "done" looks like.

Specs are tracked in version control alongside code, so every change has a documented rationale.

## Version control with Jujutsu (jj)

This repo uses **jj** on top of git. The `.git` directory is the source of truth; `.jj` is a parallel metadata layer. Commits from either tool are visible to the other.

### User config

User identity is set at the user level (not project level):
- `jj config set --user user.name "Your Name"`
- `jj config set --user user.email "your@personal-email.com"`

### Making changes

1. **Start a new change:**
   ```
   jj new main
   ```
   This creates a new change on top of main. jj's working copy is always a commit, so there's no separate "staging" step — just edit files and they're tracked.

2. **Describe the change (required before pushing):**
   ```
   jj describe -m "feat: add event filtering by date"
   ```
   Follow conventional commits format (feat:, fix:, refactor:, chore:, etc.). First line under 72 characters.

3. **Push to GitHub:**
   ```
   jj git push
   ```
   This pushes the current change and creates/updates the corresponding git bookmark (branch).

### Rules for proper tracking

- **Describe every change before pushing.** `jj describe` is how the log stays readable. Don't push with the auto-generated description.
- **Use conventional commits** (`feat:`, `fix:`, `refactor:`, `chore:`, etc.).
- **Rebase onto main before pushing** with `jj rebase -d main` if main has moved ahead.
- **Don't mix `git branch` and `jj bookmark`** — they correspond but can get out of sync. Stick to jj commands for managing bookmarks.
- **The working copy is always a commit.** There's no git-style "dirty working tree" — changes are tracked in the working copy commit automatically.
- **Amend instead of committing anew:** `jj squash` or just continue editing and use `jj describe` to update the description.
- **To abandon a change:** `jj abandon` (like `git reset --hard` but the change stays in the log for recovery).

## Commands

### Local development
```bash
make install              # pip install -r requirements.txt
make run-api              # Start FastAPI backend on :8082
make run-frontend         # Start frontend on :8081
make test                 # Run unit tests (python -m unittest discover tests)
make clean                # Remove logs/temp files
```

### Docker (production)
```bash
docker compose up -d api frontend                    # Start API + frontend with nginx reverse proxy
docker compose --profile pipeline run --rm pipeline  # Run data pipeline (one-shot)
docker compose up -d                                 # Start everything + Caddy reverse proxy
```

### Pipeline stages (run individually)
```bash
python src/discovery_stage.py   # Brave Search + Eventbrite discovery
python src/fetcher.py           # Fetch page content
python src/processor.py         # Score and categorize events via LLM
python src/notifier.py          # Send email alerts
```

## Architecture

```
├── data/               # SQLite database (events.db)
├── frontend/           # Single-page Vue.js + Tailwind (index.html, no build step)
├── openspec/           # OpenSpec specs and configurations
├── src/
│   ├── api.py          # FastAPI backend
│   ├── pipeline.py     # Pipeline orchestrator
│   ├── discovery.py    # Brave Search discovery
│   ├── api_discovery.py    # Eventbrite discovery
│   ├── processor.py    # LLM scoring
│   ├── notifier.py     # Email notifications
│   ├── fetcher.py      # Content extraction
│   ├── db.py           # SQLite database layer
│   └── llm.py          # OpenRouter LLM client
├── tests/              # Unit tests (test_db.py, test_dedup.py, test_llm.py)
├── Dockerfile          # Python 3.11 + Node.js (for browser_fetcher.js)
├── docker-compose.yml  # api, frontend, caddy, pipeline services
└── nginx.conf          # nginx config: static serving + API reverse proxy
```

## Gotchas

- **Production Hetzner server uses host-level nginx + certbot** for SSL, bypassing the Docker nginx container. Docker is only for the API and frontend serving.
- **The Dockerfile installs Node.js** even though it's a Python app — needed for `browser_fetcher.js` (Playwright-based JS rendering).
- **Frontend auto-detects dev vs prod**: on port 8081 it assumes dev and calls API on 8082 directly; behind nginx it uses the same origin with proxy pass.
- **Pipeline has a separate Docker profile** (`--profile pipeline`) so it doesn't start with `docker compose up`.
- **The frontend is a single `index.html`** — no build step, no framework CLI. Vue.js and Tailwind are loaded via CDN.
- **Database is a SQLite file** in `data/events.db`. It's mounted as a volume in Docker — data persists across container restarts.
- **The `.env` file is loaded at runtime** by `python-dotenv`. API runs locally via `uvicorn`, not through a full ASGI server wrapper.
- **Don't modify MEMORY.md directly** — it's managed by Claude's memory system for cross-session context.