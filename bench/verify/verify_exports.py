"""Verify exports/llms.txt structure and linked files."""

from __future__ import annotations

import re
from pathlib import Path

from bench.verify._shared import LINK_RE, VerifyResult, is_external_link, resolve_link

H1_RE = re.compile(r"^#\s+.+")
H2_RE = re.compile(r"^##\s+.+")
BLOCKQUOTE_RE = re.compile(r"^>\s+.+")

def verify(workspace_path: Path) -> VerifyResult:
    root = workspace_path.resolve()
    issues: list[str] = []

    llms_path = root / "exports" / "llms.txt"
    if not llms_path.is_file():
        return VerifyResult(False, ["exports/llms.txt missing"], 0.0)

    lines = llms_path.read_text(encoding="utf-8").splitlines()
    if not lines or not H1_RE.match(lines[0]):
        issues.append("exports/llms.txt must start with H1 (# title)")

    if not any(BLOCKQUOTE_RE.match(line) for line in lines):
        issues.append("exports/llms.txt missing blockquote summary (> ...)")

    h2_lines = [line for line in lines if H2_RE.match(line)]
    if not h2_lines:
        issues.append("exports/llms.txt missing H2 sections (## ...)")

    in_h2 = False
    h2_with_link = False
    for line in lines:
        if H2_RE.match(line):
            in_h2 = True
            continue
        if in_h2 and LINK_RE.search(line):
            h2_with_link = True
            for m in LINK_RE.finditer(line):
                href = m.group(2).strip()
                if is_external_link(href):
                    continue
                target = resolve_link(llms_path, href, root)
                if not target.is_file():
                    issues.append(f"exports/llms.txt: broken export link: {href}")

    if h2_lines and not h2_with_link:
        issues.append("exports/llms.txt H2 sections should contain markdown links")

    edges = root / "exports" / "wiki_edges.csv"
    if edges.is_file():
        header = edges.read_text(encoding="utf-8").splitlines()[:1]
        if not header or "source" not in header[0].lower():
            issues.append("exports/wiki_edges.csv missing source,target,type header")

    passed = len(issues) == 0
    return VerifyResult(passed, issues, 1.0 if passed else max(0.0, 1.0 - 0.2 * len(issues)))
