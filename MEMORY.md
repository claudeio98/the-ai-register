s# Project Memory: AI Events Intelligence Pipeline

## Objective
Build a system to discover, score, and notify the user of high-value ML/AI events in London and internationally.

## Technical Stack
- **Language**: Python 3.9
- **Storage**: SQLite (`/data/events.db`)
- **Discovery/Extraction**: Brave Search API (via `search.js` and `content.js` skills)
- **Intelligence**: OpenRouter API using `google/gemma-4-31b-it`
- **Delivery**: Gmail CLI (`gmcli`)

## Key Lessons & Troubleshooting

### 1. The Harness Timeout (The "Stuck" Issue)
- **Symptom**: Pipeline would run for a long time and then end with `Command aborted`.
- **Root Cause**: The pi agent harness has a global timeout for `bash` calls. A monolithic `pipeline.py` performing dozens of network requests exceeded this limit.
- **Solution**: 
    - **Safe Batching**: Modified `fetcher.py` to process only 5 URLs per execution.
    - **Strict Timeouts**: Added `timeout=15` to `subprocess.run` calls to prevent individual slow pages from hanging the process.
    - **Decoupled Orchestration**: Shifted from a monolithic script to stage-by-stage execution.

### 2. The Failure Loop
- **Symptom**: Pipeline would repeatedly try the same failing URLs at the start of every run, blocking progress.
- **Root Cause**: `last_checked` timestamp was only updated upon successful content extraction.
- **Solution**: 
    - Update `last_checked` regardless of whether the fetch succeeded or failed.
    - Implement a `failures` counter in the `sources` table; URLs with $\ge 3$ failures are pruned from the viable source list.

### 3. Database Schema Migration
- **Symptom**: `sqlite3.OperationalError: no such column: s.failures`.
- **Root Cause**: Updating the `CREATE TABLE` statement in code does not affect existing `.db` files on disk.
- **Solution**: Developed a standalone migration script (`src/migrate.py`) using `ALTER TABLE` to update the schema without and deleting existing data.

### 4. API & Model Configuration
- **Configuration**: Integrated OpenRouter with a specific focus on `google/gemma-4-31b-it`.
- **Header Requirements**: OpenRouter requires `HTTP-Referer` and `X-Title` headers for proper request handling.
- **Response Format**: Used `response_format={"type": "json_object"}` to ensure stable parsing of event data.

## Frontend Implementation (2026-04-21)
- **API**: FastAPI backend providing event data with filtering (status), sorting (date, score, title), and a toggle for future vs. past events.
- **Frontend**: Vue.js + Tailwind CSS single-page application.
- **Troubleshooting**: 
    - Fixed `ModuleNotFoundError: No module named 'src'` by updating imports to `from db import get_connection` and running the API from within the `src` directory.

## Final Pipeline Architecture
`Discovery (Dynamic LLM Queries)` $\rightarrow$ `Fetcher (Safe Batches)` $\rightarrow$ `Processor (Gemma-4 Scoring)` $\rightarrow$ `Notifier (Gmail CLI)`
