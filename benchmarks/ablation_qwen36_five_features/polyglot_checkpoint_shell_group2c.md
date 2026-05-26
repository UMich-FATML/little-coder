# Aider Polyglot: checkpoint + shell-session + group2b + hello (evidence, evidence-compact, extra-tools, finalize-warn, hello)

## Setup

Extension setting: checkpoint, shell-session, llama-cpp-provider, evidence, evidence-compact, extra-tools, finalize-warn, hello.

Model:
* `umich/qwen/qwen3.6-35b-a3b`

Dataset:
* Exercism Python (140 exercises)

## Results

- Total: 140
- Pass: 131 (93.6%)
- Fail: 9 (5.7%)

## Failed Exercises

- book-store, bowling, camicia, connect, paasio, pov, react, rest-api, sgf-parsing, two-bucket

## Analysis

`bowling` took 47.7s — long-runtime behavior still present despite adding hello. This means hello alone is also not the suppressor.

Combined with group2a and group2b results, no single extension in group2 is individually responsible for suppressing long runtimes. The suppression appears to require a **combination** of extensions from group2 working together.

## Raw Result

```text
benchmarks/results_full_polyglot_checkpoint_shell_group2c.json
```
