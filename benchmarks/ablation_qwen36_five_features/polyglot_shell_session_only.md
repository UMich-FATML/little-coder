# Aider Polyglot: shell-session only (+ llama-cpp-provider)

## Setup

Extension setting: only shell-session and llama-cpp-provider enabled.

Model:
* `umich/qwen/qwen3.6-35b-a3b`

Dataset:
* Exercism Python (140 exercises)

## Results

- Total: 140
- Pass: 129 (92.1%)
- Fail: 11 (6.4%)

## Failed Exercises

- book-store, bowling, camicia, connect, forth, paasio, pov, react, rest-api, scale-generator, sgf-parsing, two-bucket

## Analysis

`bowling` took 100.8s — confirming that shell-session alone causes long-runtime behavior. This is consistent with shell-session maintaining persistent shell state across turns, allowing the agent to keep retrying rather than stopping early.

Pass rate (92.1%) is slightly higher than all-off (91.4%) but lower than all-on (96.4%).

## Raw Result

```text
benchmarks/results_full_polyglot_shell_session_only.json
```
