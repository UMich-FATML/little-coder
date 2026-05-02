from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extension_ablation_batch import (  # noqa: E402
    build_harbor_command,
    summarize_harbor_run,
    variant_output_paths,
)
from extension_ablation_worktrees import VariantSpec  # noqa: E402


def test_variant_output_paths_are_named_by_bit_pattern(tmp_path):
    variant = VariantSpec(
        subset_id="001011",
        branch="ablate/001011",
        worktree_name="lc-001011",
        bit_pattern="001011",
        enabled_extensions=["quality-monitor", "skill-inject", "write-guard"],
        disabled_extensions=["knowledge-inject", "output-parser", "thinking-budget"],
    )

    paths = variant_output_paths(tmp_path, variant)
    assert paths["jobs_dir"] == tmp_path / "001011" / "jobs"
    assert paths["log_path"] == tmp_path / "001011" / "run.log"


def test_build_harbor_command_for_full_benchmark():
    cmd = build_harbor_command(
        model="llamacpp/qwen3.6-35b-a3b",
        jobs_dir=Path("/tmp/jobs"),
    )

    assert cmd[:3] == ["harbor", "run", "--dataset"]
    assert "--include-task-name" not in cmd
    assert cmd[-2:] == ["--n-concurrent", "1"]


def test_build_harbor_command_for_selected_tasks():
    cmd = build_harbor_command(
        model="llamacpp/qwen3.6-35b-a3b",
        jobs_dir=Path("/tmp/jobs"),
        tasks=["hello-world", "break-filter-js-from-html"],
    )

    assert cmd.count("--include-task-name") == 2
    assert "hello-world" in cmd
    assert "break-filter-js-from-html" in cmd


def test_summarize_harbor_run_counts_completed_and_passed(tmp_path):
    run_dir = tmp_path / "tb2-2026-05-02__00-00-00"
    task_a = run_dir / "task-a__abc"
    task_b = run_dir / "task-b__def"
    task_a.mkdir(parents=True)
    task_b.mkdir(parents=True)
    (task_a / "result.json").write_text(
        json.dumps({"task_name": "task-a", "verifier_result": {"rewards": {"reward": 1.0}}})
    )
    (task_b / "result.json").write_text(
        json.dumps({"task_name": "task-b", "verifier_result": {"rewards": {"reward": 0.0}}})
    )

    summary = summarize_harbor_run(run_dir)
    assert summary["completed_trials"] == 2
    assert summary["passed_trials"] == 1
    assert summary["score_sum"] == 1.0


def test_summarize_harbor_run_returns_empty_counts_when_missing(tmp_path):
    summary = summarize_harbor_run(tmp_path / "missing-run-dir")
    assert summary["completed_trials"] == 0
    assert summary["passed_trials"] == 0
    assert summary["score_sum"] == 0.0
