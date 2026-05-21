# All Off Result

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
--jobs-dir benchmarks/harbor_runs/ablation_all_off 
--n-concurrent 7 
--n-attempts 5
## Harbor Output Summary

- Total attempted: 445 / 445
- Scored trials: 236
- Exceptions: 219
- Mean: 0.108
- Pass@2: 0.184
- Pass@4: 0.270
- Pass@5: 0.292
- Total runtime: 3h 48m 21s

## Reward Counts

| Reward | Count |
|---:|---:|
| 0.0 | 188 |
| 1.0 | 48 |

## Exception Counts

| Exception | Count |
|---|---:|
| AgentTimeoutError | 11 |
| VerifierTimeoutError | 1 |
| RuntimeError | 207 |

## Raw Result

Local raw result path:
```text
benchmarks/harbor_runs/ablation_all_off/2026-05-20__20-47-13/result.json
```

Raw `harbor_runs` artifacts are not committed because verifier logs may contain secrets/tokens.
