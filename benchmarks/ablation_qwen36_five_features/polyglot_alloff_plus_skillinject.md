# Aider Polyglot: All-Off + skill-inject

## Setup

Extension setting: all-off (14 extensions) plus skill-inject.

Model:
* `umich/qwen/qwen3.6-35b-a3b`

Dataset:
* Exercism Python (140 exercises)

## Results

- Total: 140
- Pass: 130 (92.9%)
- Fail: 10 (6.4%)

## Failed Exercises

- camicia, connect, paasio, pov, react, rest-api, scale-generator, sgf-parsing, transpose (+ 1 crash)

## Crash

One crash occurred mid-run with "Agent is already processing" race condition error. Recovered via --resume.

## Analysis

Pass rate improved from 91.4% (all-off) to 92.9% (+1.5%). skill-inject has a modest positive contribution. Long-runtime anomaly: ledger 136.2s on first attempt (failed), then passed on resume at 54.7s.

## Raw Result

```text
benchmarks/results_full_polyglot_alloff_plus_skillinject.json
```
