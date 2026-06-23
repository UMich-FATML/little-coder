# Aider Polyglot: checkpoint + shell-session + tool-gating + permission-gate (+ llama-cpp-provider)

## Setup

Extension setting: checkpoint, shell-session, tool-gating, permission-gate, and llama-cpp-provider enabled.

Model:
* `umich/qwen/qwen3.6-35b-a3b`

Dataset:
* Exercism Python (140 exercises)

## Results

- Total: 140
- Pass: 133 (95.0%)
- Fail: 7 (6.4%)

## Failed Exercises

- bowling, camicia, connect, pov, sgf-parsing, transpose (+ 1 crash mid-run)

## Analysis

Adding tool-gating and permission-gate to the checkpoint + shell-session baseline caused pass rate to drop from 95.7% to 95.0%, and the run still crashed once with the same "Agent is already processing" race condition error. Also, `forth` took 133.4s — a long-runtime anomaly.

**Two key findings:**

1. **tool-gating and permission-gate do not prevent the race condition.** The earlier hypothesis that these extensions serialize tool calls and guard checkpoint's retry timing was wrong. The crash persists regardless of their presence.

2. **tool-gating and permission-gate slightly hurt performance.** By restricting which tools the agent can call, they reduce the agent's ability to explore solutions, leading to a marginally lower pass rate. This is consistent with all-off (which includes these two) being lower than checkpoint + shell-session alone.

**Updated understanding of race condition:** The crash is intrinsic to checkpoint's retry mechanism and is not guarded by any of the extensions tested so far. The root cause remains checkpoint sending a retry prompt before pi has finished processing, but the fix must come from within checkpoint itself or the pi RPC layer, not from other extensions.

## Raw Result

```text
benchmarks/results_full_polyglot_checkpoint_shell_toolgate_permgate.json
```
