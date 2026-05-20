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
