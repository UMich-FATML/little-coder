"""
uv_reconstruction.py

Implements the saturated model of equation (3.1) at the feature level:

    g(E[Y_ij]) = mu + beta_j + u_i^T v_j
               = mu + beta_j + alpha_i + gamma_ij

and shows, step by step, how each quantity is built from the raw per-task
ablation results. Every number in the "decomposition" and "reconstruction"
tables of the summary comes out of the functions below.

Pipeline
--------
1. Parse each coalition's txt file -> pass count.
2. Coalition pass rate -> empirical logit v(S) (the coalitional value).
3. KernelSHAP (exact constrained WLS) -> per-model Shapley vector v_j.
4. beta_j = empirical logit of the empty coalition (LLM main effect).
5. vbar = mean of v_j over models -> alpha_i = u_i^T vbar
   delta_j = v_j - vbar           -> gamma_ij = u_i^T delta_j
6. u_i^T v_j = alpha_i + gamma_ij -> reconstruction beta_j + u_i^T v_j
   compared against the observed coalition logit.

Usage:
    python3 uv_reconstruction.py <results_root>
results_root contains ablation_qwen_11player/ and ablation_gemma_11player/,
each with polyglot_<label>.txt files.
"""

import os
import re
import sys
from math import comb

import numpy as np

N = 140
PLAYERS = ['Q', 'W', 'OP', 'KS', 'TB', 'CP', 'SS', 'BR', 'ET', 'EV', 'INFRA']
M = len(PLAYERS)

COALITIONS = {
    'zero_ext': set(),
    'baseline_empty': {'INFRA'},
    'grand_all10': set(PLAYERS),
    **{f'addone_{p}': {p, 'INFRA'} for p in PLAYERS if p != 'INFRA'},
    **{f'noinfra_{p}': {p} for p in PLAYERS if p != 'INFRA'},
    **{f'loo_{p}': set(PLAYERS) - {p} for p in PLAYERS},
    'pair_Q_W': {'Q', 'W', 'INFRA'}, 'pair_Q_CP': {'Q', 'CP', 'INFRA'},
    'pair_Q_SS': {'Q', 'SS', 'INFRA'}, 'pair_W_CP': {'W', 'CP', 'INFRA'},
    'pair_W_SS': {'W', 'SS', 'INFRA'}, 'pair_CP_SS': {'CP', 'SS', 'INFRA'},
    'lt2o_Q_W': set(PLAYERS) - {'Q', 'W'},
    'lt2o_Q_CP': set(PLAYERS) - {'Q', 'CP'},
    'lt2o_Q_SS': set(PLAYERS) - {'Q', 'SS'},
    'lt2o_W_CP': set(PLAYERS) - {'W', 'CP'},
    'lt2o_W_SS': set(PLAYERS) - {'W', 'SS'},
    'lt2o_CP_SS': set(PLAYERS) - {'CP', 'SS'},
}

LINE = re.compile(r'\]\s+(PASS|FAIL)\s')


# ---- step 1: parse a coalition file into a pass count -------------------

def pass_count(path):
    passes = total = 0
    for line in open(path, errors='ignore'):
        m = LINE.search(line)
        if not m:
            continue
        total += 1
        if m.group(1) == 'PASS':
            passes += 1
    return passes, total


# ---- step 2: coalitional value v(S) = empirical logit of pass rate ------

def empirical_logit(x, n):
    return np.log((x + 0.5) / (n - x + 0.5))


def load_model(results_dir):
    out = {}
    for label, pset in COALITIONS.items():
        f = os.path.join(results_dir, f'polyglot_{label}.txt')
        if not os.path.exists(f):
            continue
        p, t = pass_count(f)
        if t != N:
            raise RuntimeError(f'{label}: {t} tasks, expected {N}')
        out[label] = (pset, empirical_logit(p, N))
    return out


# ---- step 3: KernelSHAP, exact constrained WLS -------------------------

def kernel_weight(s):
    if s == 0 or s == M:
        return None
    return (M - 1) / (comb(M, s) * s * (M - s))


def shapley(data):
    """Constrained weighted least squares for the Shapley vector.

    minimize  sum_S k(|S|) ( v(S) - v0 - sum_{i in S} phi_i )^2
    subject to sum_i phi_i = v(grand) - v(empty).

    Lagrange closed form with A = Z' W Z, b = Z' W y, y = v(S)-v0:
        phi = A^{-1} b - A^{-1} 1 (1' A^{-1} b - Delta) / (1' A^{-1} 1)
    """
    v0 = data['zero_ext'][1]
    vG = data['grand_all10'][1]
    Delta = vG - v0
    Z, y, w = [], [], []
    for label, (pset, v) in data.items():
        s = len(pset)
        kw = kernel_weight(s)
        if kw is None:
            continue
        Z.append([1.0 if p in pset else 0.0 for p in PLAYERS])
        y.append(v - v0)
        w.append(kw)
    Z, y, w = np.array(Z), np.array(y), np.array(w)
    W = np.diag(w)
    A = Z.T @ W @ Z
    b = Z.T @ W @ y
    Ainv_b = np.linalg.solve(A, b)
    ones = np.ones(M)
    Ainv_1 = np.linalg.solve(A, ones)
    phi = Ainv_b - Ainv_1 * ((ones @ Ainv_b - Delta) / (ones @ Ainv_1))
    return phi, v0


# ---- steps 4-6: decomposition and reconstruction -----------------------

def u_vec(pset):
    return np.array([1.0 if p in pset else 0.0 for p in PLAYERS])


def main():
    root = os.path.expanduser(sys.argv[1] if len(sys.argv) > 1
                              else '~/little-coder/results/analysis_clean')

    models = {}
    for name, sub in [('Qwen', 'ablation_qwen_11player'),
                      ('Gemma', 'ablation_gemma_11player')]:
        data = load_model(os.path.join(root, sub))
        phi, beta = shapley(data)
        models[name] = {'data': data, 'v': phi, 'beta': beta}
        print(f'[{name}] beta_j (empty logit) = {beta:+.3f}')
        print('  v_j = ' + ', '.join(f'{p}:{phi[i]:+.3f}'
                                      for i, p in enumerate(PLAYERS)))

    vq = models['Qwen']['v']
    vg = models['Gemma']['v']
    vbar = (vq + vg) / 2.0
    delta = {'Qwen': vq - vbar, 'Gemma': vg - vbar}

    print('\n=== decomposition  u^T v_j = alpha_i + gamma_ij ===')
    print(f'{"coalition":<14}{"model":<7}{"alpha":>9}{"gamma":>9}{"u^T v_j":>9}')
    for label in ['grand_all10', 'addone_W', 'pair_Q_W']:
        u = u_vec(COALITIONS[label])
        alpha = u @ vbar
        for mname, v in [('Qwen', vq), ('Gemma', vg)]:
            gamma = u @ delta[mname]
            print(f'{label:<14}{mname:<7}{alpha:>+9.3f}{gamma:>+9.3f}'
                  f'{alpha + gamma:>+9.3f}')

    print('\n=== reconstruction  beta_j + u^T v_j  vs  observed ===')
    print(f'{"model":<7}{"coalition":<14}{"u^T v_j":>9}{"pred":>9}{"observed":>10}')
    show = ['zero_ext', 'grand_all10', 'addone_Q', 'addone_W', 'loo_W']
    for mname in ['Qwen', 'Gemma']:
        mv = models[mname]['v']
        beta = models[mname]['beta']
        for label in show:
            if label not in models[mname]['data']:
                continue
            pset, obs = models[mname]['data'][label]
            uv = u_vec(pset) @ mv
            print(f'{mname:<7}{label:<14}{uv:>+9.3f}{beta + uv:>+9.3f}'
                  f'{obs:>+10.3f}')

    print('\n=== reconstruction R2 (all coalitions, per model) ===')
    for mname in ['Qwen', 'Gemma']:
        mv, beta = models[mname]['v'], models[mname]['beta']
        obs, pred = [], []
        for label, (pset, v) in models[mname]['data'].items():
            obs.append(v)
            pred.append(beta + u_vec(pset) @ mv)
        obs, pred = np.array(obs), np.array(pred)
        r2 = 1 - np.sum((obs - pred) ** 2) / np.sum((obs - obs.mean()) ** 2)
        print(f'  {mname}: R2 = {r2:.3f}')


if __name__ == '__main__':
    main()
