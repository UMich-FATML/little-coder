# 10-Player Shapley: Qwen & Gemma Results

The baseline sub-harness is vanilla `pi` + INFRA, so INFRA is substrate and the game has M = 10 players over 34 coalitions.
Shapley values use exact constrained WLS (KernelSHAP, Lagrange closed form); 95% CIs from task bootstrap (2000 reps, all coalitions share the same 140 tasks).

## Setup
- **Benchmark**: Aider Polyglot, 140 Python tasks
- **Models**: Qwen3.6-35B-A3B, Gemma-4-26B-A4B-IT (via vLLM)
- **Players (10)**: Q (quality-monitor), W (write-guard), OP (output-parser), KS (knowledge-inject + skill-inject), TB (thinking-budget), CP (checkpoint), SS (shell-session), BR (browser), ET (extra-tools), EV (evidence + evidence-compact + browser-extract-retention)
- **Substrate (always-on)**: llama-cpp-provider, plus the six INFRA extensions (permission-gate, tool-gating, turn-cap, benchmark-profiles, hello, finalize-warn). INFRA implements the basic safeguards any agent is expected to carry, e.g. a cap on ReAct iterations, so the baseline sub-harness is vanilla `pi` + INFRA and INFRA is not a player.
- **Coalitions**: 34 per model (the INFRA-on subset)
- **Scale**: logit (empirical logit of pass rate)
- **Estimation**: exact constrained WLS

## Coalition design (34 per model)

The full game has 2^10 = 1024 coalitions. We evaluate a deterministic subsample of 34, so the fitted values are the kernel-weighted projection onto these configurations (not an unbiased estimate of the full-game Shapley values). The families, with their exact member sets (verified against `coalition_defs` in `analyze_shapley_v3.py`):

- `baseline_empty`: the baseline coalition, all ten players off, INFRA on. (anchor)
- `grand_all10`: all ten players on.
- `addone_X` (10): {X} for each player X. With INFRA as substrate these are the true singletons of the subgame.
- `loo_X` (10): grand minus player X.
- `pair_X_Y` (6): {X, Y} for (Q,W), (Q,CP), (Q,SS), (W,CP), (W,SS), (CP,SS).
- `lt2o_X_Y` (6): grand minus {X, Y} for the same six pairs.

All 34 occur in seventeen complementary pairs: `baseline_empty`/`grand_all10`, the ten `addone_X`/`loo_X`, and the six
`pair_X_Y`/`lt2o_X_Y`. This is what the variance-reduction recommendation for KernelSHAP subsampling asks for.

**Note: out of scope**: twelve further configurations with INFRA switched off (`zero_ext`, the ten `noinfra_X`, and `loo_INFRA`) were also run. They are not coalitions of this game and are excluded from the fit.

## Inference (se and 95% CI)

All 34 coalitions are evaluated on the same 140 tasks, so their pass rates are correlated and the bootstrap resamples at the task level. In each of 2000 replicates we draw 140 tasks with replacement, recompute every coalition's pass rate on the resampled set, and rerun the full pipeline (empirical logit, then exact constrained WLS) to obtain one set of 10 Shapley values. Both models use the same task resample within each replicate, so the draws of v_Qwen and v_Gemma are coupled and their difference can be tested directly. The reported **se** is the standard deviation of a feature's 2000 bootstrap values; the **95% CI** is their 2.5th and 97.5th percentiles, i.e. **pointwise**, with no multiplicity correction. 

## Endpoints

| Configuration | Qwen | Gemma |
|---|---|---|
| `baseline_empty` (anchor) | 133/140 | 111/140 |
| `grand_all10` | 130/140 | 102/140 |
| **Sum phi = v(grand) - v(baseline)** | **-0.359** | **-0.350** |

Both models lose almost the same log-odds from the optional suite despite differing by 22 tasks at the baseline.

## Fitted feature values (kernel-weighted projection onto the 34 coalitions)

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

## Bilinear decomposition u_i^T v_j
 
This is the quantity that replaces alpha_i + gamma_ij in the saturated model. For each coalition i, u_i is the 0/1 indicator of the switched-on players and v_j is the model's fitted feature vector above. vbar is the two-model average and delta_Qwen = v_Qwen - vbar, so u_i^T vbar plays the role of the harness main effect and u_i^T delta_Qwen the role of the interaction. Prediction is beta_j + u_i^T v_j with beta_j = v_j(baseline); observed is the coalition's empirical logit. beta_Qwen = +2.879, beta_Gemma = +1.330.
 
| Coalition | u*vbar | u*delta_Qwen | beta_j+ui^Tvj (prediction) Qwen | observation Qwen | beta_j+ui^Tvj (prediction) Gemma | observation Gemma |
|---|---|---|---|---|---|---|
| `baseline_empty` | +0.000 | +0.000 | +2.879 | +2.879 | +1.330 | +1.330 |
| `grand_all10` | -0.355 | -0.005 | +2.519 | +2.520 | +0.980 | +0.979 |
| `addone_Q` | +0.214 | +0.049 | +3.142 | +3.030 | +1.494 | +1.771 |
| `addone_W` | -0.184 | +0.175 | +2.870 | +2.520 | +0.971 | +1.246 |
| `addone_OP` | -0.084 | -0.035 | +2.760 | +2.628 | +1.280 | +1.330 |
| `addone_KS` | -0.015 | +0.097 | +2.961 | +2.747 | +1.218 | +1.418 |
| `addone_TB` | -0.033 | -0.086 | +2.760 | +2.628 | +1.384 | +1.707 |
| `addone_CP` | -0.134 | -0.084 | +2.661 | +2.421 | +1.280 | +1.601 |
| `addone_SS` | -0.089 | -0.071 | +2.719 | +2.520 | +1.312 | +1.551 |
| `addone_BR` | -0.056 | -0.062 | +2.760 | +2.628 | +1.336 | +1.653 |
| `addone_ET` | -0.021 | +0.044 | +2.902 | +2.628 | +1.265 | +1.511 |
| `addone_EV` | +0.048 | -0.032 | +2.895 | +2.747 | +1.410 | +1.511 |
| `loo_Q` | -0.569 | -0.055 | +2.256 | +2.747 | +0.816 | +1.206 |
| `loo_W` | -0.171 | -0.180 | +2.528 | +2.628 | +1.339 | +1.715 |
| `loo_OP` | -0.270 | +0.029 | +2.638 | +3.030 | +1.030 | +1.206 |
| `loo_KS` | -0.340 | -0.102 | +2.437 | +2.747 | +1.092 | +1.418 |
| `loo_TB` | -0.322 | +0.081 | +2.638 | +3.030 | +0.926 | +1.330 |
| `loo_CP` | -0.221 | +0.079 | +2.737 | +3.030 | +1.030 | +1.418 |
| `loo_SS` | -0.266 | +0.066 | +2.679 | +3.030 | +0.998 | +1.330 |
| `loo_BR` | -0.298 | +0.057 | +2.638 | +3.030 | +0.974 | +1.373 |
| `loo_ET` | -0.334 | -0.049 | +2.496 | +2.747 | +1.045 | +1.418 |
| `loo_EV` | -0.403 | +0.027 | +2.503 | +2.879 | +0.900 | +1.127 |
| `pair_Q_W` | +0.030 | +0.224 | +3.133 | +3.671 | +1.135 | +1.418 |
| `pair_Q_CP` | +0.080 | -0.035 | +2.924 | +2.879 | +1.444 | +1.661 |
| `pair_Q_SS` | +0.125 | -0.022 | +2.982 | +3.412 | +1.476 | +1.661 |
| `pair_W_CP` | -0.318 | +0.091 | +2.652 | +2.330 | +0.921 | +1.127 |
| `pair_W_SS` | -0.273 | +0.104 | +2.710 | +2.520 | +0.953 | +1.052 |
| `pair_CP_SS` | -0.223 | -0.155 | +2.501 | +2.520 | +1.262 | +1.829 |
| `lt2o_Q_W` | -0.385 | -0.229 | +2.265 | +2.879 | +1.175 | +1.418 |
| `lt2o_Q_CP` | -0.434 | +0.029 | +2.474 | +2.421 | +0.866 | +1.206 |
| `lt2o_Q_SS` | -0.479 | +0.017 | +2.416 | +2.166 | +0.834 | +1.052 |
| `lt2o_W_CP` | -0.037 | -0.096 | +2.746 | +2.421 | +1.389 | +1.771 |
| `lt2o_W_SS` | -0.082 | -0.109 | +2.688 | +3.030 | +1.357 | +1.511 |
| `lt2o_CP_SS` | -0.132 | +0.150 | +2.897 | +2.879 | +1.048 | +1.463 |

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

## Files
 
- `analyze_shapley_v3.py`: analysis script (constrained WLS, bootstrap CIs)
- `uv_reconstruction.py`: bilinear decomposition and reconstruction
- `shapley_v3_results.json`: full numeric output
- `ablation_qwen_11player_clean/`, `ablation_gemma_11player_clean/`: per-task result files, 46 configurations on disk, 34 entering the fit
