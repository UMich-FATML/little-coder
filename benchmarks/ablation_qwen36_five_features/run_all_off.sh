#!/usr/bin/env bash
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

rm -rf .pi/extensions
cp -r .pi/extensions_backup .pi/extensions

rm -rf \
  .pi/extensions/write-guard \
  .pi/extensions/skill-inject \
  .pi/extensions/knowledge-inject \
  .pi/extensions/thinking-budget \
  .pi/extensions/output-parser \
  .pi/extensions/quality-monitor

docker network prune -f

harbor run \
  --dataset terminal-bench@2.0 \
  --agent-import-path benchmarks.harbor_adapter.little_coder_agent:LittleCoderAgent \
  --model umich/qwen/qwen3.6-35b-a3b \
  --jobs-dir benchmarks/harbor_runs/ablation_all_off \
  --n-concurrent 7 \
  --n-attempts 5
