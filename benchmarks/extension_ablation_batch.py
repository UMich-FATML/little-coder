#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from extension_ablation_worktrees import VariantSpec, load_manifest


def variant_output_paths(results_root: Path, variant: VariantSpec) -> dict[str, Path]:
    base = results_root / variant.bit_pattern
    return {
        "base_dir": base,
        "jobs_dir": base / "jobs",
        "log_path": base / "run.log",
    }


def build_harbor_command(model: str, jobs_dir: Path, tasks: list[str] | None = None) -> list[str]:
    cmd = [
        "harbor",
        "run",
        "--dataset",
        "terminal-bench@2.0",
    ]
    for task in tasks or []:
        cmd.extend(["--include-task-name", task])
    cmd.extend(
        [
            "--agent-import-path",
            "benchmarks.harbor_adapter.little_coder_agent:LittleCoderAgent",
            "--model",
            model,
            "--jobs-dir",
            str(jobs_dir),
            "--n-concurrent",
            "1",
        ]
    )
    return cmd


def summarize_harbor_run(run_dir: Path) -> dict[str, int | float | None]:
    if not run_dir.exists():
        return {
            "completed_trials": 0,
            "passed_trials": 0,
            "score_sum": 0.0,
        }

    completed = 0
    passed = 0
    score_sum = 0.0
    for result_path in sorted(run_dir.glob("*/result.json")):
        completed += 1
        data = json.loads(result_path.read_text(encoding="utf-8"))
        rewards = ((data.get("verifier_result") or {}).get("rewards") or {})
        score = rewards.get("reward")
        if score is None:
            for value in rewards.values():
                if isinstance(value, (int, float)):
                    score = float(value)
                    break
        if isinstance(score, (int, float)):
            score_sum += float(score)
            if float(score) >= 1.0:
                passed += 1
    return {
        "completed_trials": completed,
        "passed_trials": passed,
        "score_sum": score_sum,
    }


def newest_run_dir(jobs_dir: Path, before: set[Path]) -> Path | None:
    after = {path for path in jobs_dir.iterdir() if path.is_dir()} if jobs_dir.exists() else set()
    created = sorted(after - before, key=lambda path: path.name)
    if created:
        return created[-1]
    existing = sorted(after, key=lambda path: path.name)
    return existing[-1] if existing else None


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=True) + "\n")


def run_variant(
    *,
    variant: VariantSpec,
    worktree_root: Path,
    results_root: Path,
    model: str,
    tasks: list[str] | None,
    dry_run: bool,
) -> dict:
    worktree_path = worktree_root / variant.worktree_name
    output_paths = variant_output_paths(results_root, variant)
    output_paths["jobs_dir"].mkdir(parents=True, exist_ok=True)
    cmd = build_harbor_command(model=model, jobs_dir=output_paths["jobs_dir"], tasks=tasks)

    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "subset_id": variant.subset_id,
        "bit_pattern": variant.bit_pattern,
        "branch": variant.branch,
        "worktree_name": variant.worktree_name,
        "worktree_path": str(worktree_path),
        "enabled_extensions": variant.enabled_extensions,
        "disabled_extensions": variant.disabled_extensions,
        "model": model,
        "command": cmd,
        "jobs_dir": str(output_paths["jobs_dir"]),
        "log_path": str(output_paths["log_path"]),
        "dry_run": dry_run,
    }
    if dry_run:
        row["returncode"] = None
        row["run_dir"] = None
        row.update(summarize_harbor_run(Path("/nonexistent")))
        return row

    before = {path for path in output_paths["jobs_dir"].iterdir() if path.is_dir()} if output_paths["jobs_dir"].exists() else set()
    env = dict(os.environ)
    env.setdefault("TB_LITTLE_CODER_MODEL", model)
    env.setdefault("LLAMACPP_API_KEY", "noop")
    env.setdefault("OLLAMA_API_KEY", "noop")
    with output_paths["log_path"].open("w", encoding="utf-8") as log_fh:
        proc = subprocess.run(
            cmd,
            cwd=str(worktree_path),
            env=env,
            stdout=log_fh,
            stderr=subprocess.STDOUT,
        )
    run_dir = newest_run_dir(output_paths["jobs_dir"], before)
    row["returncode"] = proc.returncode
    row["run_dir"] = str(run_dir) if run_dir else None
    row.update(summarize_harbor_run(run_dir) if run_dir else summarize_harbor_run(Path("/nonexistent")))
    return row


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Run harbor benchmarks across extension-ablation worktrees.")
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--worktree-root", required=True)
    ap.add_argument("--results-root", required=True)
    ap.add_argument("--model", default="llamacpp/qwen3.6-35b-a3b")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--include-task-name", action="append", default=[])
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    variants = load_manifest(Path(args.manifest).resolve())
    if args.limit > 0:
        variants = variants[: args.limit]

    results_root = Path(args.results_root).resolve()
    worktree_root = Path(args.worktree_root).resolve()
    summary_path = results_root / "summary.jsonl"

    for variant in variants:
        row = run_variant(
            variant=variant,
            worktree_root=worktree_root,
            results_root=results_root,
            model=args.model,
            tasks=args.include_task_name or None,
            dry_run=args.dry_run,
        )
        append_jsonl(summary_path, row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
