"""
4-Player Shapley Value Analysis — Logit Scale
Mirrors shapley_exact_model.py but uses logit(pass_rate) as response.
Aligns with the GLM framework in Sun & Han (Part 1).
"""
import numpy as np
from math import factorial
import itertools
import json

N = 140
features = ['Q', 'W', 'OP', 'KS']
M = 4

raw = {
    frozenset():128, frozenset(['Q']):138, frozenset(['W']):135,
    frozenset(['OP']):131, frozenset(['KS']):132,
    frozenset(['Q','W']):134, frozenset(['Q','OP']):134, frozenset(['Q','KS']):136,
    frozenset(['W','OP']):134, frozenset(['W','KS']):133, frozenset(['OP','KS']):131,
    frozenset(['Q','W','OP']):134, frozenset(['Q','W','KS']):133,
    frozenset(['Q','OP','KS']):134, frozenset(['W','OP','KS']):129,
    frozenset(['Q','W','OP','KS']):134,
}

def logit(p):
    p = np.clip(p, 0.001, 0.999)
    return np.log(p / (1 - p))

v = {k: logit(val/N) for k, val in raw.items()}
v_r = {k: val/N for k, val in raw.items()}
v0 = v[frozenset()]
vM = v[frozenset(features)]
total = vM - v0

print("=" * 70)
print("  4-PLAYER SHAPLEY VALUE ANALYSIS -- LOGIT SCALE")
print("  v(S) = logit(pass_rate(S))")
print("=" * 70)
print(f"\n  v(empty) = logit(91.4%) = {v0:+.4f}")
print(f"  v(grand) = logit(95.7%) = {vM:+.4f}")
print(f"  Total gain = {total:+.4f} log-odds\n")

# Exact Shapley on logit
phi = {}
for j in features:
    others = [f for f in features if f != j]
    s = 0
    for r in range(M):
        for combo in itertools.combinations(others, r):
            S = frozenset(combo)
            w = factorial(r) * factorial(M-r-1) / factorial(M)
            s += w * (v[frozenset(combo+(j,))] - v[S])
    phi[j] = s

# Exact Shapley on raw
phi_raw = {}
for j in features:
    others = [f for f in features if f != j]
    s = 0
    for r in range(M):
        for combo in itertools.combinations(others, r):
            S = frozenset(combo)
            w = factorial(r) * factorial(M-r-1) / factorial(M)
            s += w * (v_r[frozenset(combo+(j,))] - v_r[S])
    phi_raw[j] = s

print("=" * 70)
print("  COMPARISON: RAW vs LOGIT SHAPLEY VALUES")
print("=" * 70)
print(f"\n  {'Feature':<6} {'phi_raw (pp)':>14} {'phi_logit':>12} {'% of total':>12}")
ranked = sorted(phi.items(), key=lambda x: x[1], reverse=True)
for f, val in ranked:
    pct = val / total * 100
    print(f"  {f:<6} {phi_raw[f]*100:>+13.3f} {val:>+11.4f} {pct:>11.1f}%")
print(f"  {'Sum':<6} {sum(phi_raw.values())*100:>+13.3f} {sum(phi.values()):>+11.4f}")
assert abs(sum(phi.values()) - total) < 1e-10
print(f"  Efficiency satisfied: sum = {total:+.4f}")

# Additive model on logit
Z = np.array([[1]+[1 if f in c else 0 for f in features] for c in raw.keys()])
y = np.array([v[c] for c in raw.keys()])
beta = np.linalg.lstsq(Z, y, rcond=None)[0]
y_pred = Z @ beta
R2 = 1 - np.sum((y-y_pred)**2) / np.sum((y-y_mean)**2) if (y_mean := y.mean()) else 0
R2 = 1 - np.sum((y-y_pred)**2) / np.sum((y-y.mean())**2)

print(f"\n{'='*70}")
print(f"  ADDITIVE MODEL (logit scale)")
print(f"{'='*70}")
names = ['b0'] + [f'b_{f}' for f in features]
for n, b in zip(names, beta):
    print(f"  {n:<8} = {b:>+8.4f} log-odds")
print(f"\n  R2 (logit) = {R2:.4f}")
print(f"  R2 (raw)   = 0.4533")
print(f"  RMSE = {np.sqrt(np.mean((y-y_pred)**2)):.4f} log-odds")

print(f"\n{'='*70}")
print(f"  PAIRWISE INTERACTIONS (both scales)")
print(f"{'='*70}")
print(f"\n  {'Pair':<8} {'gamma_raw (pp)':>16} {'gamma_logit':>14}")
for i, a in enumerate(features):
    for j, b in enumerate(features):
        if i >= j: continue
        g_raw = (v_r[frozenset([a,b])] - v_r[frozenset([a])]
                 - v_r[frozenset([b])] + v_r[frozenset()]) * 100
        g_log = (v[frozenset([a,b])] - v[frozenset([a])]
                 - v[frozenset([b])] + v[frozenset()])
        print(f"  {a}x{b:<4} {g_raw:>+15.2f} {g_log:>+13.4f}")

# Save JSON
results = {
    'scale': 'logit',
    'v_empty_logit': round(v0, 4),
    'v_grand_logit': round(vM, 4),
    'total_gain_logit': round(total, 4),
    'shapley_logit': {f: round(phi[f], 4) for f in features},
    'shapley_raw_pp': {f: round(phi_raw[f]*100, 3) for f in features},
    'additive_R2_logit': round(R2, 4),
    'additive_R2_raw': 0.4533,
    'note': 'Rankings and signs identical on both scales. Non-additivity is structural.'
}
with open('shapley_logit_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\n  Saved shapley_logit_results.json")
