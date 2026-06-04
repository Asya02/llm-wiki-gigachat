"""Verify wiki bootstrap structure was created correctly."""

from __future__ import annotations

from pathlib import Path

from bench.verify._shared import VerifyResult
from bench.verify.verify_raw_immutability import verify as verify_raw


def verify(workspace_path: Path) -> VerifyResult:
    root = workspace_path.resolve()
    issues: list[str] = []

    index_path = root / "wiki" / "index.md"
    log_path = root / "wiki" / "log.md"

    if not index_path.is_file():
        issues.append("wiki/index.md missing")
    else:
        first = index_path.read_text(encoding="utf-8").splitlines()[:1]
        if not first or first[0] != "# Knowledge Base Index":
            issues.append("wiki/index.md must start with '# Knowledge Base Index'")

    if not log_path.is_file():
        issues.append("wiki/log.md missing")
    else:
        first = log_path.read_text(encoding="utf-8").splitlines()[:1]
        if not first or first[0] != "# Wiki Log":
            issues.append("wiki/log.md must start with '# Wiki Log'")

    raw_result = verify_raw(root)
    issues.extend(raw_result.issues)

    passed = len(issues) == 0
    score = 1.0 if passed else max(0.0, 1.0 - 0.2 * len(issues))
    return VerifyResult(passed, issues, score)
