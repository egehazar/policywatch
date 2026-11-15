"""Evaluate the stale-point suggestions and the "not stated any more" question against full-read gold
(stale/PREREG_suggest.md). Reads stale/out/fullread/key.json, gold_<family>.json, human_gate.json (when present) and
stale/out/suggest_<arm>.jsonl.  Usage  py -m stale.suggest_eval  -> stale/out/suggest_result.json  ( --primary <family>: that key instead, -> suggest_result_<family>.json)
"""
import json, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(HERE, 'out')
FDIR = os.path.join(OUT, 'fullread')
sys.path.insert(0, ROOT)
from stale.suggest import drops

ARMS = ('kev', 'quote', 'quote_bm25', 'hunk', 'bm25', 'bge')
PRIMARY, SECOND = 'opus', 'sonnet'
SEED = 20261112; DRAWS = 2000
T_FLAG = 0.3578


def auroc(pos, neg):
    if not pos or not neg: return None
    return sum((x > y) + .5 * (x == y) for x in pos for y in neg) / (len(pos) * len(neg))


def kappa(a, b):
    n = len(a)
    if not n: return None
    po = sum(x == y for x, y in zip(a, b)) / n; pa = sum(a) / n; pb = sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return None if pe == 1 else (po - pe) / (1 - pe)


def ci(xs):
    xs = sorted(x for x in xs if x is not None)
    return [round(xs[int(.025 * len(xs))], 3), round(xs[int(.975 * len(xs)) - 1], 3)] if xs else None


def main(primary=PRIMARY, second=SECOND, out_name='suggest_result.json'):
    key = json.load(open(os.path.join(FDIR, 'key.json'), encoding='utf-8'))
    G = {f: json.load(open(os.path.join(FDIR, f'gold_{f}.json'), encoding='utf-8')) for f in (primary, second)
         if os.path.exists(os.path.join(FDIR, f'gold_{f}.json'))}
    assert primary in G, 'primary rater gold missing'
    S = {}
    for a in ARMS:
        rows = [json.loads(l) for l in open(os.path.join(OUT, f'suggest_{a}.jsonl'), encoding='utf-8')]
        S[a] = {int(r['point']): r for r in rows}
        assert {r['archive_head'] for r in rows} == {key['archive_head']}, f'{a}: archive head differs from the gold'
    R = {int(r['point']): r for r in drops()}
    label = {}                                     # point -> (doc, case label)
    for d, items in key['plan'].items():
        for it in items:
            if it['kind'] == 'stale':
                for p in it['points']: label[p] = (d, it['label'])
    assert set(label) == set(R), 'gold plan and stale list differ'
    gold = {p: set(G[primary]['gold'][d][l]) for p, (d, l) in label.items()}
    stated = {p: bool(g) for p, g in gold.items()}
    res = {'archive_head': key['archive_head'], 'points': len(R), 'stated': sum(stated.values()),
           'none': len(R) - sum(stated.values()), 'verify_stats': {f: G[f]['stats'] for f in G}}
    # rater quality: control recall, and agreement on stated/none where both raters read the batch
    rq = {}
    for f in G:
        ctl = [(d, it) for d, items in key['plan'].items() for it in items if it['kind'] == 'control' and it['label'] in G[f]['gold'].get(d, {})]
        rq[f] = {'controls': len(ctl), 'control_recall': round(sum(bool(set(G[f]['gold'][d][it['label']]) & set(it['gold'])) for d, it in ctl) / max(1, len(ctl)), 3),
                 'control_none': sum(not G[f]['gold'][d][it['label']] for d, it in ctl)}
    if second in G:
        shared = [(d, it['label']) for d, items in key['plan'].items() for it in items if it['kind'] == 'stale' and it['label'] in G[second]['gold'].get(d, {})]
        a = [bool(G[primary]['gold'][d][l]) for d, l in shared]; b = [bool(G[second]['gold'][d][l]) for d, l in shared]
        k = kappa(a, b)
        rq['stated_agreement'] = {'cases': len(shared), 'agree': sum(x == y for x, y in zip(a, b)), 'kappa': round(k, 3) if k is not None else None}
    res['raters'] = rq
    rng = random.Random(SEED)
    docs_all = sorted({R[p]['doc'] for p in R}); by_all = {d: [p for p in R if R[p]['doc'] == d] for d in docs_all}

    def boot(stat, docs, by):
        out = []
        for _ in range(DRAWS):
            smp = [p for d in (rng.choice(docs) for _ in docs) for p in by[d]]
            out.append(stat(smp))
        return out

    # 1. the "not stated any more" question
    top = {a: {p: (S[a][p]['top'][0]['score'] if S[a][p]['top'] else None) for p in R} for a in ARMS}
    nq = {}
    for a in ('kev', 'quote'):
        f = lambda P: auroc([top[a][p] for p in P if stated[p]], [top[a][p] for p in P if not stated[p]])
        nq[f'auroc_{a}_max'] = {'point': round(f(list(R)), 3) if f(list(R)) is not None else None, 'ci95': ci(boot(f, docs_all, by_all))}
    ab = [p for p in R if not S['hunk'][p]['top']]
    nq['hunk_abstain_as_none'] = {'abstained': len(ab), 'none_among_abstained': sum(not stated[p] for p in ab),
                                  'none_caught': f"{sum(not stated[p] for p in ab)} of {res['none']}"}
    fl = [p for p in R if top['kev'][p] < T_FLAG]
    nq['flag'] = {'T': T_FLAG, 'flagged': len(fl), 'none_among_flagged': sum(not stated[p] for p in fl)}
    res['not_stated_question'] = nq
    # 2. suggestions on stated points
    sug = {}
    for sname, cond in (('gone', lambda p: R[p]['status'] == 'gone'), ('partly', lambda p: R[p]['status'] == 'partly'), ('all', lambda p: True)):
        P = [p for p in R if cond(p) and stated[p]]
        docs = sorted({R[p]['doc'] for p in P}); by = {d: [p for p in P if R[p]['doc'] == d] for d in docs}
        hit = {a: {p: float(bool(S[a][p]['top']) and S[a][p]['top'][0]['piece'] in gold[p]) for p in P} for a in ARMS}
        f3 = {a: {p: float(any(t['piece'] in gold[p] for t in S[a][p]['top'][:3])) for p in P} for a in ARMS}
        perdoc = lambda a, ds: sum(sum(hit[a][p] for p in by[d]) / len(by[d]) for d in ds) / len(ds)
        row = {'stated_points': len(P), 'documents': len(docs),
               'p1_doc_mean': {a: round(perdoc(a, docs), 3) for a in ARMS},
               'p1_pooled': {a: round(sum(hit[a].values()) / len(P), 3) for a in ARMS},
               'found3_pooled': {a: round(sum(f3[a].values()) / len(P), 3) for a in ARMS},
               'hunk_answered': {'points': sum(1 for p in P if S['hunk'][p]['top']),
                                 'p1': round(sum(hit['hunk'][p] for p in P if S['hunk'][p]['top']) / max(1, sum(1 for p in P if S['hunk'][p]['top'])), 3)}}
        row['p1_doc_mean_leave_one_doc_out'] = {a: [round(min(perdoc(a, [x for x in docs if x != d]) for d in docs), 3),
                                                   round(max(perdoc(a, [x for x in docs if x != d]) for d in docs), 3)] for a in ARMS} if len(docs) > 1 else None
        for other in ARMS[1:]:
            diffs = []
            for _ in range(DRAWS):
                ds = [rng.choice(docs) for _ in docs]
                diffs.append(sum(sum(hit[other][p] - hit['kev'][p] for p in by[d]) / len(by[d]) for d in ds) / len(ds))
            row[f'{other}_minus_kev_doc_mean'] = {'point': round(perdoc(other, docs) - perdoc('kev', docs), 3), 'ci95': ci(diffs)}
        sug[sname] = row
    res['suggestions'] = sug
    # readings
    hg_path = os.path.join(FDIR, 'human_gate.json')
    hg = json.load(open(hg_path, encoding='utf-8')) if os.path.exists(hg_path) else None
    gate = None if hg is None else bool(hg.get('kappa') is not None and hg['kappa'] >= .6)
    au = nq['auroc_kev_max']['ci95']; cr = rq[primary]['control_recall']
    conds = {'auroc_lower_ge_.70': bool(au and au[0] >= .70), 'flags_ge_8': nq['flag']['flagged'] >= 8,
             'flag_precision_ge_.75': nq['flag']['flagged'] > 0 and nq['flag']['none_among_flagged'] >= .75 * nq['flag']['flagged'],
             'control_recall_ge_.85': cr >= .85, 'human_gate': gate}
    res['label_conditions'] = conds
    res['label_ships'] = 'PENDING HUMAN GATE' if gate is None and all(v for k, v in conds.items() if k != 'human_gate') else \
        bool(all(conds.values()))
    lead = [a for a in ARMS[1:] if sug['gone'][f'{a}_minus_kev_doc_mean']['ci95'] and sug['gone'][f'{a}_minus_kev_doc_mean']['ci95'][0] > 0]
    res['page_leads_with'] = lead[0] if len(lead) == 1 else ('kev' if not lead else max(lead, key=lambda a: sug['gone']['p1_doc_mean'][a]))
    res['status'] = 'PROVISIONAL (human gate pending)' if gate is None else ('VOID (human gate failed)' if gate is False else 'FINAL')
    res['human_gate'] = hg
    with open(os.path.join(OUT, out_name), 'w', encoding='utf-8') as f: json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    if '--primary' in sys.argv:            # exploratory: another rater's key in place of Opus's (stale/PREREG_fullread_gpt.md)
        f = sys.argv[sys.argv.index('--primary') + 1]
        main(primary=f, second=PRIMARY, out_name=f'suggest_result_{f}.json')
    else:
        main()
