# Aider Polyglot: checkpoint + shell-session + turn-cap (+ llama-cpp-provider)

## Setup

Extension setting: checkpoint, shell-session, turn-cap, and llama-cpp-provider.

Model:
* `umich/qwen/qwen3.6-35b-a3b`

Dataset:
* Exercism Python (140 exercises)

## Results

- Total: 140
- Pass: 133 (95.0%)
- Fail: 7 (5.7%)

## Failed Exercises

- camicia, connect, pov, relative-distance, scale-generator, sgf-parsing, two-bucket

## Analysis

turn-cap partially suppressed long-runtime behavior:
- `bowling`: 62.3s (vs 100-116s without turn-cap, vs 52s in checkpoint+shell alone)
- `ledger`: 73.5s, `paasio`: 68.3s, `scrabble-score`: 68.3s — still elevated

Interestingly, checkpoint + shell-session **without** turn-cap showed shorter bowling runtime (52s) than with turn-cap (62s), suggesting turn-cap is not the primary suppressor of long-runtime behavior in all-off. The search for what causes all-off to show no long runtimes continues.

No crashes occurred in this run.

## Raw Result

```text
benchmarks/results_full_polyglot_checkpoint_shell_turncap.json
```
