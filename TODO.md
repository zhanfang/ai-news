# AI News Aggregator - Improvement Plan

## Completed

- [x] **Add Official AI Company Blogs**: Fetch news directly from OpenAI, Anthropic, Google DeepMind, Meta AI, etc.
- [x] **Persistent Deduplication (SQLite)**: Track sent news URLs to avoid repeating the same news across days.

## Medium Priority

- [ ] **Cross-source Deduplication**: Merge similar stories from different sources (e.g., same event on HN and TechCrunch).
- [ ] **Full-text Content Extraction**: Fetch article text (using `trafilatura` or similar) for better LLM summaries.
- [ ] **Weekly Digest Mode**: Generate a weekly summary from the database.

## Low Priority

- [ ] **Image/Thumbnail Support**: Extract images for richer Feishu cards.
- [ ] **Health Checks**: Alert when sources fail repeatedly.
