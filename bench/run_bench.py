#!/usr/bin/env python3
"""Orchestrate LLM-Wiki benchmark runs (agent invocation stubbed until deepagents is wired)."""

from __future__ import annotations

import argparse
import importlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    print("PyYAML required: pip install pyyaml", file=sys.stderr)
    raise SystemExit(1)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VERIFIERS = {
    "verify_bootstrap": "bench.verify.verify_bootstrap",
    "verify_ingest": "bench.verify.verify_ingest",
    "verify_links": "bench.verify.verify_links",
    "verify_provenance": "bench.verify.verify_provenance",
    "verify_contradictions": "bench.verify.verify_contradictions",
    "verify_query": "bench.verify.verify_query",
    "verify_exports": "bench.verify.verify_exports",
    "verify_raw_immutability": "bench.verify.verify_raw_immutability",
}
CRITICAL_MAP = {
    "raw_modified": "verify_raw_immutability",
    "missing_index": "verify_ingest",
    "missing_index_update": "verify_ingest",
    "missing_log": "verify_ingest",
    "missing_log_update": "verify_ingest",
    "stale_claim_active": "verify_contradictions",
    "answer_not_in_wiki": "verify_query",
    "broken_wikilinks_remaining": "verify_links",
}


def load_tasks(path: Path) -> list[dict[str, Any]]:
    return list(yaml.safe_load(path.read_text(encoding="utf-8")).get("tasks") or [])


def reset_workspace(project_root: Path, fixture_rel: str, workspace: Path) -> None:
    fixture = project_root / fixture_rel
    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.mkdir(parents=True)
    if fixture.is_dir():
        shutil.copytree(fixture, workspace, dirs_exist_ok=True)
    for name in ("raw", "tools"):
        if not (workspace / name).is_dir() and (project_root / name).is_dir():
            shutil.copytree(project_root / name, workspace / name)
    if not (workspace / "AGENTS.md").is_file() and (project_root / "AGENTS.md").is_file():
        shutil.copy2(project_root / "AGENTS.md", workspace / "AGENTS.md")


def apply_config(workspace: Path, config_dir: Path) -> None:
    if (config_dir / "AGENTS.md").is_file():
        shutil.copy2(config_dir / "AGENTS.md", workspace / "AGENTS.md")
    for sub in ("skills", "tools"):
        src = config_dir / sub
        if src.is_dir():
            dst = workspace / sub
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)


def save_raw_baseline(workspace: Path, run_dir: Path) -> None:
    from bench.verify._shared import raw_file_snapshot

    (run_dir / "raw_baseline.json").write_text(
        json.dumps(raw_file_snapshot(workspace / "raw"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def invoke_agent(model: str, prompt: str, workspace: Path) -> list[dict[str, Any]]:
    ts = datetime.now(timezone.utc).isoformat()
    try:
        import deepagents  # noqa: F401
    except ImportError:
        return [{
            "type": "stub", "timestamp": ts, "model": model,
            "message": "deepagents not installed; agent.invoke() skipped",
            "prompt_preview": prompt[:500],
        }]
    # agent = create_agent(model=model, workspace=workspace)
    # result = agent.invoke({"messages": [{"role": "user", "content": prompt}]})
    return [{
        "type": "stub", "timestamp": ts, "model": model,
        "message": "deepagents import OK but invoke not implemented yet",
        "prompt_preview": prompt[:500],
    }]


def run_verifiers(workspace: Path, names: list[str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for name in names:
        mod = importlib.import_module(VERIFIERS[name])
        r = mod.verify(workspace)
        out[name] = {"passed": r.passed, "score": r.score, "issues": r.issues}
    return out


def critical_hits(task: dict[str, Any], results: dict[str, Any]) -> list[str]:
    hits = []
    for tag in task.get("critical") or []:
        v = CRITICAL_MAP.get(tag)
        if v and not results.get(v, {}).get("passed", True):
            hits.append(tag)
    return hits


def lint_counts(workspace: Path) -> dict[str, int]:
    keys = ("broken_wikilinks", "orphan_pages", "missing_index_entries",
            "missing_log_entries", "claims_without_source_id")
    base = dict.fromkeys(keys, 0)
    script = workspace / "tools" / "wiki_lint.py"
    if not script.is_file():
        script = PROJECT_ROOT / "tools" / "wiki_lint.py"
    if not script.is_file():
        return base
    proc = subprocess.run(
        [sys.executable, str(script), "--root", str(workspace), "--json"],
        capture_output=True, text=True, cwd=str(workspace),
    )
    try:
        report = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return base
    for item in report.get("issues") or []:
        if (item.get("severity") or "").lower() != "error":
            continue
        msg = (item.get("message") or "").lower()
        cat = (item.get("category") or "").lower()
        if "wikilink" in cat or "broken link" in msg:
            base["broken_wikilinks"] += 1
        if "index" in cat:
            base["missing_index_entries"] += 1
        if "orphan" in msg:
            base["orphan_pages"] += 1
        if "log" in cat:
            base["missing_log_entries"] += 1
        if "source_id" in msg:
            base["claims_without_source_id"] += 1
    return base


def git_diff_patch(workspace: Path) -> str:
    if not (workspace / ".git").exists():
        subprocess.run(["git", "init"], cwd=workspace, capture_output=True)
        subprocess.run(["git", "add", "-A"], cwd=workspace, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "bench baseline", "--allow-empty"],
            cwd=workspace, capture_output=True,
        )
    proc = subprocess.run(
        ["git", "diff", "HEAD"], cwd=workspace, capture_output=True, text=True,
    )
    return proc.stdout or ""


def write_result_md(run_dir: Path, config: str, model: str, tasks: list[dict]) -> None:
    lines = [f"# Benchmark run: {config}", "", f"- **Model:** {model}", ""]
    for t in tasks:
        mark = "PASS" if t["passed"] else "FAIL"
        lines.append(f"### {t['id']} {t['name']} — {mark} ({t['score']}/{t['max_score']})")
        if t["critical_hits"]:
            lines.append(f"- Critical: {', '.join(t['critical_hits'])}")
        for v, r in t["verifiers"].items():
            if not r["passed"]:
                lines.append(f"- {v}: {len(r['issues'])} issue(s)")
                lines.extend(f"  - {i}" for i in r["issues"][:3])
        lines.append("")
    (run_dir / "result.md").write_text("\n".join(lines), encoding="utf-8")


def run_benchmark(config_dir: Path, model: str, tasks_path: Path, run_dir: Path) -> int:
    tasks = load_tasks(tasks_path)
    run_dir.mkdir(parents=True, exist_ok=True)
    workspace, trace_path = run_dir / "workspace", run_dir / "trace.jsonl"
    if trace_path.exists():
        trace_path.unlink()

    task_rows: list[dict] = []
    score, critical, tool_errors = 0.0, [], 0

    for task in tasks:
        tid = task.get("id", "?")
        if task.get("fixture") != "from_previous":
            reset_workspace(PROJECT_ROOT, task.get("fixture", "fixtures/empty_vault"), workspace)
            save_raw_baseline(workspace, run_dir)
        elif not workspace.exists():
            reset_workspace(PROJECT_ROOT, "fixtures/empty_vault", workspace)
            save_raw_baseline(workspace, run_dir)

        apply_config(workspace, config_dir)
        events = invoke_agent(model, (task.get("prompt") or "").strip(), workspace)
        for ev in events:
            ev["task_id"] = tid
            if ev.get("type") == "error":
                tool_errors += 1
        with trace_path.open("a", encoding="utf-8") as f:
            for ev in events:
                f.write(json.dumps(ev, ensure_ascii=False) + "\n")

        vresults = run_verifiers(workspace, list(task.get("verifiers") or []))
        chits = critical_hits(task, vresults)
        critical.extend(chits)
        max_s = float(task.get("score", 0))
        passed = all(r["passed"] for r in vresults.values()) and not chits
        if passed:
            score += max_s
        task_rows.append({
            "id": tid, "name": task.get("name", ""), "passed": passed,
            "score": max_s if passed else 0, "max_score": max_s,
            "critical_hits": chits, "verifiers": vresults,
        })

    lint = lint_counts(workspace)
    metrics = {
        "config": config_dir.name, "model": model,
        "tasks_total": len(tasks), "tasks_passed": sum(1 for t in task_rows if t["passed"]),
        "score": round(score, 2), "critical_failures": sorted(set(critical)),
        "tool_call_errors": tool_errors, "run_finished": True, **lint,
    }
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    (run_dir / "tasks.json").write_text(json.dumps(task_rows, indent=2) + "\n", encoding="utf-8")
    (run_dir / "diff.patch").write_text(git_diff_patch(workspace), encoding="utf-8")
    write_result_md(run_dir, config_dir.name, model, task_rows)
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Run LLM-Wiki benchmark tasks")
    p.add_argument("--config", required=True, type=Path)
    p.add_argument("--model", default="gigachat:GigaChat-3-Ultra")
    p.add_argument("--tasks", type=Path, default=PROJECT_ROOT / "bench" / "tasks.yaml")
    p.add_argument("--out", type=Path, default=None)
    args = p.parse_args(argv)

    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    config = args.config if args.config.is_absolute() else PROJECT_ROOT / args.config
    if not config.is_dir():
        print(f"Config not found: {config}", file=sys.stderr)
        return 1
    tasks = args.tasks if args.tasks.is_absolute() else PROJECT_ROOT / args.tasks
    if not tasks.is_file():
        print(f"Tasks not found: {tasks}", file=sys.stderr)
        return 1
    out = args.out or (PROJECT_ROOT / "outputs" / "runs" / (
        f"{config.name}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    ))
    if not out.is_absolute():
        out = PROJECT_ROOT / out
    return run_benchmark(config, args.model, tasks, out)


if __name__ == "__main__":
    raise SystemExit(main())
