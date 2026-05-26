# Aider Polyglot: All-Off + output-parser

## Setup

Extension setting: all-off (14 extensions) plus output-parser.

Model:
* `umich/qwen/qwen3.6-35b-a3b`

Dataset:
* Exercism Python (140 exercises)

## Results

- Total: 140
- Pass: 131 (93.6%)
- Fail: 9 (6.4%)

## Failed Exercises

- book-store, camicia, connect, forth, ledger, pov, react, rest-api, sgf-parsing

## Analysis

Pass rate improved from 91.4% (all-off) to 93.6% (+2.2%). output-parser has a modest positive contribution to performance. Long-runtime anomalies still present (connect 113.3s, bowling 90.0s), confirming output-parser does not affect timeout behavior.

## Raw Result

```text
benchmarks/results_full_polyglot_alloff_plus_outputparser.json
```
