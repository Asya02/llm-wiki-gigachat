"""Verify query answers were archived in the wiki with index/log updates."""

from __future__ import annotations

import re
from pathlib import Path

from bench.verify._shared import LINK_RE, VerifyResult, read_lines

QUERY_LOG_RE = re.compile(r"^## .+ query \|", re.I)


def verify(workspace_path: Path) -> VerifyResult:
    root = workspace_path.resolve()
    wiki_dir = root / "wiki"
    issues: list[str] = []

    answer_files = _find_answer_files(wiki_dir)
    if not answer_files:
        issues.append("no query answer file under wiki/answers/")
        return VerifyResult(False, issues, 0.0)

    for path in answer_files:
        rel = str(path.relative_to(root))
        lines = read_lines(path)
        if len(lines) < 3 or not lines[2].startswith("> Sources:"):
            issues.append(f"{rel}: answer missing '> Sources:' metadata")

        body_links = [
            m.group(2)
            for line in lines[4:]
            for m in LINK_RE.finditer(line)
            if m.group(2).endswith(".md") and not m.group(2).startswith("http")
        ]
        if not body_links:
            issues.append(f"{rel}: answer should contain wikilinks to relevant articles")

        index_path = wiki_dir / "index.md"
        if index_path.is_file():
            rel_wiki = str(path.relative_to(wiki_dir)).replace("\\", "/")
            index_text = index_path.read_text(encoding="utf-8")
            if rel_wiki not in index_text and path.stem not in index_text:
                issues.append(f"wiki/index.md has no entry for answer {rel_wiki}")

    log_path = wiki_dir / "log.md"
    if not log_path.is_file():
        issues.append("wiki/log.md missing")
    elif not any(QUERY_LOG_RE.match(line) for line in read_lines(log_path)):
        issues.append("wiki/log.md has no query log entry")

    passed = len(issues) == 0
    return VerifyResult(passed, issues, 1.0 if passed else max(0.0, 1.0 - 0.15 * len(issues)))


def _find_answer_files(wiki_dir: Path) -> list[Path]:
    out: list[Path] = []
    for sub in ("answers", "archive", "queries"):
        d = wiki_dir / sub
        if d.is_dir():
            out.extend(sorted(d.rglob("*.md")))
    return out
