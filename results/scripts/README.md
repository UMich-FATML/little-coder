# Extension-combo ablation scripts

Toggles little-coder's pi extensions into coalitions and runs Aider Polyglot,
for Shapley-value attribution of each extension's effect on pass rate.

## Files
- `run_ablation_interactive.sh` — main driver. 34 INFRA-on coalitions
  (empty, grand, add-one, leave-one-out, pairs, leave-two-out). Prompts for
  ENTER between coalitions.
- `run_ablation_auto.sh` — non-interactive version for unattended runs.
- `aider_polyglot.py` — benchmark runner. Separates "already processing"
  crashes (`status=error`) from real failures (`status=fail`); use this one.
- `analyze_shapley_v2.py` — reads the per-task result files, fits KernelSHAP
  (exact constrained WLS), task-bootstrap 95% CIs, and a nested test of
  whether feature value is model-agnostic.
- `RPC_NOTE.md` — why the manual RPC-restart step is vestigial.

## Before running (edit these, they are hard-coded to our setup)
1. `cd ~/little-coder` path at the top of the script.
2. `LLAMACPP_BASE_URL` — your vLLM endpoint.
3. `LITTLE_CODER_MODELS_FILE` and the `MODEL_ID` values in the `case` block.
4. Create the extension backup the driver restores from, or the first
   coalition will wipe `.pi/extensions` with nothing to restore:
   ```
   cp -r .pi/extensions .pi/extensions_backup
   ```

## Run
```
bash run_ablation_interactive.sh <qwen|gemma>
```
Skips coalitions whose result file already has PASS/FAIL lines, so it is safe
to stop and resume. Results go to `benchmarks/ablation_<model>_11player/`.
Each result file has 140 detail lines plus a JSON dump; the analysis script
reads the detail lines.

## Notes
- The manual "restart RPC then press ENTER" step can be answered with ENTER
  directly: `aider_polyglot.py` spawns its own PiRpc per exercise and
  re-reads `.pi/extensions` each time, so toggling takes effect purely
  through the on-disk directory (see `RPC_NOTE.md`).
- This driver covers only the 34 INFRA-on coalitions. The 12 INFRA-off ones
  (the 10 `noinfra_*`, `loo_INFRA`, `zero_ext`) were run separately with the
  same toggling logic, deleting the INFRA group as well.
