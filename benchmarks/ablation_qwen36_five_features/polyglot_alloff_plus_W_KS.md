# Aider Polyglot: All-Off + write-guard + knowledge-inject + skill-inject

## Setup
Extension setting: all-off (14 extensions) plus write-guard, knowledge-inject,
and skill-inject enabled. (knowledge-inject depends on skill-inject.)
Model:

* `umich/qwen/qwen3.6-35b-a3b`

Dataset:

* Exercism Python (140 exercises)

## Results

* Total: 140
* Pass: 133 (95.0%)
* Fail: 7 (5.0%)

## Failed Exercises

* book-store, bowling, camicia, forth, pov, react, sgf-parsing

## Analysis

Pass rate is 95.0% (133/140), slightly below the recurring 95.7% ceiling seen in
most other two-feature coalitions. This is the first pair that drops below that level.

The pairwise interaction between W and KS:

gamma_{W,KS} = v({W,KS}) - v({W}) - v({KS}) + v(empty)
             = 95.0 - 96.4 - 94.3 + 91.4
             = -4.3pp

Comparison of all observed pairs so far:

| Pair     | v(S)  | Interaction |
|----------|-------|-------------|
| {Q, W}   | 95.7% | -7.9pp      |
| {Q, OP}  | 95.7% | -5.0pp      |
| {Q, KS}  | 97.1% | -4.3pp      |
| {W, KS}  | 95.0% | -4.3pp      |
| {W, OP}  | 95.7% | -2.9pp      |

All pairwise interactions are negative. The W x KS interaction (-4.3pp) is identical
in magnitude to Q x KS (-4.3pp), suggesting KS introduces a fixed level of interference
regardless of which feature it is paired with.

## Raw Result
```text
benchmarks/results_full_polyglot_alloff_plus_W_KS.json
```
