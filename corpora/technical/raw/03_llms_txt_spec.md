# The /llms.txt Specification

> Source: https://llmstxt.org/
> source_id: llms_txt_spec

## What It Is

**/llms.txt** is a proposed markdown file format designed to be **human-readable and LLM-friendly** at the same time. Sites and knowledge bases publish a single `llms.txt` (often at the domain root, analogous to `robots.txt`) that gives models a compact, structured map of important documentation—without scraping entire sites or relying on noisy HTML.

The format prioritizes **parseability**: predictable headings, a short summary up front, and link lists that agents can follow selectively.

## Document Structure

A conforming `llms.txt` file typically contains:

1. **H1 title** — The project or site name (one top-level heading).

2. **Blockquote summary** — A brief paragraph (in a blockquote) explaining what the resource is and how to use the file.

3. **H2 sections** — Thematic groups (e.g., "Docs", "API", "Guides") each containing **markdown links** to canonical pages, optionally with one-line descriptions.

4. **Optional secondary section** — Lower-priority or auxiliary links (blogs, changelogs, community) separated so primary resources stay prominent.

No proprietary binary envelope—plain markdown keeps it diffable, versionable, and easy to generate from a wiki index.

## Purpose

- Give LLMs a **curated entry point** instead of whole-site crawl.
- Let maintainers **declare** which URLs matter, in what order.
- Provide a **stable export shape** for documentation products and personal knowledge bases.

For LLM-Wiki projects, `llms.txt` is a natural **export target**: `wiki/index.md` and topic articles can be compiled into an `llms.txt` snapshot for external tools, RAG-free handoff, or publishing alongside the wiki.

## Relation to LLM-Wiki

| Layer | Role |
|-------|------|
| raw/ | Immutable sources |
| wiki/ | Rich articles with cross-links |
| llms.txt export | Thin, link-oriented index for LLM consumers |

The wiki remains the source of truth for depth; `llms.txt` is a **distilled facade**—similar to how `index.md` catalogs articles but oriented toward off-the-shelf LLM parsers and the llmstxt.org convention.

## Adoption Notes

The spec is evolving community practice (see llmstxt.org for examples). When generating from a wiki, keep summaries honest, refresh links on lint, and avoid dumping raw/untrusted text into the blockquote—export compiled descriptions only.
