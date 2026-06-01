# Aider Polyglot: All-Off + thinking-budget

## Setup
Extension setting: all-off (14 extensions) plus thinking-budget.
Model:
* `umich/qwen/qwen3.6-35b-a3b`
Dataset:
* Exercism Python (140 exercises)

## Results
- Status: incomplete — could not obtain clean benchmark run

## Why This Run Could Not Be Completed
thinking-budget accelerates model responses, which exposes a race condition in the harness:
pi rejects retry prompts ("Agent is already processing") when the agent has not yet settled
from the previous turn. All other ablation runs do not trigger this bug because their
response latency is sufficient for pi to settle naturally.

Adding a sleep patch to the harness would fix the crash but introduces an asymmetric
intervention specific to this configuration. The run was therefore left incomplete rather
than producing results under modified conditions.

## Implication
The thinking-budget extension cannot be cleanly ablated under the current harness without
patching rpc_client behavior. Its contribution to all-on vs all-off performance gap remains
unmeasured in this experiment set.
