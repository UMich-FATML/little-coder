# Aider Polyglot: All-Off + write-guard + output-parser + knowledge-inject + skill-inject

## Setup
Extension setting: all-off (14 extensions) plus write-guard, output-parser, knowledge-inject,
and skill-inject enabled. This is the leave-one-out of quality-monitor from the grand coalition.
Model:

* `umich/qwen/qwen3.6-35b-a3b`

Dataset:

* Exercism Python (140 exercises)

## Results

* Total: 140
* Pass: 129 (92.1%)
* Fail: 11 (7.9%)

## Failed Exercises

* bowling, camicia, connect, forth, paasio, pov, react, rest-api, sgf-parsing, transpose, two-bucket

## Analysis

Pass rate is 92.1% (129/140), only 0.7pp above all-off baseline (91.4%). Without
quality-monitor, the remaining three features (W, OP, KS) contribute almost nothing.

Q's marginal contribution at different coalition sizes:

| Q enters after...       | Marginal contribution |
|-------------------------|-----------------------|
| ∅ (first)               | 98.6% − 91.4% = +7.2pp |
| {W}                     | 95.7% − 96.4% = −0.7pp |
| {OP}                    | 95.7% − 93.6% = +2.1pp |
| {KS}                    | 97.1% − 94.3% = +2.8pp |
| {W, OP, KS} (last)     | 95.7% − 92.1% = +3.6pp |

Q's contribution diminishes from +7.2pp (entering first) to +3.6pp (entering last),
and is even negative when added on top of W alone. This confirms strong negative
interactions between Q and other features, especially W.

## Raw Result
```text
benchmarks/results_full_polyglot_alloff_plus_W_OP_KS.json
```
