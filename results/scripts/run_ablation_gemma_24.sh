#!/usr/bin/env bash
set -euo pipefail
MODEL_ID="umich/google/gemma-4-26b-a4b-it"
cd ~/little-coder
export PATH="$HOME/.local/bin:$PATH"
export LLAMACPP_API_KEY=noop
export LLAMACPP_BASE_URL=http://vllm.tail31d5a5.ts.net:8000/v1
export LITTLE_CODER_PERMISSION_MODE=accept-all
export LITTLE_CODER_MODELS_FILE=~/umich-models.json
RESULTS_DIR="benchmarks/ablation_gemma_11player"
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
    echo "  INFRA: $infra_on | ON: ${on_players:-"(none)"}"
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
            if [ "$p" = "$op" ]; then is_on=true; break; fi
        done
        if [ "$is_on" = "false" ]; then
            for d in $(get_dirs "$p"); do
                rm -rf ".pi/extensions/$d"
            done
        fi
    done
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
echo "  Gemma 24-coalition priority run"
echo "  Results: $RESULTS_DIR/"
echo "============================================"

# Endpoints
run_one "zero_ext"        off
run_one "grand_all10"     on  Q W OP KS TB CP SS BR ET EV

# Size 1: INFRA-off + single feature (11)
run_one "baseline_empty"  on
run_one "noinfra_Q"       off Q
run_one "noinfra_W"       off W
run_one "noinfra_OP"      off OP
run_one "noinfra_KS"      off KS
run_one "noinfra_TB"      off TB
run_one "noinfra_CP"      off CP
run_one "noinfra_SS"      off SS
run_one "noinfra_BR"      off BR
run_one "noinfra_ET"      off ET
run_one "noinfra_EV"      off EV

# Size 10: leave-one-out (11)
run_one "loo_Q"           on  W OP KS TB CP SS BR ET EV
run_one "loo_W"           on  Q OP KS TB CP SS BR ET EV
run_one "loo_OP"          on  Q W KS TB CP SS BR ET EV
run_one "loo_KS"          on  Q W OP TB CP SS BR ET EV
run_one "loo_TB"          on  Q W OP KS CP SS BR ET EV
run_one "loo_CP"          on  Q W OP KS TB SS BR ET EV
run_one "loo_SS"          on  Q W OP KS TB CP BR ET EV
run_one "loo_BR"          on  Q W OP KS TB CP SS ET EV
run_one "loo_ET"          on  Q W OP KS TB CP SS BR EV
run_one "loo_EV"          on  Q W OP KS TB CP SS BR ET
run_one "loo_INFRA"       off Q W OP KS TB CP SS BR ET EV

echo ""
echo "============================================"
echo "  DONE. Ran: $COALITION_COUNT  Skipped: $SKIP_COUNT"
echo "============================================"
