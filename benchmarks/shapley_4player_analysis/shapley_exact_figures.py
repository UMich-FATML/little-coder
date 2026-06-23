import numpy as np
import matplotlib.pyplot as plt
from math import factorial
import itertools
import os

N = 140
features = ['Q', 'W', 'OP', 'KS']
feature_full = {'Q':'quality-\nmonitor','W':'write-\nguard','OP':'output-\nparser','KS':'knowledge+\nskill-inject'}
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
v = {k:val/N for k,val in raw.items()}
v0 = v[frozenset()]

# Exact Shapley
phi = {}
for j in features:
    others = [f for f in features if f != j]
    s = 0
    for r in range(M):
        for combo in itertools.combinations(others, r):
            S = frozenset(combo)
            w = factorial(r)*factorial(M-r-1)/factorial(M)
            s += w * (v[frozenset(combo+(j,))] - v[S])
    phi[j] = s

# Interactions
gamma = {}
for i,a in enumerate(features):
    for j,b in enumerate(features):
        if i>=j: continue
        gamma[(a,b)] = v[frozenset([a,b])] - v[frozenset([a])] - v[frozenset([b])] + v0

plt.rcParams.update({'font.family':'sans-serif','font.size':11,'axes.spines.top':False,
    'axes.spines.right':False,'figure.facecolor':'white','savefig.dpi':200,'savefig.bbox':'tight'})
GREEN,RED,BLUE,GRAY,ORANGE='#1D9E75','#C4453C','#2D6CA2','#888888','#E8963E'
out = '.'

# ── Fig 1: Exact Shapley bar chart ──
fig, ax = plt.subplots(figsize=(8,4.5))
singletons = [(v[frozenset([f])]-v0)*100 for f in features]
shapley = [phi[f]*100 for f in features]
total = (v[frozenset(features)]-v0)*100

x = np.arange(M)
bw = 0.35
ax.bar(x-bw/2, singletons, bw, color=BLUE, alpha=0.7, label='Singleton v({j})−v(∅)', zorder=3)
ax.bar(x+bw/2, shapley, bw, color=[GREEN if s>=0 else RED for s in shapley], alpha=0.85,
       label='Exact Shapley φⱼ', zorder=3)
ax.axhline(y=total, color=GRAY, ls='--', lw=1, zorder=1)
ax.text(M-0.5, total+0.3, f'Total gain = {total:.1f}pp', ha='right', fontsize=9, color=GRAY)
ax.axhline(y=0, color='black', lw=0.5)
ax.set_xticks(x)
ax.set_xticklabels([f'{f}\n{feature_full[f]}' for f in features], fontsize=10)
ax.set_ylabel('Contribution (percentage points)')
ax.set_title('Singleton Effect vs. Exact Shapley Value (16/16 coalitions)', fontweight='bold', fontsize=13)
ax.legend(fontsize=9)
ax.set_ylim(-1, 9)
ax.grid(axis='y', alpha=0.3, zorder=0)
for i,(s,sh) in enumerate(zip(singletons, shapley)):
    ax.text(i-bw/2, s+0.2, f'+{s:.1f}', ha='center', fontsize=8, fontweight='bold', color=BLUE)
    ax.text(i+bw/2, max(sh,0)+0.2 if sh>=0 else sh-0.5,
            f'{sh:+.1f}', ha='center', fontsize=8, fontweight='bold', color=GREEN if sh>=0 else RED)
fig.tight_layout()
fig.savefig(os.path.join(out,'fig1_exact_shapley.png'))
plt.close()

# ── Fig 2: Full interaction heatmap ──
fig, ax = plt.subplots(figsize=(5.5,4.5))
mat = np.full((M,M), np.nan)
for (a,b),g in gamma.items():
    i,j = features.index(a), features.index(b)
    mat[i][j] = g*100; mat[j][i] = g*100
im = ax.imshow(mat, cmap='RdYlGn', vmin=-10, vmax=2, aspect='equal')
ax.set_xticks(range(M)); ax.set_yticks(range(M))
ax.set_xticklabels(features, fontsize=12, fontweight='bold')
ax.set_yticklabels(features, fontsize=12, fontweight='bold')
for i in range(M):
    for j in range(M):
        if i==j:
            ax.text(j,i,'—',ha='center',va='center',fontsize=11,color=GRAY)
        elif not np.isnan(mat[i][j]):
            ax.text(j,i,f'{mat[i][j]:+.1f}',ha='center',va='center',fontsize=12,
                    fontweight='bold',color='white' if mat[i][j]<-3 else 'black')
fig.colorbar(im, ax=ax, shrink=0.8).set_label('Interaction γ (pp)')
ax.set_title('Complete Pairwise Interactions (all 6 pairs)', fontweight='bold', fontsize=13)
fig.tight_layout()
fig.savefig(os.path.join(out,'fig2_exact_interactions.png'))
plt.close()

# ── Fig 3: Coalition landscape ──
fig, ax = plt.subplots(figsize=(10,6))
coal_list = []
for c,val in v.items():
    if c==frozenset(): label='∅ (all-off)'
    elif c==frozenset(features): label='{Q,W,OP,KS} ★'
    else: label='{'+','.join(sorted(c))+'}'
    coal_list.append((label, val*100, len(c)))
coal_list.sort(key=lambda x: x[1], reverse=True)

colors = []
for l,val,s in coal_list:
    if '★' in l: colors.append(ORANGE)
    elif l=='∅ (all-off)': colors.append(GRAY)
    elif val>=97: colors.append(GREEN)
    elif val>=95: colors.append(BLUE)
    else: colors.append('#6B7280')

ax.barh(range(len(coal_list)), [c[1] for c in coal_list], color=colors, alpha=0.8, zorder=3)
ax.set_yticks(range(len(coal_list)))
ax.set_yticklabels([c[0] for c in coal_list], fontsize=9, fontfamily='monospace')
ax.invert_yaxis()
ax.set_xlabel('Pass Rate (%)')
ax.set_title('All 16 Coalitions — Aider Polyglot (140 tasks)', fontweight='bold', fontsize=13)
ax.set_xlim(89,100)
ax.grid(axis='x', alpha=0.3, zorder=0)
for i,(l,val,s) in enumerate(coal_list):
    ax.text(val+0.1, i, f'{val:.1f}%', va='center', fontsize=8, fontweight='bold', color=colors[i])
ax.axvline(x=v0*100, color=GRAY, ls=':', lw=1)
fig.tight_layout()
fig.savefig(os.path.join(out,'fig3_exact_coalition_landscape.png'))
plt.close()

# ── Fig 4: Shapley decomposition waterfall ──
fig, ax = plt.subplots(figsize=(8,4.5))
ordered = sorted(phi.items(), key=lambda x: x[1], reverse=True)
labels = ['v(∅)'] + [f'φ_{f}' for f,_ in ordered] + ['v(M)']
vals = [v0*100] + [p*100 for _,p in ordered] + [0]

cumsum = v0*100
positions = [cumsum]
for _,p in ordered:
    cumsum += p*100
    positions.append(cumsum)
positions.append(cumsum)

bar_bottoms = []
bar_heights = []
bar_colors = []
# First bar: baseline
bar_bottoms.append(0); bar_heights.append(v0*100); bar_colors.append(GRAY)
# Feature bars
running = v0*100
for f,p in ordered:
    if p >= 0:
        bar_bottoms.append(running); bar_heights.append(p*100); bar_colors.append(GREEN)
    else:
        bar_bottoms.append(running+p*100); bar_heights.append(-p*100); bar_colors.append(RED)
    running += p*100
# Grand coalition
bar_bottoms.append(0); bar_heights.append(running); bar_colors.append(ORANGE)

ax.bar(range(len(labels)), bar_heights, bottom=bar_bottoms, color=bar_colors, alpha=0.85, zorder=3, width=0.6)

# Connector lines
for i in range(len(labels)-2):
    top = bar_bottoms[i] + bar_heights[i]
    ax.plot([i+0.3, i+0.7], [top, top], color='black', lw=0.5, ls='--', zorder=2)

ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels, fontsize=10, fontweight='bold')
ax.set_ylabel('Pass Rate (%)')
ax.set_title('Shapley Value Waterfall Decomposition', fontweight='bold', fontsize=13)
ax.set_ylim(88, 100)
ax.grid(axis='y', alpha=0.3, zorder=0)

# Annotate
for i in range(1, len(labels)-1):
    f, p = ordered[i-1]
    y = bar_bottoms[i] + bar_heights[i]/2
    ax.text(i, bar_bottoms[i]+bar_heights[i]+0.2 if p>=0 else bar_bottoms[i]-0.3,
            f'{p*100:+.2f}pp', ha='center', fontsize=9, fontweight='bold',
            color=GREEN if p>=0 else RED)
ax.text(0, v0*100+0.2, f'{v0*100:.1f}%', ha='center', fontsize=9, color=GRAY, fontweight='bold')
ax.text(len(labels)-1, running+0.2, f'{running:.1f}%', ha='center', fontsize=9, color=ORANGE, fontweight='bold')

fig.tight_layout()
fig.savefig(os.path.join(out,'fig4_shapley_waterfall.png'))
plt.close()

print("Generated 4 exact figures.")
