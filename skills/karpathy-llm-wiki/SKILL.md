---
name: karpathy-llm-wiki
description: "Use when building or maintaining a personal LLM-powered knowledge base. Triggers: ingesting sources into a wiki, querying wiki knowledge, linting wiki quality, 'add to wiki', 'what do I know about', or any mention of 'LLM wiki' or 'Karpathy wiki'."
---

# Karpathy LLM Wiki

Build and maintain a personal knowledge base using LLMs. Two directories: `raw/` (immutable sources) and `wiki/` (compiled knowledge). The wiki is a persistent, compounding artifact.

## CRITICAL RULES

Violating any of these is a critical error.

1. **raw/ is immutable.** Never modify or delete files in raw/ after they are saved.
2. **Use today's date.** For Collected, Updated, and log entries, always use the actual current date. Never fabricate or guess dates. If you do not know today's date, ask.
3. **Follow the exact format.** Every raw file, wiki article, index entry, and log entry must match the format shown in this document character-for-character. Do not invent alternative formats.
4. **Synthesize, never copy.** Wiki articles must reorganize and distill source material. Never paste raw source text as-is into a wiki article.
5. **Update index.md AND log.md.** Every ingest and every archive operation must update both files. No exceptions.
6. **Use relative paths consistently.** Inside wiki/ files, all paths are relative to the current file. Never use project-root-relative paths (never `wiki/topic/...` from inside wiki/).
7. **Check before writing.** Before creating any file, check if it already exists. Use edit_file for existing files. Use write_file only for new files.
8. **Read index.md before querying.** Never guess file paths. Always read wiki/index.md first to find where articles are located.

---

## Architecture

```
project-root/
  raw/                        ← Immutable source material
    <topic>/                  ← One level of subdirectories by topic
      <slug>.md
  wiki/                       ← Compiled knowledge articles
    <topic>/                  ← One level of subdirectories by topic
      <article>.md
    index.md                  ← Global index (TABLE format, not lists)
    log.md                    ← Append-only operation log
```

One level of topic subdirectories only. No deeper nesting.

---

## Initialization

On first ingest only. Check whether `raw/` and `wiki/` exist. Create only what is missing; never overwrite existing files.

1. Create `raw/` directory (with `.gitkeep` if empty)
2. Create `wiki/` directory (with `.gitkeep` if empty)
3. Create `wiki/index.md` with exactly: `# Knowledge Base Index` and an empty line
4. Create `wiki/log.md` with exactly: `# Wiki Log` and an empty line

If Query or Lint is called before any ingest, respond: "Run an ingest first to initialize the wiki."

---

## Ingest

Follow these steps in exact order. Do not skip any step.

### Step 1: Read the source

Read the provided source content. Identify: title, author/origin, publication date (if known).

### Step 2: Save to raw/

1. Pick a topic directory. Check existing `raw/` subdirectories first. Reuse if topic matches.
2. Choose a filename: `<slug>.md` where slug is kebab-case from the title, max 60 chars.
   - If published date is known, optionally prefix: `YYYY-MM-DD-<slug>.md`
   - If a file with the same name exists, append `-2`, `-3`, etc.
3. Write the file using the **exact format below**.

#### Raw file format

```
# <Title>

> Source: <URL or origin description>
> Collected: <YYYY-MM-DD>
> Published: <YYYY-MM-DD or Unknown>

<Original content, preserved faithfully. Clean formatting noise only.>
```

Concrete example of a correct raw file:

```
# Attention Is All You Need

> Source: https://arxiv.org/abs/1706.03762
> Collected: 2026-06-04
> Published: 2017-06-12

The Transformer architecture, introduced by Vaswani et al. in 2017,
replaced recurrent layers entirely with self-attention mechanisms...
```

**Mandatory format rules:**
- Line 1: `# ` followed by the title (H1 heading)
- Line 2: empty
- Line 3: `> Source: ` followed by the URL or description
- Line 4: `> Collected: ` followed by TODAY's date in YYYY-MM-DD
- Line 5: `> Published: ` followed by the publication date or `Unknown`
- Line 6: empty
- Lines 7+: the original content

**Common mistakes to avoid:**
- `Source URL: ...` instead of `> Source: ...` — WRONG
- `Collected Date: ...` instead of `> Collected: ...` — WRONG
- Omitting the `>` blockquote prefix — WRONG
- Omitting the `# Title` heading — WRONG
- Using a date you made up instead of today's actual date for Collected — WRONG

### Step 3: Compile wiki article

Decide where the content belongs:
- **Same core thesis as an existing article** → Merge into that article. Add new source to Sources/Raw.
- **New concept** → Create new article. Name the file after the concept, not the source.
- **Both** → Merge into one article AND create another for a distinct sub-concept.

Write the article using the **exact format below**.

#### Wiki article format

```
# <Article Title>

> Sources: <Author1, YYYY; Author2, YYYY>
> Raw: [<source-name>](../../raw/<topic>/<filename>.md)

## Overview

<One paragraph summarizing key points.>

## <Section Title>

<Synthesized content. Distill and reorganize — do NOT paste source text.>

## See Also

- [<Related Article>](<relative-path>)
```

Concrete example of a correct wiki article:

```
# Transformer Architecture

> Sources: Vaswani et al., 2017
> Raw: [Attention Is All You Need](../../raw/nlp/attention-is-all-you-need.md)

## Overview

The Transformer is a neural network architecture based entirely on attention
mechanisms, replacing recurrent layers for sequence modeling.

## Self-Attention Mechanism

The core operation is scaled dot-product attention: softmax(QK^T / sqrt(d_k)) * V.
Multi-head attention runs several such functions in parallel with different
learned projections, then concatenates and projects the results.

## Encoder-Decoder Structure

Each encoder layer pairs multi-head self-attention with a feed-forward network.
Decoder layers add cross-attention over encoder output. All sub-layers use
residual connections and layer normalization.

## See Also

- [BERT](bert.md)
- [GPT](gpt.md)
- [FlashAttention](../attention/flash-attention.md)
```

**Mandatory format rules:**
- Line 1: `# ` followed by the article title (H1 heading)
- Line 2: empty
- Line 3: `> Sources: ` followed by authors/dates, semicolon-separated
- Line 4: `> Raw: ` followed by markdown links to raw files, semicolon-separated
- Line 5: empty
- Line 6: `## Overview` heading
- Body: synthesized sections with `##` headings
- Last section (if cross-refs exist): `## See Also` with relative links

**Path rules for Raw links:**
- From `wiki/<topic>/article.md` to `raw/<topic>/file.md`: use `../../raw/<topic>/file.md`
- The path goes: up from article → up from topic dir → into raw/ → into topic → file

**Common mistakes to avoid:**
- Using `## Sources` as a section heading — WRONG (use `> Sources:` blockquote)
- Using `## Raw Materials` as a section heading — WRONG (use `> Raw:` blockquote)
- Using `### Sources` (wrong heading level) — WRONG
- Omitting Sources or Raw fields entirely — WRONG
- Pasting source text without synthesis — WRONG
- Omitting `## Overview` — WRONG

### Step 4: Cascade updates

After the primary article, check for ripple effects:

1. Read `wiki/index.md` to list all existing articles
2. For each article in the same topic directory, ask: does the new source add relevant information?
3. For articles in other topics, check if they reference related concepts
4. For every affected article:
   a. Update the relevant content
   b. Add or update a `## See Also` entry linking to the new article
   c. The article's Updated date in index.md gets refreshed to today

### Step 5: Update wiki/index.md

**IMPORTANT: Use TABLE format, not bullet lists.**

Read the existing index.md first. Then add or update entries.

#### Index format

```
# Knowledge Base Index

## <topic-name>

<One-line description of this topic.>

| Article | Summary | Updated |
|---------|---------|---------|
| [<Title>](<topic>/<filename>.md) | <One-line summary> | <YYYY-MM-DD> |
```

Concrete example of correct index.md:

```
# Knowledge Base Index

## nlp

Natural language processing models and architectures.

| Article | Summary | Updated |
|---------|---------|---------|
| [Transformer Architecture](nlp/transformer.md) | Self-attention-based architecture that replaced RNNs | 2026-06-04 |
| [BERT](nlp/bert.md) | Bidirectional encoder for language understanding | 2026-06-04 |
| [GPT](nlp/gpt.md) | Autoregressive decoder for language generation | 2026-06-04 |

## attention

Attention mechanism optimizations.

| Article | Summary | Updated |
|---------|---------|---------|
| [FlashAttention](attention/flash-attention.md) | IO-aware exact attention with O(N) memory | 2026-06-04 |
```

**Mandatory format rules:**
- Each topic section starts with `## <topic-name>` followed by a one-line description
- Articles listed in a markdown TABLE with three columns: Article, Summary, Updated
- Article column contains a markdown link: `[Title](topic/filename.md)`
- All paths are relative to wiki/ (since index.md is in wiki/)
- Summary is one line, no pipes or special characters
- Updated is YYYY-MM-DD format

**Common mistakes to avoid:**
- Using bullet lists (`- [Title](path)`) instead of a table — WRONG
- Using `•` as a separator instead of table columns — WRONG
- Path starting with `wiki/` (e.g., `wiki/nlp/article.md`) — WRONG (already inside wiki/)
- Omitting Updated date — WRONG
- Omitting Summary — WRONG
- Inconsistent separators between entries — WRONG

### Step 6: Append to wiki/log.md

Read the existing log.md first. Append a new entry at the end.

#### Log entry format

```
## [YYYY-MM-DD] ingest | <primary article title>
- Updated: <cascade-updated article title>
- Updated: <another cascade-updated article title>
```

Concrete example of a correct log entry:

```
## [2026-06-04] ingest | BERT
- Updated: Transformer Architecture
```

**Mandatory format rules:**
- Date in square brackets: `[YYYY-MM-DD]`
- Operation type: `ingest`
- Pipe separator between date+operation and title: ` | `
- Use today's actual date. Never fabricate.
- Cascade-updated articles listed with `- Updated:` prefix (omit if none)

**Common mistakes to avoid:**
- `## 2026-06-04 ingest` (missing square brackets) — WRONG but tolerable
- `## [2024-10-31] ingest` (fabricated date from the past) — WRONG
- Inconsistent bracket usage across entries — WRONG

### Step 7: Verify

After completing the ingest, verify:

1. Every wiki article file listed in index.md exists on disk
2. Every link in the new article points to an existing file
3. The new article has both `> Sources:` and `> Raw:` fields
4. log.md has a new entry with today's date
5. No raw/ files were modified

---

## Query

Search the wiki and answer questions.

### Steps

1. **Read wiki/index.md** to find relevant articles. NEVER guess file paths.
2. Read those articles and synthesize an answer.
3. Prefer wiki content over training knowledge. Cite with markdown links.
4. In conversation, use project-root-relative paths: `[Title](wiki/topic/article.md)`.
5. Output the answer in conversation. Do not write files unless asked.

### Archiving a query answer

When the user asks to save/archive the answer:

1. Write a new wiki page using this format:

```
# <Answer Title>

> Sources: [<Cited Article 1>](article1.md); [<Cited Article 2>](../other-topic/article2.md)
> Archived: <YYYY-MM-DD>

## Overview

<One paragraph summarizing the query and findings.>

## <Body Sections>

<The synthesized answer.>

## See Also

- [<Related Article>](<relative-path>)
```

2. Always create a NEW page. Never merge into existing articles.
3. Update `wiki/index.md` — prefix Summary with `[Archived]`.
4. Append to `wiki/log.md`:

```
## [YYYY-MM-DD] query | Archived: <page title>
```

---

## Lint

Quality checks on the wiki.

### Deterministic checks (auto-fix)

Fix these automatically:

1. **Index consistency.** Compare `wiki/index.md` against actual wiki/ files:
   - File exists but missing from index → add entry with `(no summary)` placeholder
   - Index entry points to nonexistent file → mark as `[MISSING]` in the index

2. **Internal links.** For every markdown link in wiki/ article bodies:
   - Target does not exist → search wiki/ for file with same name
   - One match → fix the path
   - Zero or multiple → report to user

3. **Raw references.** Every link in a `> Raw:` field must point to an existing raw/ file:
   - Target does not exist → search raw/ for file with same name
   - One match → fix the path
   - Zero or multiple → report to user

4. **Format consistency.** Check every wiki article for:
   - Has `> Sources:` on line 3 → if missing, add placeholder `> Sources: Unknown`
   - Has `> Raw:` on line 4 → if missing, add placeholder `> Raw: (none)`
   - Has `## Overview` section → if missing, report to user

5. **See Also.** Within each topic directory:
   - Add obviously missing cross-references between related articles
   - Remove links to deleted files

### Heuristic checks (report only)

Report without auto-fixing:
- Factual contradictions across articles
- Outdated claims superseded by newer sources
- Orphan pages with no inbound links
- Concepts frequently mentioned but lacking a dedicated page

### Post-Lint

Append to `wiki/log.md`:

```
## [YYYY-MM-DD] lint | <N> issues found, <M> auto-fixed
```

---

## Conventions Summary

- Standard markdown with relative links throughout
- wiki/ has one level of topic subdirectories only — no deeper nesting
- Today's date for: Collected, Updated, log entries, Archived dates
- Published dates come from the source (use `Unknown` when unavailable)
- Inside wiki/ files: paths relative to current file
- In conversation: project-root-relative paths (e.g., `wiki/topic/article.md`)
- Ingest always updates both index.md and log.md
- Archive always updates both index.md and log.md
- Lint updates log.md (and index.md only when auto-fixing)
- Plain queries do not write any files
