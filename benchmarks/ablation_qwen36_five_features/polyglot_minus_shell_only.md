# Aider Polyglot: All-Off minus {shell-session}

## Setup

Extension setting: all-off (14 extensions) further minus shell-session (13 extensions total).

Model:
* `umich/qwen/qwen3.6-35b-a3b`

Dataset:
* Exercism Python (140 exercises)

## Results

- Total: 140
- Pass: 131 (93.6%)
- Fail: 9 (6.4%)

## Failed Exercises

- book-store
- bowling
- camicia
- dominoes
- forth
- paasio
- pov
- scale-generator
- sgf-parsing

## Analysis

Compared to minus4 (shell-session + checkpoint + tool-gating + permission-gate removed):
- `ledger` and `sgf-parsing` returned to normal runtimes (~22s and ~40s) — confirming shell-session was responsible for their long runtimes in minus4.
- However, new long runtimes appeared: `bowling` (113.7s), `alphametics` (75.0s) — indicating checkpoint also contributes to runaway behavior.

*Conclusion: both shell-session and checkpoint cause long-running/timeout behavior. Removing either one alone may be insufficient, which suggests that both should be removed to fully resolve the issue.*

## Raw Result

```text
benchmarks/results_full_polyglot_minus_shell_only.json
```
