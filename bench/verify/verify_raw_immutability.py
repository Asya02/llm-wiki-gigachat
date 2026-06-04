"""Verify raw/ was not modified during agent runs."""

from __future__ import annotations

from pathlib import Path

from bench.verify._shared import (
    VerifyResult,
    load_baseline,
    parse_manifest_paths,
    raw_file_snapshot,
)


def verify(workspace_path: Path) -> VerifyResult:
    root = workspace_path.resolve()
    raw_dir = root / "raw"
    issues: list[str] = []

    if not raw_dir.is_dir():
        return VerifyResult(False, ["raw/ directory missing"], 0.0)

    baseline = load_baseline(root)
    current = raw_file_snapshot(raw_dir)

    if baseline is not None:
        for path, old_hash in baseline.items():
            if path not in current:
                issues.append(f"raw file removed: {path}")
            elif current[path] != old_hash:
                issues.append(f"raw file modified: {path}")
        for path in sorted(set(current) - set(baseline)):
            issues.append(f"new file added to raw/: {path}")
    else:
        issues.append("raw baseline snapshot missing (run_bench should create raw_baseline.json)")

    for candidate in (raw_dir / "raw_manifest.yaml", root / "raw_manifest.yaml"):
        if not candidate.is_file():
            continue
        manifest_paths = parse_manifest_paths(candidate)
        actual = {p for p in current if not p.endswith("raw_manifest.yaml")}
        expected = set(manifest_paths.keys())
        for missing in sorted(expected - actual):
            issues.append(f"manifest lists missing file: {missing}")
        for extra in sorted(actual - expected):
            if extra.startswith("raw/"):
                issues.append(f"file not in manifest (raw/ changed): {extra}")
        break

    passed = len(issues) == 0
    return VerifyResult(passed, issues, 1.0 if passed else 0.0)
