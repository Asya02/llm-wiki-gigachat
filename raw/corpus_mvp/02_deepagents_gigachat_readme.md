# DeepAgents GigaChat Profile

> Source: https://github.com/ai-forever/deepagents-gigachat
> source_id: deepagents_gigachat_readme

## Purpose

**deepagents-gigachat** is a harness profile package that optimizes [DeepAgents](https://github.com/langchain-ai/deepagents) for **GigaChat** models from Sber. Stock DeepAgents tool descriptions and calling conventions assume Western-model patterns; GigaChat benefits from adapted schemas, explicit file-operation contracts, and middleware that structures reasoning before tool use.

Install the profile alongside DeepAgents; discovery happens automatically via **Python entry points**, registering a named profile selectable at agent startup.

## Provider Configuration

The profile targets the GigaChat OpenAI-compatible API:

- **Endpoint:** `https://gigachat.sberdevices.ru/v1`
- Credentials and model IDs are configured through standard harness environment variables and profile settings (API keys, model name such as GigaChat-3-Ultra).

No fork of DeepAgents core is required—the profile is a thin adaptation layer.

## Key Adaptations

1. **Tool descriptions** — Shorter, clearer parameter docs aligned with GigaChat's tool-calling format; avoids overloaded JSON schemas that confuse the model.

2. **`think` middleware** — Inserts a structured reasoning step before tool calls so the model plans file paths and operations instead of firing tools impulsively—critical for multi-file wiki ingest.

3. **Filesystem path conventions** — Explicit rules: relative paths inside `wiki/`, never project-root prefixes like `wiki/topic/article.md` from within wiki files; consistent slugs and topic directories.

4. **File operation contracts** — When to use `write_file` (new files only) vs `edit_file` (existing `index.md`, `log.md`); reduces full-file overwrite errors after initialization.

## Benchmark Impact

On a mechanical LLM-Wiki benchmark (231 checks), **GigaChat-3-Ultra** improved from **164/231** (generic DeepAgents) to **195/231** with the GigaChat profile—gains concentrated in index/log updates, valid wikilinks, and metadata consistency rather than raw comprehension.

## When to Use Profile vs Skills

The profile fixes **model–harness friction** (tool calling, path wording, reasoning cadence). Domain skills (e.g., Karpathy LLM-Wiki `SKILL.md`) still define **what** to write in `wiki/`. For GigaChat wiki benchmarks, use **profile + schema + linter** as the baseline; add skills only for failure modes the profile and schema do not cover.

## Repository

Full install instructions, version compatibility (e.g., deepagents v0.6.x), and changelog: https://github.com/ai-forever/deepagents-gigachat
