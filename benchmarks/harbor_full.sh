#!/usr/bin/env bash
# Full Terminal-Bench 2.0 runner via harbor.
#
# Env:
#   TB_LITTLE_CODER_MODEL  — model override (default: openai-compat/qwen/qwen3.6-35b-a3b)
#   TB_HARBOR_ENV         — harbor environment (default: daytona)
#   TB_HARBOR_CONCURRENCY — concurrent trials (default: 32)
#   TB_HARBOR_JOB_NAME    — optional Harbor job name
#
# Requires:
#   - harbor installed (uv tool install harbor)
#   - DAYTONA_API_KEY when TB_HARBOR_ENV=daytona
#   - docker access when TB_HARBOR_ENV=docker
set -euo pipefail

MODEL="${TB_LITTLE_CODER_MODEL:-openai-compat/qwen/qwen3.6-35b-a3b}"
HB_ENV="${TB_HARBOR_ENV:-daytona}"
N_CONCURRENT="${TB_HARBOR_CONCURRENCY:-32}"
JOB_NAME="${TB_HARBOR_JOB_NAME:-}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$REPO_ROOT/benchmarks/harbor_runs"

export TB_LITTLE_CODER_MODEL="$MODEL"
export LLAMACPP_API_KEY="${LLAMACPP_API_KEY:-noop}"
export OLLAMA_API_KEY="${OLLAMA_API_KEY:-noop}"
export OPENAI_COMPAT_BASE_URL="${OPENAI_COMPAT_BASE_URL:-http://fs-mbz-gpu-257:8000/v1}"
export OPENAI_COMPAT_API_KEY="${OPENAI_COMPAT_API_KEY:-noop}"

echo "model:   $MODEL"
echo "dataset: terminal-bench@2.0"
echo "env:     $HB_ENV"
echo "output:  $OUT"
echo

HB_CMD=(harbor run
  --dataset terminal-bench@2.0
  --env "$HB_ENV"
  --agent-import-path benchmarks.harbor_adapter.little_coder_agent:LittleCoderAgent
  --model "$MODEL"
  --jobs-dir "$OUT"
  --n-attempts 1
  --n-concurrent "$N_CONCURRENT")

if [[ -n "$JOB_NAME" ]]; then
  HB_CMD+=(--job-name "$JOB_NAME")
fi

if [[ "$HB_ENV" == "docker" ]] && ! groups | grep -q '\bdocker\b'; then
  printf -v CMD_STR '%q ' "${HB_CMD[@]}"
  sg docker -c "cd '$REPO_ROOT' && $CMD_STR"
else
  cd "$REPO_ROOT" && "${HB_CMD[@]}"
fi
