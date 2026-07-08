# 11-Player Shapley Ablation: Qwen & Gemma Results 

All 46 coalitions per model re-run under the corrected client with zero
crashes. Shapley values use exact constrained WLS (KernelSHAP, Lagrange
closed form); 95% CIs from task bootstrap (2000 reps, all coalitions share
the same 140 tasks). Cross-model comparison uses a nested Wald test.

## Setup
- **Benchmark**: Aider Polyglot, 140 Python tasks
- **Models**: Qwen3.6-35B-A3B, Gemma-4-26B-A4B-IT (via vLLM)
- **Players (11)**: Q (quality-monitor), W (write-guard), OP (output-parser), KS (knowledge-inject + skill-inject), TB (thinking-budget), CP (checkpoint), SS (shell-session), BR (browser), ET (extra-tools), EV (evidence + evidence-compact + browser-extract-retention), INFRA (permission-gate, tool-gating, turn-cap, benchmark-profiles, hello, finalize-warn)
- **Substrate (always-on)**: llama-cpp-provider
- **Coalitions**: 46 per model (34 INFRA-on + 12 INFRA-off)
- **Scale**: logit (empirical logit of pass rate)
- **Estimation**: exact constrained WLS; 95% CIs from task bootstrap (2000 reps)
- ## Inference (se and 95% CI)

Standard errors and confidence intervals come from a task bootstrap. All 46
coalitions are evaluated on the same 140 tasks, so their pass rates are
correlated; the bootstrap resamples at the task level to respect this. In
each of 2000 replicates we draw 140 tasks with replacement, recompute every
coalition's pass rate on the resampled set, and rerun the full pipeline
(empirical logit, then exact constrained WLS) to obtain one set of 11 Shapley
values. The reported se is the standard deviation of a feature's 2000
bootstrap values; the 95% CI is their 2.5th and 97.5th percentiles. A feature
is marked significant (*) when its 95% CI excludes zero. Cross-model deltas
(v_Qwen - v_Gemma) use the same resampled task set for both models in each
replicate, so their CIs are computed jointly.
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

## Cross-Model Comparison (model-agnostic test)

Nested test: shared feature vector (Model 0) vs per-model vectors (Model 1).
Joint Wald on delta = v_Qwen - v_Gemma.

- Weighted RSS: Model 0 = 50.75, Model 1 = 32.93
- chi2(11) = 40.93, p < 0.0001 (reject shared-vector model)
- Only INFRA and W have a cross-model delta whose CI excludes zero

| Player | vbar | v_Qwen | v_Gemma | delta | 95% CI (delta) | sig |
|--------|------|--------|---------|-------|----------------|-----|
| INFRA | -0.172 | +0.066 | -0.284 | +0.351 | [+0.176, +0.563] | * |
| W | -0.264 | -0.021 | -0.351 | +0.331 | [+0.120, +0.538] | * |
| KS | -0.045 | +0.063 | -0.089 | +0.152 | [-0.108, +0.383] |  |
| Q | +0.223 | +0.345 | +0.195 | +0.149 | [-0.096, +0.348] |  |
| TB | +0.013 | -0.090 | +0.057 | -0.147 | [-0.431, +0.142] |  |
| EV | +0.035 | -0.060 | +0.074 | -0.135 | [-0.459, +0.122] |  |
| BR | -0.005 | -0.050 | +0.008 | -0.059 | [-0.309, +0.199] |  |
| OP | -0.018 | -0.050 | -0.012 | -0.038 | [-0.291, +0.229] |  |
| SS | -0.005 | +0.016 | -0.021 | +0.037 | [-0.102, +0.194] |  |
| ET | -0.028 | -0.018 | -0.026 | +0.008 | [-0.200, +0.270] |  |
| CP | -0.051 | -0.063 | -0.059 | -0.004 | [-0.188, +0.178] |  |

## Files
- `analyze_shapley_v2.py`: analysis script (constrained WLS, bootstrap CIs, nested test)
- `shapley_v2_results.json`: full numeric output
- `ablation_qwen_11player/`, `ablation_gemma_11player/`: 46 per-task result files per model
