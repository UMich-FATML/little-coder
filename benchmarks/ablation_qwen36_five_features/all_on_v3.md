# All On Result (v3)

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
--jobs-dir benchmarks/harbor_runs/ablation_all_on_v3 
--n-concurrent 7 
--n-attempts 5
## Harbor Output Summary

- Total attempted: 445 / 445
- Scored trials: 289
- Exceptions: 171
- Mean: 0.130
- Pass@2: 0.203
- Pass@4: 0.267
- Pass@5: 0.281
- Total runtime: 5h 30m 59s

## Reward Counts

| Reward | Count |
|---:|---:|
| 0.0 | 231 |
| 1.0 | 58 |

## Exception Counts

| Exception | Count |
|---|---:|
| AgentTimeoutError | 15 |
| VerifierTimeoutError | 3 |
| RuntimeError | 153 |

## Variance Estimate

- Number of scored trials: `n = 289`
- Number of successful scored trials: `58`
- Scored reward mean: `58 / 289 = 0.2007`
- Sample variance of scored binary rewards: `0.1604`
- Standard error of scored reward mean: `0.0235`

## Raw Result

Local raw result path:
```text
benchmarks/harbor_runs/ablation_all_on_v3/2026-05-21__18-12-33/result.json
```
