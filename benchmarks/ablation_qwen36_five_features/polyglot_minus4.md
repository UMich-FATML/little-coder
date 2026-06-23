# Aider Polyglot: All-Off minus {shell-session, checkpoint, tool-gating, permission-gate}

## Setup

Extension setting: all-off (14 extensions) further minus shell-session, checkpoint, tool-gating, and permission-gate (10 extensions total).

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
- paasio
- pov
- react
- rest-api
- sgf-parsing

## Analysis

Two exercises showed abnormally long runtimes despite passing:
- `ledger`: 148.3s (well above the typical 5-30s range)
- `sgf-parsing`: 146.1s (fail, but took far longer than the 40s timeout seen in all-off)

This suggests that removing these 4 extensions causes the agent to run significantly longer before completing or timing out, which is consistent with one or more of these extensions playing a role in preventing timeout/runaway behavior in Terminal-Bench. The effect is visible even in aider polyglot as unusually long runtimes.

Pass rate (93.6%) is slightly higher than all-off (91.4%), suggesting these 4 extensions do not contribute positively to performance and may even slightly hurt it.


## Raw Result

```text
benchmarks/results_full_polyglot_minus4.json
```
