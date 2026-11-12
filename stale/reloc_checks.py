"""Post-hoc artifact checks on the relocation result (exploratory; not part of the pre-registered reading).
Usage  python stale/reloc_checks.py   (from the repo root)"""
import json, collections, statistics as st, sys
sys.path.insert(0, '.')
R = json.load(open('stale/out/reloc_result.json', encoding='utf-8'))['rows']
D = json.load(open('stale/out/reloc_docs.json', encoding='utf-8'))
K = json.load(open('stale/out/reloc_kev.json', encoding='utf-8'))
A = {p['point']: p for p in json.load(open('stale/out/reanchored.json', encoding='utf-8'))['points']}
arms = ['KEV', 'BGE', 'BM25', 'QNN']
h = lambda rows, a: round(sum(r[a]['hit']['1'] if '1' in r[a]['hit'] else r[a]['hit'][1] for r in rows) / max(1, len(rows)), 3)
# 1. per document
by = collections.defaultdict(list)
for r in R: by[r['doc']].append(r)
w = {o: [0, 0, 0] for o in ('BGE', 'BM25', 'QNN')}
for d, rows in by.items():
    for o in w:
        k, b = h(rows, 'KEV'), h(rows, o); w[o][0 if k > b else 1 if k == b else 2] += 1
print('docs where KEV hit@1 > = < other:', w)
# 2. position and hub checks
items = {(d['doc'], it['point']): (d, it) for d in D['docs'] for it in d['items']}
pos_k, pos_g, hub, ties, toplen, avglen = [], [], [], [], [], []
first_piece_hits = 0
for r in R:
    d, it = items[(r['doc'], r['point'])]; n = len(d['pieces'])
    s = [x[it['question']] for x in K[r['doc']]['scores']]
    top = max(range(n), key=lambda i: s[i]); pos_k.append(top / max(1, n - 1)); pos_g.append(min(it['gold']) / max(1, n - 1))
    ties.append(sum(1 for x in s if x == s[top]))
    toplen.append(len(d['pieces'][top])); avglen.append(st.mean(len(p) for p in d['pieces']))
    first_piece_hits += (0 in it['gold'])
print('mean relative position: Kev top %.2f, gold %.2f' % (st.mean(pos_k), st.mean(pos_g)))
print('first-piece baseline hit@1: %.3f' % (first_piece_hits / len(R)))
print('Kev ties at top (mean, max):', round(st.mean(ties), 2), max(ties), ' points with a tie >1:', sum(t > 1 for t in ties))
print('Kev top piece length mean %.0f vs doc mean %.0f' % (st.mean(toplen), st.mean(avglen)))
for doc, rows in by.items():
    tops = []
    for r in rows:
        d, it = items[(doc, r['point'])]; s = [x[it['question']] for x in K[doc]['scores']]
        tops.append(max(range(len(s)), key=lambda i: s[i]))
    c = collections.Counter(tops).most_common(1)[0][1]; hub.append((c, len(rows)))
print('hub: share of points whose Kev top piece is the doc\'s most common top piece: %.2f' % (sum(c for c, _ in hub) / sum(n for _, n in hub)))
# 3. memorisation split: quote first seen in the archive, and ToS;DR point created
for key, cut in (('quote_first_seen', '2025-01-01'), ('quote_first_seen', '2025-07-01'), ('created_at', '2025-01-01'), ('created_at', '2025-07-01')):
    old = [r for r in R if A.get(r['point'], {}).get(key, '0') < cut]; new = [r for r in R if A.get(r['point'], {}).get(key, '0') >= cut]
    print(f'{key} < {cut}: n={len(old)} ' + ' '.join(f'{a} {h(old, a)}' for a in arms) + f' | >= : n={len(new)} ' + ' '.join(f'{a} {h(new, a)}' for a in arms))
print('missing in reanchored:', sum(r['point'] not in A for r in R))
# 4. by document size
for lo, hi in ((0, 30), (30, 60), (60, 999)):
    rows = [r for r in R if lo <= r['n_pieces'] < hi]
    print(f'pieces {lo}-{hi}: n={len(rows)} ' + ' '.join(f'{a} {h(rows, a)}' for a in arms + ['RANDOM']))
