# Aider Polyglot: All-On minus thinking-budget

## Setup
Extension setting: all extensions enabled except thinking-budget (excluded due to race condition).
This serves as the grand coalition v({Q, W, OP, KS}) for the 4-player Shapley game.
Model:

* `umich/qwen/qwen3.6-35b-a3b`

Dataset:

* Exercism Python (140 exercises)

## Results

* Total: 140
* Pass: 134 (95.7%)
* Fail: 6 (4.3%)

## Failed Exercises

* camicia, connect, paasio, pov, react, rectangles

## Analysis

Pass rate is 95.7% (134/140), identical to all-off + quality-monitor + write-guard (also 95.7%).
This means adding output-parser and knowledge-inject+skill-inject on top of {Q, W} provides
zero additional gain — the grand coalition equals the {Q, W} coalition.

Updated 4-player Shapley game data:

| Coalition              | Pass | Rate  |
|------------------------|------|-------|
| ∅ (all-off)            | 128  | 91.4% |
| {OP}                   | 131  | 93.6% |
| {SI}                   | 130  | 92.9% |
| {KS} (KI+SI)          | 132  | 94.3% |
| {W}                    | 135  | 96.4% |
| {Q, W}                 | 134  | 95.7% |
| {Q}                    | 138  | 98.6% |
| {Q, W, OP, KS} (grand)| 134  | 95.7% |

## Raw Result
```text
benchmarks/results_full_polyglot_allon_minus_thinkingbudget.json
```
