## Why

The current data pipeline relies on a simple content extractor that frequently misses dynamic content on JS-heavy event pages and is limited to extracting content from a single URL. This results in missed events from modern websites and a low volume of discovered high-value opportunities.

## What Changes

- **Browser-Based Fetching**: Replace or augment the current `content.js` extractor with a full browser automation tool capable of rendering JavaScript, handling redirects, and interacting with page elements (e.g., scrolling, clicking "load more").
- **Deep Event Discovery**: Enhance the discovery process to not only find landing pages but to identify and extract multiple specific event/calendar URLs from a single source.
- **Content Extraction Pipeline**: Update `fetcher.py` to support a queue of discovered sub-links, allowing the pipeline to "deep dive" into a site once a high-value calendar is found.
- **Improved Error Handling**: Implement more robust browser session management to avoid timeouts and detection by anti-bot measures.

## Capabilities

### New Capabilities
- `browser-automation-fetcher`: Capability to render dynamic pages and extract structured content using browser automation.
- `deep-event-discovery`: Capability to analyze a page for event-related links and automatically add them to the discovery queue.

### Modified Capabilities
- None (No existing specs to modify).

## Impact

- **Code**: `src/discovery.py` and `src/fetcher.py` will be significantly rewritten.
- **Dependencies**: Potential addition of a browser automation library or API (e.g., `agent-browser` or Playwright).
- **Storage**: `sources` and `raw_pages` tables may need updates to track the relationship between "seed" URLs and "discovered" sub-links.
