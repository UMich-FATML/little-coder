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

Pass rate is 95.7% (134/140). This is the v({Q, W}) coalition for the two-player
Shapley game with quality-monitor (Q) and write-guard (W).

Key comparison against other coalitions:

| Coalition       | Pass | Rate  |
|-----------------|------|-------|
| ∅ (all-off)     | 128  | 91.4% |
| {W}             | 135  | 96.4% |
| {Q, W}          | 134  | 95.7% |
| {Q}             | 138  | 98.6% |

v({Q, W}) = 95.7% is **lower** than v({Q}) = 98.6%, indicating a strong negative
interaction between quality-monitor and write-guard: adding write-guard on top of
quality-monitor reduces pass rate by 2.9pp. The interaction effect is:

γ_QW = v({Q,W}) − v({Q}) − v({W}) + v(∅) = 95.7 − 98.6 − 96.4 + 91.4 = −7.9pp

## Raw Result
```text
benchmarks/results_full_polyglot_alloff_plus_qualitymonitor_writeguard.json
```
