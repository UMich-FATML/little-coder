# All On Result

## Setup

Extension setting: full little-coder extension set.

Model:
- `umich/qwen/qwen3.6-35b-a3b`

Dataset:
- `terminal-bench@2.0`

Agent:
- `benchmarks.harbor_adapter.little_coder_agent:LittleCoderAgent`

Command:

```bash
harbor run \
  --dataset terminal-bench@2.0 \
  --agent-import-path benchmarks.harbor_adapter.little_coder_agent:LittleCoderAgent \
  --model umich/qwen/qwen3.6-35b-a3b \
  --jobs-dir benchmarks/harbor_runs/ablation_all_on \
  --n-concurrent 7 \
  --n-attempts 5

## Harbor Output Summary

- Total attempted: 445 / 445
- Scored trials: 205
- Exceptions: 244
- Mean: 0.094
- Pass@2: 0.163
- Pass@4: 0.240
- Pass@5: 0.258
- Total runtime: 2h 41m 14s

## Reward Counts

| Reward | Count |
|---:|---:|
| 0.0 | 163 |
| 1.0 | 42 |

## Exception Counts

| Exception | Count |
|---|---:|
| VerifierTimeoutError | 3 |
| AgentTimeoutError | 4 |
| RuntimeError | 237 |

## Variance Estimate

For the scored reward outcomes only:

- Number of scored trials: `n = 205`
- Number of successful scored trials: `42`
- Scored reward mean: `42 / 205 = 0.2049`
- Sample variance of scored binary rewards: `0.1638`
- Standard error of scored reward mean: `0.0282`

Note: Harbor's reported `Mean = 0.094` uses the full benchmark accounting with exceptions counted as errors. The variance estimate above is computed only from the 205 scored reward outcomes.

## Raw Result

Local raw result path:

```text
benchmarks/harbor_runs/ablation_all_on/2026-05-19__23-56-30/result.json
```

Raw `harbor_runs` artifacts are not committed because verifier logs may contain secrets/tokens.
