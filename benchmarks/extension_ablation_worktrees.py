#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TOGGLE_EXTENSIONS = [
    "knowledge-inject",
    "output-parser",
    "quality-monitor",
    "skill-inject",
    "thinking-budget",
    "write-guard",
]
DEFAULT_SEED = 20260502
DEFAULT_SAMPLE_COUNT = 32


@dataclass(frozen=True)
class VariantSpec:
    subset_id: str
    branch: str
    worktree_name: str
    bit_pattern: str
    enabled_extensions: list[str]
    disabled_extensions: list[str]

    def disabled_extension_paths(self, repo_root: Path) -> list[Path]:
        ext_dir = repo_root / ".pi" / "extensions"
        return [ext_dir / name for name in self.disabled_extensions]


def _all_bit_patterns() -> list[str]:
    width = len(TOGGLE_EXTENSIONS)
    return [format(value, f"0{width}b") for value in range(2**width)]


def _variant_from_pattern(subset_id: str, bit_pattern: str) -> VariantSpec:
    enabled, disabled = [], []
    for bit, name in zip(bit_pattern, TOGGLE_EXTENSIONS, strict=True):
        if bit == "1":
            enabled.append(name)
        else:
            disabled.append(name)
    branch = f"ablate/{subset_id}"
    worktree_name = f"lc-{subset_id}"
    return VariantSpec(
        subset_id=subset_id,
        branch=branch,
        worktree_name=worktree_name,
        bit_pattern=bit_pattern,
        enabled_extensions=enabled,
        disabled_extensions=disabled,
    )


def build_variant_specs(seed: int = DEFAULT_SEED, sample_count: int = DEFAULT_SAMPLE_COUNT) -> list[VariantSpec]:
    if sample_count < 2:
        raise ValueError("sample_count must be >= 2 so all-on and all-off can be included")
    all_patterns = _all_bit_patterns()
    all_on = "1" * len(TOGGLE_EXTENSIONS)
    all_off = "0" * len(TOGGLE_EXTENSIONS)
    remaining = [pattern for pattern in all_patterns if pattern not in {all_on, all_off}]
    if sample_count - 2 > len(remaining):
        raise ValueError("sample_count is too large for the toggle space")

    rng = random.Random(seed)
    sampled = rng.sample(remaining, sample_count - 2)

    variants = [
        _variant_from_pattern(all_on, all_on),
        _variant_from_pattern(all_off, all_off),
    ]
    for pattern in sampled:
        variants.append(_variant_from_pattern(pattern, pattern))
    return variants


def write_manifest(
    path: Path,
    *,
    seed: int,
    sample_count: int,
    repo_root: Path,
    worktree_root: Path,
    variants: list[VariantSpec],
) -> None:
    variant_rows = []
    for variant in variants:
        row = asdict(variant)
        row["worktree_path"] = str(worktree_root / variant.worktree_name)
        variant_rows.append(row)
    payload = {
        "seed": seed,
        "sample_count": sample_count,
        "repo_root": str(repo_root),
        "worktree_root": str(worktree_root),
        "toggle_extensions": TOGGLE_EXTENSIONS,
        "variants": variant_rows,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def load_manifest(path: Path) -> list[VariantSpec]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    variants = []
    for entry in payload["variants"]:
        filtered = {key: entry[key] for key in VariantSpec.__dataclass_fields__ if key in entry}
        variants.append(VariantSpec(**filtered))
    return variants


def _git(args: list[str], cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=str(cwd), check=True)


def _remove_disabled_extensions(worktree_path: Path, variant: VariantSpec) -> None:
    for ext_path in variant.disabled_extension_paths(worktree_path):
        if ext_path.exists():
            shutil.rmtree(ext_path)


def setup_worktrees(
    *,
    repo_root: Path,
    worktree_root: Path,
    variants: list[VariantSpec],
    force: bool = False,
) -> None:
    worktree_root.mkdir(parents=True, exist_ok=True)
    for variant in variants:
        worktree_path = worktree_root / variant.worktree_name
        if worktree_path.exists():
            if not force:
                raise FileExistsError(f"Worktree already exists: {worktree_path}")
            _git(["worktree", "remove", "--force", str(worktree_path)], cwd=repo_root)

        _git(["branch", "-f", variant.branch, "main"], cwd=repo_root)
        _git(["worktree", "add", "--force", str(worktree_path), variant.branch], cwd=repo_root)
        _remove_disabled_extensions(worktree_path, variant)


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Create and materialize branch/worktree extension ablation variants.")
    sub = ap.add_subparsers(dest="command", required=True)

    manifest_cmd = sub.add_parser("manifest", help="Generate a fixed manifest of extension subsets.")
    manifest_cmd.add_argument("--seed", type=int, default=DEFAULT_SEED)
    manifest_cmd.add_argument("--sample-count", type=int, default=DEFAULT_SAMPLE_COUNT)
    manifest_cmd.add_argument("--repo-root", default=str(REPO_ROOT))
    manifest_cmd.add_argument("--worktree-root", required=True)
    manifest_cmd.add_argument("--out", required=True)

    setup_cmd = sub.add_parser("setup", help="Create branches/worktrees from a manifest.")
    setup_cmd.add_argument("--repo-root", default=str(REPO_ROOT))
    setup_cmd.add_argument("--manifest", required=True)
    setup_cmd.add_argument("--worktree-root", required=True)
    setup_cmd.add_argument("--force", action="store_true")
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "manifest":
        repo_root = Path(args.repo_root).resolve()
        worktree_root = Path(args.worktree_root).resolve()
        variants = build_variant_specs(seed=args.seed, sample_count=args.sample_count)
        write_manifest(
            Path(args.out).resolve(),
            seed=args.seed,
            sample_count=args.sample_count,
            repo_root=repo_root,
            worktree_root=worktree_root,
            variants=variants,
        )
        return 0

    if args.command == "setup":
        repo_root = Path(args.repo_root).resolve()
        worktree_root = Path(args.worktree_root).resolve()
        variants = load_manifest(Path(args.manifest).resolve())
        setup_worktrees(
            repo_root=repo_root,
            worktree_root=worktree_root,
            variants=variants,
            force=args.force,
        )
        return 0

    raise AssertionError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
