"""Pick the relocation sample size N from Kev's measured timing (stale/PREREG_relocate.md): fit
sec = c0 + c1*chars + c2*Q + c3*chars*Q on bench/out/kev_timing.jsonl + kev_scale.jsonl (one request at a time,
idle CPU), then price every candidate N on the pieces and questions it needs. No relocation score is read.
Usage  py -m stale.cost [budget_hours=6]
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from stale.relocate import sample, DOCS
from bench.kev_vs_llm import load_pairs, read, bank70

FROZEN = os.path.join(ROOT, '..', 'decision-serving', 'play', 'reviewq', 'out')
CANDIDATES = (100, 150, 200, 300, 400, 500, 726)


def fit():
    regions = {}
    for p in load_pairs(FROZEN):
        regions[p['id'] + '|old'] = len(p['old_region']); regions[p['id'] + '|new'] = len(p['new_region'])
    X, y = [], []
    for r in read(os.path.join(ROOT, 'bench', 'out', 'kev_timing.jsonl')):
        c = regions[r['id']]; X.append([1, c, 70, c * 70]); y.append(r['sec'])
    for r in read(os.path.join(ROOT, 'bench', 'out', 'kev_scale.jsonl')):
        c, q = r['chars'], r['n_questions']; X.append([1, c, q, c * q]); y.append(r['sec'])
    X, y = np.array(X, float), np.array(y, float)
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    pred = X @ coef
    return coef, float(np.mean(np.abs(pred - y) / y)), len(y)


def main(budget_h=6.0):
    coef, mape, n = fit()
    print(f'fit on {n} timed requests: sec = {coef[0]:.2f} + {coef[1]:.5f}*chars + {coef[2]:.3f}*Q + {coef[3]:.7f}*chars*Q '
          f'(mean abs error {mape:.0%})')
    best = None
    for N in CANDIDATES:
        D, need, _ = sample(N); P = {d['doc']: d['pieces'] for d in D['docs']}
        sec = sum(max(0.0, coef @ np.array([1, len(p), len(qs), len(p) * len(qs)])) for doc, qs in need.items() for p in P[doc])
        fits = sec / 3600 <= budget_h
        print(f'N={N}: {sum(len(P[d]) * len(q) for d, q in need.items())} cells, {sec / 3600:.1f} h {"fits" if fits else ""}')
        if fits: best = N
    print('N =', best)
    return best


if __name__ == '__main__':
    main(*(float(a) for a in sys.argv[1:]))
