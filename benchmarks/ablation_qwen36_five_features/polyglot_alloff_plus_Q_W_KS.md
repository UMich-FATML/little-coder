# Aider Polyglot: All-Off + quality-monitor + write-guard + knowledge-inject + skill-inject

## Setup
Extension setting: all-off (14 extensions) plus quality-monitor, write-guard,
knowledge-inject, and skill-inject enabled. This is the leave-one-out of OP
from the grand coalition.
Model:

* `umich/qwen/qwen3.6-35b-a3b`

Dataset:

* Exercism Python (140 exercises)

## Results

* Total: 140
* Pass: 133 (95.0%)
* Fail: 7 (5.0%)

## Failed Exercises

* camicia, connect, forth, ledger, pov, react, sgf-parsing

## Analysis

Pass rate is 95.0% (133/140), slightly below the grand coalition (95.7%). Removing
OP from the grand coalition costs 0.7pp, meaning OP has a small positive marginal
contribution when entering last.

OP's marginal contribution when entering last:
v({Q,W,OP,KS}) - v({Q,W,KS}) = 95.7% - 95.0% = +0.7pp

Updated leave-one-out summary:

| Removed | v(remaining) | Marginal loss |
|---------|-------------|---------------|
| Q       | v({W,OP,KS}) = 92.1% | -3.6pp (dominant) |
| W       | not yet observed      |    ?              |
| OP      | v({Q,W,KS}) = 95.0%  | -0.7pp (small)    |
| KS      | v({Q,W,OP}) = 95.7%  |  0.0pp (null)     |

Q is clearly the most valuable feature when entering last. KS is a null player.
OP has a small but nonzero contribution. W remains to be measured.

## Raw Result
```text
benchmarks/results_full_polyglot_alloff_plus_Q_W_KS.json
```
