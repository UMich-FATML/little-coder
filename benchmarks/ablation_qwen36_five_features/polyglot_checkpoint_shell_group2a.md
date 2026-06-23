# Aider Polyglot: checkpoint + shell-session + group2a (evidence, evidence-compact, extra-tools)

## Setup

Extension setting: checkpoint, shell-session, llama-cpp-provider, evidence, evidence-compact, extra-tools.

Model:
* `umich/qwen/qwen3.6-35b-a3b`

Dataset:
* Exercism Python (140 exercises)

## Results

- Total: 140
- Pass: 130 (92.9%)
- Fail: 10 (5.7%)

## Failed Exercises

- book-store, bowling, camicia, connect, paasio, pov, react, rest-api, scale-generator, sgf-parsing

## Analysis

Long-runtime anomalies persisted: `bowling` 56.4s, `sgf-parsing` 161.6s, `alphametics` 71.5s, `forth` 81.2s. This confirms that evidence-compact and extra-tools are **not** the suppressor of long-runtime behavior. The suppressor must be `finalize-warn` or `hello`.

Pass rate (92.9%) is also lower than group2 (96.4%), suggesting finalize-warn or hello also contribute positively to performance.

## Raw Result

```text
benchmarks/results_full_polyglot_checkpoint_shell_group2a.json
```
