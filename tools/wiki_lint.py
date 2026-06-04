#!/usr/bin/env python3
"""Mechanical linter for LLM-Wiki workspaces (Karpathy pattern). Stdlib only."""

from __future__ import annotations

import argparse
import dataclasses
import difflib
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable

LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
LOG_ENTRY_RE = re.compile(
    r"^## \[?(\d{4}-\d{2}-\d{2})\]? (\S+) \| (.+)$"
)
INDEX_TABLE_LINK_RE = re.compile(r"\|\s*\[([^\]]*)\]\(([^)]+)\)\s*\|")
H1_RE = re.compile(r"^#\s+(.+)$")
SKIP_LINK_PREFIXES = ("http://", "https://", "mailto:", "#", "data:")

EXCLUDED_WIKI = frozenset({"index.md", "log.md"})


@dataclasses.dataclass
class LintIssue:
    severity: str  # error | warning | info
    category: str
    file: str
    line: int
    message: str

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


class WikiWorkspace:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.raw_dir = self.root / "raw"
        self.wiki_dir = self.root / "wiki"

    def wiki_md_files(self) -> list[Path]:
        if not self.wiki_dir.is_dir():
            return []
        return sorted(
            p for p in self.wiki_dir.rglob("*.md") if p.name not in EXCLUDED_WIKI
        )

    def rel(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.root))
        except ValueError:
            return str(path)


def issue(
    severity: str,
    category: str,
    file: str,
    line: int,
    message: str,
) -> LintIssue:
    return LintIssue(severity, category, file, line, message)


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def is_external_link(target: str) -> bool:
    return target.startswith(SKIP_LINK_PREFIXES)


def resolve_link(source_file: Path, target: str, workspace: WikiWorkspace) -> Path:
    target = target.split("#", 1)[0].strip()
    if not target or is_external_link(target):
        return Path()
    if target.startswith("/"):
        return workspace.root / target.lstrip("/")
    return (source_file.parent / target).resolve()


def iter_markdown_links(
    path: Path, lines: Iterable[str]
) -> Iterable[tuple[int, str, str]]:
    for lineno, line in enumerate(lines, start=1):
        for m in LINK_RE.finditer(line):
            yield lineno, m.group(1), m.group(2)


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_manifest_paths(manifest: Path) -> dict[str, str]:
    """Return path -> optional sha256 from raw_manifest.yaml (minimal parse)."""
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


def raw_immutability(ws: WikiWorkspace) -> list[LintIssue]:
    issues: list[LintIssue] = []
    if not ws.raw_dir.is_dir():
        return [
            issue("error", "raw_immutability", str(ws.raw_dir), 0, "raw/ directory missing")
        ]
    raw_files = [p for p in ws.raw_dir.rglob("*") if p.is_file()]
    if not raw_files:
        issues.append(
            issue("error", "raw_immutability", ws.rel(ws.raw_dir), 0, "raw/ is empty")
        )
        return issues

    for candidate in (ws.raw_dir / "raw_manifest.yaml", ws.root / "raw_manifest.yaml"):
        if not candidate.is_file():
            continue
        manifest_paths = parse_manifest_paths(candidate)
        actual = {
            ws.rel(p) for p in raw_files if p.name != "raw_manifest.yaml"
        }
        expected = set(manifest_paths.keys())
        for missing in sorted(expected - actual):
            issues.append(
                issue(
                    "error",
                    "raw_immutability",
                    ws.rel(candidate),
                    0,
                    f"manifest lists missing file: {missing}",
                )
            )
        for extra in sorted(actual - expected):
            issues.append(
                issue(
                    "error",
                    "raw_immutability",
                    ws.rel(candidate),
                    0,
                    f"file not in manifest (raw/ changed): {extra}",
                )
            )
        for rel_path, expected_hash in manifest_paths.items():
            if not expected_hash:
                continue
            full = ws.root / rel_path
            if full.is_file() and file_hash(full) != expected_hash:
                issues.append(
                    issue(
                        "error",
                        "raw_immutability",
                        rel_path,
                        0,
                        "file modified since manifest (sha256 mismatch)",
                    )
                )
        break
    return issues


def frontmatter_check(ws: WikiWorkspace) -> list[LintIssue]:
    issues: list[LintIssue] = []
    for path in ws.wiki_md_files():
        lines = read_lines(path)
        rel = ws.rel(path)
        if not lines:
            issues.append(issue("error", "frontmatter_check", rel, 1, "empty file"))
            continue
        if not lines[0].startswith("# "):
            issues.append(
                issue("error", "frontmatter_check", rel, 1, "line 1 must be H1 (# Title)")
            )
        if len(lines) < 3:
            issues.append(issue("error", "frontmatter_check", rel, 0, "missing metadata block"))
            continue
        if not lines[2].startswith("> Sources:"):
            issues.append(
                issue(
                    "error",
                    "frontmatter_check",
                    rel,
                    3,
                    "line 3 must start with '> Sources:'",
                )
            )
        if len(lines) < 4:
            issues.append(issue("error", "frontmatter_check", rel, 0, "missing line 4 metadata"))
            continue
        line4 = lines[3]
        if not (line4.startswith("> Raw:") or line4.startswith("> Archived:")):
            issues.append(
                issue(
                    "error",
                    "frontmatter_check",
                    rel,
                    4,
                    "line 4 must start with '> Raw:' or '> Archived:'",
                )
            )
    return issues


def wikilink_check(ws: WikiWorkspace) -> list[LintIssue]:
    issues: list[LintIssue] = []
    for path in ws.wiki_md_files():
        lines = read_lines(path)
        for lineno, _text, href in iter_markdown_links(path, lines):
            if is_external_link(href):
                continue
            resolved = resolve_link(path, href, ws)
            if not resolved or not resolved.is_file():
                issues.append(
                    issue(
                        "error",
                        "wikilink_check",
                        ws.rel(path),
                        lineno,
                        f"broken link: {href}",
                    )
                )
    return issues


def raw_reference_check(ws: WikiWorkspace) -> list[LintIssue]:
    issues: list[LintIssue] = []
    for path in ws.wiki_md_files():
        for lineno, line in enumerate(read_lines(path), start=1):
            if not line.startswith("> Raw:"):
                continue
            refs = list(LINK_RE.finditer(line))
            if not refs:
                tail = line[len("> Raw:") :].strip()
                if tail:
                    target = resolve_link(path, tail, ws)
                    if not target.is_file():
                        issues.append(
                            issue(
                                "error",
                                "raw_reference_check",
                                ws.rel(path),
                                lineno,
                                f"broken raw reference: {tail}",
                            )
                        )
                continue
            for m in refs:
                href = m.group(2)
                target = resolve_link(path, href, ws)
                if not target.is_file():
                    issues.append(
                        issue(
                            "error",
                            "raw_reference_check",
                            ws.rel(path),
                            lineno,
                            f"broken raw reference: {href}",
                        )
                    )
    return issues


def normalize_wiki_path(path: str) -> str:
    return path.replace("\\", "/").removeprefix("wiki/").lstrip("/")


def extract_index_paths(index_path: Path) -> set[str]:
    paths: set[str] = set()
    for line in index_path.read_text(encoding="utf-8").splitlines():
        for m in INDEX_TABLE_LINK_RE.finditer(line):
            paths.add(normalize_wiki_path(m.group(2).strip()))
        for m in LINK_RE.finditer(line):
            href = m.group(2)
            if href.endswith(".md"):
                paths.add(normalize_wiki_path(href.strip()))
    return paths


def wiki_article_index_paths(ws: WikiWorkspace) -> set[str]:
    return {
        str(p.relative_to(ws.wiki_dir)).replace("\\", "/")
        for p in ws.wiki_md_files()
    }


def index_consistency(ws: WikiWorkspace) -> list[LintIssue]:
    issues: list[LintIssue] = []
    index_path = ws.wiki_dir / "index.md"
    if not index_path.is_file():
        return [issue("error", "index_consistency", "wiki/index.md", 0, "index.md missing")]
    indexed = extract_index_paths(index_path)
    actual = wiki_article_index_paths(ws)
    for rel in sorted(actual - indexed):
        issues.append(
            issue(
                "warning",
                "index_consistency",
                "wiki/index.md",
                0,
                f"article missing from index: {rel}",
            )
        )
    for rel in sorted(indexed):
        if rel not in actual:
            full = ws.wiki_dir / rel
            if not full.is_file():
                issues.append(
                    issue(
                        "error",
                        "index_consistency",
                        "wiki/index.md",
                        0,
                        f"index points to missing file: {rel}",
                    )
                )
    return issues


def log_format(ws: WikiWorkspace) -> list[LintIssue]:
    issues: list[LintIssue] = []
    log_path = ws.wiki_dir / "log.md"
    rel = ws.rel(log_path)
    if not log_path.is_file():
        return [issue("error", "log_format", rel, 0, "log.md missing")]
    lines = read_lines(log_path)
    if not lines:
        return [issue("error", "log_format", rel, 0, "log.md is empty")]
    dates: list[tuple[datetime, int]] = []
    for lineno, line in enumerate(lines, start=1):
        if not line.startswith("## "):
            continue
        m = LOG_ENTRY_RE.match(line)
        if not m:
            issues.append(
                issue(
                    "error",
                    "log_format",
                    rel,
                    lineno,
                    "entry must match: ## [YYYY-MM-DD] <operation> | <description>",
                )
            )
            continue
        try:
            dt = datetime.strptime(m.group(1), "%Y-%m-%d")
            dates.append((dt, lineno))
        except ValueError:
            issues.append(
                issue("error", "log_format", rel, lineno, f"invalid date: {m.group(1)}")
            )
    for i in range(1, len(dates)):
        if dates[i][0] < dates[i - 1][0]:
            issues.append(
                issue(
                    "error",
                    "log_format",
                    rel,
                    dates[i][1],
                    "log entries are not in chronological order",
                )
            )
    return issues


def build_inbound_links(ws: WikiWorkspace) -> dict[str, set[str]]:
    inbound: dict[str, set[str]] = {}
    articles = {ws.rel(p) for p in ws.wiki_md_files()}
    for path in ws.wiki_md_files():
        src = ws.rel(path)
        for _lineno, _text, href in iter_markdown_links(path, read_lines(path)):
            if is_external_link(href):
                continue
            resolved = resolve_link(path, href, ws)
            if not resolved.suffix == ".md":
                continue
            try:
                target = ws.rel(resolved)
            except ValueError:
                continue
            if target in articles:
                inbound.setdefault(target, set()).add(src)
    return inbound


def orphan_check(ws: WikiWorkspace) -> list[LintIssue]:
    issues: list[LintIssue] = []
    inbound = build_inbound_links(ws)
    for path in ws.wiki_md_files():
        rel = ws.rel(path)
        if not inbound.get(rel):
            issues.append(
                issue(
                    "warning",
                    "orphan_check",
                    rel,
                    0,
                    "no inbound links from other wiki articles",
                )
            )
    return issues


def parse_see_also_links(lines: list[str]) -> set[str]:
    links: set[str] = set()
    in_section = False
    for line in lines:
        if line.startswith("## See Also"):
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            for m in LINK_RE.finditer(line):
                links.add(m.group(2).split("#", 1)[0])
    return links


def slug_tokens(name: str) -> set[str]:
    base = Path(name).stem.lower()
    return {t for t in re.split(r"[-_\s]+", base) if len(t) > 3}


def see_also_check(ws: WikiWorkspace) -> list[LintIssue]:
    issues: list[LintIssue] = []
    by_topic: dict[str, list[Path]] = {}
    for path in ws.wiki_md_files():
        topic = path.parent.name if path.parent != ws.wiki_dir else ""
        by_topic.setdefault(topic, []).append(path)

    for topic, paths in by_topic.items():
        if len(paths) < 2:
            continue
        for path in paths:
            lines = read_lines(path)
            see_also = parse_see_also_links(lines)
            if not see_also:
                issues.append(
                    issue(
                        "warning",
                        "see_also_check",
                        ws.rel(path),
                        0,
                        f"no See Also section (topic '{topic}' has {len(paths)} articles)",
                    )
                )
        for i, a in enumerate(paths):
            for b in paths[i + 1 :]:
                ratio = difflib.SequenceMatcher(
                    None, a.stem.lower(), b.stem.lower()
                ).ratio()
                shared = slug_tokens(a.name) & slug_tokens(b.name)
                if ratio < 0.55 and not shared:
                    continue
                for src, dst in ((a, b), (b, a)):
                    see = parse_see_also_links(read_lines(src))
                    dst_name = dst.name
                    if not any(
                        dst_name in link or Path(link).name == dst_name for link in see
                    ):
                        issues.append(
                            issue(
                                "info",
                                "see_also_check",
                                ws.rel(src),
                                0,
                                f"related article not in See Also: {dst.name}",
                            )
                        )
    return issues


def duplicate_check(ws: WikiWorkspace) -> list[LintIssue]:
    issues: list[LintIssue] = []
    titles: dict[str, list[str]] = {}
    paths = ws.wiki_md_files()
    for path in paths:
        lines = read_lines(path)
        m = H1_RE.match(lines[0]) if lines else None
        if m:
            title = m.group(1).strip().lower()
            titles.setdefault(title, []).append(ws.rel(path))
    for title, files in titles.items():
        if len(files) > 1:
            issues.append(
                issue(
                    "error",
                    "duplicate_check",
                    files[0],
                    1,
                    f"duplicate title '{title}' in: {', '.join(files)}",
                )
            )
    for i, a in enumerate(paths):
        for b in paths[i + 1 :]:
            ratio = difflib.SequenceMatcher(None, a.stem, b.stem).ratio()
            if ratio >= 0.85 and a.stem != b.stem:
                issues.append(
                    issue(
                        "warning",
                        "duplicate_check",
                        ws.rel(a),
                        0,
                        f"similar filename to {b.name} (ratio {ratio:.2f})",
                    )
                )
    return issues


def all_wiki_md(ws: WikiWorkspace) -> list[Path]:
    if not ws.wiki_dir.is_dir():
        return []
    return sorted(ws.wiki_dir.rglob("*.md"))


def path_consistency(ws: WikiWorkspace) -> list[LintIssue]:
    issues: list[LintIssue] = []
    bad_prefixes = ("wiki/", "raw/", "/wiki/", "/raw/")
    for path in all_wiki_md(ws):
        for lineno, _text, href in iter_markdown_links(path, read_lines(path)):
            if is_external_link(href):
                continue
            if href.startswith(bad_prefixes):
                issues.append(
                    issue(
                        "error",
                        "path_consistency",
                        ws.rel(path),
                        lineno,
                        f"use relative path, not project-root path: {href}",
                    )
                )
    return issues


CHECKS = [
    raw_immutability,
    frontmatter_check,
    wikilink_check,
    raw_reference_check,
    index_consistency,
    log_format,
    orphan_check,
    see_also_check,
    duplicate_check,
    path_consistency,
]


def find_single_basename_match(href: str, ws: WikiWorkspace) -> str | None:
    name = Path(href.split("#", 1)[0]).name
    if not name:
        return None
    matches = [p for p in ws.wiki_md_files() if p.name == name]
    if len(matches) == 1:
        return str(matches[0].relative_to(ws.wiki_dir)).replace("\\", "/")
    return None


def apply_fixes(ws: WikiWorkspace, issues: list[LintIssue]) -> list[str]:
    actions: list[str] = []
    index_path = ws.wiki_dir / "index.md"

    for path in ws.wiki_md_files():
        lines = read_lines(path)
        changed = False
        new_lines: list[str] = []
        for lineno, line in enumerate(lines):
            new_line = line
            for m in LINK_RE.finditer(line):
                href = m.group(2)
                if is_external_link(href):
                    continue
                resolved = resolve_link(path, href, ws)
                if resolved.is_file():
                    continue
                fix = find_single_basename_match(href, ws)
                if fix:
                    try:
                        fixed_href = str(
                            (path.parent / fix).relative_to(path.parent)
                        ).replace("\\", "/")
                    except ValueError:
                        fixed_href = fix
                    new_line = new_line.replace(f"({href})", f"({fixed_href})")
                    changed = True
                    actions.append(
                        f"fixed link in {ws.rel(path)}:{lineno} {href} -> {fixed_href}"
                    )
            new_lines.append(new_line)
        if changed:
            path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

    indexed = extract_index_paths(index_path) if index_path.is_file() else set()
    actual = wiki_article_index_paths(ws)
    missing = sorted(actual - indexed)
    if missing and index_path.is_file():
        extra_lines = ["", "## Auto-added by wiki_lint", ""]
        extra_lines.append("| Article | Summary | Updated |")
        extra_lines.append("|---------|---------|---------|")
        today = datetime.now().strftime("%Y-%m-%d")
        for rel in missing:
            article = ws.wiki_dir / rel
            title = rel
            if article.is_file():
                m = H1_RE.match(read_lines(article)[0])
                if m:
                    title = m.group(1).strip()
            extra_lines.append(f"| [{title}]({rel}) | (pending) | {today} |")
            actions.append(f"added index entry for {rel}")
        text = index_path.read_text(encoding="utf-8")
        if not text.endswith("\n"):
            text += "\n"
        index_path.write_text(text + "\n".join(extra_lines) + "\n", encoding="utf-8")

    return actions


def format_human(issues: list[LintIssue], fix_actions: list[str]) -> str:
    lines: list[str] = []
    if fix_actions:
        lines.append("Fixes applied:")
        for a in fix_actions:
            lines.append(f"  - {a}")
        lines.append("")
    if not issues:
        lines.append("No issues found.")
        return "\n".join(lines)
    by_severity = {"error": 0, "warning": 0, "info": 0}
    for i in issues:
        by_severity[i.severity] = by_severity.get(i.severity, 0) + 1
    lines.append(
        f"Found {len(issues)} issue(s): "
        + ", ".join(f"{k}={v}" for k, v in by_severity.items() if v)
    )
    lines.append("")
    for i in sorted(issues, key=lambda x: (x.severity, x.category, x.file, x.line)):
        loc = f"{i.file}:{i.line}" if i.line else i.file
        lines.append(f"[{i.severity}] {i.category} @ {loc}: {i.message}")
    return "\n".join(lines)


def run_checks(ws: WikiWorkspace) -> list[LintIssue]:
    out: list[LintIssue] = []
    for check in CHECKS:
        out.extend(check(ws))
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Mechanical LLM-Wiki linter")
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path.cwd(),
        help="Project root (default: current directory)",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix deterministic issues (links, index)",
    )
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args(argv)

    ws = WikiWorkspace(args.workspace)
    issues = run_checks(ws)
    fix_actions: list[str] = []
    if args.fix:
        fix_actions = apply_fixes(ws, issues)
        issues = run_checks(ws)

    if args.json:
        payload = {
            "issues": [i.to_dict() for i in issues],
            "fixes": fix_actions,
            "summary": {"total": len(issues)},
        }
        print(json.dumps(payload, indent=2))
    else:
        print(format_human(issues, fix_actions))

    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
