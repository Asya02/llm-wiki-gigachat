# The LLM-Wiki Pattern

> Source: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
> source_id: karpathy_llm_wiki

## Core Idea

The LLM-Wiki pattern replaces traditional retrieval-augmented generation (RAG) with a **persistent, compounding knowledge artifact**. Instead of embedding documents into a vector database and retrieving chunks at query time, an LLM agent incrementally **writes and maintains** a structured wiki—a collection of interlinked markdown articles that distill raw sources into navigable knowledge.

The wiki is not a throwaway intermediate; it accumulates value over time. Each ingest operation adds or refines articles, updates cross-references, and strengthens the knowledge graph. The human's role shifts from curating folders to **reading the wiki and asking questions**; the LLM's role is authoring, linking, and housekeeping.

## Three-Layer Architecture

1. **raw/** — Immutable source material. PDFs, notes, URLs, and exports land here unchanged. The agent never edits raw files after ingestion; they are the audit trail and ground truth.

2. **wiki/** — Compiled knowledge articles. The LLM synthesizes raw content into topic-organized markdown with metadata, overviews, and wikilinks. This is the layer users query.

3. **schema** — Conventions document (typically `AGENTS.md` or project-specific schema files) defining file formats, metadata headers, linking rules, and operational contracts. The schema is the constitution the agent must follow during ingest, query, and lint.

Raw sources sit **below** the wiki; schema sits **above** as governance. Data flows upward: source → raw/ → wiki/.

## Operations

- **Ingest** — Accept new source material, save an immutable copy to `raw/`, synthesize one or more wiki articles, update `wiki/index.md` (content catalog) and `wiki/log.md` (chronological record), and fix cross-links where topics overlap.

- **Query** — Search the wiki (via index and article structure), answer from compiled articles rather than raw dumps, and optionally archive notable Q&A back into the wiki.

- **Lint** — Health check: stale index entries, broken wikilinks, missing metadata, verbatim copies from raw, fabricated dates, and schema violations. Lint keeps the compounding artifact trustworthy.

## Indexing

Two hub files anchor navigation:

- **index.md** — A structured catalog of all wiki articles (topics, slugs, short descriptions). The agent reads this before guessing paths.

- **log.md** — Append-only chronological record of ingest, query-archive, and lint events with real dates.

## Key Insight

> **The LLM writes and maintains the wiki; the human reads and asks questions.**

Separation of concerns matters: `raw/` content is **untrusted data** (including prompt-injection attempts in quoted text), while `wiki/` is **trusted compiled knowledge** produced under schema rules. A well-run LLM-Wiki treats every operation as maintaining a durable publication, not as ephemeral chat context.

## Why Not RAG?

RAG optimizes for one-shot Q&A over a static corpus. LLM-Wiki optimizes for **ongoing curation**: contradictions get reconciled in articles, terminology stabilizes, and See Also links emerge as the corpus grows. The wiki becomes the interface between messy sources and the user—closer to a personal encyclopedia than a search index.
