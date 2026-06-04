"""Verify contradiction sources were ingested and older claims superseded."""

from __future__ import annotations

import re
from pathlib import Path

from bench.verify._shared import VerifyResult, wiki_md_files

OLD_RAW = "raw/corpus_mvp/04_synthetic_contradiction_old.md"
NEW_RAW = "raw/corpus_mvp/05_synthetic_contradiction_new.md"
SUPERSEDED_MARKERS = (
    "superseded",
    "supersede",
    "outdated",
    "obsolete",
    "replaced",
    "former",
    "old claim",
    "previous decision",
)
ACTIVE_AGENTS = ("agents.md", "use agents.md", "default is now agents.md")
STALE_CLAUDE = (
    "must always be named claude.md",
    "agents.md is not supported",
    "only claude.md",
    "authoritative schema document",
)


def verify(workspace_path: Path) -> VerifyResult:
    root = workspace_path.resolve()
    issues: list[str] = []

    if not (root / OLD_RAW).is_file():
        issues.append(f"missing contradiction source: {OLD_RAW}")
    if not (root / NEW_RAW).is_file():
        issues.append(f"missing contradiction source: {NEW_RAW}")

    old_ingested = _raw_referenced_in_wiki(root, OLD_RAW)
    new_ingested = _raw_referenced_in_wiki(root, NEW_RAW)
    if not old_ingested:
        issues.append("older contradiction source not referenced in any wiki article")
    if not new_ingested:
        issues.append("newer contradiction source not referenced in any wiki article")

    for path in wiki_md_files(root / "wiki"):
        rel = str(path.relative_to(root))
        text = path.read_text(encoding="utf-8").lower()
        has_superseded = any(m in text for m in SUPERSEDED_MARKERS)
        presents_stale = any(m in text for m in STALE_CLAUDE)
        presents_active = any(m in text for m in ACTIVE_AGENTS)

        if presents_stale and not has_superseded:
            issues.append(
                f"{rel}: presents old CLAUDE.md-only claim as current truth (not marked superseded)"
            )
        if presents_stale and presents_active and not has_superseded:
            issues.append(f"{rel}: contradiction not reconciled (old and new claims both active)")

    if not _wiki_mentions_supersession(root):
        issues.append("no wiki page marks the older schema claim as superseded")

    if not _wiki_endorses_agents_md(root):
        issues.append("no wiki page marks AGENTS.md as the current active decision")

    passed = len(issues) == 0
    return VerifyResult(passed, issues, 1.0 if passed else max(0.0, 1.0 - 0.2 * len(issues)))


def _raw_referenced_in_wiki(root: Path, raw_rel: str) -> bool:
    needle = raw_rel.replace("\\", "/")
    for path in wiki_md_files(root / "wiki"):
        if needle in path.read_text(encoding="utf-8"):
            return True
    return False


def _wiki_mentions_supersession(root: Path) -> bool:
    for path in wiki_md_files(root / "wiki"):
        text = path.read_text(encoding="utf-8").lower()
        if any(m in text for m in SUPERSEDED_MARKERS):
            return True
    return False


def _wiki_endorses_agents_md(root: Path) -> bool:
    for path in wiki_md_files(root / "wiki"):
        text = path.read_text(encoding="utf-8").lower()
        if "agents.md" in text and any(m in text for m in ("current", "default", "decision", "use ")):
            return True
    return False
