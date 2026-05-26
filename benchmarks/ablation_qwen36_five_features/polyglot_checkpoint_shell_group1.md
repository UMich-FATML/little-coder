# Aider Polyglot: checkpoint + shell-session + group1 (benchmark-profiles, browser, browser-extract-retention, evidence)

## Setup

Extension setting: checkpoint, shell-session, llama-cpp-provider, benchmark-profiles, browser, browser-extract-retention, evidence.

Model:
* `umich/qwen/qwen3.6-35b-a3b`

Dataset:
* Exercism Python (140 exercises)

## Results

- Total: 140
- Pass: 131 (93.6%)
- Fail: 9 (5.7%)

## Failed Exercises

- bowling, camicia, connect, ledger, paasio, pov, scale-generator, sgf-parsing, two-bucket

## Analysis

`bowling` took 161.2s — the longest runtime observed in any condition so far. This indicates that benchmark-profiles, browser, browser-extract-retention, and/or evidence **worsen** long-runtime behavior rather than suppressing it.

This narrows the search: the extension(s) responsible for suppressing long runtimes in all-off must be in the other group: evidence-compact, extra-tools, finalize-warn, hello.

## Raw Result

```text
benchmarks/results_full_polyglot_checkpoint_shell_group1.json
```
