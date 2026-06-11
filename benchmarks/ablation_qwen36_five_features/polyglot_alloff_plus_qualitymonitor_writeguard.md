# Aider Polyglot: All-Off + quality-monitor + write-guard

## Setup
Extension setting: all-off (14 extensions) plus quality-monitor and write-guard enabled.
Model:

* `umich/qwen/qwen3.6-35b-a3b`

Dataset:

* Exercism Python (140 exercises)

## Results

* Total: 140
* Pass: 134 (95.7%)
* Fail: 6 (4.3%)

## Failed Exercises

* bowling, camicia, forth, pov, react, sgf-parsing

## Analysis

Pass rate is 95.7% (134/140). The interaction effect between Q and W is:

γ_QW = v({Q,W}) − v({Q}) − v({W}) + v(∅) = 95.7 − 98.6 − 96.4 + 91.4 = −7.9pp

Strong negative interaction: adding write-guard on top of quality-monitor reduces
pass rate by 2.9pp (98.6% → 95.7%). The two features interfere with each other
on Polyglot tasks.

## Raw Result
```text
benchmarks/results_full_polyglot_alloff_plus_qualitymonitor_writeguard.json
```
