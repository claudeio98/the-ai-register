## 1. Scoring Prompt Update

- [x] 1.1 Replace the `SYSTEM_PROMPT` in `src/processor.py` with an expanded rubric that recognizes a broader set of top-tier AI labs (DeepMind, OpenAI, Meta AI, Google Research, Anthropic, Microsoft Research), top-tier universities (Imperial, UCL, KCL, Oxford, Cambridge, MIT, Stanford), and recognized conference organizers (AI Accelerator Institute, Gartner, etc.)
- [x] 1.2 Add speaker quality scoring criteria: speakers from reputable companies (not just top-tier) contribute +2–3, world-renowned academics/industry leaders contribute +3–5, and multiple reputable speakers on a roster contribute additional points
- [x] 1.3 Add explicit instruction to NOT penalize conference/registration pages for having marketing copy — instead evaluate based on organizer reputation, speaker quality, and agenda
- [x] 1.4 Add a few-shot example in the prompt showing how to correctly score a conference registration page (e.g., the AI Accelerator Institute's Generative AI Summit with speakers from OpenAI, Meta, Hugging Face, Wayve should score 5–7, not 0)

## 2. Verification (Phase 1)

- [x] 2.1 Verify the prompt compiles (syntax check — Python parser, no logic changes needed)
- [x] 2.2 Run the processor on a test page to confirm the new prompt produces reasonable scores (manually trigger `processor.py` on a known problematic page)
- [x] 2.3 Check score distribution: verify new scores use the full 0–10 range and are not inflated or collapsed
- [x] 2.4 Verify existing test suite still passes (`tests/test_llm.py`, `tests/test_db.py`, `tests/test_dedup.py`) — update any tests that hardcode expected scores from the old prompt
- [x] 2.5 Optionally re-process the AI Accelerator Institute registration page (event ID 467) by resetting its `processed` flag and re-running the processor — verify the conference page now scores significantly above 0

## 3. Database & Source Linking

- [x] 3.1 Add `conference_id INTEGER REFERENCES events(id)` column and index to the events table in `src/db.py` init_db, with a migration for existing databases
- [x] 3.2 Update `src/processor.py` event insertion logic: conference_id linking is handled by the conference scorer's URL prefix matching instead (more robust than source parent_id chains)
- [x] 3.3 Verify linking works: conference scorer found 7 child talk events for event ID 524 and all 7 had valid speaker data

## 4. Conference Scorer Module

- [x] 4.1 Create `src/conference_scorer.py` with a `score_conferences()` function that:
  - Queries for canonical events that look like conferences (institution + no speaker)
  - Finds child talk events via URL prefix matching (common directory path)
  - Aggregates speaker data from child events
  - Sends aggregated speaker roster to the LLM for re-scoring
  - Updates the conference event's score only if the new score is higher

## 5. Pipeline Integration

- [x] 5.1 Add the conference scorer phase to `src/pipeline.py` (after the processor phase)

## 6. Verification (Phase 2)

- [x] 6.1 Re-run the pipeline on the AI Accelerator Institute conference: initial score (4) → after conference scoring with 7 aggregated speakers → **8/10** ✓
- [x] 6.2 Verify that conferences without child events are not affected (many zero-event conferences were correctly skipped)
- [x] 6.3 Verify existing test suite still passes (`tests/test_llm.py`, `tests/test_db.py`, `tests/test_dedup.py`)

## 7. Documentation & Completion

- [x] 7.1 Update any internal docs or notes that reference the old scoring rubric
- [x] 7.2 Mark all tasks complete and archive the change