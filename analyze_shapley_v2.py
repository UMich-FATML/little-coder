"""
Shapley ablation analysis, v2.

Fixes relative to the v1 script:
  1. Per-task parsing. Crashes ("Agent is already processing") are counted
     separately from genuine FAILs and reported. Coalitions with fewer than
     N tasks parsed raise an error instead of being silently dropped.
  2. Empirical logit log((x+0.5)/(n-x+0.5)) instead of hard clipping.
  3. Exact constrained WLS solution for KernelSHAP (Lagrange closed form)
     instead of distributing the efficiency residual equally, which is only
     valid for symmetric sampling designs.
  4. Task bootstrap: 95% percentile CIs for every Shapley value, exploiting
     the paired structure (all coalitions share the same 140 tasks).
  5. Cross-model analysis replaced by a correctly specified nested
     comparison:
        Model 0 (shared):    elogit(S, j) = beta_j + u_S' vbar
        Model 1 (per-model): elogit(S, j) = beta_j + u_S' v_j
     both fit jointly by WLS with binomial information weights. A paired
     task bootstrap gives the covariance of delta = v_qwen - v_gemma and a
     joint Wald test of H0: delta = 0 (feature value is model agnostic).

Usage: python3 analyze_shapley_v2.py [results_root]
  results_root defaults to ~/little-coder/results and must contain
  ablation_qwen_11player/ and ablation_gemma_11player/.
"""

import json
import os
import re
import sys
from math import comb

import numpy as np

N = 140
B_BOOT = 2000
SEED = 20260705
PLAYERS = ['Q', 'W', 'OP', 'KS', 'TB', 'CP', 'SS', 'BR', 'ET', 'EV', 'INFRA']
M = len(PLAYERS)

coalition_defs = {
    'zero_ext': set(),
    'baseline_empty': {'INFRA'},
    'grand_all10': set(PLAYERS),
    'addone_Q': {'Q', 'INFRA'}, 'addone_W': {'W', 'INFRA'},
    'addone_OP': {'OP', 'INFRA'}, 'addone_KS': {'KS', 'INFRA'},
    'addone_TB': {'TB', 'INFRA'}, 'addone_CP': {'CP', 'INFRA'},
    'addone_SS': {'SS', 'INFRA'}, 'addone_BR': {'BR', 'INFRA'},
    'addone_ET': {'ET', 'INFRA'}, 'addone_EV': {'EV', 'INFRA'},
    'noinfra_Q': {'Q'}, 'noinfra_W': {'W'}, 'noinfra_OP': {'OP'},
    'noinfra_KS': {'KS'}, 'noinfra_TB': {'TB'}, 'noinfra_CP': {'CP'},
    'noinfra_SS': {'SS'}, 'noinfra_BR': {'BR'}, 'noinfra_ET': {'ET'},
    'noinfra_EV': {'EV'},
    'loo_Q': set(PLAYERS) - {'Q'}, 'loo_W': set(PLAYERS) - {'W'},
    'loo_OP': set(PLAYERS) - {'OP'}, 'loo_KS': set(PLAYERS) - {'KS'},
    'loo_TB': set(PLAYERS) - {'TB'}, 'loo_CP': set(PLAYERS) - {'CP'},
    'loo_SS': set(PLAYERS) - {'SS'}, 'loo_BR': set(PLAYERS) - {'BR'},
    'loo_ET': set(PLAYERS) - {'ET'}, 'loo_EV': set(PLAYERS) - {'EV'},
    'loo_INFRA': set(PLAYERS) - {'INFRA'},
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

LINE_PAT = re.compile(r'\[([^\]]+)\]\s+(PASS|FAIL)')
CRASH_PAT = re.compile(r'Agent is already processing')


# ---------------------------------------------------------------- parsing

def load_coalition(fpath):
    """Return (task -> 0/1 dict, crash count). Last occurrence wins so that
    appended rerun lines override the original crashed lines."""
    tasks, crashes = {}, 0
    with open(fpath) as f:
        for line in f:
            m = LINE_PAT.search(line)
            if not m:
                continue
            task, res = m.group(1), m.group(2)
            tasks[task] = 1 if res == 'PASS' else 0
            if res == 'FAIL' and CRASH_PAT.search(line):
                crashes += 1
    return tasks, crashes


def load_model(results_dir, model_name):
    """Return (task_matrix [n_tasks x n_coalitions], labels, task_names)."""
    per_label, crash_report = {}, {}
    for label in coalition_defs:
        fpath = os.path.join(results_dir, f'polyglot_{label}.txt')
        if not os.path.exists(fpath):
            print(f'  [{model_name}] MISSING coalition file: {label}')
            continue
        tasks, crashes = load_coalition(fpath)
        if len(tasks) < N:
            raise RuntimeError(
                f'[{model_name}] coalition {label}: only {len(tasks)}/{N} '
                f'tasks parsed. Fix the run before analysing.')
        per_label[label] = tasks
        if crashes:
            crash_report[label] = crashes
    if crash_report:
        print(f'  [{model_name}] WARNING: crash lines still present '
              f'(rerun lines may supersede them): {crash_report}')
    labels = sorted(per_label)
    task_names = sorted(set().union(*[set(t) for t in per_label.values()]))
    if len(task_names) != N:
        raise RuntimeError(
            f'[{model_name}] union of task names has {len(task_names)} '
            f'entries, expected {N}. Task naming inconsistent across files.')
    Ymat = np.zeros((N, len(labels)), dtype=float)
    for c, label in enumerate(labels):
        for t, name in enumerate(task_names):
            if name not in per_label[label]:
                raise RuntimeError(
                    f'[{model_name}] task {name} missing in {label}.')
            Ymat[t, c] = per_label[label][name]
    return Ymat, labels, task_names


# ------------------------------------------------------------- estimators

def elogit(x, n):
    return np.log((x + 0.5) / (n - x + 0.5))


def kernel_weight(s):
    if s == 0 or s == M:
        return None
    return (M - 1) / (comb(M, s) * s * (M - s))


def shapley_constrained(labels, vals):
    """Exact constrained WLS KernelSHAP.

    labels/vals include zero_ext and grand_all10; those two pin the
    constraint, the rest enter the weighted regression with an intercept.
    """
    v0 = vals[labels.index('zero_ext')]
    vG = vals[labels.index('grand_all10')]
    delta = vG - v0
    Z, y, w = [], [], []
    for label, v in zip(labels, vals):
        coal = coalition_defs[label]
        s = len(coal)
        kw = kernel_weight(s)
        if kw is None:
            continue
        Z.append([1.0 if p in coal else 0.0 for p in PLAYERS])
        y.append(v - v0)
        w.append(kw)
    Z, y, w = np.array(Z), np.array(y), np.array(w)
    W = np.diag(w)
    A = Z.T @ W @ Z
    b = Z.T @ W @ y
    Ainv_b = np.linalg.solve(A, b)
    ones = np.ones(M)
    Ainv_1 = np.linalg.solve(A, ones)
    phi = Ainv_b - Ainv_1 * ((ones @ Ainv_b - delta) / (ones @ Ainv_1))
    return phi, delta


def coalition_logits(Ymat, labels, idx=None):
    """Empirical logits per coalition, optionally on a task subsample."""
    sub = Ymat if idx is None else Ymat[idx]
    n = sub.shape[0]
    passes = sub.sum(axis=0)
    return elogit(passes, n), passes, n


# ------------------------------------------------- cross-model nested test

def build_joint(labels_common, u_rows, v_by_model):
    """Design matrices for the nested comparison. v_by_model is a dict
    model -> vector of elogits aligned with labels_common."""
    models = sorted(v_by_model)
    J = len(models)
    nC = len(labels_common)
    y = np.concatenate([v_by_model[m] for m in models])
    # weights: inverse variance of elogit, approx n * p * (1-p)
    w = []
    for m in models:
        p = 1.0 / (1.0 + np.exp(-v_by_model[m]))
        w.append(N * p * (1 - p))
    w = np.concatenate(w)
    # Model 0: beta_j + u' vbar
    X0 = np.zeros((J * nC, J + M))
    # Model 1: beta_j + u' v_j
    X1 = np.zeros((J * nC, J + J * M))
    for jm, m in enumerate(models):
        for c in range(nC):
            r = jm * nC + c
            X0[r, jm] = 1.0
            X0[r, J:] = u_rows[c]
            X1[r, jm] = 1.0
            X1[r, J + jm * M: J + (jm + 1) * M] = u_rows[c]
    return y, w, X0, X1, models


def wls(X, y, w):
    Xw = X * w[:, None]
    beta = np.linalg.lstsq(Xw.T @ X, Xw.T @ y, rcond=None)[0]
    resid = y - X @ beta
    rss = float(np.sum(w * resid ** 2))
    return beta, rss


# --------------------------------------------------------------------- main

def main():
    root = os.path.expanduser(
        sys.argv[1] if len(sys.argv) > 1 else '~/little-coder/results')
    rng = np.random.default_rng(SEED)

    data = {}
    for model, sub in [('Qwen', 'ablation_qwen_11player'),
                       ('Gemma', 'ablation_gemma_11player')]:
        d = os.path.join(root, sub)
        if not os.path.isdir(d):
            print(f'[{model}] directory not found, skipping: {d}')
            continue
        Ymat, labels, tasks = load_model(d, model)
        data[model] = (Ymat, labels, tasks)
        print(f'[{model}] {len(labels)} coalitions x {len(tasks)} tasks loaded')

    results = {'n_tasks': N, 'bootstrap_reps': B_BOOT}

    # ---- per-model Shapley with bootstrap CIs
    for model, (Ymat, labels, tasks) in data.items():
        vals, passes, _ = coalition_logits(Ymat, labels)
        phi, delta = shapley_constrained(labels, list(vals))

        boot = np.empty((B_BOOT, M))
        for b in range(B_BOOT):
            idx = rng.integers(0, N, size=N)
            bvals, _, _ = coalition_logits(Ymat, labels, idx)
            boot[b], _ = shapley_constrained(labels, list(bvals))
        lo, hi = np.percentile(boot, [2.5, 97.5], axis=0)
        se = boot.std(axis=0, ddof=1)

        i0, iG = labels.index('zero_ext'), labels.index('grand_all10')
        print(f'\n{"=" * 74}\n  {model}: Shapley values with task-bootstrap '
              f'95% CIs\n{"=" * 74}')
        print(f'  v(empty) = {int(passes[i0])}/{N}, '
              f'v(grand) = {int(passes[iG])}/{N}, '
              f'total = {delta:+.3f} logits')
        print(f'  {"Player":<8} {"phi":>8} {"se":>7} {"95% CI":>18}  sig')
        order = np.argsort(-phi)
        for i in order:
            sig = '*' if (lo[i] > 0 or hi[i] < 0) else ''
            print(f'  {PLAYERS[i]:<8} {phi[i]:>+8.3f} {se[i]:>7.3f} '
                  f'[{lo[i]:>+7.3f}, {hi[i]:>+7.3f}]  {sig}')

        # additive fit quality on the logit scale
        Z = np.array([[1.0 if p in coalition_defs[l] else 0.0
                       for p in PLAYERS] for l in labels])
        X = np.column_stack([np.ones(len(labels)), Z])
        bhat = np.linalg.lstsq(X, vals, rcond=None)[0]
        r2 = 1 - np.sum((vals - X @ bhat) ** 2) / np.sum(
            (vals - vals.mean()) ** 2)
        print(f'  additive R2 (coalition logits): {r2:.4f}')

        results[model] = {
            'phi': {p: round(float(phi[i]), 4) for i, p in enumerate(PLAYERS)},
            'se': {p: round(float(se[i]), 4) for i, p in enumerate(PLAYERS)},
            'ci_lo': {p: round(float(lo[i]), 4) for i, p in enumerate(PLAYERS)},
            'ci_hi': {p: round(float(hi[i]), 4) for i, p in enumerate(PLAYERS)},
            'additive_R2': round(float(r2), 4),
            'total_logits': round(float(delta), 4),
        }

    # ---- nested test: shared vector vs per-model vectors
    if len(data) == 2:
        (Y_q, lab_q, _), (Y_g, lab_g, _) = data['Qwen'], data['Gemma']
        common = sorted(set(lab_q) & set(lab_g))
        u_rows = np.array([[1.0 if p in coalition_defs[l] else 0.0
                            for p in PLAYERS] for l in common])
        cq = [lab_q.index(l) for l in common]
        cg = [lab_g.index(l) for l in common]

        def fit_once(idx=None):
            vq, _, _ = coalition_logits(Y_q[:, cq], common, idx)
            vg, _, _ = coalition_logits(Y_g[:, cg], common, idx)
            y, w, X0, X1, _ = build_joint(common, u_rows,
                                          {'Qwen': vq, 'Gemma': vg})
            b0, rss0 = wls(X0, y, w)
            b1, rss1 = wls(X1, y, w)
            vbar = b0[2:]
            v_q = b1[2: 2 + M]          # models sorted: Gemma, Qwen
            v_g = b1[2 + M:]
            # sorted(models) = ['Gemma', 'Qwen'] so slice order is Gemma first
            v_g, v_q = v_q, v_g
            return vbar, v_q, v_g, rss0, rss1

        vbar, v_q, v_g, rss0, rss1 = fit_once()
        dhat = v_q - v_g

        boot_d = np.empty((B_BOOT, M))
        for b in range(B_BOOT):
            idx = rng.integers(0, N, size=N)
            _, bq, bg, _, _ = fit_once(idx)
            boot_d[b] = bq - bg
        cov = np.cov(boot_d.T)
        wald = float(dhat @ np.linalg.solve(cov, dhat))
        from scipy.stats import chi2
        pval = float(chi2.sf(wald, M))
        d_lo, d_hi = np.percentile(boot_d, [2.5, 97.5], axis=0)

        print(f'\n{"=" * 74}\n  Nested test: shared feature vector (Model 0) '
              f'vs per-model (Model 1)\n{"=" * 74}')
        print(f'  weighted RSS: Model 0 = {rss0:.2f}, Model 1 = {rss1:.2f}')
        print(f'  joint Wald on delta = v_Qwen - v_Gemma: '
              f'chi2({M}) = {wald:.2f}, p = {pval:.4f}')
        print(f'\n  {"Player":<8} {"vbar":>8} {"v_Qwen":>8} {"v_Gemma":>9} '
              f'{"delta":>8} {"95% CI(delta)":>20}  sig')
        for i in np.argsort(-np.abs(dhat)):
            sig = '*' if (d_lo[i] > 0 or d_hi[i] < 0) else ''
            print(f'  {PLAYERS[i]:<8} {vbar[i]:>+8.3f} {v_q[i]:>+8.3f} '
                  f'{v_g[i]:>+9.3f} {dhat[i]:>+8.3f} '
                  f'[{d_lo[i]:>+7.3f}, {d_hi[i]:>+7.3f}]  {sig}')

        results['nested_test'] = {
            'wald_chi2': round(wald, 3), 'df': M, 'p_value': round(pval, 5),
            'vbar': {p: round(float(vbar[i]), 4)
                     for i, p in enumerate(PLAYERS)},
            'delta': {p: round(float(dhat[i]), 4)
                      for i, p in enumerate(PLAYERS)},
        }

    out = os.path.join(root, 'shapley_v2_results.json')
    with open(out, 'w') as f:
        json.dump(results, f, indent=2)
    print(f'\nSaved to {out}')


if __name__ == '__main__':
    main()
