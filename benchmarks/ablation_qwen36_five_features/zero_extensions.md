# Zero Extensions Result

## Setup

Extension setting: no extensions at all (empty `.pi/extensions/` directory).

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
--jobs-dir benchmarks/harbor_runs/ablation_zero_extensions_v3 
--n-concurrent 7 
--n-attempts 5
## Harbor Output Summary

- Total attempted: 445 / 445
- Scored trials: 436
- Exceptions: 445
- Mean: 0.000
- Pass@2: 0.000
- Pass@4: 0.000
- Pass@5: 0.000
- Total runtime: 1h 53m 46s

## Reward Counts

| Reward | Count |
|---:|---:|
| 0.0 | 436 |

## Exception Counts

| Exception | Count |
|---|---:|
| AgentTimeoutError | 436 |
| RuntimeError | 9 |

## Notes

All trials timed out. Without the `turn-cap` extension, the agent has no turn limit and runs until the global timeout is reached. This result confirms that `turn-cap` is a prerequisite for meaningful evaluation — the zero-extensions condition is not a viable baseline.

## Raw Result

Local raw result path:
```text
benchmarks/harbor_runs/ablation_zero_extensions_v3/2026-05-23__10-16-51/result.json
```
