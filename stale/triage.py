"""For each approved ToS;DR point whose quote vanished in a platform edit: the passage that replaced it, and the
decision model's answer to the point's case question on the old and on the new passage.

The model is a comparator here too: |p_new - p_old| on the same question says whether the edit moved the point.
Whether the point still holds is a person's call; the output is a triage list for a curator, with the evidence.

Usage  py -m stale.triage prep  <pga-versions>          -> stale/out/passages.jsonl (no model)
       py -m stale.triage score [server]                  -> stale/out/triage.jsonl (Kev-4B, cached in out/cache.sqlite)
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(HERE, 'out')
sys.path.insert(0, ROOT)
from policywatch import archive
from policywatch.diffing import diff, paras
from policywatch.watch import pieces, REGION_CAP
from stale.match import words, grams, coverage

TEMPLATE = 'Does the text state or clearly imply the following: {}?'      # data/bank.json's template


def qcov(quote, text):
    qw = words(quote, quote=True); ws = words(text)
    return coverage(qw, grams(qw), ' ' + ' '.join(ws) + ' ', grams(ws))


def tri(ws):
    return {tuple(ws[i:i + 3]) for i in range(len(ws) - 2)}


def align(quote, O, Nw, max_win=4, min_sim=.25):
    """Old window: the fewest consecutive old paragraphs (up to max_win) holding >= .8 of the quote, else the best one.
    New window: the consecutive new paragraphs (up to max_win) whose word 3-grams best cover the old window's.
    Both get one paragraph of context on each side. min_sim (a fixed heuristic): below it the old text has no
    counterpart, and the new side is the context alone ('removed')."""
    best = None
    for w in range(1, max_win + 1):
        for i in range(len(O) - w + 1):
            c = qcov(quote, '\n'.join(O[i:i + w]))
            if best is None or c > best[0] + 1e-9: best = (c, i, w)
        if best and best[0] >= .8: break
    if best is None or best[0] < .5: return None
    c, i, w = best
    ot = tri(words(' '.join(O[i:i + w])))
    if not ot: return None
    cand = []
    for v in range(1, max_win + 1):
        for j in range(len(Nw) - v + 1):
            nt = tri(words(' '.join(Nw[j:j + v])))
            if nt: cand.append((len(ot & nt) / len(ot) - .02 * v, j, v, len(ot & nt) / len(ot)))
    s, j, v, sim = max(cand, default=(0, 0, 0, 0.0))
    ctx = lambda P, a, b: '\n\n'.join(P[max(0, a - 1):min(len(P), b + 1)])
    if sim < min_sim:
        return {'old': ctx(O, i, i + w), 'new': '', 'quote_coverage': round(c, 3), 'similarity': round(sim, 3), 'removed': True}
    return {'old': ctx(O, i, i + w), 'new': ctx(Nw, j, j + v), 'quote_coverage': round(c, 3), 'similarity': round(sim, 3),
            'removed': False, 'new_quote_coverage': round(qcov(quote, '\n'.join(Nw[j:j + v])), 3)}


def prep(arch):
    rows = [json.loads(l) for l in open(os.path.join(OUT, 'points.jsonl'), encoding='utf-8')]
    sel = [r for r in rows if r['status'] in ('gone', 'partly') and r.get('drop_kind') == 'platform edit']
    out = []
    for r in sel:
        old = archive.git(arch, 'show', f"{r['last_present']['commit']}:{r['doc']}")
        new = archive.git(arch, 'show', f"{r['dropped_at']['commit']}:{r['doc']}")
        ch = diff(old, new)
        rec = {k: r[k] for k in ('platform', 'point', 'case_id', 'case_title', 'classification', 'doc', 'quote', 'status',
                                 'point_updated_at', 'drop_after_point_update')}
        rec.update(question=TEMPLATE.format(r['case_title']), last_present=r['last_present'], dropped_at=r['dropped_at'],
                   n_changed=ch.n_changed, passage=align(r['quote'], paras(old), paras(new)))
        out.append(rec)
    with open(os.path.join(OUT, 'passages.jsonl'), 'w', encoding='utf-8') as f:
        for x in out: f.write(json.dumps(x, ensure_ascii=False) + '\n')
    print(len(out), 'points dropped in a platform edit;', sum(1 for x in out if x['passage']), 'placed;',
          sum(1 for x in out if x['passage'] and x['passage']['removed']), 'with no similar new passage (removed)')


def score(server='http://127.0.0.1:9995'):
    from policywatch.scorer import Server, Cache, Scorer, qid
    rows = [json.loads(l) for l in open(os.path.join(OUT, 'passages.jsonl'), encoding='utf-8')]
    S = Scorer(Server(server), Cache(os.path.join(ROOT, 'out', 'cache.sqlite')))
    with open(os.path.join(OUT, 'triage.jsonl'), 'w', encoding='utf-8') as f:
        for r in rows:
            if r['passage']:
                k = qid(r['question'])
                side = {}
                for s in ('old', 'new'):
                    txt = r['passage'][s]
                    side[s] = max((S.score(t, [r['question']])[k] for t in pieces(txt, REGION_CAP) if t.strip()), default=0.0)
                r.update(p_old=side['old'], p_new=side['new'], dp=round(abs(side['new'] - side['old']), 4))
            f.write(json.dumps(r, ensure_ascii=False) + '\n'); f.flush()
            print(r['platform'], r['point'], r.get('p_old'), r.get('p_new'), flush=True)
    print('asked', S.asked, 'cache hits', S.hits)


if __name__ == '__main__':
    if sys.argv[1] == 'prep': prep(sys.argv[2])
    else: score(*sys.argv[2:])
