# Aider Polyglot: Zero-extension + output-parser

## Setup
Extension setting: only llama-cpp-provider and output-parser enabled.
No infrastructure extensions.
Model:

* `umich/qwen/qwen3.6-35b-a3b`

Dataset:

* Exercism Python (140 exercises)

## Results

* Total: 140
* Pass: 129 (92.1%)
* Fail: 11 (7.9%)

## Failed Exercises

* book-store, bowling, camicia, forth, paasio, poker, pov, react, scale-generator, sgf-parsing, zebra-puzzle

## Analysis

Pass rate is 92.1% (129/140), the lowest single-feature configuration observed.
OP without infrastructure causes -2.9pp degradation from zero-extension baseline.

gamma_{OP,INFRA} = v({OP,INFRA}) - v({OP}) - v({INFRA}) + v(empty)
                 = 93.6% - 92.1% - 91.4% + 95.0%
                 = +5.1pp

All three tested features show the same pattern:

| Feature | Alone      | With INFRA  | Interaction |
|---------|-----------|-------------|-------------|
| Q       | -0.7pp    | +3.6pp      | +7.9pp      |
| W       | -1.4pp    | +1.4pp      | +6.4pp      |
| OP      | -2.9pp    | -1.4pp      | +5.1pp      |

Every target feature is harmful without infrastructure but improves
(or becomes less harmful) with it. The interaction is always strongly positive.

## Raw Result
```text
benchmarks/polyglot_results_zero_plus_OP.txt
```
