# Aider Polyglot: Zero-extension + write-guard

## Setup
Extension setting: only llama-cpp-provider and write-guard enabled.
No infrastructure extensions.
Model:

* `umich/qwen/qwen3.6-35b-a3b`

Dataset:

* Exercism Python (140 exercises)

## Results

* Total: 140
* Pass: 131 (93.6%)
* Fail: 9 (6.4%)

## Failed Exercises

* camicia, connect, forth, ocr-numbers, paasio, pov, react, rest-api, sgf-parsing

## Analysis

Pass rate is 93.6% (131/140), LOWER than zero-extension (95.0%) by -1.4pp.
Write-guard without infrastructure hurts performance, same pattern as Q.

W x INFRA interaction:
gamma_{W,INFRA} = v({W,INFRA}) - v({W}) - v({INFRA}) + v(empty)
                = 96.4% - 93.6% - 91.4% + 95.0%
                = +6.4pp

Emerging pattern — all target features tested so far are harmful without INFRA:

| Feature | Alone (no INFRA) | With INFRA | Interaction |
|---------|-----------------|------------|-------------|
| Q       | 94.3% (-0.7pp)  | 98.6% (+3.6pp) | +7.9pp |
| W       | 93.6% (-1.4pp)  | 96.4% (+1.4pp) | +6.4pp |
| OP      | ?               | 93.6% (-1.4pp) | ?      |
| KS      | ?               | 94.3% (-0.7pp) | ?      |

## Raw Result
```text
benchmarks/polyglot_results_zero_plus_W.txt
```
