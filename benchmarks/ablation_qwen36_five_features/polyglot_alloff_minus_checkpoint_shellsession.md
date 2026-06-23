# Aider Polyglot: All-Off minus checkpoint minus shell-session

## Setup
Extension setting: all-off (14 extensions) minus checkpoint and shell-session.
Model:
* `umich/qwen/qwen3.6-35b-a3b`
Dataset:
* Exercism Python (140 exercises)

## Results
- Total: 140
- Pass: 128 (91.4%)
- Fail: 12 (8.6%)

## Failed Exercises
- bowling, camicia, connect, forth, paasio, pov, react, relative-distance, rest-api, scale-generator, sgf-parsing, variable-length-quantity

## Analysis
Pass rate is 91.4%, identical to all-off baseline (128/140). Removing checkpoint and
shell-session causes no performance degradation on the Aider Polyglot benchmark, confirming
that these two extensions contribute nothing to pass rate on this task — their value lies
elsewhere (session recovery, state persistence across turns).

## Raw Result
```text
benchmarks/results_full_polyglot_alloff_minus_checkpoint_shellsession.json
```
