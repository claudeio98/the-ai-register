## Context

The AI Events Intelligence Pipeline has grown through several iterations, each adding migration scripts, new files, and patches. The current `src/` directory contains 17 Python files, of which 6 are one-time migration scripts that serve no ongoing purpose. The pipeline orchestrator has a hardcoded developer-specific path that prevents the project from being portable.

The project uses SQLite for storage, FastAPI for the backend API, Vue.js for the frontend, and OpenRouter for LLM calls. There is no `.gitignore` — log files and the virtual environment are tracked.

## Goals / Non-Goals

**Goals:**
- Remove all one-time migration scripts that are no longer needed
- Fix the hardcoded absolute path in pipeline.py to be project-relative
- Fix the fragile relative path in fetcher.py to use `os.path.dirname(__file__)`
- Centralize the OpenRouter API key into `src/llm.py`; have `src/processor.py` import it
- Move the `semantic_check` function into `src/dedup.py` and have `src/processor.py` import from there
- Remove the unused `totalEvents` computed from the Vue.js frontend
- Create a proper `.gitignore`
- Archive completed change in openspec

**Non-Goals:**
- No logic changes to the pipeline stages
- No API changes
- No database changes
- No new features or functionality

## Decisions

### 1. Path Resolution Strategy
**Decision**: Use `os.path.dirname(os.path.abspath(__file__))` to resolve all sibling-file paths relative to the script's own directory.
**Rationale**: This works regardless of the working directory from which the script is invoked. It is the standard Python idiom.
**Files affected**: `src/pipeline.py`, `src/fetcher.py`

### 2. API Key Centralization
**Decision**: Move the hardcoded API key fallback from `src/processor.py` into `src/llm.py` (which already has it). Have `src/processor.py` import the `client` from `src/llm.py` instead of creating its own.
**Rationale**: Eliminates duplication. `src/llm.py` is already the designated LLM client wrapper.
**Impact**: `src/processor.py` no longer creates its own OpenAI client — it imports `client` from `src.llm`.

### 3. Logical Reorganization of `semantic_check`
**Decision**: Move the `semantic_check` function from `src/processor.py` into `src/dedup.py`, since it belongs to the deduplication concern. `src/processor.py` imports and uses it.
**Rationale**: Better separation of concerns. Keeps `processor.py` focused on LLM extraction/scoring rather than dedup logic.
**Impact**: `src/dedup.py` gains `semantic_check(conn, event_a, event_b)` which accepts a database connection (or None) and returns `(is_duplicate, reason)`. The `processor.py` import changes accordingly.

### 4. Migration Script Removal
**Decision**: Remove these files entirely:
- `src/migrate_browser_automation.py` — added `parent_id` column (done)
- `src/migrate_dedup.py` — added `canonical_event_id` and `fingerprint` columns (done)
- `src/migrate_existing_dedup.py` — one-time backfill of existing duplicates (done)
- `src/migrate_semantic_all.py` — one-time comprehensive semantic dedup (done)
- `src/migrate_semantic_dedup.py` — one-time semantic dedup (done)
- `src/migrate_semantic_targeted.py` — one-time targeted dedup (done)
**Rationale**: These were run once and will never be needed again. Keeping them adds noise and confusion. The current `src/migrate.py` is the active migration script and should be kept.

### 5. `.gitignore` Design
**Decision**: Create a `.gitignore` covering:
- `__pycache__/` and `*.pyc`
- `.venv/`
- `logs/*.log`
- `data/*.db`
- `.env`
- `.DS_Store`
- `node_modules/`
**Rationale**: Standard Python project ignores plus project-specific files.

### 6. Archive Completed Change
**Decision**: Move `openspec/changes/add-email-subscription/` into `openspec/changes/archive/add-email-subscription/`.
**Rationale**: This change is fully implemented. Archiving keeps the active changes list clean.

## Risks / Trade-offs

- **[Risk] Removing migration scripts that someone might want to re-run**: Mitigated by keeping `src/migrate.py` (the active migration). The one-time scripts are only needed if rebuilding the database from scratch, in which case `src/db.py`'s `init_db()` already creates the full schema.
- **[Risk] Moving `semantic_check` might break imports**: Mitigated by careful attention to the import chain and testing `processor.py` after the move.
- **[Trade-off] Removing dead code improves clarity but reduces historical reference**: The git history preserves the removed scripts if ever needed for reference.