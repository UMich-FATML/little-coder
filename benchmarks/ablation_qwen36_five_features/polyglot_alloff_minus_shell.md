# Aider Polyglot: All-Off minus shell-session

## Setup

Extension setting: all-off (14 extensions) minus shell-session (13 extensions total).

Model:
* `umich/qwen/qwen3.6-35b-a3b`

Dataset:
* Exercism Python (140 exercises)

## Results

- Total: 140
- Pass: 130 (92.9%)
- Fail: 10 (5.7%)

## Failed Exercises

- book-store, bowling, camicia, connect, dot-dsl, forth, paasio, pov, react, sgf-parsing

## Analysis

`bowling` took 112.3s — long-runtime behavior persisted even without shell-session, confirming that **checkpoint alone is also sufficient to cause long-runtime behavior**.

Combined with `polyglot_alloff_minus_checkpoint.md` (which also showed long runtimes when only checkpoint was removed), the full picture is:

- Both shell-session and checkpoint independently cause long-runtime behavior
- When both are present together (as in all-off), they appear to **mutually suppress** each other's long-runtime tendency — all-off shows no long runtimes despite containing both
- Only removing both eliminates long runtimes entirely

This interaction is currently not well understood and warrants further investigation.

## Raw Result

```text
benchmarks/results_full_polyglot_alloff_minus_shell.json
```
