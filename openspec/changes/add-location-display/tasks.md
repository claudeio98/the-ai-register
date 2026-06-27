## 1. Database

- [ ] 1.1 Add `location TEXT` column via ALTER TABLE in `src/db.py`

## 2. LLM Prompt

- [ ] 2.1 Add `location` field to SYSTEM_PROMPT extraction fields in `src/processor.py`

## 3. Processor

- [ ] 3.1 Update all INSERT statements in `src/processor.py` to include `location`

## 4. API

- [ ] 4.1 Add `e.location` to the SELECT query in `src/api.py`

## 5. Frontend

- [ ] 5.1 Add location pill badge to highlight cards (~line 218)
- [ ] 5.2 Add location pill badge to event list cards (~line 273)
- [ ] 5.3 Add location pill badge to mobile event cards

## 6. Deploy

- [ ] 6.1 Run processor to backfill locations
- [ ] 6.2 Push to git and update server