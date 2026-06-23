# Aider Polyglot: All-Off + quality-monitor + output-parser + knowledge-inject + skill-inject

## Setup
Extension setting: all-off (14 extensions) plus quality-monitor, output-parser,
knowledge-inject, and skill-inject enabled. This is the leave-one-out of W (write-guard)
from the grand coalition.
Model:

* `umich/qwen/qwen3.6-35b-a3b`

Dataset:

* Exercism Python (140 exercises)

## Results

* Total: 140
* Pass: 134 (95.7%)
* Fail: 6 (4.3%)

## Failed Exercises

* book-store, bowling, camicia, connect, pov, sgf-parsing

## Analysis

Pass rate is 95.7% (134/140), identical to the grand coalition v({Q,W,OP,KS}) = 95.7%.
Removing W from the grand coalition has zero effect — W is a null player when entering
last, just like KS.

W's marginal contribution when entering last:
v({Q,W,OP,KS}) - v({Q,OP,KS}) = 95.7% - 95.7% = 0.0pp

Complete leave-one-out summary:

| Removed | v(remaining) | Marginal loss |
|---------|-------------|---------------|
| Q       | v({W,OP,KS}) = 92.1% | -3.6pp (dominant) |
| W       | v({Q,OP,KS}) = 95.7% |  0.0pp (null)     |
| OP      | v({Q,W,KS}) = 95.0%  | -0.7pp (small)    |
| KS      | v({Q,W,OP}) = 95.7%  |  0.0pp (null)     |

Only Q has a meaningful marginal contribution when entering last. OP has a small
positive effect. W and KS are null players in the leave-one-out sense.

This completes all 16 coalitions for the 4-player Shapley game. The full coalition
table:

| Coalition        | Pass | Rate  |
|------------------|------|-------|
| empty (all-off)  | 128  | 91.4% |
| {Q}              | 138  | 98.6% |
| {W}              | 135  | 96.4% |
| {OP}             | 131  | 93.6% |
| {KS}             | 132  | 94.3% |
| {Q,W}            | 134  | 95.7% |
| {Q,OP}           | 134  | 95.7% |
| {Q,KS}           | 136  | 97.1% |
| {W,OP}           | 134  | 95.7% |
| {W,KS}           | 133  | 95.0% |
| {OP,KS}          | 131  | 93.6% |
| {Q,W,OP}         | 134  | 95.7% |
| {Q,W,KS}         | 133  | 95.0% |
| {Q,OP,KS}        | 134  | 95.7% |
| {W,OP,KS}        | 129  | 92.1% |
| {Q,W,OP,KS}      | 134  | 95.7% |

## Raw Result
```text
benchmarks/results_full_polyglot_alloff_plus_Q_OP_KS.json
```
