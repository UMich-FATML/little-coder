# Aider Polyglot: checkpoint + shell-session (+ llama-cpp-provider)

## Setup

Extension setting: only checkpoint, shell-session, and llama-cpp-provider enabled.

Model:
* `umich/qwen/qwen3.6-35b-a3b`

Dataset:
* Exercism Python (140 exercises)

## Results

- Total: 140
- Pass: 134 (95.7%)
- Fail: 6 (6.4%)

## Failed Exercises

- camicia, connect, paasio, pov, react, scale-generator, sgf-parsing

## Crash Analysis

The run crashed twice mid-execution with two distinct errors:
1. `TimeoutError: pi did not respond to request within 30s` — pi subprocess became unresponsive during retry
2. `RuntimeError: Agent is already processing. Specify streamingBehavior ('steer' or 'followUp') to queue the message` — checkpoint triggered a retry while pi was still processing, causing a concurrency conflict

**Root cause: checkpoint's retry mechanism conflicts with pi's single-threaded processing.**

When the agent fails on the first attempt, checkpoint triggers a retry by sending a second prompt to pi. However, pi may not have fully finished processing the first request (e.g., still writing checkpoint files or cleaning up state). When pi receives the second prompt in this half-finished state, it either becomes unresponsive or explicitly rejects it.

**Why doesn't this happen in all-off (which also includes checkpoint)?**

all-off includes `permission-gate` and `tool-gating`, which add wait/confirmation steps between tool calls. This inadvertently gives pi enough time to fully finish the previous request before receiving the retry prompt, preventing the race condition.

**Why does checkpoint + shell-session crash more often than checkpoint alone?**

shell-session increases per-tool-call latency (managing tmux/subprocess state), making it more likely that pi is still in a half-finished state when checkpoint sends the retry prompt.

**In short**: checkpoint's retry timing does not account for pi's processing state — this is a race condition that only manifests when the guarding extensions (permission-gate, tool-gating) are absent.

## Raw Result

```text
benchmarks/results_full_polyglot_checkpoint_shell.json
```
