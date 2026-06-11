# Aider Polyglot: All-Off + write-guard + output-parser

## Setup
Extension setting: all-off (14 extensions) plus write-guard and output-parser enabled.
Model:

* `umich/qwen/qwen3.6-35b-a3b`

Dataset:

* Exercism Python (140 exercises)

## Results

* Total: 140
* Pass: 134 (95.7%)
* Fail: 6 (4.3%)

## Failed Exercises

* camicia, connect, forth, pov, scale-generator, sgf-parsing

## Analysis

Pass rate is 95.7% (134/140). This is the first non-Q pair we have observed, and it
matches the recurring 95.7% ceiling seen in {Q,W}, {Q,OP}, and the grand coalition.

The pairwise interaction between W and OP:

gamma_{W,OP} = v({W,OP}) - v({W}) - v({OP}) + v(empty)
             = 95.7 - 96.4 - 93.6 + 91.4
             = -2.9pp

This is negative but substantially milder than the Q-pair interactions (Q x W = -7.9pp,
Q x OP = -5.0pp). The 95.7% value appearing across so many different two-feature
coalitions suggests a natural ceiling on Polyglot where any two active features converge
to approximately the same pass rate regardless of which two are chosen.

Comparison of all observed pairs:

| Pair     | v(S)  | Interaction |
|----------|-------|-------------|
| {Q, W}   | 95.7% | -7.9pp      |
| {Q, OP}  | 95.7% | -5.0pp      |
| {Q, KS}  | 97.1% | -4.3pp      |
| {W, OP}  | 95.7% | -2.9pp      |

## Raw Result
```text
benchmarks/results_full_polyglot_alloff_plus_W_OP.json
```
