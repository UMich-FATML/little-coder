# Aider Polyglot: Zero-extension + quality-monitor

## Setup
Extension setting: only llama-cpp-provider and quality-monitor enabled.
No infrastructure extensions (no benchmark-profiles, turn-cap, evidence, browser, etc.)
Model:

* `umich/qwen/qwen3.6-35b-a3b`

Dataset:

* Exercism Python (140 exercises)

## Results

* Total: 140
* Pass: 132 (94.3%)
* Fail: 8 (5.7%)

## Failed Exercises

* book-store, camicia, connect, paasio, pov, react, scale-generator, sgf-parsing

## Analysis

Pass rate is 94.3% (132/140), which is LOWER than zero-extension (133/140 = 95.0%).
Quality-monitor without infrastructure actually hurts performance by -0.7pp.

This contrasts sharply with all-off + Q = 98.6%, where Q with infrastructure is the
highest-performing configuration observed.

The Q x INFRA interaction effect:

gamma_{Q,INFRA} = v({Q,INFRA}) - v({Q}) - v({INFRA}) + v(empty)
                = 98.6% - 94.3% - 91.4% + 95.0%
                = +7.9pp

This is a strong POSITIVE interaction — the largest magnitude interaction observed
in the entire analysis, and the only positive one. All pairwise interactions among
the 4 target features were negative (-2.9 to -7.9pp), but Q x INFRA is +7.9pp.

Interpretation: Q's correction mechanism (detect errors -> force retry) needs the
infrastructure's tools and context to be effective. Without INFRA, Q detects problems
but lacks the tool chain to resolve them, resulting in worse performance than doing
nothing. With INFRA, Q can leverage the full scaffold to recover from errors.

Complete 2x2 table for {Q, INFRA}:

| Config       | Q off  | Q on   |
|-------------|--------|--------|
| INFRA off   | 95.0%  | 94.3%  |
| INFRA on    | 91.4%  | 98.6%  |

## Raw Result
```text
benchmarks/results_full_polyglot_zero_plus_Q.json
```
