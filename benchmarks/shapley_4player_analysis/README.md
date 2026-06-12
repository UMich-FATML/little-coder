# Shapley Value Analysis: 4-Player Feature Attribution
Exact Shapley value decomposition for little-coder's pi extension features
on Aider Polyglot (140 Python exercises, Qwen3.6-35B-A3B via vLLM).
## Players
| Player | Extension(s) | Mechanism |
|--------|-------------|-----------|
| Q | quality-monitor | Detects empty/hallucinated/looping output, forces correction |
| W | write-guard | Blocks overwrites of existing files |
| OP | output-parser | Repairs malformed tool calls (JSON/code fence) |
| KS | knowledge-inject + skill-inject | Injects task-solving hints (bundled due to code dependency) |
thinking-budget excluded due to race-condition crash ("Agent is already processing").
## Baseline
v(empty) = all-off (14 scaffold extensions, 0 target features) = 128/140 = 91.4%
## Results
All 16/16 coalitions observed. Exact Shapley values (no approximation):
| Feature | Singleton | Exact phi (raw) | Exact phi (logit) | % of total gain |
|---------|-----------|-----------------|-------------------|-----------------|
| Q | +7.14pp | +3.214pp | +0.7436 | 75.0% |
| W | +5.00pp | +0.952pp | +0.1191 | 22.2% |
| KS | +2.86pp | +0.119pp | -0.0464 | 2.8% |
| OP | +2.14pp | +0.000pp | -0.0774 | 0.0% |
| **Total** | 17.14pp | **4.286pp** | **+0.7390** | 100% |
Total gain = v(grand) - v(empty) = 95.7% - 91.4% = 4.3pp.
Singleton sum (17.1pp) >> total gain (4.3pp) due to strong negative interactions.
## Pairwise Interactions
All 6 pairs are negative (no synergy observed):
| Pair | gamma (raw, pp) | gamma (logit) |
|------|-----------------|---------------|
| Q x W | -7.9 | -2.0567 |
| Q x OP | -5.0 | -1.4389 |
| Q x KS | -4.3 | -1.1440 |
| W x KS | -4.3 | -0.7876 |
| W x OP | -2.9 | -0.5006 |
| OP x KS | -2.9 | -0.4362 |
## Linear Regression Model Fit
| Model | Scale | Params | R-squared | RMSE |
|-------|-------|--------|-----------|------|
| Additive (main effects) | raw | 5 | 0.453 | 1.28pp |
| + Pairwise interactions | raw | 11 | 0.704 | 0.94pp |
| Additive (main effects) | logit | 5 | 0.455 | 0.313 log-odds |
Additive model explains only 45% of variance on both scales; interactions account for an additional 25%.
The logit transformation does not improve additive fit (R-squared 0.453 vs 0.455), confirming that non-additivity is structural rather than a scale artifact.
## Summary
1. Quality-monitor alone (98.6%) outperforms the grand coalition (95.7%), which shows that more features doesn't guarantee a better performance.
2. Quality-monitor accounts for ~100% of the Shapley-attributed gain, while all other features are near zero or negative on logit scale.
3. All pairwise interactions are negative, among them, the strongest one is Q x W (-7.9pp / -2.06 log-odds).
4. The additive model is a poor fit (R-squared = 0.45 on both raw and logit scales)!:(

## Files
- `shapley_exact_model.py` — Exact Shapley computation + linear regression models (raw scale)
- `shapley_logit_model.py` — Same analysis on logit scale
- `shapley_exact_figures.py` — Generates 4 publication figures
- `shapley_exact_results.json` — Machine-readable results (raw scale)
- `shapley_logit_results.json` — Machine-readable results (logit scale)
- `fig1_exact_shapley.png` — Singleton vs exact Shapley bar chart
- `fig2_exact_interactions.png` — Complete pairwise interaction heatmap
- `fig3_exact_coalition_landscape.png` — All 16 coalitions ranked by pass rate
- `fig4_shapley_waterfall.png` — Waterfall decomposition from baseline to grand coalition
