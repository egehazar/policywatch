"""Part D of the relocation follow-up (stale/PREREG_relocate_d.md): the relocation arms on Open Terms Archive's contrib
collection, the text the wider curator pages run on, and the reranker-first cascade as the cheaper pipeline.

prep    no model. Points of stale/wide/contrib/out/points.jsonl whose quote is still in the current text, outside the
        20 platforms and outside part B's 41 services, drawn with a fixed seed (up to PER_SERVICE per ToS;DR service,
        TARGET points) -> stale/out/contrib_docs.json, in the format of heldout_docs.json
kev     KEV with the r20 wrapper: stale.relocate_b.kev, unchanged, pointed at contrib_docs.json -> contrib_kev.json
base    RERANK, BGE, BM25: stale.relocate_b.base, unchanged (needs the sentence-transformers venv) -> contrib_base.json
eval    -> stale/out/contrib_result.json
Usage   py -m stale.relocate_d prep | kev [port] | eval;   <venv python> -m stale.relocate_d base
"""
import glob, json, math, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(HERE, 'out')
sys.path.insert(0, ROOT)
from stale.relocate import PIECE, GOLD_MIN, GOLD_MAX, KS, psha, hit
from stale.relocate2 import boot, reading
from stale.match import words
from stale.triage import TEMPLATE, qcov

SEED = 20261115; PER_SERVICE = 5; TARGET = 200; TOPK = 10; MARGIN = -.03
WIDE = os.path.join(HERE, 'wide', 'contrib')
DOCS = os.path.join(OUT, 'contrib_docs.json')
F = {a: os.path.join(OUT, f'contrib_{a}.json') for a in ('kev', 'base')}
EN = set('the of and to in a is that for you we or by be this are with as on your may our any not it from at us'.split())


def current_pieces(path):
    from policywatch import archive
    from policywatch.diffing import paras
    from policywatch.watch import pieces
    from stale.wide import vdir
    text = '\n\n'.join(paras(archive.git(vdir('contrib'), 'show', f'HEAD:{path}')))
    return text, [p for p in pieces(text, PIECE) if p.strip()]


def prep():
    M = json.load(open(os.path.join(WIDE, 'map.json'), encoding='utf-8'))['mapped']
    rows = [json.loads(l) for l in open(os.path.join(WIDE, 'out', 'points.jsonl'), encoding='utf-8')]
    part_b = {json.load(open(f, encoding='utf-8'))['service'] for f in glob.glob(os.path.join(HERE, 'data', 'heldout', '*.json'))}
    by_sid = {}
    for r in rows:
        sid = M[r['platform']]['tosdr_id']
        if r['status'] == 'present' and sid not in part_b and len(words(r['quote'], quote=True)) >= 6:
            by_sid.setdefault(sid, []).append(r)
    texts, chosen = {}, []
    sids = sorted(by_sid); random.Random(SEED).shuffle(sids)
    for sid in sids:
        pts = sorted(by_sid[sid], key=lambda r: r['point']); random.Random(f'{SEED}-{sid}').shuffle(pts); took = 0
        for r in pts:
            if took >= PER_SERVICE: break
            if r['doc'] not in texts: texts[r['doc']] = current_pieces(r['doc'])
            text, P = texts[r['doc']]; ws = words(text)
            if not (2000 <= len(text) <= 150_000 and ws and sum(w in EN for w in ws) / len(ws) >= .2): continue
            gold = [i for i, x in enumerate(P) if qcov(r['quote'], x) >= GOLD_MIN]
            if not 1 <= len(gold) <= GOLD_MAX: continue
            chosen.append((sid, r, gold)); took += 1
        if len(chosen) >= TARGET: break
    docs = {}
    for sid, r, gold in chosen:
        d = docs.setdefault(r['doc'], {'doc': r['doc'], 'service': sid, 'items': []})
        d['items'].append({'point': r['point'], 'platform': r['platform'], 'case_title': r['case_title'], 'status': 'present',
                           'question': TEMPLATE.format(r['case_title']), 'gold': gold})
    out = []
    for path, d in sorted(docs.items()):
        P = texts[path][1]; cases = sorted({it['case_title'] for it in d['items']})
        out.append({**d, 'chars': sum(len(x) for x in P), 'pieces': P, 'cases': cases,
                    'questions': [TEMPLATE.format(c) for c in cases], 'pieces_sha': psha(P)})
    with open(DOCS, 'w', encoding='utf-8') as f:
        json.dump({'order': [r['point'] for _, r, _ in chosen], 'docs': out}, f, ensure_ascii=False)
    print(len(chosen), 'points,', len({s for s, _, _ in chosen}), 'services,', len(out), 'documents,',
          sum(len(d['pieces']) for d in out), 'pieces,', sum(len(d['pieces']) * len(d['questions']) for d in out), 'cells;',
          len(by_sid), 'services had a present point outside part B')


def _point_b():
    from stale import relocate_b
    relocate_b.DOCS, relocate_b.F = DOCS, {**relocate_b.F, **F}
    return relocate_b


def evaluate():
    from stale.wide import vdir
    D = json.load(open(DOCS, encoding='utf-8'))['docs']
    K, B = (json.load(open(F[a], encoding='utf-8')) for a in ('kev', 'base'))
    assert all(d['doc'] in K and K[d['doc']]['pieces_sha'] == psha(d['pieces']) for d in D)
    assert all(B['pieces_sha'][d['doc']] == psha(d['pieces']) for d in D)
    arm = {'KEV': lambda d, q: [s[q] for s in K[d]['scores']], 'RERANK': lambda d, q: B['RERANK'][d][q],
           'BM25': lambda d, q: B['BM25'][d][q], 'BGE': lambda d, q: B['BGE'][d][q]}
    asked = {}

    def cascade(d, q):
        s0 = arm['RERANK'](d, q); cut = sorted(s0, reverse=True)[min(TOPK, len(s0)) - 1]   # pieces tied with the 10th stay
        keep = {i for i, x in enumerate(s0) if x >= cut}; k = arm['KEV'](d, q); asked[(d, q)] = len(keep)
        return [k[i] if i in keep else -1.0 for i in range(len(k))]
    arm['CASCADE_RERANK'] = cascade
    per = []
    for d in D:
        n = len(d['pieces'])
        for it in d['items']:
            row = {'point': it['point'], 'doc': d['service'], 'n_pieces': n}      # 'doc' holds the service: the cluster
            for a, f in arm.items():
                hk, rr = hit(f(d['doc'], it['question']), it['gold']); row[a] = {'hit': hk, 'rr': rr}
            g = len(it['gold']); row['RANDOM'] = {'hit': {k: 1 - math.comb(n - g, k) / math.comb(n, k) if n - g >= k else 1.0 for k in KS}, 'rr': 0}
            per.append(row)
    names = list(arm) + ['RANDOM']; N = len(per)
    res = {'points': N, 'services': len({r['doc'] for r in per}), 'documents': len(D),
           'archive_head': __import__('subprocess').run(['git', '-C', vdir('contrib'), 'rev-parse', 'HEAD'], capture_output=True, encoding='utf-8').stdout.strip(),
           'hit_at': {a: {k: round(sum(r[a]['hit'][k] for r in per) / N, 3) for k in KS} for a in names},
           'mrr': {a: round(sum(r[a]['rr'] for r in per) / N, 3) for a in names if a != 'RANDOM'}}
    d_ = lambda a, b: (lambda r: r[a]['hit'][1] - r[b]['hit'][1])
    for a, b in (('KEV', 'BM25'), ('KEV', 'BGE'), ('KEV', 'RERANK'), ('CASCADE_RERANK', 'KEV')):
        res[f'{a}_minus_{b}'] = boot(per, d_(a, b))
    cells = sum(len(d['pieces']) * len(d['questions']) for d in D)
    res['cost'] = {'KEV_sec_per_cell': round(sum(K[d['doc']]['sec'] for d in D) / cells, 3),
                   'RERANK_sec_per_cell': round(B['rerank_sec'] / cells, 3), 'cells': cells,
                   'cascade_kev_cells': sum(asked.values()), 'cascade_kev_share': round(sum(asked.values()) / cells, 3)}
    res['reading'] = {
        'D0_replication': 'REPLICATED' if res['KEV_minus_BM25']['raw'][0] > 0 and res['KEV_minus_BGE']['raw'][0] > 0 else 'NOT REPLICATED',
        'D1_cascade': 'CASCADE ADOPTED' if res['CASCADE_RERANK_minus_KEV']['raw'][0] >= MARGIN else 'KEV KEPT',
        'D2_reranker': reading(res['KEV_minus_RERANK']['raw'], 'DECISION MODEL BETTER THAN THE RERANKER', 'RERANKER BETTER', 'NO DIFFERENCE SHOWN')}
    with open(os.path.join(OUT, 'contrib_result.json'), 'w', encoding='utf-8') as f: json.dump({'result': res, 'rows': per}, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'prep': prep()
    elif cmd == 'kev': _point_b().kev(*sys.argv[2:])
    elif cmd == 'base': _point_b().base()
    elif cmd == 'eval': evaluate()
    else: raise SystemExit(__doc__)
