# Initial GigaChat Test

Preserved output from the first GigaChat-3-Ultra test run through deepagents v0.6.7 + deepagents-gigachat v0.0.2. This run exposed the 9 failure modes documented in `../../ANALYSIS.md`.

## Contents

- `sources/` — 4 input source documents (Transformer, BERT, GPT, FlashAttention)
- `raw/` — GigaChat-generated raw layer (inconsistent formats)
- `wiki/` — GigaChat-generated wiki layer (broken metadata, paths, dates)
- `test_wiki.py` — Original test harness
- `source.md` — Misc source file from initial setup

## Known Issues

See `../../ANALYSIS.md` for the full breakdown. Key problems:

1. Three different raw file formats across 4 files
2. Four different wiki article metadata styles
3. Bullet lists instead of tables in index.md
4. Mixed relative/absolute paths
5. Fabricated dates in log.md
6. GPT article is a verbatim copy (no synthesis)
7. No cascade updates or See Also cross-references
