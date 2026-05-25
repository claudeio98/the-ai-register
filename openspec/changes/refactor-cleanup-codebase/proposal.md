## Why

The codebase has accumulated significant technical debt through iterative development. There are several issues:

1. **Dead migration scripts**: Six one-time migration scripts (`migrate_browser_automation.py`, `migrate_dedup.py`, `migrate_existing_dedup.py`, `migrate_semantic_all.py`, `migrate_semantic_dedup.py`, `migrate_semantic_targeted.py`) clutter the `src/` directory. These were used for one-off schema changes and data backfills — they are no longer needed and add confusion about which scripts are part of the active pipeline.

2. **Hardcoded absolute path in pipeline.py**: `src/pipeline.py` uses `/Users/claudio/.pi/workspace/ai-events-tracker/src/{script_name}` as the script path. This will break on any other machine or if the workspace moves.

3. **Fragile relative path in fetcher.py**: `BROWSER_FETCHER_PATH = "src/browser_fetcher.js"` breaks if the script is run from outside the project root.

4. **Duplicated API key**: The OpenRouter API key is hardcoded in both `src/llm.py` and `src/processor.py` — it should be centralized.

5. **Unused variable and dead code**: `src/processor.py` imports `get_duplicate_count` but the function `semantic_check` is defined inside the file when it could live in `dedup.py`. The `totalEvents` computed property in `frontend/index.html` is defined but never used.

6. **Completed change artifacts in openspec/**: Archived changes are mixed with active ones.

7. **Log files tracked in repo**: `logs/api.log` and `logs/frontend.log` are checked in.

## What Changes

- **Remove** one-time migration scripts from `src/` (6 files)
- **Fix** `src/pipeline.py` to use a relative or resolved path instead of an absolute user-specific path
- **Fix** `src/fetcher.py` to resolve `BROWSER_FETCHER_PATH` relative to the script directory
- **Centralize** API key in `src/llm.py` and have `src/processor.py` import from there
- **Move** `semantic_check` from `src/processor.py` into `src/dedup.py` for logical grouping
- **Remove** unused `totalEvents` computed property from `frontend/index.html`
- **Archive** completed change `add-email-subscription` in `openspec/changes/archive/`
- **Add** `logs/*.log` to `.gitignore`
- **Add** a `.gitignore` if missing (covering `__pycache__`, `.venv`, `logs/*.log`, `data/*.db`, `.env`)

## Non-goals

- No functional changes to event discovery, processing, or notification logic
- No database schema changes
- No changes to the API endpoints or frontend behavior
- No new features