## Context

Events are currently extracted from pages by the LLM with fields: title, speaker, institution, date, url, score, reasoning. There's no location field, so users can't distinguish between London events, online events, and events in other cities (e.g., ICML in Seoul). The detail panel already renders `detail.location || 'Remote'` but the field is never populated.

## Goals / Non-Goals

**Goals:**
- Add `location` to the LLM extraction prompt
- Store it in the database
- Return it from the API
- Show it as a pill badge on event cards

**Non-Goals:**
- Not retroactively filling location for existing events (will be filled on re-process)
- Not using geocoding or lat/lng — just free-text venue/city
- Not changing dedup logic

## Decisions

1. **Free-text location field** — No structured address or coordinates. The LLM extracts whatever is available (e.g. "Seoul, South Korea", "UCL, London", "Online"). Simple and sufficient.

2. **ALTER TABLE migration, not schema reset** — Add column with `ALTER TABLE events ADD COLUMN location TEXT` in db.py's init_db. Safe for existing databases.

3. **LLM prompt instruction** — Add a simple line to the extraction fields. The LLM already sees page content with venue info; this just captures it.

## Risks / Trade-offs

- LLM may extract noisy or inconsistent location strings → mitigated by showing it as-is, not relying on it for filtering
- Existing events won't have location until re-processed → acceptable, fills in gradually