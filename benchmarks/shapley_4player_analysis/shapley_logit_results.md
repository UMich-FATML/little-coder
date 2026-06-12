# Shapley Value Analysis — Logit Scale Results

## Setup

Response variable: `logit(pass_rate)` = `log(p / (1-p))`

- v(empty) = logit(91.4%) = +2.3671
- v(grand) = logit(95.7%) = +3.1061
- Total gain = +0.7390 log-odds

Aligns with the GLM framework in Sun & Han Part 1 (logit link).

## Exact Shapley Values (both scales)

| Feature | phi_raw (pp) | phi_logit | % of total |
|---------|-------------|-----------|------------|
| Q (quality-monitor) | +3.214 | +0.7436 | 100.6% |
| W (write-guard) | +0.952 | +0.1191 | 16.1% |
| KS (knowledge+skill) | +0.119 | -0.0464 | -6.3% |
| OP (output-parser) | +0.000 | -0.0774 | -10.5% |
| **Sum** | **+4.286** | **+0.7390** | 100% |

Efficiency satisfied: Σφ = +0.7390 = v(grand) − v(empty).

Rankings and signs are identical on both scales except KS and OP, which flip
from slightly positive/zero on raw to slightly negative on logit. The negative
values are genuine — these features hurt performance on average across all
coalition contexts.

## Additive Model (logit scale)

v(S) = β₀ + Σ βⱼ · 1{j ∈ S}

| Coefficient | Value (log-odds) |
|-------------|-----------------|
| β₀ | +3.0250 |
| β_Q | +0.4876 |
| β_W | -0.0535 |
| β_OP | -0.2342 |
| β_KS | -0.1786 |

- R² (logit) = 0.4551
- R² (raw)   = 0.4533
- RMSE = 0.3130 log-odds

R² is essentially unchanged across scales (0.455 vs 0.453). The non-additivity
is structural — not a scale artifact. Over half the variance comes from
pairwise and higher-order interactions.

## Pairwise Interactions (both scales)

γ_{jk} = v({j,k}) − v({j}) − v({k}) + v(∅)

| Pair | γ_raw (pp) | γ_logit |
|------|-----------|---------|
| Q × W | -7.86 | -2.0567 |
| Q × OP | -5.00 | -1.4389 |
| Q × KS | -4.29 | -1.1440 |
| W × KS | -4.29 | -0.7876 |
| W × OP | -2.86 | -0.5006 |
| OP × KS | -2.86 | -0.4362 |

All 6 pairwise interactions are negative on both scales. No feature pair
exhibits synergy. The logit scale makes the interactions more interpretable
as log-odds ratios.

## Key Conclusion

Using logit scale does not resolve the negative Shapley values — they are
slightly more pronounced. The negative φ for OP and KS reflects their net
negative average marginal contribution across all coalition contexts, driven
by the strong pairwise interference effects.
