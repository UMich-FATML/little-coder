# Aider Polyglot: Zero Extension (llama-cpp-provider only)

## Setup
Extension setting: all extensions removed except llama-cpp-provider (model backend).
Model:

* `umich/qwen/qwen3.6-35b-a3b`

Dataset:

* Exercism Python (140 exercises)

## Results

* Total: 140
* Pass: 133 (95.0%)
* Fail: 7 (5.0%)

## Failed Exercises

* book-store, bowling, camicia, paasio, pov, react, rest-api

## Analysis

Pass rate is 95.0% (133/140), **higher** than all-off baseline (128/140 = 91.4%).
The 14 scaffold extensions in all-off have a net negative effect of −3.6pp on Aider
Polyglot pass rate. The scaffold adds context complexity and tool overhead that
hinders the agent on short, self-contained coding tasks.

This also confirms that Aider Polyglot cannot detect timeout behavior: even with no
extensions, the agent completes all tasks without any AgentTimeoutError.

## Raw Result
```text
benchmarks/results_full_polyglot_zero_extension.json
```
