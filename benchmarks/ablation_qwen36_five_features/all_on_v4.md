# All On Result (v4)

## Setup

Extension setting: full little-coder extension set (all 20 extensions enabled).

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
--jobs-dir benchmarks/harbor_runs/ablation_all_on_v4 
--n-concurrent 7 
--n-attempts 5
## Harbor Output Summary

- Total attempted: 445 / 445
- Scored trials: 441
- Exceptions: 15
- Mean: 0.211
- Pass@2: 0.272
- Pass@4: 0.339
- Pass@5: 0.360
- Total runtime: 5h 58m 25s

## Reward Counts

| Reward | Count |
|---:|---:|
| 0.0 | 347 |
| 1.0 | 94 |

## Exception Counts

| Exception | Count |
|---|---:|
| VerifierTimeoutError | 3 |
| AgentTimeoutError | 11 |
| RuntimeError | 1 |

## Variance Estimate

- Number of scored trials: `n = 441`
- Number of successful scored trials: `94`
- Scored reward mean: `94 / 441 = 0.2131`
- Sample variance of scored binary rewards: `0.1678`
- Standard error of scored reward mean: `0.0195`

## Raw Result

Local raw result path:
```text
benchmarks/harbor_runs/ablation_all_on_v4/2026-05-22__18-45-41/result.json
```
