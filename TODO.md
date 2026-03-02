# AI News Aggregator - Improvement Plan

## Completed

- [x] **Add Official AI Company Blogs**: Fetch news directly from OpenAI, Anthropic, Google DeepMind, Meta AI, etc.
- [x] **Persistent Deduplication (SQLite)**: Track sent news URLs to avoid repeating the same news across days.
- [x] **Cross-source Deduplication**: Merge similar stories from different sources (e.g., same event on HN and TechCrunch).
- [x] **Full-text Content Extraction**: Fetch article text for better LLM summaries.
- [x] **High-Volume Processing**: Support summarizing 100+ news items daily using batch processing.
- [x] **Database Schema Upgrade**: Store full content, summaries, categories, and scores for future analysis.
- [x] **Detailed Chinese Report**: Generate high-density, categorized AI news reports in Chinese.
- [x] **Force Fetch Mode**: Added `--all` flag to fetch all news regardless of history.

## Medium Priority

- [ ] **Weekly Digest Mode**: Generate a weekly summary from the database (Partially implemented, needs refinement).
- [ ] **Structured Data Analysis**: Re-enable JSON output from LLM for better database querying (currently using text-only fallback for reliability).

## Low Priority

- [ ] **Image/Thumbnail Support**: Extract images for richer Feishu cards.
- [ ] **Health Checks**: Alert when sources fail repeatedly.
