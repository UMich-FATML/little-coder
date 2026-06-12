# Aider Polyglot: All-Off + quality-monitor + write-guard + output-parser

## Setup
Extension setting: all-off (14 extensions) plus quality-monitor, write-guard, and
output-parser enabled. This is the leave-one-out of KS from the grand coalition.
Model:

* `umich/qwen/qwen3.6-35b-a3b`

Dataset:

* Exercism Python (140 exercises)

## Results

* Total: 140
* Pass: 134 (95.7%)
* Fail: 6 (4.3%)

## Failed Exercises

* bowling, camicia, paasio, pov, react, sgf-parsing

## Note on first run

The first attempt crashed at exercise 18 (bowling) with a TimeoutError: "pi did not
respond to request within 30s". This is a different error from the race-condition crash
seen with {OP,KS} and thinking-budget. The retry completed successfully. The crash
occurred during a retry prompt on a long-running exercise (bowling typically takes
>100s), suggesting the agent was still processing when the RPC client timed out.

## Analysis

Pass rate is 95.7% (134/140), identical to the grand coalition v({Q,W,OP,KS}) = 95.7%.
Removing KS from the grand coalition has zero effect, confirming that KS contributes
nothing in the presence of {Q, W, OP}.

KS's marginal contribution when entering last:
v({Q,W,OP,KS}) - v({Q,W,OP}) = 95.7% - 95.7% = 0.0pp

This is consistent with the Shapley analysis showing phi_KS near zero. KS is a
null player in the presence of the other three features.

Leave-one-out summary (removing each feature from the grand coalition):

| Removed | v(remaining) | Marginal loss |
|---------|-------------|---------------|
| Q       | v({W,OP,KS}) = 92.1% | -3.6pp |
| KS      | v({Q,W,OP}) = 95.7%  |  0.0pp |
| W       | not yet observed      |    ?   |
| OP      | not yet observed      |    ?   |

## Raw Result
```text
benchmarks/results_full_polyglot_alloff_plus_Q_W_OP.json
```
