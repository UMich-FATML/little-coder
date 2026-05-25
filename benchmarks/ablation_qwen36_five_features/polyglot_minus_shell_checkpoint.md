# Aider Polyglot: All-Off minus {shell-session, checkpoint}

## Setup

Extension setting: all-off (14 extensions) further minus shell-session and checkpoint (12 extensions total).

Model:
* `umich/qwen/qwen3.6-35b-a3b`

Dataset:
* Exercism Python (140 exercises)

## Results

- Total: 140
- Pass: 131 (93.6%)
- Fail: 9 (6.4%)

## Failed Exercises

- bowling
- camicia
- connect
- forth
- ocr-numbers
- pov
- react
- scale-generator
- sgf-parsing

## Analysis

Compared to minus4 (which removed shell-session, checkpoint, tool-gating, permission-gate), the long-runtime anomalies disappeared:
- `ledger`: back to 22.2s (was 148.3s in minus4)
- `sgf-parsing`: back to 40.3s (was 146.1s in minus4)

This confirms that the long-runtime behavior was **probably(up to now)** caused by **shell-session or checkpoint** (not tool-gating or permission-gate **?**). The next step is to isolate which of the two is responsible by removing only shell-session.

## Raw Result

```text
benchmarks/results_full_polyglot_minus_shell_checkpoint.json
```
