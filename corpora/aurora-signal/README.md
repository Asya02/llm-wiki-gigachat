# Aurora Signal — LLM-Wiki demo raw pack

This is a fictional raw-source corpus for demonstrating an LLM-Wiki workflow.
It is intentionally more story-like than a documentation corpus: the model has to build a wiki from expedition logs, emails, interviews, sensor data, lab notes, artifacts, contradictory updates, and one prompt-injection trap.

The demo question:

> What is the Aurora Signal, what most likely caused it, and what should the research team publish as the final evidence-backed explanation?

Recommended use:

1. Copy this folder into a clean agent workspace.
2. Use `prompts/demo_prompt_full.md` as the task prompt.
3. Ask the agent to build a persistent LLM-Wiki under `wiki/`.
4. Open the generated wiki in Obsidian or inspect the markdown graph.
5. Show `wiki/timeline.md`, `wiki/hypotheses/`, `wiki/contradictions.md`, and `wiki/answers/final-explanation.md`.

Why this corpus is useful:

- It tests multilingual ingestion: Russian and English sources.
- It tests structured data ingestion: CSV and JSON.
- It tests chronology reconstruction.
- It tests contradiction handling.
- It tests provenance: every durable claim should cite a source_id.
- It tests raw-source trust boundaries: one file contains malicious-looking instructions that must remain source content only.
- It creates a more visually interesting wiki than a purely technical documentation corpus.
