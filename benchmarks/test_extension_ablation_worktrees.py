from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extension_ablation_worktrees import (  # noqa: E402
    TOGGLE_EXTENSIONS,
    VariantSpec,
    build_variant_specs,
    load_manifest,
    write_manifest,
)


def test_build_variant_specs_includes_required_baselines():
    variants = build_variant_specs(seed=7, sample_count=32)

    assert len(variants) == 32
    assert len({variant.bit_pattern for variant in variants}) == 32
    assert variants[0].subset_id == "111111"
    assert variants[0].enabled_extensions == TOGGLE_EXTENSIONS
    assert variants[1].subset_id == "000000"
    assert variants[1].disabled_extensions == TOGGLE_EXTENSIONS


def test_build_variant_specs_uses_stable_names_and_paths():
    variants = build_variant_specs(seed=11, sample_count=32)

    assert variants[0].branch == "ablate/111111"
    assert variants[0].worktree_name == "lc-111111"
    assert variants[1].branch == "ablate/000000"
    assert variants[1].worktree_name == "lc-000000"
    assert variants[2].subset_id == variants[2].bit_pattern
    assert variants[2].branch == f"ablate/{variants[2].bit_pattern}"
    assert variants[2].worktree_name == f"lc-{variants[2].bit_pattern}"
    assert len(variants[2].bit_pattern) == len(TOGGLE_EXTENSIONS)


def test_build_variant_specs_assigns_enabled_and_disabled_extensions():
    variants = build_variant_specs(seed=3, sample_count=8)

    for variant in variants:
        assert sorted(variant.enabled_extensions + variant.disabled_extensions) == TOGGLE_EXTENSIONS
        assert set(variant.enabled_extensions).isdisjoint(variant.disabled_extensions)


def test_write_and_load_manifest_round_trip(tmp_path):
    manifest_path = tmp_path / "subsets.json"
    variants = build_variant_specs(seed=19, sample_count=6)

    write_manifest(
        manifest_path,
        seed=19,
        sample_count=6,
        repo_root=Path("/tmp/repo"),
        worktree_root=Path("/tmp/worktrees"),
        variants=variants,
    )

    payload = json.loads(manifest_path.read_text())
    assert payload["seed"] == 19
    assert payload["sample_count"] == 6
    assert payload["toggle_extensions"] == TOGGLE_EXTENSIONS
    assert payload["variants"][0]["worktree_path"] == "/tmp/worktrees/lc-111111"

    loaded = load_manifest(manifest_path)
    assert loaded == variants


def test_variant_spec_resolves_extension_paths(tmp_path):
    variant = VariantSpec(
        subset_id="101010",
        branch="ablate/101010",
        worktree_name="lc-101010",
        bit_pattern="101010",
        enabled_extensions=[
            "write-guard",
            "knowledge-inject",
            "output-parser",
        ],
        disabled_extensions=[
            "skill-inject",
            "thinking-budget",
            "quality-monitor",
        ],
    )

    paths = variant.disabled_extension_paths(tmp_path / "repo")
    assert paths == [
        tmp_path / "repo" / ".pi" / "extensions" / "skill-inject",
        tmp_path / "repo" / ".pi" / "extensions" / "thinking-budget",
        tmp_path / "repo" / ".pi" / "extensions" / "quality-monitor",
    ]
