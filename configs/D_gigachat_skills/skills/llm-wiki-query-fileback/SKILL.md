---
name: llm-wiki-query-fileback
description: "Use when answering questions from the wiki and filing answers back. Triggers: 'query', 'what do I know about', 'answer and save'."
---

# LLM-Wiki Query with File-Back

Step-by-step procedure for answering questions using wiki content and optionally saving answers.

## Procedure

1. Read wiki/index.md to find relevant articles. NEVER guess file paths.
2. Read relevant articles from wiki/ (not from raw/).
3. Synthesize an answer using wiki content. Cite sources with links.
4. Present the answer in conversation with project-root-relative paths.
5. If user asks to save/archive the answer:
   a. Create wiki/answers/<topic-slug>.md using format:
      ```
      # <Answer Title>

      > Sources: [<Article1>](../topic/article.md); [<Article2>](../other/article.md)
      > Archived: <TODAY>

      ## Overview

      <summary>

      ## <body sections>

      ## See Also

      - [<related>](<path>)
      ```
   b. Update wiki/index.md with `[Archived]` prefix in Summary
   c. Append to wiki/log.md: `## [YYYY-MM-DD] query | Archived: <title>`

## Critical Rules

- ALWAYS read index.md first — never guess paths
- Prefer wiki/ content over raw/ content
- File answer back to wiki/ if user requests archiving
- Use relative paths in the archived answer page
- NEVER fabricate dates
