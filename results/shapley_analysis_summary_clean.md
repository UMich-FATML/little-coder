# 11-Player Shapley: Qwen & Gemma Results

All 46 coalitions per model re-run under the corrected client with zero
crashes. Shapley values use exact constrained WLS (KernelSHAP, Lagrange
closed form); 95% CIs from task bootstrap (2000 reps, all coalitions share
the same 140 tasks). Cross-model comparison uses the saturated model of
equation (3.1) and a nested Wald test.

## Setup
- **Benchmark**: Aider Polyglot, 140 Python tasks
- **Models**: Qwen3.6-35B-A3B, Gemma-4-26B-A4B-IT (via vLLM)
- **Players (11)**: Q (quality-monitor), W (write-guard), OP (output-parser), KS (knowledge-inject + skill-inject), TB (thinking-budget), CP (checkpoint), SS (shell-session), BR (browser), ET (extra-tools), EV (evidence + evidence-compact + browser-extract-retention), INFRA (permission-gate, tool-gating, turn-cap, benchmark-profiles, hello, finalize-warn)
- **Substrate (always-on)**: llama-cpp-provider
- **Coalitions**: 46 per model (34 INFRA-on + 12 INFRA-off)
- **Scale**: logit (empirical logit of pass rate)
- **Estimation**: exact constrained WLS; 95% CIs from task bootstrap (2000 reps)

## Inference (se and 95% CI)

Standard errors and confidence intervals come from a bootstrap. All 46
coalitions are evaluated on the same 140 tasks, so their pass rates are
correlated; the bootstrap resamples at the task level to respect this. In
each of 2000 replicates we draw 140 tasks with replacement, recompute every
coalition's pass rate on the resampled set, and rerun the full pipeline
(empirical logit, then exact constrained WLS) to obtain one set of 11 Shapley
values. The reported **se** is the standard deviation of a feature's 2000
bootstrap values; the **95% CI** is their 2.5th and 97.5th percentiles. A
feature is marked **sig** (`*`) when its 95% CI excludes zero, i.e. its effect
is distinguishable from zero given sampling noise.

## KernelSHAP Shapley Values

### Qwen3.6-35B-A3B
- v(empty) = 130/140 = 92.9%, v(grand) = 130/140 = 92.9%
- Total: +0.000 logits
- Additive R2 (coalition logits): 0.343
- No feature's 95% CI excludes zero (at ceiling; effects indistinguishable from noise)

| Rank | Player | phi (logit) | se | 95% CI | sig |
|------|--------|-------------|------|----------------|-----|
| 1 | INFRA | +0.282 | 0.183 | [-0.020, +0.694] |  |
| 2 | W | +0.109 | 0.146 | [-0.163, +0.411] |  |
| 3 | SS | +0.088 | 0.158 | [-0.181, +0.424] |  |
| 4 | Q | +0.084 | 0.137 | [-0.187, +0.345] |  |
| 5 | KS | +0.018 | 0.122 | [-0.240, +0.254] |  |
| 6 | CP | +0.018 | 0.147 | [-0.250, +0.302] |  |
| 7 | ET | -0.039 | 0.155 | [-0.354, +0.260] |  |
| 8 | OP | -0.122 | 0.162 | [-0.450, +0.181] |  |
| 9 | BR | -0.122 | 0.185 | [-0.517, +0.227] |  |
| 10 | EV | -0.142 | 0.128 | [-0.415, +0.072] |  |
| 11 | TB | -0.173 | 0.169 | [-0.534, +0.116] |  |

### Gemma-4-26B-A4B-IT
- v(empty) = 118/140 = 84.3%, v(grand) = 102/140 = 72.9%
- Total: -0.682 logits
- Additive R2 (coalition logits): 0.784
- Significant (CI excludes zero): W, INFRA, CP (all negative)

| Rank | Player | phi (logit) | se | 95% CI | sig |
|------|--------|-------------|------|----------------|-----|
| 1 | Q | +0.145 | 0.106 | [-0.061, +0.360] |  |
| 2 | EV | +0.115 | 0.090 | [-0.054, +0.293] |  |
| 3 | OP | +0.099 | 0.101 | [-0.089, +0.312] |  |
| 4 | TB | +0.058 | 0.088 | [-0.110, +0.240] |  |
| 5 | ET | +0.008 | 0.110 | [-0.203, +0.229] |  |
| 6 | BR | +0.004 | 0.102 | [-0.188, +0.210] |  |
| 7 | KS | -0.056 | 0.109 | [-0.263, +0.162] |  |
| 8 | SS | -0.152 | 0.086 | [-0.328, +0.014] |  |
| 9 | CP | -0.163 | 0.075 | [-0.315, -0.025] | * |
| 10 | INFRA | -0.315 | 0.093 | [-0.508, -0.150] | * |
| 11 | W | -0.425 | 0.091 | [-0.618, -0.268] | * |

## Saturated model and cross-model comparison

We plug the per-model Shapley vectors into the saturated model of equation
(3.1),

    g(E[Y_ij]) = mu + beta_j + u_i^T v_j,

where the row index i is a coalition and the column index j is a model.
Variable definitions:

- **u_i** in {0,1}^11: the coalition indicator, 1 for each switched-on player.
- **v_j** in R^11: model j's fitted Shapley vector (the tables above), read as
  how much model j relies on each feature.
- **u_i^T v_j** = sum of the Shapley values of the on-players; the per-model
  additive reconstruction of coalition i's effect relative to that model's
  empty coalition. This is the term that replaces the harness main effect plus
  interaction (alpha_i + gamma_ij) of equation (3.1).
- **beta_j**: model j's empty-coalition log-odds.
- **vbar** = (v_Qwen + v_Gemma)/2: the shared feature vector. u_i^T vbar is the
  harness main effect **alpha_i** (same across models).
- **delta_j** = v_j - vbar: model j's departure from the shared vector.
  u_i^T delta_j is the harness-LLM interaction **gamma_ij**. Since currently, two models are tested, then we have
  delta_Qwen = -delta_Gemma, so the two interactions are equal and opposite.

Thus u_i^T v_j = u_i^T vbar + u_i^T delta_j = alpha_i + gamma_ij, the folding
used in equation (3.1).

### Decomposition u_i^T v_j = alpha_i + gamma_ij (log-odds)

| Coalition | Model | alpha = u^T vbar | gamma = u^T delta_j | u^T v_j |
|-----------|-------|------------------|---------------------|---------|
| grand_all10 | Qwen | -0.341 | +0.341 | -0.000 |
| grand_all10 | Gemma | -0.341 | -0.341 | -0.682 |
| addone_W | Qwen | -0.175 | +0.566 | +0.391 |
| addone_W | Gemma | -0.175 | -0.566 | -0.740 |
| pair_Q_W | Qwen | -0.060 | +0.535 | +0.475 |
| pair_Q_W | Gemma | -0.060 | -0.535 | -0.596 |

The shared alpha is identical across models; the interaction gamma carries all
the cross-model difference (equal and opposite here because J = 2).

### Reconstruction: beta_j + u_i^T v_j vs observed coalition logit

For each coalition, **observed** is the empirical logit of the actual pass
rate measured in the run, and **pred** = beta_j + u_i^T v_j is the model's
reconstruction from the empty-coalition baseline plus the Shapley values of
the on-players.
Note: for Qwen, beta_j = +2.520; for Gemma, beta_j = +1.661.

| Model | Coalition | u^T v_j | pred = beta_j + u^T v_j | observed |
|-------|-----------|---------|-------------------------|----------|
| Qwen | zero_ext | +0.000 | +2.520 | +2.520 |
| Qwen | grand_all10 | -0.000 | +2.520 | +2.520 |
| Qwen | addone_Q | +0.366 | +2.886 | +3.030 |
| Qwen | addone_W | +0.391 | +2.911 | +2.520 |
| Qwen | loo_W | -0.109 | +2.411 | +2.628 |
| Gemma | zero_ext | +0.000 | +1.661 | +1.661 |
| Gemma | grand_all10 | -0.682 | +0.979 | +0.979 |
| Gemma | addone_Q | -0.170 | +1.491 | +1.771 |
| Gemma | addone_W | -0.740 | +0.921 | +1.246 |
| Gemma | loo_W | -0.257 | +1.405 | +1.715 |

Empty and grand coalitions reconstruct exactly by the efficiency constraint.
Intermediate coalitions carry residual (within-model feature interaction).

## Files
- `analyze_shapley_v2.py`: analysis script (constrained WLS, bootstrap CIs, nested test)
- `uv_reconstruction.py`: saturated-model decomposition and reconstruction
- `shapley_v2_results.json`: full numeric output
- `ablation_qwen_11player/`, `ablation_gemma_11player/`: 46 per-task result files per model
