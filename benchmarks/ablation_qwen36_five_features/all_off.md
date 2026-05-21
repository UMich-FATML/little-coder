# All Off Result

## Setup

Extension setting: full little-coder extension set minus the target scaffold adaptations.

Removed extension folders:
- `write-guard`
- `skill-inject`
- `knowledge-inject`
- `output-parser`
- `quality-monitor`
- `thinking-budget`

Remaining extensions observed before the run:
- `benchmark-profiles`
- `browser`
- `browser-extract-retention`
- `checkpoint`
- `evidence`
- `evidence-compact`
- `extensions`
- `extra-tools`
- `finalize-warn`
- `hello`
- `llama-cpp-provider`
- `permission-gate`
- `shell-session`
- `tool-gating`
- `turn-cap`

Model:
- `umich/qwen/qwen3.6-35b-a3b`

Dataset:
- `terminal-bench@2.0`

Agent:
- `benchmarks.harbor_adapter.little_coder_agent:LittleCoderAgent`

Endpoint:
- `http://vllm-qwen3-6-35b.tail31d5a5.ts.net:8000/v1`

Command:

```bash
harbor run \
  --dataset terminal-bench@2.0 \
  --agent-import-path benchmarks.harbor_adapter.little_coder_agent:LittleCoderAgent \
  --model umich/qwen/qwen3.6-35b-a3b \
  --jobs-dir benchmarks/harbor_runs/ablation_all_off \
  --n-concurrent 7 \
  --n-attempts 5
