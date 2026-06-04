"""Verify ingest operations updated wiki articles, index, and log."""

from __future__ import annotations

import re
from pathlib import Path

from bench.verify._shared import (
    LINK_RE,
    VerifyResult,
    read_lines,
    resolve_link,
    wiki_md_files,
)

INGEST_LOG_RE = re.compile(r"^## .+ ingest \|", re.I)


def verify(workspace_path: Path) -> VerifyResult:
    root = workspace_path.resolve()
    wiki_dir = root / "wiki"
    issues: list[str] = []

    articles = wiki_md_files(wiki_dir)
    if not articles:
        issues.append("no wiki articles found (expected at least one ingest)")

    for path in articles:
        rel = str(path.relative_to(root))
        lines = read_lines(path)
        if len(lines) < 4:
            issues.append(f"{rel}: missing metadata block (need > Sources: and > Raw: on lines 3-4)")
            continue
        if not lines[2].startswith("> Sources:"):
            issues.append(f"{rel}: line 3 must start with '> Sources:'")
        if not (lines[3].startswith("> Raw:") or lines[3].startswith("> Archived:")):
            issues.append(f"{rel}: line 4 must start with '> Raw:' or '> Archived:'")
        if lines[3].startswith("> Raw:"):
            raw_line = lines[3]
            refs = list(LINK_RE.finditer(raw_line))
            if refs:
                for m in refs:
                    href = m.group(2)
                    target = resolve_link(path, href, root)
                    if not target.is_file():
                        issues.append(f"{rel}: broken raw link: {href}")
            else:
                tail = raw_line[len("> Raw:") :].strip()
                if tail:
                    target = resolve_link(path, tail, root)
                    if not target.is_file():
                        issues.append(f"{rel}: broken raw reference: {tail}")

    index_path = wiki_dir / "index.md"
    if not index_path.is_file():
        issues.append("wiki/index.md missing")
    elif articles:
        index_text = index_path.read_text(encoding="utf-8")
        for path in articles:
            rel = str(path.relative_to(wiki_dir)).replace("\\", "/")
            stem = path.stem
            if rel not in index_text and stem not in index_text:
                issues.append(f"wiki/index.md has no entry for {rel}")

    log_path = wiki_dir / "log.md"
    if not log_path.is_file():
        issues.append("wiki/log.md missing")
    else:
        has_ingest = any(
            INGEST_LOG_RE.match(line) for line in read_lines(log_path)
        )
        if not has_ingest:
            issues.append("wiki/log.md has no ingest log entry")

    passed = len(issues) == 0
    score = 1.0 if passed else max(0.0, 1.0 - 0.1 * len(issues))
    return VerifyResult(passed, issues, score)
