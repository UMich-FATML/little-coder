# Aider Polyglot: checkpoint + shell-session + group2b (evidence, evidence-compact, extra-tools, finalize-warn)

## Setup

Extension setting: checkpoint, shell-session, llama-cpp-provider, evidence, evidence-compact, extra-tools, finalize-warn.

Model:
* `umich/qwen/qwen3.6-35b-a3b`

Dataset:
* Exercism Python (140 exercises)

## Results

- Total: 140
- Pass: 132 (94.3%)
- Fail: 8 (5.7%)

## Failed Exercises

- bowling, camicia, connect, forth, paasio, pov, react, rest-api, scale-generator

## Analysis

`bowling` took 135.7s — long-runtime behavior persists even with finalize-warn added. This eliminates finalize-warn as the suppressor. By elimination, `hello` must be the extension responsible for suppressing long-runtime behavior in all-off.

## Raw Result

```text
benchmarks/results_full_polyglot_checkpoint_shell_group2b.json
```
