---
name: llm-wiki-lint-repair
description: "Use when linting or repairing the wiki. Triggers: 'lint', 'health check', 'fix wiki', 'check quality'."
---

# LLM-Wiki Lint & Repair

Step-by-step procedure for checking and fixing wiki quality.

## Procedure

1. Run `python tools/wiki_lint.py --workspace .` to get current issues.
2. For each ERROR-level issue:
   a. Broken wikilink → find correct file path, fix the link
   b. Missing index entry → add table row to wiki/index.md
   c. Missing metadata → add `> Sources: Unknown` and `> Raw: (none)` to article
   d. Broken raw reference → find correct raw/ file path, fix the link
3. For each WARNING-level issue:
   a. Orphan page → add a link from a related article's See Also section
   b. Missing See Also → add cross-references between related articles in same topic
   c. Path consistency → fix project-root paths to relative paths
4. Report heuristic findings (do not auto-fix):
   - Factual contradictions between articles
   - Outdated claims
   - Concepts mentioned but lacking dedicated pages
5. Append to wiki/log.md: `## [YYYY-MM-DD] lint | <N> issues found, <M> auto-fixed`
6. Run wiki_lint.py again to verify fixes.
7. Report final status.

## Critical Rules

- NEVER modify raw/ files
- NEVER delete wiki articles during lint (only fix/update)
- ALWAYS use edit_file for existing files
- ALWAYS update log.md after lint
