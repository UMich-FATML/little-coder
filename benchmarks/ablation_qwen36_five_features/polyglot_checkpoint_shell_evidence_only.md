# Aider Polyglot: checkpoint + shell-session + evidence only (+ llama-cpp-provider)

## Setup

Extension setting: checkpoint, shell-session, llama-cpp-provider, evidence.

Model:
* `umich/qwen/qwen3.6-35b-a3b`

Dataset:
* Exercism Python (140 exercises)

## Results

- Total: 140
- Pass: 133 (95.0%)
- Fail: 7 (5.7%)

## Failed Exercises

- bowling, camicia, connect, forth, pov, react, sgf-parsing

## Analysis

`bowling` took 125.6s, `ledger` 56.6s, `zipper` 93.2s — long-runtime behavior persists. Evidence alone is not sufficient to suppress long runtimes. The suppression requires a combination of extensions from group2.

## Raw Result

```text
benchmarks/results_full_polyglot_checkpoint_shell_evidence_only.json
```
