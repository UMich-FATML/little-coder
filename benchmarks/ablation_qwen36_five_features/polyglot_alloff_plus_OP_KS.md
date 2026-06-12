# Aider Polyglot: All-Off + output-parser + knowledge-inject + skill-inject

## Setup
Extension setting: all-off (14 extensions) plus output-parser, knowledge-inject,
and skill-inject enabled. (knowledge-inject depends on skill-inject.)
Model:

* `umich/qwen/qwen3.6-35b-a3b`

Dataset:

* Exercism Python (140 exercises)

## Results

* Total: 140
* Pass: 131 (93.6%)
* Fail: 9 (6.4%)

## Failed Exercises

* camicia, connect, forth, paasio, palindrome-products, poker, pov, react, sgf-parsing

## Note on first run

The first attempt crashed at exercise ~80 (after minesweeper) with the race-condition
error "Agent is already processing." This is the same error seen with thinking-budget,
but here it was triggered by the {OP, KS} combination without thinking-budget present.
The retry completed successfully. This suggests the race condition is not exclusive to
thinking-budget — it can also be triggered by output-parser + skill-inject interaction
under certain timing conditions.

## Analysis

Pass rate is 93.6% (131/140), identical to v({OP}) = 93.6%. Adding KS on top of OP
provides zero marginal benefit — KS's contribution is completely absorbed.

The pairwise interaction between OP and KS:

gamma_{OP,KS} = v({OP,KS}) - v({OP}) - v({KS}) + v(empty)
              = 93.6 - 93.6 - 94.3 + 91.4
              = -2.9pp

Complete pairwise interaction table:

| Pair     | v(S)  | Interaction |
|----------|-------|-------------|
| {Q, W}   | 95.7% | -7.9pp      |
| {Q, OP}  | 95.7% | -5.0pp      |
| {Q, KS}  | 97.1% | -4.3pp      |
| {W, KS}  | 95.0% | -4.3pp      |
| {W, OP}  | 95.7% | -2.9pp      |
| {OP, KS} | 93.6% | -2.9pp      |

All six pairwise interactions are negative. The strongest interference is Q x W (-7.9pp),
the weakest are W x OP and OP x KS (both -2.9pp).

## Raw Result
```text
benchmarks/results_full_polyglot_alloff_plus_OP_KS.json
```
