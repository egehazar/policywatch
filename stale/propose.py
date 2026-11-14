"""Proposed quote for the stale-points page. Part C of stale/PREREG_relocate2.md cleared its shipping bar on 2026-11-14:
given a gold piece, Kev's top sentence matched the curator's quote for 83% of points (BM25 56%, first sentence 19%).

For each stale point, Kev's top piece (stale/out/suggest_kev.jsonl) is cut into units exactly as in Part C
(relocate2.units), Kev with the r20 wrapper is asked the point's case question of every unit, and the top unit (the
earliest on ties) is the proposed quote. Points sharing a document and a top piece share one request per unit.
Usage  py -m stale.propose [port] [out dir]    -> <out dir>/propose_kev.jsonl (default stale/out; resumes per piece)
"""
import collections, json, os, re, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(HERE, 'out')
sys.path.insert(0, ROOT)
from stale.relocate2 import units, top_piece
from stale.match import words
from stale.triage import TEMPLATE


def nav(u):
    """A navigation unit: at least half of its words are link text in [square brackets] (a table of contents, a row of
    links). Added after part C's result: skipping them left part C's .831 unchanged (1 of 124 picks changed;
    stale/propose_nav.py), and a row of links is never a quote a curator can paste."""
    inside = sum(len(words(m)) for m in re.findall(r'\[([^\]]*)\]', u)); total = len(words(u))
    return total > 0 and inside / total >= .5


def skip_nav(U, scores):
    """Navigation units rank last, unless every unit is one."""
    if all(nav(u) for u in U): return scores
    return [x if not nav(u) else -1.0 for u, x in zip(U, scores)]


def run(port='9995', out=OUT, cache=None):
    """out: the folder holding points.jsonl and suggest_kev.jsonl (stale/out, or stale/wide/<collection>/out);
    cache: the score cache (default out/cache.sqlite, shared with every Kev step)."""
    from policywatch.scorer import Server, Cache, Scorer, qid
    F = os.path.join(out, 'propose_kev.jsonl')
    S = Scorer(Server(f'http://127.0.0.1:{port}'), Cache(cache or os.path.join(ROOT, 'out', 'cache.sqlite')))
    assert S.server.served == 'Kev-4B-Q8_0.gguf', 'port does not serve Kev-4B Q8'
    case = {r['point']: r['case_title'] for r in map(json.loads, open(os.path.join(out, 'points.jsonl'), encoding='utf-8'))}
    sug = [json.loads(l) for l in open(os.path.join(out, 'suggest_kev.jsonl'), encoding='utf-8')]
    done = {json.loads(l)['point'] for l in open(F, encoding='utf-8')} if os.path.exists(F) else set()
    groups = collections.defaultdict(list)                 # (doc, piece) -> the points whose top piece it is
    for s in sug:
        if s['point'] not in done and s['top']: groups[(s['doc'], s['top'][0]['piece'])].append(s)
    t0 = time.time()
    with open(F, 'a', encoding='utf-8') as f:
        for k, ((doc, i), ss) in enumerate(sorted(groups.items()), 1):
            U = units(ss[0]['top'][0]['text']); qs = sorted({TEMPLATE.format(case[s['point']]) for s in ss})
            rows = [S.score(u, qs) for u in U]
            for s in ss:
                q = TEMPLATE.format(case[s['point']]); sc = skip_nav(U, [r[qid(q)] for r in rows]); j = top_piece(sc)
                f.write(json.dumps({'point': s['point'], 'doc': doc, 'piece': i, 'unit': j, 'units': len(U), 'ties': sc.count(sc[j]),
                                    'score': round(sc[j], 4), 'quote': U[j]}, ensure_ascii=False) + '\n')
            f.flush()
            print(f'[{k}/{len(groups)} {time.time() - t0:.0f}s] {doc} piece {i}: {len(U)} units x {len(qs)} questions', flush=True)
    print('asked', S.asked, 'cache hits', S.hits)


if __name__ == '__main__':
    run(*sys.argv[1:])
