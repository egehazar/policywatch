"""Exploratory, not pre-registered: does Kev's top score say when its top passage is right, and do Kev and Qwen agree?

Uses the scores on disk for parts A and B (no model call):
- confidence: for each point, Kev's p(yes) on its top piece, and the margin over the second piece. AUROC of each for
  "the top piece is gold" (hit@1 counted as in relocate.hit, ties in expectation), and hit@1 by score band.
- agreement: how often Kev's and QWEN's top pieces are the same, and hit@1 for agree / Kev-only / QWEN-only.
Usage  py -m stale.reloc_conf
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out')
sys.path.insert(0, os.path.dirname(HERE))
from stale.relocate import hit
from stale.relocate2 import top_piece


def auroc(pos, neg):
    if not pos or not neg: return None
    w = sum((p > n) + .5 * (p == n) for p in pos for n in neg)
    return round(w / (len(pos) * len(neg)), 3)


def part(name, items):
    """items: [(kev scores, qwen scores, gold)] per point."""
    rows = []
    for k, q, gold in items:
        s = sorted(k, reverse=True); h1 = hit(k, gold)[0][1]
        rows.append({'top': s[0], 'margin': s[0] - (s[1] if len(s) > 1 else 0), 'hit': h1,
                     'agree': top_piece(k) == top_piece(q), 'kev_hit': top_piece(k) in gold, 'qwen_hit': top_piece(q) in gold})
    out = {'points': len(rows)}
    for key in ('top', 'margin'):
        out[f'auroc_{key}'] = auroc([r[key] for r in rows if r['hit'] >= .5], [r[key] for r in rows if r['hit'] < .5])
    bands = [(.9, 1.01), (.7, .9), (.5, .7), (0, .5)]
    out['hit_by_top_score'] = {f'{lo:.1f}-{min(hi, 1):.1f}': (lambda S: {'n': len(S), 'hit@1': round(sum(r['hit'] for r in S) / len(S), 3) if S else None})(
        [r for r in rows if lo <= r['top'] < hi]) for lo, hi in bands}
    ag = [r for r in rows if r['agree']]; dis = [r for r in rows if not r['agree']]
    out['agreement'] = {'agree': len(ag), 'agree_hit': round(sum(r['kev_hit'] for r in ag) / len(ag), 3) if ag else None,
                        'disagree': len(dis), 'disagree_kev_hit': sum(r['kev_hit'] for r in dis), 'disagree_qwen_hit': sum(r['qwen_hit'] for r in dis),
                        'disagree_neither': sum(not r['kev_hit'] and not r['qwen_hit'] for r in dis),
                        'oracle_either': round(sum(r['kev_hit'] or r['qwen_hit'] for r in rows) / len(rows), 3)}
    print(name, json.dumps(out, indent=1))
    return out


def main():
    import stale.relocate2 as A, stale.relocate_b as B
    docs, need, chosen = A.needed()
    K = json.load(open(os.path.join(OUT, 'reloc_kev.json'), encoding='utf-8')); Q = json.load(open(A.F['qwen'], encoding='utf-8'))
    ia = [([s[it['question']] for s in K[d['doc']]['scores']], [s[it['question']]['lo'] for s in Q[d['doc']]['scores']], it['gold'])
          for d in docs for it in d['items'] if it['point'] in chosen]
    KB = json.load(open(B.F['kev'], encoding='utf-8')); QB = json.load(open(B.F['qwen'], encoding='utf-8'))
    ib = [([s[it['question']] for s in KB[d['doc']]['scores']], [s[it['question']]['lo'] for s in QB[d['doc']]['scores']], it['gold'])
          for d in B.docs() for it in d['items']]
    res = {'A': part('A', ia), 'B': part('B', ib)}
    with open(os.path.join(OUT, 'reloc_conf.json'), 'w', encoding='utf-8') as f: json.dump(res, f, indent=1)


if __name__ == '__main__':
    main()
