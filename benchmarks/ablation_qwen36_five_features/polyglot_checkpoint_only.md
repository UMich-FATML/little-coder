# Aider Polyglot: checkpoint only (+ llama-cpp-provider)

## Setup

Extension setting: only checkpoint and llama-cpp-provider enabled.

Model:
* `umich/qwen/qwen3.6-35b-a3b`

Dataset:
* Exercism Python (140 exercises)

## Results

- Total: 140
- Pass: 133 (95.0%)
- Fail: 7 (6.4%)

## Failed Exercises

- bowling, camicia, paasio, pov, rest-api, scale-generator, sgf-parsing

## Analysis

- `bowling`: 116.6s, `sgf-parsing`: 104.7s — confirms checkpoint alone causes long-runtime behavior, consistent with its file-snapshot mechanism enabling safe retries.
- `forth` crashed mid-run with "Agent is already processing" error, suggesting checkpoint's retry mechanism can trigger a concurrency conflict in pi. After resume it passed — indicating the crash is recoverable but represents an instability when checkpoint is used in isolation.
- Pass rate (95.0%) is the highest of any single-extension condition, and close to all-on (96.4%), suggesting checkpoint is the most impactful individual extension for performance.

## Raw Result

```text
benchmarks/results_full_polyglot_checkpoint_only.json
```
