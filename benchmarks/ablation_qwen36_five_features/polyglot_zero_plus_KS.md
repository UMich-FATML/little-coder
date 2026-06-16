# Aider Polyglot: Zero-extension + knowledge-inject + skill-inject

## Setup
Extension setting: only llama-cpp-provider, knowledge-inject, and skill-inject enabled.
No infrastructure extensions.
Model:

* `umich/qwen/qwen3.6-35b-a3b`

Dataset:

* Exercism Python (140 exercises)

## Results

* Total: 140
* Pass: 130 (92.9%)
* Fail: 10 (7.1%)

## Failed Exercises

* bowling, camicia, connect, forth, paasio, palindrome-products, pov, react, sgf-parsing, two-bucket

## Analysis

Pass rate is 92.9% (130/140), -2.1pp below zero-extension baseline.

gamma_{KS,INFRA} = v({KS,INFRA}) - v({KS}) - v({INFRA}) + v(empty)
                 = 94.3% - 92.9% - 91.4% + 95.0%
                 = +5.0pp

Complete feature x INFRA interaction table:

| Feature | Alone (no INFRA) | With INFRA      | Interaction |
|---------|-----------------|-----------------|-------------|
| Q       | 94.3% (-0.7pp)  | 98.6% (+3.6pp)  | +7.9pp      |
| W       | 93.6% (-1.4pp)  | 96.4% (+1.4pp)  | +6.4pp      |
| OP      | 92.1% (-2.9pp)  | 93.6% (-1.4pp)  | +5.1pp      |
| KS      | 92.9% (-2.1pp)  | 94.3% (-0.7pp)  | +5.0pp      |

All four target features are harmful without infrastructure and all four
have strong positive interactions with INFRA (+5.0 to +7.9pp). This is
the central empirical finding: target features require the infrastructure
scaffold to function. Without it, their correction/protection/injection
mechanisms add cognitive overhead without a supporting tool chain.

## Raw Result
```text
benchmarks/polyglot_results_zero_plus_KS.txt
```
