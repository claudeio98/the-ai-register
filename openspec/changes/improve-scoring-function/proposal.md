## Why

The current scoring function in `src/processor.py` systematically under-scores legitimate AI/ML conferences and events. Over a dozen events in the database have score 0 despite being clearly relevant — including the "Generative AI Summit | London" (AI Accelerator Institute with speakers from OpenAI, Meta, Hugging Face, Wayve), events on DeepMind's own Luma page ("Big Berlin Hack"), and recognized conferences like "AI & Big Data Expo Europe" and "Crescendo Live." Individual talk pages from these same conferences score 5–7, yet their conference/registration pages score 0. This means the system surfaces individual talks but misses the conference itself as a high-value item, creating a blind spot where users don't get alerted about major events.

## What Changes

- Expand the LLM scoring rubric in `src/processor.py` to evaluate conference quality signals, not just institution names
  - Add positive scoring signals for recognized AI conference organizers, speaker quality, etc.
  - Remove the blanket -2 penalty for conference pages with marketing copy
- Add a **post-processing phase** (`conference_scorer.py`) that runs after the initial processor pass:
  - Identifies conference/event pages that have related talk/agenda sub-pages (via the `sources.parent_id` chain)
  - Aggregates speaker information from those sub-pages
  - Re-scores the conference event based on the full aggregated speaker roster and quality
  - Only then is the conference event's score final

This two-phase approach means a conference page initially gets a modest score (based on organizer alone), then after its talk sub-pages are scored, the conference event is updated with the aggregated speaker intelligence.

## Capabilities

### New Capabilities
- `event-scoring`: The core logic that assigns a relevance score (0–10) to each discovered event during content processing. This covers the prompt template sent to the LLM, scoring rubric criteria, and any post-processing or aggregation logic. Currently embedded in `src/processor.py` as a single system prompt.

### Modified Capabilities
*(No existing spec-level behavior changes — scoring is an internal pipeline detail that feeds into existing specs. The dashboard, listing, and calendar views display whatever score they receive; their requirements don't change.)*

## Impact

- **Backend**: `src/processor.py` — the `SYSTEM_PROMPT` scoring rubric update. No API changes.
- **Backend (new)**: `src/conference_scorer.py` — new module for post-processing phase that aggregates speaker info from related talk pages and re-scores conference events.
- **Backend**: `src/pipeline.py` — add the conference scoring phase after the processor phase.
- **Database**: Add a `conference_id` column to the `events` table to link talk events to their parent conference event (populated via source `parent_id` chain).
- **Frontend**: No changes. The existing score display, annotations, and filters continue to work with improved score values.
- **Tests**: Update `tests/test_llm.py` and `tests/test_db.py` if they hardcode expected scores. Add tests for conference scoring.
- **No new external dependencies**: Uses existing SQLite + LLM infrastructure.
