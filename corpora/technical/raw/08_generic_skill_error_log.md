# Generic skills error log

source_id: generic_skill_error_log

Observed errors when running generic LLM-Wiki skills with GigaChat-3-Ultra
through deepagents v0.6.7 + deepagents-gigachat v0.0.2:

1. Stale index.md after ingest
   - Agent created wiki article but did not update wiki/index.md
   - Occurred in 3 out of 4 ingests when using independent agent.invoke() calls

2. Missing log.md update
   - Agent completed ingest but forgot to append to wiki/log.md
   - Especially common when the agent encounters and recovers from a tool error

3. Broken wikilinks
   - Links using project-root paths (wiki/nlp/article.md) instead of relative paths
   - Mixed path schemes within the same file
   - Phantom paths to directories that don't exist (e.g., wiki/machine-learning/)

4. Invalid or inconsistent metadata format
   - Raw files using 3 different header formats across 4 files
   - Wiki articles using 4 different metadata styles (blockquotes, headings, plain text, none)
   - Some files missing metadata entirely

5. Full file overwrite instead of edit
   - Agent used write_file on existing index.md, got error, then switched to edit_file
   - This happens every time for index.md and log.md after initialization

6. Answered from raw source but did not file answer back into wiki
   - Query answered correctly in chat but no wiki page was created when archiving was requested
   - Agent sometimes reads raw/ directly instead of compiled wiki/ articles

7. Fabricated dates
   - All 4 ingests happened on the same day but log.md shows 4 different dates
   - Dates appear to be hallucinated or taken from source publication dates

8. Verbatim copy instead of synthesis
   - One wiki article was a byte-for-byte copy of the raw source
   - No metadata header, no overview section, no See Also references

9. No cascade updates
   - Ingesting BERT (which directly references Transformer) did not update transformer.md
   - No See Also sections created in any article despite obvious cross-references
