# DeepAgents Agent Harness

> Source: https://github.com/langchain-ai/deepagents
> source_id: deepagents_readme

## Overview

DeepAgents is an open-source, batteries-included **agent harness** for building LLM-powered agents that can work autonomously over files, shells, and long-horizon tasks. Rather than wiring tools, memory, and context management from scratch for each project, developers configure a harness profile and deploy an agent with a consistent tool surface and lifecycle.

The harness sits between the LLM provider and the application: it handles tool invocation, state, optional subagents, and pluggable **skills**—reusable behavior modules that encode procedures the agent should follow for specific domains (e.g., wiki ingest, code review, deployment checklists).

## Built-In Capabilities

DeepAgents typically exposes:

- **Filesystem tools** — `read_file`, `write_file`, `edit_file`, and `list_directory` for reading and mutating project files under sandbox rules.
- **Shell access** — Execute commands for builds, tests, and environment inspection (with configurable restrictions).
- **Context management** — Trimming, summarization, and structured handoff so multi-step runs stay within context limits.
- **Memory** — Persistent or session-scoped recall for facts the agent should retain across turns.
- **Skills system** — Skills live as `SKILL.md` files (with YAML frontmatter) that the agent loads when triggered; they specify workflows, formats, and guardrails.
- **Subagent support** — Delegate subtasks to child agents with isolated context, useful for parallel research or specialized passes.

## How Skills Work

A skill is a **reusable behavior module**: markdown instructions plus metadata (`name`, `description`, triggers). When a user request matches, the harness surfaces the skill; the agent reads `SKILL.md` and follows its procedures step by step. Skills complement generic reasoning with domain-specific formats (e.g., exact wiki article templates, lint checklists).

Tools are exposed to the LLM as **function calls** (or provider-native tool schemas). The harness translates model outputs into tool executions and feeds results back into the conversation loop.

## Multi-Provider Support

DeepAgents supports multiple LLM backends through **harness profiles**—configuration packages that adapt tool descriptions, middleware (e.g., reasoning steps), and endpoint settings to each model family's quirks. Profiles can be discovered via Python entry points, allowing ecosystem packages (such as provider-specific profiles) to plug in without forking core harness code.

## Role in LLM-Wiki Benchmarks

For LLM-Wiki workloads, DeepAgents supplies the execution environment: filesystem tools to write `raw/` and `wiki/`, skills that encode Karpathy-style ingest/query/lint flows, and profiles tuned for models like GigaChat that need simpler tool schemas or extra reasoning middleware. The harness does not replace the wiki schema—it **enforces** agent access to the filesystem and skills that implement schema rules.
