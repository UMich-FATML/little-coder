# All Off Result (v3)

## Setup

Extension setting: full little-coder extension set **minus** the five features (write-guard, skill-inject, knowledge-inject, output-parser, quality-monitor, thinking-budget).

Model:
* `umich/qwen/qwen3.6-35b-a3b`

Dataset:
* `terminal-bench@2.0`

Agent:
* `benchmarks.harbor_adapter.little_coder_agent:LittleCoderAgent`

Command:
harbor run 
--dataset terminal-bench@2.0 
--agent-import-path benchmarks.harbor_adapter.little_coder_agent:LittleCoderAgent 
--model umich/qwen/qwen3.6-35b-a3b 
--jobs-dir benchmarks/harbor_runs/ablation_all_off_v3 
--n-concurrent 7 
--n-attempts 5
## Harbor Output Summary

- Total attempted: 445 / 445
- Scored trials: 435
- Exceptions: 25
- Mean: 0.200
- Pass@2: 0.246
- Pass@4: 0.288
- Pass@5: 0.303
- Total runtime: 7h 52m 38s

## Reward Counts

| Reward | Count |
|---:|---:|
| 0.0 | 346 |
| 1.0 | 89 |

## Exception Counts

| Exception | Count |
|---|---:|
| AgentTimeoutError | 15 |
| VerifierTimeoutError | 7 |
| EnvironmentStartTimeoutError | 2 |
| RuntimeError | 1 |

## Variance Estimate

- Number of scored trials: `n = 435`
- Number of successful scored trials: `89`
- Scored reward mean: `89 / 435 = 0.2046`
- Sample variance of scored binary rewards: `0.1627`
- Standard error of scored reward mean: `0.0193`

## Raw Result

Local raw result path:
```text
benchmarks/harbor_runs/ablation_all_off_v3/2026-05-22__09-31-29/result.json
```
