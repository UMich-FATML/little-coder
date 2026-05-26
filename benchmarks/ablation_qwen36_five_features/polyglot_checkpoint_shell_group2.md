# Aider Polyglot: checkpoint + shell-session + group2 (evidence-compact, extra-tools, finalize-warn, hello) + evidence

## Setup

Extension setting: checkpoint, shell-session, llama-cpp-provider, evidence, evidence-compact, extra-tools, finalize-warn, hello.

Model:
* `umich/qwen/qwen3.6-35b-a3b`

Dataset:
* Exercism Python (140 exercises)

## Results

- Total: 140
- Pass: 135 (96.4%)
- Fail: 5 (3.6%)

## Failed Exercises

- bowling, camicia, paasio, pov, sgf-parsing

## Analysis

Pass rate matches all-on (96.4%) exactly. `bowling` returned to normal runtime (42.9s), confirming that group2 contains the extension(s) responsible for suppressing long-runtime behavior.

Note: `dot-dsl` took 418.6s — an extreme outlier — but still passed. This may be a one-off anomaly or indicate some instability in this configuration.

Next step: binary search within group2 (evidence-compact, extra-tools, finalize-warn, hello) to isolate which extension is responsible.

## Raw Result

```text
benchmarks/results_full_polyglot_checkpoint_shell_group2.json
```
