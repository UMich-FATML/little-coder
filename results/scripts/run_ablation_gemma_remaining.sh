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
COALITION_COUNT=0
SKIP_COUNT=0
run_one() {
    local label="$1"
    shift
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
    echo "  ON: INFRA + ${on_players:-"(none)"}"
    echo "============================================"
    rm -rf .pi/extensions/*
    cp -r .pi/extensions_backup/* .pi/extensions/
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
echo "  Gemma remaining: 24 coalitions"
echo "  (7 loo re-runs + 17 new)"
echo "  Results: $RESULTS_DIR/"
echo "============================================"

# 7 loo re-runs (bad files already deleted)
run_one "loo_BR"      Q W OP KS TB CP SS ET EV
run_one "loo_CP"      Q W OP KS TB SS BR ET EV
run_one "loo_ET"      Q W OP KS TB CP SS BR EV
run_one "loo_KS"      Q W OP TB CP SS BR ET EV
run_one "loo_OP"      Q W KS TB CP SS BR ET EV
run_one "loo_SS"      Q W OP KS TB CP BR ET EV
run_one "loo_TB"      Q W OP KS CP SS BR ET EV

# 10 addone (INFRA + single feature)
run_one "addone_CP"   CP
run_one "addone_SS"   SS
run_one "addone_BR"   BR
run_one "addone_ET"   ET
run_one "addone_EV"   EV

# 6 pairwise {Q,W,CP,SS}
run_one "pair_Q_W"    Q W
run_one "pair_Q_CP"   Q CP
run_one "pair_Q_SS"   Q SS
run_one "pair_W_CP"   W CP
run_one "pair_W_SS"   W SS
run_one "pair_CP_SS"  CP SS

# 6 leave-two-out {Q,W,CP,SS}
run_one "lt2o_Q_W"    W OP KS TB CP SS BR ET EV
run_one "lt2o_Q_CP"   W OP KS TB SS BR ET EV
run_one "lt2o_Q_SS"   W OP KS TB CP BR ET EV
run_one "lt2o_W_CP"   Q OP KS TB SS BR ET EV
run_one "lt2o_W_SS"   Q OP KS TB CP BR ET EV
run_one "lt2o_CP_SS"  Q W OP KS TB BR ET EV

echo ""
echo "============================================"
echo "  DONE. Ran: $COALITION_COUNT  Skipped: $SKIP_COUNT"
echo "============================================"
