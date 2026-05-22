## Context

The current AI Events Intelligence Pipeline uses a basic Node.js script (`content.js`) that performs simple HTTP requests and basic content extraction. This approach fails on modern Single Page Applications (SPAs) and sites that require JavaScript rendering to display event calendars. Additionally, the discovery phase only identifies "seed" URLs, with no mechanism to explore links found on those pages to find actual event listings.

## Goals / Non-Goals

**Goals:**
- Implement a browser-automation-based fetcher that can handle JS-heavy sites.
- Enable "Deep Discovery": the ability to identify event-related links on a page and add them back into the `sources` table for future fetching.
- Maintain the batch-processing nature of the pipeline to avoid harness timeouts.
- Improve content quality for the LLM processor by capturing rendered HTML or structured text.

**Non-Goals:**
- Building a full-scale web crawler. We will focus on targeted "deep dives" into identified high-value sources.
- Real-time monitoring. The pipeline remains a scheduled/periodic batch process.

## Decisions

### 1. Browser Automation Tool
**Decision**: Use the `agent-browser` CLI (integrated into the pi harness) or a dedicated Playwright/Puppeteer wrapper.
**Rationale**: `agent-browser` provides high-level abstractions for interaction (click, fill, scroll) and handles snapshots, making it ideal for dynamic content. It avoids the need to manage low-level browser binaries in the environment.
**Alternative**: Raw Playwright. While more powerful, it requires more boilerplate for session management and is more prone to detection.

### 2. Deep Discovery Logic
**Decision**: Implement a "Discovery-to-Fetch" loop where `fetcher.py` not only extracts content but also scans for links that look like event calendars or individual event pages.
**Rationale**: Many high-value events are listed on sub-pages (e.g., `/events/2026-05-17`). If we only fetch the landing page, we miss the data.
**Alternative**: Expand the LLM-generated search queries to be more granular. This is less efficient than following internal links of a trusted source.

### 3. Database Schema Updates
**Decision**: Add a `parent_id` column to the `sources` table to track the lineage of discovered URLs.
**Rationale**: This allows us to track which seed URL led to which event page, helping in pruning ineffective seeds and prioritizing high-yield sources.
**Alternative**: Just adding URLs to the table without relationship tracking. This loses the "lineage" context.

## Risks / Trade-offs

- **[Detection/Blocking]** $\rightarrow$ The browser automation might be detected as a bot. **Mitigation**: Use realistic headers, random delays, and the `agent-browser`'s built-in evasion techniques.
- **[Performance/Timeout]** $\rightarrow$ Full browser rendering is slower than simple HTTP requests. **Mitigation**: Keep the batch size small (5 URLs per run) and implement strict timeouts per URL.
- **[Resource Exhaustion]** $\rightarrow$ Running multiple browser instances can consume memory. **Mitigation**: Use a single browser session per batch run.

## Open Questions

- Should we use the LLM to identify which links are "event-related" or use regex/keyword-based filtering for the first pass? (Current plan: Regex for fast filtering, then LLM for validation).
