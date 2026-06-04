---
name: llm-wiki-ingest
description: "Use when ingesting a source into the LLM-Wiki. Triggers: 'ingest', 'add to wiki', source material provided."
---

# LLM-Wiki Ingest

Step-by-step procedure for ingesting a source into the wiki.

## Procedure

1. Read the source content. Identify title, author, publication date.
2. Check if raw/ and wiki/ exist. If not, create them with index.md and log.md.
3. Save source to raw/<topic>/<slug>.md using EXACT format:
   ```
   # <Title>

   > Source: <URL>
   > Collected: <TODAY>
   > Published: <date or Unknown>

   <content>
   ```
4. Check if an existing wiki article covers this topic. Read wiki/index.md.
5. If merging: read existing article, add new source to > Sources: and > Raw:, update content.
6. If new article: create wiki/<topic>/<concept>.md using EXACT format:
   ```
   # <Title>

   > Sources: <Author, YYYY>
   > Raw: [<name>](../../raw/<topic>/<file>.md)

   ## Overview

   <summary>

   ## <sections>

   ## See Also

   - [<related>](<path>)
   ```
7. Check for cascade updates: scan same-topic articles, add See Also cross-references.
8. Update wiki/index.md — add TABLE row: `| [Title](topic/file.md) | Summary | YYYY-MM-DD |`
9. Append to wiki/log.md: `## [YYYY-MM-DD] ingest | <title>`
10. Run python tools/wiki_lint.py to verify.
11. Fix any errors reported by the linter.
12. Report: list files changed and lint status.

## Critical Rules

- NEVER modify raw/ files after saving
- NEVER fabricate dates — use TODAY's date
- NEVER copy source verbatim — synthesize
- ALWAYS use > Sources: and > Raw: (blockquote format, not ## headings)
- ALWAYS update both index.md and log.md
- ALWAYS use relative paths inside wiki/
- ALWAYS check if file exists before write_file (use edit_file for existing)
