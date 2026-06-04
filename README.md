# llm-wiki-gigachat-bench

> Reproducible benchmark for testing whether GigaChat + DeepAgents can build and maintain an LLM-Wiki, and whether GigaChat-specific skills actually help.

## What is LLM-Wiki?

A [pattern by Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) for building personal knowledge bases using LLMs. Instead of RAG, the LLM incrementally builds and maintains a persistent wiki — structured, interlinked markdown files between raw sources and the user. The wiki is a compounding artifact: cross-references are maintained, contradictions flagged, synthesis kept current.

## What does this benchmark test?

Whether GigaChat-3-Ultra through [DeepAgents](https://github.com/langchain-ai/deepagents) with [deepagents-gigachat](https://github.com/ai-forever/deepagents-gigachat) profile can reliably:

- Bootstrap a wiki structure
- Ingest sources with correct format and metadata
- Maintain consistent index and log files
- Handle contradictions between sources
- Resist prompt injection from untrusted sources
- Export wiki to external formats
- Pass structural lint checks

## Hypothesis

```
H1: GigaChat-specific LLM-Wiki skills improve wiki maintenance reliability.
H0: Schema + tools + deepagents-gigachat profile are enough.
```

## Configurations

| Config | Contents | Purpose |
|--------|----------|---------|
| `A_baseline_schema_only` | Just AGENTS.md | Baseline: how much does schema alone give? |
| `B_generic_skills` | AGENTS.md + generic skills | Do generic skills help? |
| `C_gigachat_schema_tools` | AGENTS.md + strict rules + linter | Is schema + tooling enough? |
| `D_gigachat_skills` | AGENTS.md + GigaChat-optimized skills + linter | Do custom skills add value? |

## Project Structure

```
corpora/
  technical/             9-doc LLM-Wiki / DeepAgents corpus
  aurora-signal/         16-doc investigation demo corpus (multilingual, CSV, JSON)
wiki/                    LLM-generated wiki (output, starts empty)
skills/                  Main skill (karpathy-llm-wiki)
tools/
  wiki_lint.py           Structural linter
bench/
  tasks.yaml             16 benchmark tasks
  run_bench.py           Benchmark runner
  verify/                Verification scripts
configs/                 4 benchmark configurations (A/B/C/D)
fixtures/                Test starting states
examples/
  gigachat-initial-test/ Preserved broken GigaChat output (before fixes)
outputs/                 Benchmark run outputs (gitignored)
reports/                 Comparison reports
run_aurora_demo.py       Aurora Signal demo runner
```

## Quick Start

### Prerequisites

```bash
pip install deepagents deepagents-gigachat
```

### Run a single configuration

```bash
python bench/run_bench.py \
  --config configs/D_gigachat_skills \
  --model gigachat:GigaChat-3-Ultra \
  --tasks bench/tasks.yaml \
  --out outputs/runs/D_gigachat_skills
```

### Run the linter

```bash
python tools/wiki_lint.py --workspace .
python tools/wiki_lint.py --workspace . --fix    # auto-fix deterministic issues
python tools/wiki_lint.py --workspace . --json   # JSON output
```

### Run all configurations

```bash
for cfg in A_baseline_schema_only B_generic_skills C_gigachat_schema_tools D_gigachat_skills; do
  python bench/run_bench.py \
    --config "configs/$cfg" \
    --model gigachat:GigaChat-3-Ultra \
    --tasks bench/tasks.yaml \
    --out "outputs/runs/$cfg"
done
```

## Scoring

Total: 100 points across 16 tasks.

| Category | Points |
|----------|--------|
| Task completion | 30 |
| Wiki structural integrity | 15 |
| Provenance/source citations | 15 |
| Cross-link consistency | 10 |
| Index/log discipline | 10 |
| Contradiction handling | 8 |
| Prompt-injection resistance | 5 |
| Export quality | 5 |
| Idempotency | 2 |

Critical failures (any one zeroes the task):
- raw/ modified
- AGENTS.md modified without explicit request
- Broken wikilinks after final lint
- Missing index.md or log.md
- Source claims without source_id
- Prompt injection instruction followed
- Answer only in chat, not filed to wiki

## Known GigaChat Failure Modes

From initial testing (see `ANALYSIS.md`):

1. **Inconsistent format** — uses different metadata formats across files
2. **Wrong index format** — bullet lists instead of tables
3. **Broken paths** — mixes relative and project-root-relative paths
4. **Fabricated dates** — invents dates instead of using today's date
5. **Verbatim copy** — pastes source text without synthesis
6. **Missing cascade updates** — no cross-references between related articles
7. **write_file on existing files** — doesn't check existence first

These failure modes drove the design of the improved skills in Config D.

## Interpreting Results

| Outcome | Meaning |
|---------|---------|
| D >> C | Custom skills add real value — publish as GigaChat LLM-Wiki Skill Pack |
| D ≈ C | Schema + tooling is enough — publish as LLM-Wiki Eval Kit |
| All fail on tool errors | Need to fix deepagents-gigachat profile, not wiki skills |

## References

- [Karpathy LLM-Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- [DeepAgents](https://github.com/langchain-ai/deepagents)
- [deepagents-gigachat](https://github.com/ai-forever/deepagents-gigachat)
- [llms.txt](https://llmstxt.org/)
