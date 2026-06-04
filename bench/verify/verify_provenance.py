"""Verify source attribution and manifest source IDs."""

from __future__ import annotations

import re
from pathlib import Path

from bench.verify._shared import (
    LINK_RE,
    VerifyResult,
    manifest_source_ids,
    read_lines,
    resolve_link,
    wiki_md_files,
)

SOURCE_ID_RE = re.compile(r"\bsource_id:\s*(\w+)", re.I)


def verify(workspace_path: Path) -> VerifyResult:
    root = workspace_path.resolve()
    wiki_dir = root / "wiki"
    issues: list[str] = []

    manifest_ids: set[str] = set()
    for candidate in (
        root / "raw" / "raw_manifest.yaml",
        root / "raw_manifest.yaml",
    ):
        if candidate.is_file():
            manifest_ids = manifest_source_ids(candidate)
            break

    for path in wiki_md_files(wiki_dir):
        rel = str(path.relative_to(root))
        lines = read_lines(path)
        if len(lines) < 4:
            issues.append(f"{rel}: missing Sources/Raw metadata")
            continue
        if not lines[2].startswith("> Sources:"):
            issues.append(f"{rel}: missing '> Sources:' field")
        raw_line = lines[3] if len(lines) > 3 else ""
        if not raw_line.startswith("> Raw:"):
            issues.append(f"{rel}: missing '> Raw:' field pointing to raw/")
            continue
        refs = list(LINK_RE.finditer(raw_line))
        if refs:
            for m in refs:
                href = m.group(2)
                target = resolve_link(path, href, root)
                if not target.is_file():
                    issues.append(f"{rel}: Raw link does not exist: {href}")
                elif "raw" not in str(target.relative_to(root)).replace("\\", "/"):
                    issues.append(f"{rel}: Raw link must point under raw/: {href}")
        else:
            issues.append(f"{rel}: > Raw: should include markdown links to raw files")

        body = "\n".join(lines[4:])
        for m in SOURCE_ID_RE.finditer(body):
            sid = m.group(1)
            if manifest_ids and sid not in manifest_ids:
                issues.append(f"{rel}: unknown source_id '{sid}' (not in raw_manifest.yaml)")

    passed = len(issues) == 0
    return VerifyResult(passed, issues, 1.0 if passed else max(0.0, 1.0 - 0.15 * len(issues)))
