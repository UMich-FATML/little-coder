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

Both crashes are recoverable via `--resume`. The root cause appears to be checkpoint's retry mechanism sending a second prompt before pi has finished the first, which is more likely to happen when shell-session is also present (adding more state/latency). This instability does not appear when checkpoint or shell-session are used in all-off (with 12 other extensions), suggesting some of those extensions help serialize or guard the retry flow.

## Prediction vs Actual

Predicted: ~94-95%. Actual: 95.7% — consistent with prediction.

## Raw Result

```text
benchmarks/results_full_polyglot_checkpoint_shell.json
```
