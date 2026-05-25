## 1. Remove Dead Migration Scripts

- [x] 1.1 Delete `src/migrate_browser_automation.py`
- [x] 1.2 Delete `src/migrate_dedup.py`
- [x] 1.3 Delete `src/migrate_existing_dedup.py`
- [x] 1.4 Delete `src/migrate_semantic_all.py`
- [x] 1.5 Delete `src/migrate_semantic_dedup.py`
- [x] 1.6 Delete `src/migrate_semantic_targeted.py`
- [x] 1.7 Verify no remaining imports or references to these files anywhere in the codebase

## 2. Fix Hardcoded Path in pipeline.py

- [x] 2.1 Replace `f"/Users/claudio/.pi/workspace/ai-events-tracker/src/{script_name}"` with project-relative path resolution using `os.path.dirname(os.path.abspath(__file__))`
- [x] 2.2 Verify `pipeline.py` runs from any working directory (test with `cd / && python3 <full-path>`)

## 3. Fix Fragile Path in fetcher.py

- [x] 3.1 Replace `BROWSER_FETCHER_PATH = "src/browser_fetcher.js"` with a path resolved via `os.path.join(os.path.dirname(__file__), "browser_fetcher.js")`
- [x] 3.2 Verify `fetcher.py` runs from any working directory

## 4. Centralize API Key

- [x] 4.1 In `src/llm.py`, confirm the `OPENROUTER_API_KEY` and `client` are already defined
- [x] 4.2 In `src/processor.py`, remove the duplicated `client` initialization and `OPENROUTER_API_KEY` constant, and add `from src.llm import client` (or relative import)
- [x] 4.3 Verify `processor.py` uses the imported `client` and still functions correctly

## 5. Reorganize `semantic_check` into dedup.py

- [x] 5.1 Move the `semantic_check` function from `src/processor.py` into `src/dedup.py`
- [x] 5.2 Update `src/processor.py` to import `semantic_check` from `src.dedup` instead of defining it locally
- [x] 5.3 Run the dedup unit tests to confirm nothing broke

## 6. Remove Unused Frontend Code

- [x] 6.1 Remove the unused `totalEvents` computed property from the Vue.js setup in `frontend/index.html`

## 7. Create .gitignore

- [x] 7.1 Create `.gitignore` at the project root with entries for: `__pycache__/`, `*.pyc`, `.venv/`, `logs/*.log`, `data/*.db`, `.env`, `.DS_Store`, `node_modules/`

## 8. Archive Completed Change

- [x] 8.1 Move `openspec/changes/add-email-subscription/` into `openspec/changes/archive/add-email-subscription/`
- [x] 8.2 Verify the archive directory is structured correctly

## 9. Verify No Regressions

- [x] 9.1 Run `python3 -m unittest discover tests` (all tests should pass)
- [x] 9.2 Run `python3 src/api.py` briefly to confirm the server starts without import errors
- [x] 9.3 Do a dry-run of pipeline imports: `python3 -c "from src.pipeline import main; print('OK')"`