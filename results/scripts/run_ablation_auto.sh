#!/usr/bin/env bash
# Non-interactive Shapley ablation driver — gemma, 11-player, Python Polyglot.
#
# Modeled on results/scripts/run_ablation_interactive.sh (same 34 coalitions,
# same extension toggling, same benchmark invocation), with the manual RPC
# restart replaced by automated process management, plus per-coalition output
# verification, one retry, and a manifest.
#
# NOTE: benchmarks/aider_polyglot.py spawns its own `pi --mode rpc` per
# exercise via rpc_client.PiRpc and never talks to an external RPC process.
# The background RPC started here (START_RPC=1) only mirrors the manual
# terminal step of the interactive workflow; set START_RPC=0 to skip it.
set -uo pipefail

MODEL_ID="umich/google/gemma-4-26b-a4b-it"

cd "$HOME/little-coder"

# anaconda3 first: the interactive runs executed in a conda-activated
# terminal, so `python3 -m pytest` (the per-exercise test runner) resolved to
# anaconda's python. Without this, python3 hits Homebrew 3.14 which has no
# pytest and every task scores FAIL (observed: pair_Q_CP 0/140, 2026-07-06).
export PATH="$HOME/anaconda3/bin:$HOME/.local/bin:$PATH"
export LLAMACPP_API_KEY=noop
export LLAMACPP_BASE_URL=http://vllm.tail31d5a5.ts.net:8000/v1
export LITTLE_CODER_PERMISSION_MODE=accept-all
export LITTLE_CODER_MODELS_FILE=~/umich-models.json

RESULTS_DIR="benchmarks/ablation_gemma_11player"
MANIFEST="$RESULTS_DIR/manifest.txt"
LOG_DIR="${ABLATION_LOG_DIR:-$HOME/little-coder/benchmarks/ablation_auto_logs}"
START_RPC="${START_RPC:-0}"
EXPECTED_TASKS=140

mkdir -p "$RESULTS_DIR" "$LOG_DIR"

if [ ! -d .pi/extensions_backup ]; then
    echo "FATAL: .pi/extensions_backup missing — refusing to run." >&2
    exit 1
fi

# Preflight: the vLLM endpoint must be reachable before touching anything.
if ! curl -s --max-time 20 "$LLAMACPP_BASE_URL/models" > /dev/null; then
    echo "FATAL: LLM endpoint unreachable at $LLAMACPP_BASE_URL/models — stopping." >&2
    exit 3
fi
echo "Preflight OK: $LLAMACPP_BASE_URL/models reachable"

if ! python3 -m pytest --version > /dev/null 2>&1; then
    echo "FATAL: python3 ($(which python3)) has no pytest — test runner would fail every task. Stopping." >&2
    exit 3
fi
echo "Preflight OK: pytest available via $(which python3)"

ALL_PLAYERS="Q W OP KS TB CP SS BR ET EV"

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

count_passfail() { local c; c=$(grep -cE '\] (PASS|FAIL) ' "$1" 2>/dev/null || true); echo "${c:-0}"; }
count_pass()     { local c; c=$(grep -cE '\] PASS ' "$1" 2>/dev/null || true); echo "${c:-0}"; }
count_already()  { local c; c=$(grep -c 'Agent is already processing' "$1" 2>/dev/null || true); echo "${c:-0}"; }

cleanup_procs() {
    # Kill any RPC (ours or leaked per-exercise pi children) + leaky extension
    # processes (browser/shell-session are suspected of leaking across tasks).
    pkill -f "mode rpc" 2>/dev/null || true
    pkill -f "tail -f /dev/null" 2>/dev/null || true
    pkill -f chromium 2>/dev/null || true
    pkill -f playwright 2>/dev/null || true
    tmux kill-server 2>/dev/null || true
    sleep 2
}

RPC_PID=""
start_rpc() {
    local label="$1"
    local rpclog="$LOG_DIR/rpc_${label}.log"
    : > "$rpclog"
    # tail -f keeps the RPC's stdin open (it exits on stdin EOF).
    tail -f /dev/null | little-coder --no-update-check --model "$MODEL_ID" --mode rpc \
        > "$rpclog" 2>&1 &
    RPC_PID=$!
    # Readiness: the scaffold prints a "little-coder scaffold loaded" notify
    # line on stdout shortly after boot. Wait up to 30s for it, then fall
    # back to alive-check.
    local waited=0
    while [ "$waited" -lt 30 ]; do
        if grep -q "scaffold loaded" "$rpclog" 2>/dev/null; then
            echo "    RPC ready (pid $RPC_PID, ${waited}s)"
            return 0
        fi
        if ! kill -0 "$RPC_PID" 2>/dev/null; then
            echo "    RPC process died during startup — see $rpclog" >&2
            return 1
        fi
        sleep 1
        waited=$((waited + 1))
    done
    if kill -0 "$RPC_PID" 2>/dev/null; then
        echo "    RPC alive after ${waited}s (no readiness line seen — proceeding)"
        return 0
    fi
    echo "    RPC process died — see $rpclog" >&2
    return 1
}

setup_extensions() {
    local on_players="$1"
    rm -rf .pi/extensions/*
    cp -r .pi/extensions_backup/* .pi/extensions/
    for p in $ALL_PLAYERS; do
        local is_on=false
        for op in $on_players; do
            [ "$p" = "$op" ] && { is_on=true; break; }
        done
        if [ "$is_on" = "false" ]; then
            for d in $(get_dirs "$p"); do
                rm -rf ".pi/extensions/$d"
            done
        fi
    done
}

COALITION_COUNT=0
SKIP_COUNT=0

run_one() {
    local label="$1"
    shift
    local on_players="$*"
    local outfile="$RESULTS_DIR/polyglot_${label}.txt"

    # Skip only if complete AND clean; delete incomplete leftovers.
    if [ -f "$outfile" ]; then
        local pf ap
        pf=$(count_passfail "$outfile")
        ap=$(count_already "$outfile")
        if [ "$pf" -eq "$EXPECTED_TASKS" ] && [ "$ap" -eq 0 ]; then
            SKIP_COUNT=$((SKIP_COUNT + 1))
            echo ">>> SKIP [$label] — complete ($pf/$EXPECTED_TASKS)"
            return 0
        fi
        echo ">>> [$label] existing file incomplete (passfail=$pf already=$ap) — deleting and rerunning"
        rm -f "$outfile"
    fi

    COALITION_COUNT=$((COALITION_COUNT + 1))

    local attempt
    for attempt in 1 2; do
        echo ""
        echo "============================================"
        echo "  COALITION: $label  (attempt $attempt)"
        echo "  ON players: ${on_players:-"(none — baseline)"}"
        echo "  $(date '+%Y-%m-%d %H:%M:%S')"
        echo "============================================"

        cleanup_procs
        setup_extensions "$on_players"
        echo "  Extensions on disk:"
        ls .pi/extensions/

        local rpclog="none"
        if [ "$START_RPC" = "1" ]; then
            if ! start_rpc "$label"; then
                echo ">>> [$label] attempt $attempt: RPC failed to start"
                continue
            fi
            rpclog="$LOG_DIR/rpc_${label}.log"
        fi

        rm -f benchmarks/results_full_polyglot.json

        local t0 t1 mins start_ts end_ts
        start_ts=$(date '+%Y-%m-%dT%H:%M:%S')
        t0=$(date +%s)
        python benchmarks/aider_polyglot.py \
            --language python \
            --model "$MODEL_ID" \
            --verbose \
            2>&1 | tee "$outfile"
        t1=$(date +%s)
        end_ts=$(date '+%Y-%m-%dT%H:%M:%S')
        mins=$(( (t1 - t0) / 60 ))

        local pf pass ap
        pf=$(count_passfail "$outfile")
        pass=$(count_pass "$outfile")
        ap=$(count_already "$outfile")

        if [ "$pf" -eq "$EXPECTED_TASKS" ] && [ "$ap" -eq 0 ]; then
            echo "$label  start=$start_ts  end=$end_ts  pass=$pass/$EXPECTED_TASKS  runtime=${mins}m  rpclog=$rpclog" >> "$MANIFEST"
            echo ">>> SUMMARY [$label] pass=$pass/$EXPECTED_TASKS runtime=${mins}m attempt=$attempt"

            # Soft checks — warn loudly, never abort.
            if [ "$pass" -lt 100 ]; then
                echo "!!! WARNING [$label]: LOW PASS COUNT $pass/$EXPECTED_TASKS (<100) !!!"
            fi
            local anom_count
            anom_count=$(grep -cE 'Traceback|ERROR|[Tt]imeout|timed out' "$outfile" || true)
            anom_count="${anom_count:-0}"
            if [ "$anom_count" -gt 0 ]; then
                echo "!!! WARNING [$label]: $anom_count anomaly line(s) (Traceback/ERROR/timeout) — first 10:"
                grep -nE 'Traceback|ERROR|[Tt]imeout|timed out' "$outfile" | head -10
            fi
            return 0
        fi

        echo ">>> VERIFY FAILED [$label] attempt $attempt: passfail=$pf (want $EXPECTED_TASKS), already_processing=$ap — deleting output"
        rm -f "$outfile"
        cleanup_procs
    done

    echo ""
    echo "############################################"
    echo "  STOPPING: [$label] failed verification twice."
    echo "  Human attention required."
    echo "############################################"
    echo "$label  $(date '+%Y-%m-%dT%H:%M:%S')  FAILED_TWICE — driver stopped" >> "$MANIFEST"
    exit 2
}

echo "============================================"
echo "  11-Player Shapley Ablation (AUTO)"
echo "  Model: $MODEL_ID"
echo "  Results: $RESULTS_DIR/   RPC logs: $LOG_DIR/"
echo "  Started: $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================"

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

cleanup_procs

echo ""
echo "============================================"
echo "  ALL DONE. Ran: $COALITION_COUNT  Skipped: $SKIP_COUNT"
echo "  Finished: $(date '+%Y-%m-%d %H:%M:%S')"
echo "  Results in: $RESULTS_DIR/"
echo "============================================"
