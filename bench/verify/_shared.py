"""Shared helpers for bench verifiers (stdlib only)."""

from __future__ import annotations

import dataclasses
import hashlib
import json
import re
from pathlib import Path

LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
SKIP_LINK_PREFIXES = ("http://", "https://", "mailto:", "#", "data:")
EXCLUDED_WIKI = frozenset({"index.md", "log.md"})


@dataclasses.dataclass
class VerifyResult:
    passed: bool
    issues: list[str]
    score: float


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def is_external_link(target: str) -> bool:
    return target.startswith(SKIP_LINK_PREFIXES)


def resolve_link(source_file: Path, target: str, root: Path) -> Path:
    target = target.split("#", 1)[0].strip()
    if not target or is_external_link(target):
        return Path()
    if target.startswith("/"):
        return root / target.lstrip("/")
    return (source_file.parent / target).resolve()


def wiki_md_files(wiki_dir: Path) -> list[Path]:
    if not wiki_dir.is_dir():
        return []
    return sorted(
        p for p in wiki_dir.rglob("*.md") if p.name not in EXCLUDED_WIKI
    )


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def raw_file_snapshot(raw_dir: Path) -> dict[str, str]:
    """Map relative path from workspace root -> sha256."""
    snap: dict[str, str] = {}
    if not raw_dir.is_dir():
        return snap
    for p in sorted(raw_dir.rglob("*")):
        if p.is_file():
            rel = str(p.relative_to(raw_dir.parent))
            snap[rel.replace("\\", "/")] = file_hash(p)
    return snap


def load_baseline(workspace: Path) -> dict[str, str] | None:
    baseline_path = workspace.parent / "raw_baseline.json"
    if not baseline_path.is_file():
        return None
    return json.loads(baseline_path.read_text(encoding="utf-8"))


def parse_manifest_paths(manifest: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    current_path: str | None = None
    for line in manifest.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\s+path:\s*(.+?)\s*$", line)
        if m:
            current_path = m.group(1).strip().strip("'\"")
            entries[current_path] = ""
            continue
        m = re.match(r"^\s+sha256:\s*([a-f0-9]+)\s*$", line, re.I)
        if m and current_path:
            entries[current_path] = m.group(1).lower()
    return entries


def manifest_source_ids(manifest: Path) -> set[str]:
    ids: set[str] = set()
    in_sources = False
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if line.strip() == "sources:":
            in_sources = True
            continue
        if in_sources:
            m = re.match(r"^  (\w+):\s*$", line)
            if m:
                ids.add(m.group(1))
    return ids
