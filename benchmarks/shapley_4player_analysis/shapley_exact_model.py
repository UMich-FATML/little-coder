"""
Exact 4-Player Shapley Value Analysis — All 16 coalitions observed.
Players: Q (quality-monitor), W (write-guard), OP (output-parser), KS (knowledge+skill-inject)
Baseline: all-off on Aider Polyglot (140 exercises, Qwen3.6-35B-A3B)
"""
import numpy as np
from math import factorial, comb
import itertools
import json
import os

# ============================================================
# COMPLETE DATA (16/16 coalitions)
# ============================================================
N = 140
features = ['Q', 'W', 'OP', 'KS']
M = len(features)

raw = {
    frozenset():                    128,
    frozenset(['Q']):               138,
    frozenset(['W']):               135,
    frozenset(['OP']):              131,
    frozenset(['KS']):              132,
    frozenset(['Q','W']):           134,
    frozenset(['Q','OP']):          134,
    frozenset(['Q','KS']):          136,
    frozenset(['W','OP']):          134,
    frozenset(['W','KS']):          133,
    frozenset(['OP','KS']):         131,
    frozenset(['Q','W','OP']):      134,
    frozenset(['Q','W','KS']):      133,
    frozenset(['Q','OP','KS']):     134,
    frozenset(['W','OP','KS']):     129,
    frozenset(['Q','W','OP','KS']): 134,
}

v = {k: val/N for k, val in raw.items()}
v0 = v[frozenset()]
vM = v[frozenset(features)]
total = vM - v0

print("=" * 70)
print("  EXACT 4-PLAYER SHAPLEY VALUE ANALYSIS")
print("  All 16/16 coalitions observed — no approximation needed")
print("=" * 70)

# ============================================================
# 1. EXACT SHAPLEY VALUES
# ============================================================
print("\n" + "─" * 70)
print("  1. EXACT SHAPLEY VALUES")
print("─" * 70)

def shapley_weight(s, M):
    return factorial(s) * factorial(M - s - 1) / factorial(M)

phi = {}
for j in features:
    others = [f for f in features if f != j]
    total_phi = 0.0
    terms = []
    for r in range(M):  # |S| = 0, 1, 2, 3
        for combo in itertools.combinations(others, r):
            S = frozenset(combo)
            S_plus_j = frozenset(combo + (j,))
            w = shapley_weight(r, M)
            margin = v[S_plus_j] - v[S]
            term = w * margin
            total_phi += term
            terms.append((S, S_plus_j, w, margin, term))
    phi[j] = total_phi

    print(f"\n  φ_{j} calculation (8 terms):")
    for S, SJ, w, margin, term in terms:
        S_label = '{' + ','.join(sorted(S)) + '}' if S else '∅'
        SJ_label = '{' + ','.join(sorted(SJ)) + '}'
        print(f"    {w:.4f} × [v{SJ_label} - v{S_label}] = {w:.4f} × {margin*100:>+6.2f}pp = {term*100:>+7.3f}pp")
    print(f"    ─────────────────────────────────────────────")
    print(f"    φ_{j} = {total_phi*100:>+7.3f}pp")

print(f"\n  Summary:")
print(f"  {'Feature':<6} {'φ (pp)':>10} {'% of total':>12} {'Rank':>6}")
ranked = sorted(phi.items(), key=lambda x: x[1], reverse=True)
for rank, (f, val) in enumerate(ranked, 1):
    pct = (val / total * 100) if total != 0 else 0
    print(f"  {f:<6} {val*100:>+9.3f}  {pct:>10.1f}%  {rank:>6}")
print(f"  {'Sum':<6} {sum(phi.values())*100:>+9.3f}  {'':>10}  (should = {total*100:.3f})")

# Verify efficiency
assert abs(sum(phi.values()) - total) < 1e-10, "Efficiency violated!"
print(f"  ✓ Efficiency constraint satisfied: Σφ = {total*100:.3f}pp")

# ============================================================
# 2. KernelSHAP WLS (should match exact values)
# ============================================================
print("\n" + "─" * 70)
print("  2. KernelSHAP WEIGHTED LEAST SQUARES")
print("─" * 70)

def shapley_kernel(s, M):
    if s == 0 or s == M:
        return float('inf')
    return (M - 1) / (comb(M, s) * s * (M - s))

Z_rows, v_vec, w_vec, labels = [], [], [], []
for coal, val in v.items():
    if coal == frozenset() or coal == frozenset(features):
        continue
    z = [1 if f in coal else 0 for f in features]
    Z_rows.append(z)
    v_vec.append(val - v0)
    w_vec.append(shapley_kernel(sum(z), M))
    labels.append('{' + ','.join(sorted(coal)) + '}')

Z = np.array(Z_rows)
y = np.array(v_vec)
W = np.diag(w_vec)

# Unconstrained WLS
phi_wls_raw = np.linalg.solve(Z.T @ W @ Z, Z.T @ W @ y)

# Constrained (efficiency projection)
residual = total - phi_wls_raw.sum()
phi_wls = phi_wls_raw + residual / M

print(f"\n  {'Feature':<6} {'Exact φ':>10} {'WLS φ':>10} {'Difference':>12}")
for i, f in enumerate(features):
    diff = phi[f] - phi_wls[i]
    print(f"  {f:<6} {phi[f]*100:>+9.3f} {phi_wls[i]*100:>+9.3f} {diff*100:>+11.6f}")

# ============================================================
# 3. PAIRWISE INTERACTIONS
# ============================================================
print("\n" + "─" * 70)
print("  3. PAIRWISE INTERACTION EFFECTS")
print("─" * 70)

gamma = {}
print(f"\n  {'Pair':<12} {'v(pair)':>8} {'v(a)':>8} {'v(b)':>8} {'v(∅)':>8} {'γ (pp)':>10}")
for i, a in enumerate(features):
    for j, b in enumerate(features):
        if i >= j:
            continue
        pair = frozenset([a, b])
        g = v[pair] - v[frozenset([a])] - v[frozenset([b])] + v0
        gamma[(a, b)] = g
        print(f"  {a}×{b:<8} {v[pair]*100:>7.1f}% {v[frozenset([a])]*100:>7.1f}% "
              f"{v[frozenset([b])]*100:>7.1f}% {v0*100:>7.1f}% {g*100:>+9.1f}")

# ============================================================
# 4. LEAVE-ONE-OUT ANALYSIS
# ============================================================
print("\n" + "─" * 70)
print("  4. LEAVE-ONE-OUT (marginal contribution entering last)")
print("─" * 70)

header_mj = 'v(M\\j)'
print(f"\n  {'Removed':<10} {header_mj:>10} {'v(M)':>10} {'Marginal':>10}")
for f in features:
    remaining = frozenset(features) - frozenset([f])
    marginal = vM - v[remaining]
    print(f"  {f:<10} {v[remaining]*100:>9.1f}% {vM*100:>9.1f}% {marginal*100:>+9.1f}pp")

# ============================================================
# 5. FULL COALITION TABLE
# ============================================================
print("\n" + "─" * 70)
print("  5. COMPLETE COALITION TABLE")
print("─" * 70)

print(f"\n  {'Coalition':<20} {'Pass':>5} {'Rate':>8} {'v(S)−v(∅)':>10}")
sorted_coals = sorted(v.items(), key=lambda x: (-len(x[0]), x[1]))
sorted_coals = sorted(v.items(), key=lambda x: x[1], reverse=True)
for coal, val in sorted_coals:
    if coal == frozenset():
        label = '∅ (all-off)'
    elif coal == frozenset(features):
        label = '{Q,W,OP,KS} ★'
    else:
        label = '{' + ','.join(sorted(coal)) + '}'
    gain = val - v0
    print(f"  {label:<20} {raw[coal]:>5} {val*100:>7.1f}% {gain*100:>+9.1f}pp")

# ============================================================
# 6. ADDITIVE MODEL FIT (Linear Regression)
# ============================================================
print("\n" + "─" * 70)
print("  6. LINEAR REGRESSION: v(S) = β₀ + Σ βⱼ·1{j∈S}")
print("─" * 70)

# Build full design matrix (all 16 coalitions)
Z_full = []
y_full = []
for coal, val in v.items():
    z = [1] + [1 if f in coal else 0 for f in features]  # intercept + indicators
    Z_full.append(z)
    y_full.append(val)

Z_full = np.array(Z_full)
y_full = np.array(y_full)

# OLS fit
beta_ols = np.linalg.lstsq(Z_full, y_full, rcond=None)[0]
y_pred = Z_full @ beta_ols
residuals = y_full - y_pred
SSR = np.sum(residuals**2)
SST = np.sum((y_full - y_full.mean())**2)
R2 = 1 - SSR / SST

print(f"\n  Coefficients (OLS, pass-rate scale):")
coef_names = ['β₀ (intercept)'] + [f'β_{f}' for f in features]
for name, b in zip(coef_names, beta_ols):
    print(f"    {name:<20} = {b*100:>+7.3f}pp")
print(f"\n  R² = {R2:.6f}")
print(f"  RMSE = {np.sqrt(SSR/len(y_full))*100:.3f}pp")
print(f"\n  Residuals (predicted vs actual):")
print(f"  {'Coalition':<20} {'Actual':>8} {'Predicted':>10} {'Residual':>10}")
idx = 0
for coal in sorted(v.keys(), key=lambda x: len(x)):
    if coal == frozenset():
        label = '∅'
    elif coal == frozenset(features):
        label = '{Q,W,OP,KS}'
    else:
        label = '{' + ','.join(sorted(coal)) + '}'
    print(f"  {label:<20} {y_full[idx]*100:>7.1f}% {y_pred[idx]*100:>9.1f}% {residuals[idx]*100:>+9.2f}pp")
    idx += 1

# ============================================================
# 7. INTERACTION MODEL (with all pairwise terms)
# ============================================================
print("\n" + "─" * 70)
print("  7. INTERACTION MODEL: v(S) = β₀ + Σ βⱼ·1{j∈S} + Σ γⱼₖ·1{j∈S}·1{k∈S}")
print("─" * 70)

Z_int = []
for coal in v.keys():
    z = [1]  # intercept
    z += [1 if f in coal else 0 for f in features]  # main effects
    # pairwise interactions
    for i, a in enumerate(features):
        for j, b in enumerate(features):
            if i >= j:
                continue
            z.append(1 if (a in coal and b in coal) else 0)
    Z_int.append(z)

Z_int = np.array(Z_int)
y_int = np.array([v[coal] for coal in v.keys()])

beta_int = np.linalg.lstsq(Z_int, y_int, rcond=None)[0]
y_pred_int = Z_int @ beta_int
resid_int = y_int - y_pred_int
SSR_int = np.sum(resid_int**2)
SST_int = np.sum((y_int - y_int.mean())**2)
R2_int = 1 - SSR_int / SST_int

pair_names = []
for i, a in enumerate(features):
    for j, b in enumerate(features):
        if i >= j:
            continue
        pair_names.append(f'γ_{a}×{b}')

all_names = ['β₀'] + [f'β_{f}' for f in features] + pair_names
print(f"\n  Coefficients:")
for name, b in zip(all_names, beta_int):
    marker = '  ★' if abs(b*100) > 2 else ''
    print(f"    {name:<20} = {b*100:>+7.3f}pp{marker}")
print(f"\n  R² = {R2_int:.6f}")
print(f"  RMSE = {np.sqrt(SSR_int/len(y_int))*100:.3f}pp")

# ============================================================
# 8. MODEL COMPARISON
# ============================================================
print("\n" + "─" * 70)
print("  8. MODEL COMPARISON")
print("─" * 70)
print(f"\n  {'Model':<30} {'Params':>7} {'R²':>10} {'RMSE (pp)':>10}")
print(f"  {'Additive (main effects)':<30} {5:>7} {R2:>10.4f} {np.sqrt(SSR/16)*100:>10.3f}")
print(f"  {'+ Pairwise interactions':<30} {11:>7} {R2_int:>10.4f} {np.sqrt(SSR_int/16)*100:>10.3f}")

# ============================================================
# OUTPUT JSON
# ============================================================
results = {
    'shapley_exact': {f: round(phi[f]*100, 3) for f in features},
    'total_gain_pp': round(total*100, 3),
    'interactions': {f'{a}x{b}': round(g*100, 3) for (a,b), g in gamma.items()},
    'additive_R2': round(R2, 6),
    'interaction_R2': round(R2_int, 6),
    'coalitions': {
        ','.join(sorted(k)) if k else 'empty': {'pass': raw[k], 'rate': round(v[k]*100, 1)}
        for k, val in v.items()
    }
}

with open('/mnt/user-data/outputs/shapley_exact_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n\nResults saved to shapley_exact_results.json")
