# Aider Polyglot: All-Off + knowledge-inject (+ skill-inject dependency)

## Setup

Extension setting: all-off (14 extensions) plus knowledge-inject and skill-inject (required dependency).

Model:
* `umich/qwen/qwen3.6-35b-a3b`

Dataset:
* Exercism Python (140 exercises)

## Results

- Total: 140
- Pass: 132 (94.3%)
- Fail: 8 (5.7%)

## Failed Exercises

- book-store, camicia, forth, paasio, pov, react, scale-generator, sgf-parsing

## Analysis

Note: knowledge-inject depends on skill-inject, so this result reflects all-off + knowledge-inject + skill-inject combined. Pass rate improved from 91.4% (all-off) to 94.3% (+2.9%). For comparison, skill-inject alone yields 92.9%, so knowledge-inject adds ~1.4% on top of skill-inject.

Long-runtime anomalies: ledger 100.2s, sgf-parsing 117.7s.

## Raw Result

```text
benchmarks/results_full_polyglot_alloff_plus_knowledgeinject.json
```
