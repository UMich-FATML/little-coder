# 10-Player Shapley: Qwen & Gemma Results

The baseline sub-harness is vanilla `pi` + INFRA, so INFRA is substrate and the game has M = 10 players over 34 coalitions.
Shapley values use exact constrained WLS (KernelSHAP, Lagrange closed form); 95% CIs from task bootstrap (2000 reps, all coalitions share the same 140 tasks).

## Setup
- **Benchmark**: Aider Polyglot, 140 Python tasks
- **Models**: Qwen3.6-35B-A3B, Gemma-4-26B-A4B-IT (via vLLM)
- **Players (10)**: Q (quality-monitor), W (write-guard), OP (output-parser), KS (knowledge-inject + skill-inject), TB (thinking-budget), CP (checkpoint), SS (shell-session), BR (browser), ET (extra-tools), EV (evidence + evidence-compact + browser-extract-retention)
- **Substrate (always-on)**: llama-cpp-provider, plus the six INFRA extensions
  (permission-gate, tool-gating, turn-cap, benchmark-profiles, hello,
  finalize-warn). INFRA implements the basic safeguards any agent is expected
  to carry, e.g. a cap on ReAct iterations, so the baseline sub-harness is
  vanilla `pi` + INFRA and INFRA is not a player.
- **Coalitions**: 34 per model (the INFRA-on subset)
- **Scale**: logit (empirical logit of pass rate)
- **Estimation**: exact constrained WLS; 95% CIs from task bootstrap (2000 reps)

## Coalition design (34 per model)

The full game has 2^10 = 1024 coalitions. We evaluate a deterministic subsample of 34, so the fitted values are the kernel-weighted projection onto these configurations (not an unbiased estimate of the full-game Shapley values). The families, with their exact member sets (verified against `coalition_defs` in `analyze_shapley_v3.py`):

- `baseline_empty`: the baseline coalition, all ten players off, substrate
  (including INFRA) on. This is the anchor.
- `grand_all10`: all ten players on.
- `addone_X` (10): {X} for each player X. With INFRA as substrate these are
  the true singletons of the subgame, so the coalition logit reflects phi_X
  alone.
- `loo_X` (10): grand minus player X.
- `pair_X_Y` (6): {X, Y} for (Q,W), (Q,CP), (Q,SS), (W,CP), (W,SS), (CP,SS).
- `lt2o_X_Y` (6): grand minus {X, Y} for the same six pairs.

All 34 occur in seventeen exactly complementary pairs: `baseline_empty`/`grand_all10`, the ten `addone_X`/`loo_X`, and the six
`pair_X_Y`/`lt2o_X_Y`. This is what the variance-reduction recommendation for KernelSHAP subsampling asks for.

**Note: out of scope**: twelve further configurations with INFRA switched off (`zero_ext`, the ten `noinfra_X`, and `loo_INFRA`) were also run. They are not coalitions of this game and are excluded from the fit. They remain useful as a
sensitivity check on the INFRA-as-substrate choice; see the endpoint section.

## Inference (se and 95% CI)

Standard errors and confidence intervals come from a bootstrap. All 34
coalitions are evaluated on the same 140 tasks, so their pass rates are
correlated; the bootstrap resamples at the task level to respect this. In
each of 2000 replicates we draw 140 tasks with replacement, recompute every
coalition's pass rate on the resampled set, and rerun the full pipeline
(empirical logit, then exact constrained WLS) to obtain one set of 10 Shapley
values. Both models use the same task resample within each replicate, so the
draws of v_Qwen and v_Gemma are coupled and their difference can be tested
directly. The reported **se** is the standard deviation of a feature's 2000
bootstrap values; the **95% CI** is their 2.5th and 97.5th percentiles, i.e.
**pointwise**, with no multiplicity correction. 

## Endpoints

| Configuration | Qwen | Gemma |
|---|---|---|
| `zero_ext` (INFRA off, out of scope) | 130/140 | 118/140 |
| `baseline_empty` (anchor) | 133/140 | 111/140 |
| `grand_all10` | 130/140 | 102/140 |
| **Sum phi = v(grand) - v(baseline)** | **-0.359** | **-0.350** |

Both models lose almost the same log-odds from the optional suite despite
differing by 22 tasks at the baseline. INFRA itself moves them in opposite
directions: +3 tasks for Qwen, -7 for Gemma.

## KernelSHAP Shapley values (INFRA anchor, M = 10, 34 coalitions)


### Qwen3.6-35B-A3B
anchor 133/140, grand 130/140, total -0.3592

| Player | phi | se | pointwise 95% CI |
|---|---|---|---|
| Q | +0.263 | 0.151 | [+0.010, +0.610] | 
| KS | +0.082 | 0.094 | [-0.087, +0.289] | 
| ET | +0.023 | 0.157 | [-0.288, +0.328] | 
| EV | +0.016 | 0.168 | [-0.302, +0.363] | 
| W | -0.009 | 0.113 | [-0.244, +0.206] |
| BR | -0.119 | 0.184 | [-0.493, +0.229] |
| TB | -0.119 | 0.161 | [-0.456, +0.176] |
| OP | -0.119 | 0.159 | [-0.471, +0.151] |
| SS | -0.160 | 0.101 | [-0.381, +0.007] |
| CP | -0.218 | 0.146 | [-0.557, +0.016] |

R2: constrained +0.055 | anchor released +0.098 | separate OLS +0.491

The degeneracy of the old empty-set anchor is gone: the total is no longer
forced to zero. But the joint test does not reject a zero feature vector, so
Qwen still carries no resolvable per-player signal on this benchmark. Its
baseline is seven tasks from the ceiling.

### Gemma-4-26B-A4B-IT
anchor 111/140, grand 102/140, total -0.3504

| Player | phi | se | pointwise 95% CI | 
|---|---|---|---|
| Q | +0.164 | 0.085 | [+0.009, +0.340] | 
| EV | +0.080 | 0.085 | [-0.090, +0.250] |
| TB | +0.054 | 0.083 | [-0.110, +0.220] |
| BR | +0.006 | 0.080 | [-0.161, +0.160] | 
| SS | -0.018 | 0.081 | [-0.173, +0.144] | 
| OP | -0.050 | 0.077 | [-0.200, +0.102] | 
| CP | -0.050 | 0.078 | [-0.208, +0.097] | 
| ET | -0.065 | 0.078 | [-0.220, +0.088] | 
| KS | -0.112 | 0.096 | [-0.308, +0.076] |
| W | -0.359 | 0.097 | [-0.572, -0.189] |

R2: constrained -0.773 | anchor released +0.675 | separate OLS +0.720

**W is the only player significant after multiplicity correction, on either model.** 

## Interaction delta_Qwen = v_Qwen - vbar

With J = 2, delta_Gemma = -delta_Qwen identically.

| Player | delta | se | 95% CI |
|---|---|---|---|
| W | +0.175 | 0.079 | [+0.030, +0.339] | 
| KS | +0.097 | 0.069 | [-0.028, +0.245] | 
| TB | -0.086 | 0.092 | [-0.272, +0.082] | 
| CP | -0.084 | 0.089 | [-0.283, +0.063] | 
| SS | -0.071 | 0.062 | [-0.205, +0.033] | 
| BR | -0.062 | 0.103 | [-0.266, +0.139] | 
| Q | +0.049 | 0.091 | [-0.111, +0.253] | 
| ET | +0.044 | 0.081 | [-0.108, +0.203] | 
| OP | -0.034 | 0.087 | [-0.215, +0.121] | 
| EV | -0.032 | 0.096 | [-0.220, +0.162] | 


## Goodness of fit

| | Qwen | Gemma |
|---|---|---|
| Constrained (the phi above) | +0.055 | -0.773 |
| Same phi, anchor released | +0.098 | +0.675 |
| Separate unweighted OLS, free intercept | +0.491 | +0.720 |


## Files
- `analyze_shapley_v3.py`: analysis script (constrained WLS, bootstrap CIs)
- `uv_reconstruction.py`: saturated-model decomposition and reconstruction
- `shapley_v3_results.json`: full numeric output
- `ablation_qwen_11player/`, `ablation_gemma_11player/`: per-task result files
  per model (46 configurations on disk; 34 enter the fit)
