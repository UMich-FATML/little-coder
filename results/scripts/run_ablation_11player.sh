#!/usr/bin/env bash
# ============================================================
# 11-Player Shapley Ablation: 34 coalitions × 1 model
# Usage:
#   bash run_ablation_11player.sh qwen    # or gemma
# ============================================================
set -euo pipefail

MODEL_KEY="${1:?Usage: $0 <qwen|gemma>}"

case "$MODEL_KEY" in
  qwen)  MODEL_ID="umich/qwen/qwen3.6-35b-a3b" ;;
  gemma) MODEL_ID="umich/gemma/gemma-3n-e4b"    ;;  # ← adjust to real model string
  *)     echo "Unknown model: $MODEL_KEY"; exit 1 ;;
esac

cd ~/little-coder
git checkout benchmarks/aider_polyglot.py

export PATH="$HOME/.local/bin:$PATH"
export LLAMACPP_API_KEY=noop
export LLAMACPP_BASE_URL=http://vllm.tail31d5a5.ts.net:8000/v1
export LITTLE_CODER_PERMISSION_MODE=accept-all
export LITTLE_CODER_MODELS_FILE=~/umich-models.json

RESULTS_DIR="benchmarks/ablation_${MODEL_KEY}_11player"
mkdir -p "$RESULTS_DIR"

# ── Directory mapping ──
# Players → extension dirs to REMOVE when that player is OFF
# INFRA dirs are NEVER removed (always on):
#   llama-cpp-provider permission-gate tool-gating turn-cap
#   benchmark-profiles hello finalize-warn browser-extract-retention extensions

declare -A PLAYER_DIRS
PLAYER_DIRS[Q]="quality-monitor"
PLAYER_DIRS[W]="write-guard"
PLAYER_DIRS[OP]="output-parser"
PLAYER_DIRS[KS]="knowledge-inject skill-inject"
PLAYER_DIRS[TB]="thinking-budget"
PLAYER_DIRS[CP]="checkpoint"
PLAYER_DIRS[SS]="shell-session"
PLAYER_DIRS[BR]="browser"
PLAYER_DIRS[ET]="extra-tools"
PLAYER_DIRS[EV]="evidence evidence-compact"

ALL_PLAYERS=(Q W OP KS TB CP SS BR ET EV)

# ── Helper: set up extensions for a coalition ──
setup_coalition() {
    local label="$1"
    shift
    local -a on_players=("$@")  # players that should be ON

    # Reset: copy everything back
    rm -rf .pi/extensions/*
    cp -r .pi/extensions_backup/* .pi/extensions/

    # Compute OFF players = ALL minus ON
    for p in "${ALL_PLAYERS[@]}"; do
        local is_on=false
        for op in "${on_players[@]}"; do
            [[ "$p" == "$op" ]] && is_on=true && break
        done
        if ! $is_on; then
            for d in ${PLAYER_DIRS[$p]}; do
                rm -rf ".pi/extensions/$d"
            done
        fi
    done

    echo "=== Coalition: $label ==="
    echo "    ON:  ${on_players[*]:-"(none)"}"
    echo "    Extensions remaining:"
    ls .pi/extensions/
    echo ""
}

# ── Helper: run one coalition ──
run_one() {
    local label="$1"
    shift
    local -a on_players=("$@")

    local outfile="$RESULTS_DIR/polyglot_${label}.txt"

    # Skip if already completed
    if [[ -f "$outfile" ]] && grep -q "passed\|failed\|Tests:" "$outfile" 2>/dev/null; then
        echo ">>> SKIP $label (result exists)"
        return 0
    fi

    setup_coalition "$label" "${on_players[@]}"

    rm -f benchmarks/results_full_polyglot.json

    # Start little-coder RPC in background
    little-coder --model "$MODEL_ID" --mode rpc &
    local rpc_pid=$!
    sleep 5  # wait for RPC to be ready

    python benchmarks/aider_polyglot.py \
        --language python \
        --model "$MODEL_ID" \
        --verbose \
        2>&1 | tee "$outfile"

    # Clean up RPC
    kill $rpc_pid 2>/dev/null || true
    wait $rpc_pid 2>/dev/null || true

    echo ">>> DONE $label → $outfile"
    echo ""
}

# ============================================================
# 34 COALITIONS
# ============================================================

# ── Tier 0: endpoints ──
run_one "baseline_empty"
run_one "grand_all10"       Q W OP KS TB CP SS BR ET EV

# ── Tier 1: add-one (size=1, highest Shapley kernel weight) ──
run_one "addone_Q"          Q
run_one "addone_W"          W
run_one "addone_OP"         OP
run_one "addone_KS"         KS
run_one "addone_TB"         TB
run_one "addone_CP"         CP
run_one "addone_SS"         SS
run_one "addone_BR"         BR
run_one "addone_ET"         ET
run_one "addone_EV"         EV

# ── Tier 1: leave-one-out (size=9, highest Shapley kernel weight) ──
run_one "loo_Q"             W OP KS TB CP SS BR ET EV
run_one "loo_W"             Q OP KS TB CP SS BR ET EV
run_one "loo_OP"            Q W KS TB CP SS BR ET EV
run_one "loo_KS"            Q W OP TB CP SS BR ET EV
run_one "loo_TB"            Q W OP KS CP SS BR ET EV
run_one "loo_CP"            Q W OP KS TB SS BR ET EV
run_one "loo_SS"            Q W OP KS TB CP BR ET EV
run_one "loo_BR"            Q W OP KS TB CP SS ET EV
run_one "loo_ET"            Q W OP KS TB CP SS BR EV
run_one "loo_EV"            Q W OP KS TB CP SS BR ET

# ── Tier 2: pairwise for focus features {Q,W,CP,SS} (size=2) ──
run_one "pair_Q_W"          Q W
run_one "pair_Q_CP"         Q CP
run_one "pair_Q_SS"         Q SS
run_one "pair_W_CP"         W CP
run_one "pair_W_SS"         W SS
run_one "pair_CP_SS"        CP SS

# ── Tier 2: symmetric leave-two-out (size=8) ──
run_one "lt2o_Q_W"          OP KS TB CP SS BR ET EV
run_one "lt2o_Q_CP"         W OP KS TB SS BR ET EV
run_one "lt2o_Q_SS"         W OP KS TB CP BR ET EV
run_one "lt2o_W_CP"         Q OP KS TB SS BR ET EV
run_one "lt2o_W_SS"         Q OP KS TB CP BR ET EV
run_one "lt2o_CP_SS"        Q W OP KS TB BR ET EV

echo ""
echo "============================================"
echo "  ALL 34 COALITIONS COMPLETE for $MODEL_KEY"
echo "  Results in: $RESULTS_DIR/"
echo "============================================"
