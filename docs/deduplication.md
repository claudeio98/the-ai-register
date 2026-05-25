# Event Deduplication System

## Overview

The AI Events Intelligence Pipeline now uses a **three-tier deduplication system** to ensure events are not duplicated in the database or frontend.

## How It Works

### Date-First Strategy

**Events on different dates are NEVER considered duplicates** (unless they're the exact same title for a multi-day conference).

### Tier 1: Fingerprint Match (Fast, Exact)
- **Method**: SHA-256 hash of normalized title + canonical date + URL domain
- **Speed**: Instant
- **Catches**: Exact duplicates with identical content

### Tier 2: Fuzzy Match (Fast, Near-Exact)
- **Method**: RapidFuzz `token_sort_ratio` ≥ 85
- **Date Window**: **EXACT same date only** (no ±1 day)
- **Speed**: Fast
- **Catches**: Minor title variations on the same day

### Tier 3: LLM Semantic Match (Slow, Most Accurate)
- **Method**: LLM compares event descriptions for semantic identity
- **Date Window**: **EXACT same date only**
- **Pre-filter**: Only checks events sharing ≥2 title words
- **Speed**: Slower (API call per comparison)
- **Catches**: Semantic duplicates on the same day like:
  - "Meta Conversations 2026" vs "2026 Conversations messaging conference" (both on 2026-06-03)
  - "The AI Summit London 2026" vs "AI Summit London 2026" (both on 2026-06-10)

**Note**: Events on different dates are **never** compared, even with LLM. This prevents false positives like merging "AI Summit 2025" with "AI Summit 2026".

## Implementation

### New Events (Automatic)
When `processor.py` extracts events from a page:
1. Computes fingerprint
2. Checks fingerprint match
3. If no match, checks fuzzy match (±1 day)
4. If no match, checks semantic match (±14 days, LLM)
5. Links to canonical or inserts as new

## Files

- `src/dedup.py`: Core deduplication logic (fingerprint, fuzzy, semantic check)
- `src/processor.py`: Event processing with LLM semantic check (imports `semantic_check` from `dedup`)
- `src/api.py`: Returns only canonical events (`WHERE canonical_event_id IS NULL`)
- `src/migrate.py`: Active schema migration script

## Frontend

The frontend displays:
- Only canonical events (duplicates are hidden)
- `+N more sources` badge on events with merged duplicates

## Example

**Before:**
- "Meta Conversations 2026" (id=7)
- "2026 Conversations messaging conference" (id=84)
- "The AI Summit London" (id=429, 2025)
- "The AI Summit London 2026" (id=501)
- "AI Summit London" (id=145)

**After:**
- "Meta Conversations 2026" (id=7, canonical) [+1 more sources]
  - ↳ "2026 Conversations messaging conference" (id=84, linked)
- "The AI Summit London 2026" (id=501, canonical) [+1 more sources]
  - ↳ "AI Summit London" (id=145, linked)
- "The AI Summit London" (id=429, canonical, 2025) - kept separate (different year)

## Configuration

The LLM model is configured in `processor.py`:
```python
model=os.environ.get("MODEL_NAME", "google/gemma-4-31b-it")
```

Change the model by setting the `MODEL_NAME` environment variable.
