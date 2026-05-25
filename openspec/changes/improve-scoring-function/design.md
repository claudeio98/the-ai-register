## Context

The AI Events Tracker pipeline discovers event pages via Brave Search, fetches their content with a headless browser, then sends that content to an LLM (gemma-4-31b-it via OpenRouter) for event extraction and scoring. The scoring is done entirely by the LLM prompt in `src/processor.py` — there is no programmatic scoring logic. The prompt scores events 0–10 based on a rubric that recognizes only 5 institutions (DeepMind, OpenAI, Meta AI, Imperial, UCL, KCL, Oxford, Cambridge) for +5, with a -2 penalty for "Low-quality, generic marketing, or irrelevant events."

Analysis of the database shows 14+ events scored 0 that are genuinely relevant AI/ML events. The root causes are:
1. **Conference pages penalized as "marketing"**: Registration/conference landing pages contain promotional copy, triggering the -2 penalty even when the conference itself is high-value (e.g., AI Accelerator Institute's Generative AI Summit with speakers from OpenAI, Meta, Hugging Face, Wayve — score 0)
2. **Rubric too narrow**: No credit for other top AI companies (Microsoft, Anthropic, Google, Amazon), major conference organizers (Gartner, AI Accelerator Institute), or speaker reputation as a signal
3. **No conference-awareness**: The LLM treats every page independently with no context about what constitutes a legitimate AI conference vs. spam
4. **No inter-page aggregation**: A conference's homepage may not list speakers on the registration page, but its child pages (individual talk/agenda pages) have all the speaker details. The system never connects these.

## Goals / Non-Goals

**Goals:**
- Expand the scoring rubric to recognize a broader set of high-quality institutions, companies, and conference organizers
- Add speaker quality as an explicit positive signal (even speakers from non-listed companies)
- Handle conference/event registration pages differently — evaluate on organizer reputation and speaker roster rather than penalizing them as marketing
- Add a post-processing phase that aggregates speaker info from related talk/agenda sub-pages to re-score conference events with a fuller picture
- Reduce the number of genuinely relevant AI/ML events that score ≤ 1

**Non-Goals:**
- Full programmatic scoring logic outside the LLM — still LLM-based scoring, with programmatic aggregation on top
- Full speaker database or speaker lookup API — the LLM extracts whatever speaker info is in the page content
- Frontend changes or API changes — scores flow through unchanged
- Re-scoring existing events from scratch — only newly processed events get the aggregation treatment

## Decisions

### 1. Scoring Approach: Two-Phase (Prompt + Post-Processing Aggregation)

**Decision:** Use a two-phase scoring approach:
1. **Phase 1 — Processor** (existing): Each page is independently sent to the LLM with the improved prompt. Conference pages get an initial score based on whatever content is present (e.g., organizer reputation). Talk/agenda sub-pages get scored on speaker quality as before.
2. **Phase 2 — Conference Scorer** (new): A post-processing module (`conference_scorer.py`) that:
   - Finds events that appear to be conference/event overview pages (linked via the `sources.parent_id` chain)
   - Aggregates speaker information from child events (talk pages from the same conference)
   - Re-scores the conference event using the LLM with the full aggregated speaker roster
   - Updates the conference event's score in the database

**Alternatives considered:**
- **Prompt-only (v1 approach)**: The conference page gets scored on whatever limited content is on the registration page. As we discovered, this misses speakers entirely when they're only listed on sub-pages.
- **Deep crawl at fetch time**: The fetcher could crawl sub-pages immediately and merge their content before passing to the processor. But this would require the fetcher to understand event structure, which is the processor's job.
- **External conference database / API**: Would add cost and dependencies. Not feasible.

**Rationale:** The conference's true quality is only measurable by its speaker roster. Since those speakers live on separate pages (agenda, individual talk descriptions), the system must aggregate across pages. The two-phase approach is clean: each page is processed independently first, then a focused post-processing pass connects related events. This avoids coupling the fetcher with event semantics and keeps the processor simple.

### 2. Rubric Structure: Additive with Baseline

**Decision:** Change the scoring rubric from a set of rigid +5/+3/+2/-2 rules to a more structured rubric that starts from a baseline and adds/subtracts based on multiple signals.

**New rubric design:**
- **Baseline**: Every event starts at score 0 (no automatic score)
- **+4 to +6** for events hosted/co-hosted by top-tier AI labs (DeepMind, OpenAI, Meta AI, Google Research, Anthropic, Microsoft Research, etc.) or top-tier universities (Imperial, UCL, KCL, Oxford, Cambridge, MIT, Stanford, etc.)
- **+3 to +5** for events organized by recognized conference organizers (AI Accelerator Institute, Gartner, etc.) OR featuring world-renowned academics/industry leaders
- **+2 to +3** for events highly relevant to ML/AI business or academic breakthroughs, OR featuring multiple reputable speakers
- **+1** for moderately relevant AI/ML events (even if no big names)
- **-2 to -4** for low-quality, generic non-AI marketing, or irrelevant events (but explicitly NOT for conference pages that are simply using registration copy — evaluate those on organizer quality)
- **Critical instruction**: "If this is a conference/event page (registration, agenda, or overview), do NOT penalize it for having marketing copy or registration language. Instead, evaluate the organizers, speakers, and agenda quality."

**Alternatives considered:**
- **Fixed weights approach**: Assigns numeric weights to each signal. More precise but harder for the LLM to follow consistently. The ordinal scale (low/medium/high within each range) is more natural for LLM output.
- **Binary checklist**: "Does the event feature a top-tier organization? +3. Does it have recognized speakers? +2." More predictable but overly rigid — missing a checkbox for "notable but not world-renowned" leaves a gap.

**Rationale:** The rubric is the prompt the LLM follows. Grouping into tiers (+4–6, +3–5, etc.) with descriptive criteria gives the LLM flexibility to make nuanced judgments while constraining the overall scale. The explicit instruction about conference/registration pages directly addresses the root cause of false-zero scores.

### 3. No Score Reprocessing

**Decision:** Only newly processed pages will benefit from the improved scoring. Existing events in the database retain their original scores.

**Rationale:** Reprocessing all existing pages would require re-fetching page content via the headless browser, re-running the LLM, and re-running dedup logic — significant time and LLM cost for uncertain benefit. The existing score-0 events represent a small fraction of total events, and users can already see individual talk pages for those conferences (which are scored correctly). If needed, a targeted re-score of specific pages can be done manually.

### 4. Scoring Model Unchanged

**Decision:** Continue using `gemma-4-31b-it` via OpenRouter for scoring. No model change.

### 5. Database Schema: Link Events to Parent Conference

**Decision:** Add a `conference_id` column to the `events` table to link individual talk/agenda events to their parent conference event.

**How it's populated:**
- Each source has a `parent_id` column (set during deep discovery — e.g., the conference homepage is parent of individual talk pages)
- When a talk event is inserted, its source's `parent_id` chain can be traced
- If a talk event's source has a parent_id pointing to a source that produced a conference event, the talk event is linked to that conference event
- This enables the Conference Scorer to find all events belonging to a conference, aggregate their speakers, and re-score

**Columns:**
- `conference_id INTEGER REFERENCES events(id)` — the parent conference event ID (NULL if not part of a conference)
- Index: `CREATE INDEX IF NOT EXISTS idx_events_conference_id ON events(conference_id)`

**Alternatives considered:**
- **URL-based matching**: Group events by normalized URL prefix (e.g., all events under `/location/london/`). Fragile — URL structures vary too much.
- **Title-based matching**: Match events whose titles share tokens with the conference name. High false-positive risk.
- **No schema change, use source parent_id at query time**: Avoids schema migration but requires reconstructing the event tree from sources each time, which is slow and complex.

**Rationale:** The `sources.parent_id` chain already captures the relationship the fetcher discovers. Adding `conference_id` to events materializes this relationship at insert time, making aggregation fast and simple.

**Alternatives considered:**
- **GPT-4o or Claude**: Better at nuanced evaluations, but significantly more expensive. Not justified for a single-person project.
- **Local model (Llama 3, etc.)**: Free, but likely worse at scoring nuance. The current model is adequate; the prompt is the bottleneck.

**Rationale:** The scoring accuracy is limited by the prompt, not the model. Changing models adds complexity and cost without addressing the root cause. Revisit only if the improved prompt still produces poor results.

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| **Expanded rubric makes scores too generous** (inflation) | The rubric still has a -2 to -4 penalty for truly irrelevant events. Monitor score distribution after deployment. If scores cluster in 7–10 range, tighten criteria. |
| **Conference scorer runs before child pages are processed** | Run conference scoring as a separate phase that triggers only when the pipeline has no more pages to process for a given conference. Or keep it simple: run it at the end of each pipeline cycle. Child events from earlier cycles will already have scores. |
| **Conference organizers get uneven treatment** (some recognized, some missed) | The prompt lists "AI Accelerator Institute, Gartner" as examples but says "or similar recognized organizers." The LLM generalizes reasonably well. |
| **Score drift over time** as LLM provider updates the model | This is inherent — the prompt constrains output format (JSON) and rubric, but different model versions may score differently. Acceptable for now. |
| **Duplicate conference events** (same conference discovered from multiple paths) | The existing dedup system handles this. The conference scorer should process the canonical event only. |
| **Conference scorer relies on source parent_id chain, which may not always be populated** | Not all conferences have a clean parent-child source tree. The scorer should gracefully skip events without a conference_id match and only boost those where it can find child events. |

## Migration Plan

1. **Update `src/processor.py`**: Replace `SYSTEM_PROMPT` with the expanded rubric. Already done.
2. **Add `conference_id` column** to events table in `src/db.py` init_db + migration for existing DB.
3. **Update `src/processor.py`**: When inserting an event, check if its source has a `parent_id`; if so, trace the chain to find a conference event and set `conference_id`.
4. **Create `src/conference_scorer.py`**: New module that queries events with child events, aggregates speaker data, calls LLM for re-scoring, and updates the conference event's score.
5. **Update `src/pipeline.py`**: Add the conference_scorer phase after processor.
6. **Run the pipeline** on new content to verify scores improve. The next discovery → fetch → process → conference-scoring cycle will use the full two-phase approach.
7. **Verify**: Re-process the AI Accelerator Institute conference page — it should score higher after its child talk pages are aggregated.

**Rollback**: Revert `src/processor.py` prompt, remove `conference_scorer.py`, revert `pipeline.py`, remove `conference_id` column. No data loss — original scores remain.

## Open Questions

1. Should we add a few-shot example in the prompt showing how to score a conference page? → **Decision**: Yes, include one example in the prompt for clarity. Already done.
2. **Conference scorer logic**: Should the conference scorer use the LLM to re-score (send aggregated speaker data with the prompt) or use a programmatic formula (count high-quality speakers, assign score)? → **Decision**: Use the LLM for re-scoring, since the rubric needs contextual understanding (not all "OpenAI" speakers are equally notable). Send the aggregated speaker roster + existing score as context.
3. **When to run conference scorer**: After every processor cycle, or only when the pipeline has processed all pages for a given conference? → **Decision**: After every processor cycle for simplicity. If a conference hasn't been fully crawled yet, it will get a bump next cycle. This is fine — scores are naturally incremental.