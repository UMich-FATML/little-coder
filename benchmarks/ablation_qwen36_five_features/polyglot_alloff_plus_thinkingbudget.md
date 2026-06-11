# Aider Polyglot: All-Off + thinking-budget

## Setup
Extension setting: all-off (14 extensions) plus thinking-budget enabled.
Model:

* `umich/qwen/qwen3.6-35b-a3b`

Dataset:

* Exercism Python (140 exercises)

## Results

* Crashed at exercise 16 (book-store) with race-condition error.
* Only 15 exercises completed (all PASS) before crash.

## Error
RuntimeError: pi rejected prompt: Agent is already processing.
Specify streamingBehavior ('steer' or 'followUp') to queue the message.
## Analysis

thinking-budget triggers a race condition when retrying: the extension caps thinking
tokens and retries with thinking disabled, but the retry is sent before the previous
agent call has fully settled. This is the same behavior observed in the Jun 1 summary
(Case 10). thinking-budget remains **untestable** in the current codebase and is
excluded from the Shapley analysis.
