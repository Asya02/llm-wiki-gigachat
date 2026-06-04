# LLM-Wiki

Build a persistent wiki from raw sources. Three layers:

- `raw/` — Immutable source documents. Never modify.
- `wiki/` — Your compiled knowledge articles.
- This file — Schema and conventions.

## Structure

- `wiki/index.md` — Index of all articles
- `wiki/log.md` — Operation log
- Articles go in topic subdirectories: `wiki/<topic>/<article>.md`

## Operations

- **Ingest**: Read source → save to raw/ → write wiki article → update index and log
- **Query**: Read index → find articles → answer
- **Lint**: Check links, index, log consistency

## Rules

- Never modify raw/ after saving
- Update index.md and log.md after every ingest
- Use relative paths in wiki/ files
- Use today's date for log entries
