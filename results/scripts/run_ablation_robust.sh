#!/usr/bin/env bash
set -euo pipefail

MODEL_KEY="${1:?Usage: $0 <qwen|gemma>}"

case "$MODEL_KEY" in
  qwen)  MODEL_ID="umich/qwen/qwen3.6-35b-a3b" ;;
  gemma) MODEL_ID="umich/gemma/gemma-3n-e4b"    ;;
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

ALL_PLAYERS=(Q W OP KS TB CP SS BR ET EV)

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

TOTAL=0
SKIPPED=0
COMPLETED=0
FAILED=0

kill_rpc() {
    echo "    [cleanup] killing all little-coder processes..."
    pkill -f 'little-coder' 2>/dev/null || true
    for i in $(seq 1 15); do
        if ! pgrep -f 'little-coder' >/dev/null 2>&1; then
            echo "    [cleanup] all little-coder processes dead after ${i}s"
            return 0
        fi
        sleep 1
    done
    echo "    [cleanup] force-killing remaining processes..."
    pkill -9 -f 'little-coder' 2>/dev/null || true
    sleep 2
}

start_rpc() {
    echo "    [rpc] starting little-coder RPC..."
    little-coder --model "$MODEL_ID" --mode rpc &
    RPC_PID=$!
    echo "    [rpc] PID=$RPC_PID, waiting 15s for ready..."
    sleep 15
    if kill -0 $RPC_PID 2>/dev/null; then
        echo "    [rpc] process alive, proceeding"
        return 0
    else
        echo "    [rpc] ERROR: RPC process died during startup"
        return 1
    fi
}

setup_coalition() {
    local label="$1"
    shift
    local on_players=("$@")

    rm -rf .pi/extensions/*
    cp -r .pi/extensions_backup/* .pi/extensions/

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
}

run_one() {
    local label="$1"
    shift
    local on_players=("$@")

    TOTAL=$((TOTAL + 1))
    local outfile="$RESULTS_DIR/polyglot_${label}.txt"

    if [[ -f "$outfile" ]] && [[ -s "$outfile" ]] && grep -q "passed\|failed\|Tests:" "$outfile" 2>/dev/null; then
        SKIPPED=$((SKIPPED + 1))
        echo ">>> [$TOTAL/34] SKIP $label (valid result exists: $(wc -c < "$outfile") bytes)"
        return 0
    fi

    rm -f "$outfile"

    echo ""
    echo "============================================"
    echo "  [$TOTAL/34] COALITION: $label"
    echo "  ON: ${on_players[*]:-"(none — baseline)"}"
    echo "  Time: $(date '+%H:%M:%S')"
    echo "============================================"

    setup_coalition "$label" "${on_players[@]}"

    kill_rpc
    if ! start_rpc; then
        echo ">>> FAILED to start RPC for $label, skipping"
        FAILED=$((FAILED + 1))
        return 0
    fi

    rm -f benchmarks/results_full_polyglot.json

    echo "    [bench] running Polyglot benchmark..."
    if python benchmarks/aider_polyglot.py \
        --language python \
        --model "$MODEL_ID" \
        --verbose \
        2>&1 | tee "$outfile"; then
        COMPLETED=$((COMPLETED + 1))
        echo ">>> DONE [$label] → $outfile ($(wc -c < "$outfile") bytes)"
    else
        FAILED=$((FAILED + 1))
        echo ">>> FAILED [$label] (benchmark returned non-zero)"
    fi

    kill_rpc
    echo "    [cleanup] pausing 3s before next coalition..."
    sleep 3
}

echo ""
echo "============================================"
echo "  11-Player Shapley Ablation (robust)"
echo "  Model: $MODEL_KEY ($MODEL_ID)"
echo "  Results: $RESULTS_DIR/"
echo "  Total coalitions: 34"
echo "  Start: $(date)"
echo "============================================"

kill_rpc

run_one "baseline_empty"
run_one "grand_all10"       Q W OP KS TB CP SS BR ET EV
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
run_one "pair_Q_W"          Q W
run_one "pair_Q_CP"         Q CP
run_one "pair_Q_SS"         Q SS
run_one "pair_W_CP"         W CP
run_one "pair_W_SS"         W SS
run_one "pair_CP_SS"        CP SS
run_one "lt2o_Q_W"          OP KS TB CP SS BR ET EV
run_one "lt2o_Q_CP"         W OP KS TB SS BR ET EV
run_one "lt2o_Q_SS"         W OP KS TB CP BR ET EV
run_one "lt2o_W_CP"         Q OP KS TB SS BR ET EV
run_one "lt2o_W_SS"         Q OP KS TB CP BR ET EV
run_one "lt2o_CP_SS"        Q W OP KS TB BR ET EV

echo ""
echo "============================================"
echo "  ALL DONE"
echo "  Completed: $COMPLETED  Skipped: $SKIPPED  Failed: $FAILED"
echo "  Results in: $RESULTS_DIR/"
echo "  End: $(date)"
echo "============================================"
