# Aider Polyglot: All-Off + quality-monitor + output-parser

## Setup
Extension setting: all-off (14 extensions) plus quality-monitor and output-parser enabled.
Model:

* `umich/qwen/qwen3.6-35b-a3b`

Dataset:

* Exercism Python (140 exercises)

## Results

* Total: 140
* Pass: 134 (95.7%)
* Fail: 6 (4.3%)

## Failed Exercises

* bowling, camicia, connect, pov, scale-generator, sgf-parsing

## Analysis

Pass rate is 95.7% (134/140), identical to v({Q, W}) and v(grand). Adding output-parser
on top of quality-monitor drops pass rate by 2.9pp (98.6% → 95.7%), the same magnitude
as adding write-guard.

Interaction effect:
γ_{Q,OP} = v({Q,OP}) − v({Q}) − v({OP}) + v(∅) = 95.7 − 98.6 − 93.6 + 91.4 = −5.1pp

The negative interaction is NOT specific to write-guard — adding ANY second feature on
top of quality-monitor causes a similar drop. This suggests quality-monitor's correction
mechanism conflicts with other features' interventions, or that the ceiling effect at
~96% creates a natural regression.

## Raw Result
```text
benchmarks/results_full_polyglot_alloff_plus_Q_OP.json
```
