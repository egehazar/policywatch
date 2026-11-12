"""Where is the case stated now? For each approved point whose quote dropped in a platform edit, rank the pieces of
the document's CURRENT version for the point's case question and keep the top 3 for the curator page.

Arms (the pre-registered relocation test, stale/PREREG_relocate.md, measures which one ranks curator-quoted passages
highest on points whose quote is still present; the page uses the arm named when it is built):
  bm25  the case title's words, no model, instant
  bge   bge-small-en-v1.5 with its retrieval instruction (needs sentence_transformers)
  kev   Kev-4B p(yes) for the case question on each piece (cached in out/cache.sqlite; about 1.9 s per piece-question
        on this CPU in the relocation run, so all 141 points take hours)
  quote      bge-small cosine between the point's OLD quote (HTML removed) and the best quote-length window of each
             piece (windows of max(quote words, 12) words, half-window stride): the obvious tool when the old quote
             exists (stale/PREREG_suggest.md); per point, not per case
  quote_bm25 BM25 with the old quote as the query
  hunk       the new side of the edit that removed the quote (stale/triage.py align, in the drop version), located in
             the current text by word 6-gram coverage; abstains (no suggestion) when the edit left no similar
             passage, when there is no aligned passage, or when that passage is no longer in the current text
A suggestion is a place to look, not a verdict. The case may no longer be stated anywhere (the point should then be
declined), and nothing here decides that.

Usage  py -m stale.suggest <pga-versions> <bm25|bge|kev|quote|quote_bm25|hunk> [server]   -> stale/out/suggest_<arm>.jsonl
"""
import html, json, os, re, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(HERE, 'out')
sys.path.insert(0, ROOT)
from policywatch import archive
from policywatch.diffing import paras
from policywatch.watch import pieces
from stale.relocate import PIECE, BGE_INSTR, bm25
from stale.triage import TEMPLATE

TOP = 3
PER_POINT = ('quote', 'quote_bm25', 'hunk')       # arms that rank per point (they use the old quote), not per case


def plain(quote):
    """A ToS;DR quote as plain text: tags removed, entities decoded, whitespace collapsed."""
    return ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', quote)).split())


def drops():
    rows = [json.loads(l) for l in open(os.path.join(OUT, 'points.jsonl'), encoding='utf-8')]
    return [r for r in rows if r['status'] in ('gone', 'partly') and r.get('drop_kind') == 'platform edit']


def run(arch, arm, server='http://127.0.0.1:9995'):
    head = archive.git(arch, 'rev-parse', 'HEAD').strip()
    R = drops(); docs = sorted({r['doc'] for r in R})
    P = {d: [p for p in pieces('\n\n'.join(paras(archive.git(arch, 'show', f'HEAD:{d}'))), PIECE) if p.strip()] for d in docs}
    cases = {d: sorted({r['case_title'] for r in R if r['doc'] == d}) for d in docs}
    scores = {}                                   # (doc, case) -> [score per piece]
    if arm == 'bm25':
        for d in docs:
            for c in cases[d]: scores[(d, c)] = bm25(c, P[d])
    elif arm == 'bge':
        os.environ.setdefault('HF_HUB_OFFLINE', '1'); os.environ.setdefault('TRANSFORMERS_OFFLINE', '1')
        from sentence_transformers import SentenceTransformer
        m = SentenceTransformer('BAAI/bge-small-en-v1.5', device='cpu')
        for d in docs:
            E = m.encode(P[d], normalize_embeddings=True, batch_size=32)
            Q = m.encode([BGE_INSTR + c for c in cases[d]], normalize_embeddings=True)
            for k, c in enumerate(cases[d]): scores[(d, c)] = [float(x) for x in (Q[k] @ E.T)]
    elif arm == 'quote':
        os.environ.setdefault('HF_HUB_OFFLINE', '1'); os.environ.setdefault('TRANSFORMERS_OFFLINE', '1')
        from sentence_transformers import SentenceTransformer
        m = SentenceTransformer('BAAI/bge-small-en-v1.5', device='cpu')
        for d in docs:
            for r in (r for r in R if r['doc'] == d):
                q = plain(r['quote']); w = max(len(q.split()), 12); step = max(1, w // 2)
                wins, owner = [], []
                for i, piece in enumerate(P[d]):
                    ws = piece.split()
                    for a in range(0, max(1, len(ws) - w + step), step):
                        wins.append(' '.join(ws[a:a + w])); owner.append(i)
                E = m.encode(wins, normalize_embeddings=True, batch_size=64)
                Q = m.encode([q], normalize_embeddings=True)[0]           # passage-to-passage: no instruction
                best = [-1.0] * len(P[d])
                for i, x in zip(owner, (E @ Q).tolist()): best[i] = max(best[i], x)
                scores[(d, r['point'])] = best
    elif arm == 'quote_bm25':
        for d in docs:
            for r in (r for r in R if r['doc'] == d): scores[(d, r['point'])] = bm25(plain(r['quote']), P[d])
    elif arm == 'hunk':
        from stale.triage import qcov
        A = {x['point']: x for x in map(json.loads, open(os.path.join(OUT, 'passages.jsonl'), encoding='utf-8'))}
        for r in R:
            a = A.get(r['point']); pas = (a or {}).get('passage')
            if not pas or pas.get('removed') or not pas.get('new', '').strip(): scores[(r['doc'], r['point'])] = None; continue
            cov = [qcov(pas['new'], piece) for piece in P[r['doc']]]
            scores[(r['doc'], r['point'])] = cov if max(cov) >= .3 else None
    elif arm == 'kev':
        from policywatch.scorer import Server, Cache, Scorer, qid
        S = Scorer(Server(server), Cache(os.path.join(ROOT, 'out', 'cache.sqlite')))
        assert S.server.served == 'Kev-4B-Q8_0.gguf', f'port serves {S.server.served}, not Kev-4B Q8'
        t0 = time.time()
        for n, d in enumerate(sorted(docs, key=lambda d: len(P[d]) * len(cases[d])), 1):
            qs = [TEMPLATE.format(c) for c in cases[d]]; per = []
            for piece in P[d]:
                ps = S.score(piece, qs); per.append([ps[qid(q)] for q in qs])
            for k, c in enumerate(cases[d]): scores[(d, c)] = [row[k] for row in per]
            print(f'[{n}/{len(docs)} {time.time() - t0:.0f}s] {d}: {len(P[d])} pieces x {len(qs)} questions', flush=True)
        print('asked', S.asked, 'cache hits', S.hits)
    else:
        raise SystemExit(f'unknown arm {arm}')
    path = os.path.join(OUT, f'suggest_{arm}.jsonl')
    with open(path, 'w', encoding='utf-8') as f:
        for r in R:
            s = scores[(r['doc'], r['point'] if arm in PER_POINT else r['case_title'])]
            order = [] if s is None else sorted(range(len(s)), key=lambda i: -s[i])[:TOP]       # None: the arm abstains
            f.write(json.dumps({'point': r['point'], 'doc': r['doc'], 'archive_head': head, 'arm': arm, 'n_pieces': len(P[r['doc']]),
                                'top': [{'piece': i, 'score': round(s[i], 4), 'text': P[r['doc']][i]} for i in order]},
                               ensure_ascii=False) + '\n')
    print(path, len(R), 'points,', len(docs), 'documents,', sum(len(P[d]) for d in docs), 'pieces')


if __name__ == '__main__':
    run(*sys.argv[1:])
