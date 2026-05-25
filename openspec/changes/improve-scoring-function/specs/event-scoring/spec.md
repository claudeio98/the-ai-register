# event-scoring Specification

## Purpose
Define the scoring logic used to assign a relevance score (0–10) to each discovered AI/ML event during content processing. The score determines which events are surfaced in the dashboard's "Highly Recommended" section and which events trigger email notifications (score ≥ 7).

## Requirements

### Requirement: Broad Institution Recognition
The system SHALL recognize and positively score events from a broader set of top-tier AI organizations and universities beyond the original "Big 5."

#### Scenario: Top-tier AI labs get high scores
- **WHEN** the LLM processes an event hosted or co-hosted by DeepMind, OpenAI, Meta AI, Google Research, Anthropic, Microsoft Research, or equivalent leading AI labs
- **THEN** the event receives a score of at least 4, with recognized keynote speakers pushing it higher

#### Scenario: Top-tier universities get high scores
- **WHEN** the LLM processes an event hosted or featuring speakers from Imperial, UCL, KCL, Oxford, Cambridge, MIT, Stanford, or equivalent top-tier universities
- **THEN** the event receives a score of at least 4

#### Scenario: Other reputable AI companies get moderate scores
- **WHEN** the LLM processes an event featuring speakers or organized by reputable AI companies (e.g., Hugging Face, Synthesia, Wayve, Luma AI, Stability AI)
- **THEN** the event receives a score of at least 2, reflecting its AI relevance

### Requirement: Conference Page Fair Scoring
The system SHALL evaluate conference/event registration or overview pages on their organizer reputation, speaker roster, and agenda quality rather than penalizing them for containing promotional copy.

#### Scenario: Registration page for a quality conference scores fairly
- **WHEN** the LLM processes a registration page for a legitimate AI conference with recognized organizers and quality speakers (e.g., the AI Accelerator Institute's Generative AI Summit with speakers from OpenAI, Meta, Hugging Face, Wayve)
- **THEN** the event receives a score reflecting the conference quality (at least 3–5), NOT a penalty for containing registration/marketing language

#### Scenario: Low-quality conference page still scores low
- **WHEN** the LLM processes a registration page for a generic non-AI conference or a clearly low-quality event
- **THEN** the event may still receive a low score (0–2) based on the actual quality assessment

### Requirement: Speaker Quality Signal
The system SHALL treat speaker reputation and speaker roster depth as a positive scoring signal, even when speakers are not from the top-tier institutions.

#### Scenario: Conference with strong speaker roster gets score boost
- **WHEN** the LLM processes a conference page listing multiple speakers from reputable companies or research backgrounds
- **THEN** the event receives additional score points proportional to the quality and number of speakers

#### Scenario: Single notable speaker gets modest boost
- **WHEN** the LLM processes an event with one clearly notable speaker (e.g., industry leader from a recognizable company)
- **THEN** the event receives a modest score boost (at least +1–2)

### Requirement: Irrelevant Event Penalty
The system SHALL penalize events that are clearly non-AI, generic marketing for non-AI products, or irrelevant to ML/AI topics.

#### Scenario: Non-AI marketing event scored low
- **WHEN** the LLM processes a page about a non-AI marketing conference, generic business event, or product launch unrelated to AI/ML
- **THEN** the event receives a low score (0–2) or is excluded entirely

#### Scenario: Conference page not confused with generic marketing
- **WHEN** the LLM processes a page for an AI/ML conference that uses registration or marketing copy
- **THEN** the LLM shall NOT apply the irrelevant event penalty; it shall instead assess the conference on its actual merits

### Requirement: Score Range Integrity
The system SHALL maintain scores within the 0–10 range and use the full scale appropriately.

#### Scenario: Scores use the full range
- **WHEN** the LLM assigns scores across multiple events in a batch
- **THEN** scores shall be distributed across the 0–10 range proportional to quality (not clustered in 0–1 or 7–10)

#### Scenario: Zero is reserved for truly irrelevant events
- **WHEN** the LLM scores an event as 0
- **THEN** 0 shall only be assigned when the event has genuinely zero AI/ML relevance or is unparseable, not for registration pages or events with unclear quality

## ADDED Requirements

### Requirement: Conference Speaker Aggregation
Events that are identified as conference/event overview pages SHALL have their score improved by aggregating speaker information from related child events (e.g., individual talk/agenda pages from the same conference).

#### Scenario: Conference page score improves after child events are processed
- **WHEN** the Conference Scorer runs after the initial processor phase
- **THEN** it SHALL query for events whose source has a `parent_id` chain linking back to a conference source
- **AND** it SHALL collect all child event data (speaker names, institutions, scores) for that conference
- **AND** it SHALL send the aggregated speaker roster to the LLM for re-scoring
- **AND** it SHALL update the conference event's score with the new, higher score reflecting the full speaker quality

#### Scenario: Conference with no child events gets no aggregation
- **WHEN** the Conference Scorer runs but a conference event has no child events
- **THEN** the conference event's existing score SHALL remain unchanged

#### Scenario: Conference Scorer runs on each pipeline cycle
- **WHEN** the pipeline executes the Conference Scorer phase
- **THEN** it SHALL update scores incrementally — child events processed in a previous cycle are already available

### Requirement: Event-Conference Linking
When an event is inserted during processor phase, the system SHALL attempt to link it to a parent conference event via the source `parent_id` chain, recording the link in the `conference_id` column of the events table.

#### Scenario: Child event linked to conference event
- **WHEN** an event is inserted from a source whose source chain has a `parent_id` that ultimately points to a conference event
- **THEN** the new event's `conference_id` SHALL be set to the conference event's ID

#### Scenario: Independent event not linked
- **WHEN** an event is inserted from a source with no meaningful `parent_id` chain
- **THEN** the event's `conference_id` SHALL remain NULL