#!/usr/bin/env bash
set -euo pipefail
MODEL_KEY="${1:?Usage: $0 <qwen|gemma>}"
case "$MODEL_KEY" in
  qwen)  MODEL_ID="umich/qwen/qwen3.6-35b-a3b" ;;
  gemma) MODEL_ID="umich/google/gemma-4-26b-a4b-it" ;;
  *)     echo "Unknown model: $MODEL_KEY"; exit 1 ;;
esac
cd ~/little-coder
export PATH="$HOME/.local/bin:$PATH"
export LLAMACPP_API_KEY=noop
export LLAMACPP_BASE_URL=http://vllm.tail31d5a5.ts.net:8000/v1
export LITTLE_CODER_PERMISSION_MODE=accept-all
export LITTLE_CODER_MODELS_FILE=~/umich-models.json
RESULTS_DIR="benchmarks/ablation_${MODEL_KEY}_11player"
mkdir -p "$RESULTS_DIR"

ALL_TARGETS="Q W OP KS TB CP SS BR ET EV"
get_dirs() {
    case "$1" in
        Q)  echo "quality-monitor" ;;
        W)  echo "write-guard" ;;
        OP) echo "output-parser" ;;
        KS) echo "knowledge-inject skill-inject" ;;
        TB) echo "thinking-budget" ;;
        CP) echo "checkpoint" ;;
        SS) echo "shell-session" ;;
        BR) echo "browser" ;;
        ET) echo "extra-tools" ;;
        EV) echo "evidence evidence-compact browser-extract-retention" ;;
    esac
}
# INFRA dirs to remove when INFRA=off (llama-cpp-provider stays always-on)
INFRA_DIRS="permission-gate tool-gating turn-cap benchmark-profiles hello finalize-warn"

COALITION_COUNT=0
SKIP_COUNT=0

run_one() {
    local label="$1"
    local infra_on="$2"
    shift 2
    local on_players="$*"
    local outfile="$RESULTS_DIR/polyglot_${label}.txt"
    if [ -f "$outfile" ] && [ "$(grep -c "PASS\|FAIL" "$outfile" 2>/dev/null || echo 0)" -ge 140 ]; then
        SKIP_COUNT=$((SKIP_COUNT + 1))
        echo ">>> SKIP [$label] — result already exists"
        return 0
    fi
    COALITION_COUNT=$((COALITION_COUNT + 1))
    echo ""
    echo "============================================"
    echo "  COALITION $COALITION_COUNT: $label"
    echo "  INFRA: $infra_on"
    echo "  ON targets: ${on_players:-"(none)"}"
    echo "============================================"
    rm -rf .pi/extensions/*
    cp -r .pi/extensions_backup/* .pi/extensions/
    if [ "$infra_on" = "off" ]; then
        for d in $INFRA_DIRS; do
            rm -rf ".pi/extensions/$d"
        done
    fi
    for p in $ALL_TARGETS; do
        is_on=false
        for op in $on_players; do
            if [ "$p" = "$op" ]; then
                is_on=true
                break
            fi
        done
        if [ "$is_on" = "false" ]; then
            for d in $(get_dirs "$p"); do
                rm -rf ".pi/extensions/$d"
            done
        fi
    done
    echo ""
    echo "  Extensions on disk:"
    ls .pi/extensions/
    echo ""
    echo ">>> Go to Tab 1: Ctrl+C old RPC, then rerun:"
    echo "    little-coder --model $MODEL_ID --mode rpc"
    echo ""
    read -rp ">>> Press ENTER when RPC is ready... "
    rm -f benchmarks/results_full_polyglot.json
    echo ">>> Running Polyglot benchmark..."
    python benchmarks/aider_polyglot.py \
        --language python \
        --model "$MODEL_ID" \
        --verbose \
        2>&1 | tee "$outfile"
    echo ""
    echo ">>> DONE [$label] → $outfile"
}
echo "============================================"
echo "  INFRA-off supplement (11-player)"
echo "  Model: $MODEL_KEY ($MODEL_ID)"
echo "  INFRA = {permission-gate, tool-gating, turn-cap,"
echo "           benchmark-profiles, hello, finalize-warn}"
echo "  llama-cpp-provider = always-on (RPC dependency)"
echo "  Results: $RESULTS_DIR/"
echo "  Coalitions: 12"
echo "============================================"

run_one "zero_ext"      off
run_one "noinfra_Q"     off Q
run_one "noinfra_W"     off W
run_one "noinfra_OP"    off OP
run_one "noinfra_KS"    off KS
run_one "noinfra_TB"    off TB
run_one "noinfra_CP"    off CP
run_one "noinfra_SS"    off SS
run_one "noinfra_BR"    off BR
run_one "noinfra_ET"    off ET
run_one "noinfra_EV"    off EV
run_one "loo_INFRA"     off Q W OP KS TB CP SS BR ET EV

echo ""
echo "============================================"
echo "  DONE. Ran: $COALITION_COUNT  Skipped: $SKIP_COUNT"
echo "============================================"
