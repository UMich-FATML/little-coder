# 11-Player Shapley Ablation: Qwen & Gemma Results

## Setup

- **Benchmark**: Aider Polyglot, 140 Python tasks
- **Models**: Qwen3.6-35B-A3B, Gemma-4-26B-A4B-IT (via vLLM)
- **Players (11)**: Q (quality-monitor), W (write-guard), OP (output-parser), KS (knowledge-inject + skill-inject), TB (thinking-budget), CP (checkpoint), SS (shell-session), BR (browser), ET (extra-tools), EV (evidence + evidence-compact + browser-extract-retention), INFRA (permission-gate, tool-gating, turn-cap, benchmark-profiles, hello, finalize-warn)
- **Substrate (always-on)**: llama-cpp-provider
- **Coalitions**: 46 per model (34 INFRA-on + 12 INFRA-off)
- **Scale**: logit (log-odds of pass rate)

## KernelSHAP Shapley Values

### Qwen3.6-35B-A3B
- v(empty) = 130/140 = 92.9%, v(grand) = 125/140 = 89.3%
- Total gain: -0.445 logits / -3.57pp

| Rank | Player | phi (logit) | phi (pp) |
|------|--------|-------------|----------|
| 1 | SS | +0.249 | +1.31 |
| 2 | INFRA | +0.211 | +1.73 |
| 3 | CP | +0.149 | +0.87 |
| 4 | BR | +0.075 | +1.01 |
| 5 | Q | +0.051 | +0.23 |
| 6 | W | +0.030 | -0.06 |
| 7 | ET | -0.036 | -0.01 |
| 8 | KS | -0.074 | -0.65 |
| 9 | OP | -0.081 | -0.68 |
| 10 | EV | -0.213 | -1.66 |
| 11 | TB | -0.805 | -5.65 |

### Gemma-4-26B-A4B-IT
- v(empty) = 118/140 = 84.3%, v(grand) = 109/140 = 77.9%
- Total gain: -0.422 logits / -6.43pp

| Rank | Player | phi (logit) | phi (pp) |
|------|--------|-------------|----------|
| 1 | Q | +0.180 | +2.74 |
| 2 | BR | +0.119 | +1.90 |
| 3 | OP | +0.102 | +1.41 |
| 4 | TB | +0.038 | +0.32 |
| 5 | ET | -0.007 | -0.25 |
| 6 | CP | -0.011 | -0.08 |
| 7 | EV | -0.070 | -1.11 |
| 8 | KS | -0.072 | -1.15 |
| 9 | SS | -0.193 | -2.74 |
| 10 | INFRA | -0.221 | -3.22 |
| 11 | W | -0.289 | -4.23 |

### Key Cross-Model Differences

| Player | Qwen | Gemma | Delta | Note |
|--------|------|-------|-------|------|
| SS | +0.249 | -0.193 | +0.441 | Sign reversal |
| INFRA | +0.211 | -0.221 | +0.432 | Sign reversal |
| W | +0.030 | -0.289 | +0.319 | Sign reversal |
| TB | -0.805 | +0.038 | -0.842 | Sign reversal (TB issue: rerun needed) |
| Q | +0.051 | +0.180 | -0.129 | Both positive, Gemma relies more on Q |
| BR | +0.075 | +0.119 | -0.045 | Both positive, consistent |

## Regression Models (per-model, logit scale)

| Model | Qwen R2 | Qwen AdjR2 | Gemma R2 | Gemma AdjR2 |
|-------|---------|------------|----------|-------------|
| Additive (12 params) | 0.774 | 0.701 | 0.738 | 0.653 |

## Bilinear Model: u_i^T v_j

Cross-model regression (92 obs = 46 configs x 2 models):

| Model | Params | R2 | RMSE |
|-------|--------|-----|------|
| (A) mu_i + beta_j (additive) | 47 | 0.862 | 0.232 |
| (B) mu_i + lambda * u_i^T v_j (bilinear) | 47 | 0.458 | 0.461 |
| (C) saturated | 92 | 1.000 | 0.000 |



## Files

- `ablation_qwen_11player/`: 46 per-task result files for Qwen
- `ablation_gemma_11player/`: 46 per-task result files for Gemma
- `shapley_bilinear_results.json`: Combined Shapley values and bilinear model fit
