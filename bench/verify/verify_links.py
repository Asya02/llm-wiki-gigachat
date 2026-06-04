"""Verify markdown links in wiki/ resolve and use relative paths."""

from __future__ import annotations

import re
from pathlib import Path

from bench.verify._shared import (
    LINK_RE,
    VerifyResult,
    is_external_link,
    read_lines,
    resolve_link,
    wiki_md_files,
)

WIKI_PREFIX_RE = re.compile(r"^wiki/", re.I)


def verify(workspace_path: Path) -> VerifyResult:
    root = workspace_path.resolve()
    wiki_dir = root / "wiki"
    issues: list[str] = []

    if not wiki_dir.is_dir():
        return VerifyResult(False, ["wiki/ directory missing"], 0.0)

    for path in wiki_md_files(wiki_dir):
        rel = str(path.relative_to(root))
        for lineno, _text, href in _iter_links(path):
            if is_external_link(href):
                continue
            if WIKI_PREFIX_RE.match(href.strip()):
                issues.append(f"{rel}:{lineno}: absolute wiki/ prefix in link: {href}")
            resolved = resolve_link(path, href, root)
            if not resolved or not resolved.is_file():
                issues.append(f"{rel}:{lineno}: broken wikilink: {href}")

    # Also check index.md and log.md
    for name in ("index.md", "log.md"):
        path = wiki_dir / name
        if not path.is_file():
            continue
        rel = str(path.relative_to(root))
        for lineno, _text, href in _iter_links(path):
            if is_external_link(href):
                continue
            if WIKI_PREFIX_RE.match(href.strip()):
                issues.append(f"{rel}:{lineno}: absolute wiki/ prefix in link: {href}")
            resolved = resolve_link(path, href, root)
            if href.endswith(".md") and (not resolved or not resolved.is_file()):
                issues.append(f"{rel}:{lineno}: broken wikilink: {href}")

    passed = len(issues) == 0
    return VerifyResult(passed, issues, 1.0 if passed else 0.0)


def _iter_links(path: Path):
    for lineno, line in enumerate(read_lines(path), start=1):
        for m in LINK_RE.finditer(line):
            yield lineno, m.group(1), m.group(2)
