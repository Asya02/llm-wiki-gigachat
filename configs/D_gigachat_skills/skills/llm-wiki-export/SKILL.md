---
name: llm-wiki-export
description: "Use when exporting the wiki to external formats. Triggers: 'export', 'llms.txt', 'graph export', 'csv export'."
---

# LLM-Wiki Export

Step-by-step procedure for exporting wiki content to external formats.

## llms.txt Export

1. Read wiki/index.md to get all articles.
2. Create exports/llms.txt:
   ```
   # <Wiki Title>

   > <One-paragraph summary of the wiki>

   ## <Topic 1>

   - [<Article Title>](wiki/<topic>/<file>.md): <summary>

   ## <Topic 2>

   - [<Article Title>](wiki/<topic>/<file>.md): <summary>

   ## Optional

   - [<Secondary page>](wiki/<topic>/<file>.md): <summary>
   ```
3. Create exports/llms-full.txt: same structure but with full article content inlined.

## Graph Export

1. Read all wiki/ articles.
2. Extract all markdown links between wiki pages.
3. Create exports/wiki_edges.csv:
   ```
   source,target,type
   wiki/nlp/transformer.md,wiki/nlp/bert.md,see_also
   wiki/nlp/bert.md,wiki/nlp/transformer.md,see_also
   ```
4. Every node must be an existing wiki page.
5. No self-edges.

## Critical Rules

- Read wiki/ content, not raw/
- All links in exports must point to existing files
- Create exports/ directory if it doesn't exist
