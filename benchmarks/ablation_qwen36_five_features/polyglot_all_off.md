# Aider Polyglot All Off Result

## Setup

Extension setting: full little-coder extension set minus the five features (write-guard, skill-inject, knowledge-inject, output-parser, quality-monitor, thinking-budget).

Model:
* `umich/qwen/qwen3.6-35b-a3b`

Dataset:
* Exercism Python (140 exercises)

Command:
python benchmarks/aider_polyglot.py 
--language python 
--model umich/qwen/qwen3.6-35b-a3b 
--verbose

## Results

- Total: 140
- Pass: 128 (91.4%)
- Fail: 12 (8.6%)

## Failed Exercises

- book-store
- bowling
- camicia
- connect
- dot-dsl
- forth
- paasio
- poker
- pov
- react
- scale-generator
- sgf-parsing

## Raw Result

```text
benchmarks/results_full_polyglot_all_off.json
```
