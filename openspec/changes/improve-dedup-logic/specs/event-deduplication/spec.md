# event-deduplication Specification

## Purpose
Detect and merge duplicate event entries based on title similarity, date proximity, and URL normalization — not just exact URL matching.

## ADDED Requirements

### Requirement: Fingerprint-based dedup on insert
The system SHALL compute a deterministic SHA-256 fingerprint for every incoming event and skip insertion (soft-link to canonical) if the fingerprint already exists in the database.

#### Scenario: Duplicate fingerprint is detected
- **WHEN** the processor extracts an event whose fingerprint matches an existing event
- **THEN** the new row SHALL NOT be inserted; the system SHALL log a message and continue

#### Scenario: Unique fingerprint passes through
- **WHEN** the processor extracts an event whose fingerprint does not match any existing event
- **THEN** the event SHALL be inserted as a new row with `canonical_event_id` set to NULL

### Requirement: Fingerprint composition
The fingerprint SHALL be computed from a canonical string consisting of: normalized title + canonical date (ISO date or date range) + domain-normalized URL (scheme + hostname only).

#### Scenario: Same event on different URLs resolves to same fingerprint
- **WHEN** two events have the same normalized title and date but different full URLs (e.g., luma.com/talk and meetup.com/talk)
- **THEN** they SHALL produce different fingerprints (because domain differs) and be candidates for the fuzzy pass

#### Scenario: Same title with punctuation differences
- **WHEN** titles differ only by punctuation, casing, or extra whitespace ("Attention Is All You Need!" vs "Attention is all you need")
- **THEN** the normalized titles SHALL be identical, producing matching fingerprints

### Requirement: Title normalization
The system SHALL normalize event titles by: lowercasing, stripping punctuation (except hyphens and apostrophes), collapsing whitespace, and trimming leading/trailing whitespace.

#### Scenario: Punctuation and casing normalization
- **WHEN** the title is "Deep Learning Workshop – London!"
- **THEN** the normalized title SHALL be "deep learning workshop  london"

### Requirement: Secondary fuzzy dedup pass
If fingerprint matching produces no result, the system SHALL run a secondary fuzzy match using RapidFuzz `token_sort_ratio` with a threshold of >= 85 against existing events with the same date (or ±1 day).

#### Scenario: Fuzzy match catches a near-duplicate
- **WHEN** an incoming event's title is "Deep Learning Workshop (London)" and an existing event's title is "Deep Learning Workshop – London"
- **THEN** the fuzzy ratio SHALL be >= 85 and the incoming event SHALL be linked as a duplicate

#### Scenario: Fuzzy match rejects genuinely different events
- **WHEN** titles differ substantially (e.g., "GANs for Image Generation" vs "Transformers for NLP")
- **THEN** the fuzzy ratio SHALL be < 85 and no duplicate link SHALL be created

### Requirement: Canonical event identity soft-link
The system SHALL add a nullable `canonical_event_id` foreign key column to the `events` table. Duplicate events SHALL set this column to the `id` of the canonical (first-seen or highest-scored) event.

#### Scenario: Duplicate is soft-linked
- **WHEN** a duplicate is detected (by fingerprint or fuzzy pass)
- **THEN** the new row's `canonical_event_id` SHALL be set to the canonical event's `id`

#### Scenario: Canonical events have NULL canonical_event_id
- **WHEN** an event is inserted as the first occurrence
- **THEN** its `canonical_event_id` SHALL be NULL

### Requirement: Canonical selection strategy
When a duplicate is detected across two existing events, the event with the higher score SHALL be the canonical. If scores are equal, the event with the earlier `created_at` timestamp SHALL be the canonical.

#### Scenario: Higher-scored event wins
- **WHEN** two events are identified as duplicates with scores 8 and 6
- **THEN** the event with score 8 SHALL be the canonical (and the other SHALL point to it)

### Requirement: Dedup logging
The system SHALL log each dedup action (fingerprint match, fuzzy match, link creation) to stdout with enough detail for auditing.

#### Scenario: Dedup actions are logged
- **WHEN** a duplicate is detected and linked
- **THEN** the system SHALL print a message like: `Duplicate detected: "Event Title" (id=X) → canonical (id=Y) via fingerprint`