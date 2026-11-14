"""Exploratory, after part C's result: does skipping navigation units change the proposed quote's accuracy?

On the curator page, about 1 in 20 proposed quotes is a table of contents or a row of links ("[Access and correct
information] * * * [Withdraw consent]"). A unit is NAVIGATION when at least half of its words sit inside [square
brackets] (markdown link text). This re-runs part C's evaluation (relocate2.quote_eval's rule, on the scores already on
disk, no model call) with navigation units ranked last unless every unit of the piece is one, and counts how many
proposed quotes on the 141 stale points it would change.
Usage  py -m stale.propose_nav
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out')
sys.path.insert(0, os.path.dirname(HERE))
import stale.relocate2 as A
from stale.relocate2 import top_piece
from stale.propose import nav, skip_nav


def main():
    docs, need, chosen = A.needed()
    P = {int(json.loads(l)['point']): json.loads(l) for l in open(os.path.join(OUT, 'points.jsonl'), encoding='utf-8')}
    C = json.load(open(A.F['quote'], encoding='utf-8')); ks = A.kev_scores(); base, filt, changed, n = [], [], 0, 0
    for d in docs:
        for it in d['items']:
            if it['point'] not in chosen: continue
            i = top_piece(ks(d['doc'], it['question']))
            if i not in it['gold']: continue
            g = C[d['doc']]['pieces'][str(i)]; U = g['units']; s = [r[it['question']] for r in g['scores']]
            q = P[int(it['point'])]['quote']; m = [A.matches(u, q) for u in U]; s2 = skip_nav(U, s)
            base.append(A.tied_mean(s, m)); filt.append(A.tied_mean(s2, m)); n += 1
            changed += top_piece(s) != top_piece(s2)
    print(f'part C, {n} points with a gold top piece: KEV {sum(base) / n:.3f}, KEV skipping navigation units {sum(filt) / n:.3f}; '
          f'{changed} picks change')
    prop = [json.loads(l) for l in open(os.path.join(OUT, 'propose_kev.jsonl'), encoding='utf-8')]
    print(f'stale points: {sum(nav(p["quote"]) for p in prop)} of {len(prop)} proposed quotes are navigation units')


if __name__ == '__main__':
    main()
