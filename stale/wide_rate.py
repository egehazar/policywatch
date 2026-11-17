"""Blind rating of the curator page's unrated suggestions (stale/PLAN_wide_rate.md).

The 28 documents whose suggestions on the page no one has rated: the two cascade runs' 26 (stale/missing_wide.py's
20, stale/missing_rest.py's 6) and Pinterest's two, which the watch re-scored on their new text (stale/missing_watch.py).
Each as the page builds it: the same candidate cases (no approved point on the platform, stale.missing_page.approved),
on the current text. Two card arms, top 10 per document each:
- PAGE: the page's suggestions, Kev (Kev-4B) on the reranker's top 3 passages per case, with the best of those passages;
- RERANK: the reranker (bge-reranker-v2-m3) on every passage, with its best passage;
plus 20 random controls (a random candidate case and a random passage of the same document). Cards that both arms
pick (same document, case and passage) are rated once.

cards  -> stale/audit_wide_a/, stale/audit_wide_b/ (cards shuffled, then halved; one fresh Claude Opus subagent per
          folder, reading only its folder), stale/out/wide_rate_key.json
score  -> stale/out/wide_rate_result.json
"""
import collections, json, os, random, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(HERE, 'out')
sys.path.insert(0, ROOT)
from stale.missing import TOP, best, wilson
from stale import missing_wide, missing_rest, missing_watch
from stale.missing_page import approved, english

SEED = 20261117; DRAWS = 2000; RANDOM_CARDS = 20; MAX_RANDOM_YES = 3
KEY = os.path.join(OUT, 'wide_rate_key.json'); RESULT = os.path.join(OUT, 'wide_rate_result.json')
FOLDERS = {x: os.path.join(HERE, f'audit_wide_{x}') for x in 'ab'}
SRC = ((missing_wide.DOCS, 'missing_wide'), (missing_rest.DOCS, 'missing_rest'))
ARMS = ('PAGE', 'RERANK')
VERD = ('YES', 'PARTLY', 'NO')


def docs():
    """[(run, doc dict, {arm: rows}, candidate cases)], built the way stale.missing_page.build builds the page."""
    wk, wr = missing_watch.current('KEV'), missing_watch.current('RERANK')
    out = []
    for path, run in SRC:
        S = {a: json.load(open(os.path.join(OUT, f'{run}_{a.lower()}.json'), encoding='utf-8')) for a in ('KEV', 'RERANK')}
        for d in json.load(open(path, encoding='utf-8'))['docs']:
            if d['doc'] not in S['KEV']: continue
            neg = [c for c in d['negatives'] if c.strip() not in approved(d['doc'].split('/', 1)[0])]
            rows = {'PAGE': S['KEV'][d['doc']], 'RERANK': S['RERANK'][d['doc']]}
            if d['doc'] in wk:
                assert d['doc'] in wr, f'{d["doc"]}: watch has Kev scores but no reranker scores'
                d, rows = wk[d['doc']][0], {'PAGE': wk[d['doc']][1], 'RERANK': wr[d['doc']][1]}
            assert all(len(r) == len(d['pieces']) for r in rows.values()), d['doc']
            out.append((run, d, rows, neg))
    seen = {d['doc'] for _, d, _, _ in out}
    for doc in sorted(set(wk) - seen):          # Pinterest's two: tested earlier on their old text, shown on the new
        d = wk[doc][0]; neg = [c for c in d['negatives'] if c.strip() not in approved(doc.split('/', 1)[0])]
        out.append(('missing_watch', d, {'PAGE': wk[doc][1], 'RERANK': wr[doc][1]}, neg))
    return out


def cards():
    assert not os.path.exists(KEY), 'cards exist already: never rebuild them after rating has started'
    rng = random.Random(SEED); D = docs(); C = collections.defaultdict(dict)   # (doc, case, piece) -> {arm: rank}
    info = {d['doc']: (run, english(d['pieces']), d['pieces']) for run, d, _, _ in D}
    for run, d, rows, neg in D:
        for a in ARMS:
            sc = {c: best(rows[a], c) for c in neg}
            for r, c in enumerate(sorted(neg, key=lambda c: -sc[c][0])[:TOP], 1): C[(d['doc'], c, sc[c][1])][a] = r
    for _ in range(RANDOM_CARDS):
        run, d, rows, neg = rng.choice(D); c = rng.choice(neg); i = rng.randrange(len(d['pieces']))
        C[(d['doc'], c, i)]['RANDOM'] = 0
    order = sorted(C); rng.shuffle(order); half = (len(order) + 1) // 2
    key = {}
    for x, part in (('a', order[:half]), ('b', order[half:])):
        os.makedirs(FOLDERS[x], exist_ok=True)
        L = [f'# {len(part)} cards', '', 'For each card: does the passage state or clearly imply the case? Answer in verdicts.json.', '']
        for doc, c, i in part:
            cid = f'W{len(key) + 1:03d}'
            key[cid] = {'doc': doc, 'case': c, 'piece': i, 'arms': C[(doc, c, i)], 'folder': x, 'run': info[doc][0],
                        'english': info[doc][1]}
            L += [f'## {cid}', f'**Case:** {c}', '', '**Passage:**', '', '```', info[doc][2][i].strip(), '```', '']
        with open(os.path.join(FOLDERS[x], 'cards.md'), 'w', encoding='utf-8', newline='\n') as f: f.write('\n'.join(L) + '\n')
        shutil.copyfile(os.path.join(HERE, 'audit_states', 'README.md'), os.path.join(FOLDERS[x], 'README.md'))
        with open(os.path.join(FOLDERS[x], 'verdicts.json'), 'w', encoding='utf-8', newline='\n') as f:
            json.dump({cid: {'verdict': '', 'why': ''} for cid in key if key[cid]['folder'] == x}, f, indent=1)
    with open(KEY, 'w', encoding='utf-8') as f: json.dump(key, f, indent=1, ensure_ascii=False)
    n = {a: sum(a in v['arms'] for v in key.values()) for a in ARMS + ('RANDOM',)}
    print(len(key), 'cards;', n, '; both arms:', sum(all(a in v['arms'] for a in ARMS) for v in key.values()),
          '; folder a', sum(v['folder'] == 'a' for v in key.values()), ', b', sum(v['folder'] == 'b' for v in key.values()))


def share(K, V, cs):
    y = sum(V[c]['verdict'] == 'YES' for c in cs)
    return {'cards': len(cs), 'yes': y, 'yes_share': round(y / len(cs), 3) if cs else None, 'wilson95': wilson(y, len(cs)),
            'yes_or_partly_share': round(sum(V[c]['verdict'] != 'NO' for c in cs) / len(cs), 3) if cs else None}


def diff(K, V, a, b, rng, keep=lambda k: True):
    """YES share of arm a minus arm b over the documents' top-10 cards, 95% interval from resampling documents."""
    by = collections.defaultdict(list)
    for c in K:
        if keep(K[c]): by[K[c]['doc']].append(c)
    docs = sorted(by)
    def sh(ds, arm):
        cs = [c for d in ds for c in by[d] if arm in K[c]['arms']]
        return sum(V[c]['verdict'] == 'YES' for c in cs) / len(cs) if cs else 0
    ds = sorted(sh(s, a) - sh(s, b) for s in ([rng.choice(docs) for _ in docs] for _ in range(DRAWS)))
    return {'documents': len(docs), 'point': round(sh(docs, a) - sh(docs, b), 3),
            'ci95': [round(ds[int(.025 * DRAWS)], 3), round(ds[int(.975 * DRAWS) - 1], 3)]}


def score():
    K = json.load(open(KEY, encoding='utf-8')); V = {}
    for x in FOLDERS: V.update(json.load(open(os.path.join(FOLDERS[x], 'verdicts.json'), encoding='utf-8')))
    assert set(V) == set(K) and all(V[c]['verdict'] in VERD for c in V), 'verdicts incomplete'
    rng = random.Random(SEED + 1)
    rnd = [V[c]['verdict'] for c in K if 'RANDOM' in K[c]['arms']]
    valid = rnd.count('YES') <= MAX_RANDOM_YES
    arm = lambda a, f=lambda k: True: [c for c in K if a in K[c]['arms'] and f(K[c])]
    d = diff(K, V, 'PAGE', 'RERANK', rng)
    res = {'random_yes': rnd.count('YES'), 'random_n': len(rnd), 'valid': valid,
           'precision_at_10': {a: share(K, V, arm(a)) for a in ARMS}, 'PAGE_minus_RERANK': d}
    p = res['precision_at_10']['PAGE']['yes_share']
    res['reading_page'] = ('NOT VALID (random controls)' if not valid else
                           'in the predicted range' if .55 <= p <= .75 else 'below the predicted range' if p < .55 else
                           'above the predicted range')
    res['reading_compare'] = ('NOT VALID (random controls)' if not valid else 'PAGE better' if d['ci95'][0] > 0 else
                              'RERANK better' if d['ci95'][1] < 0 else 'no difference shown')
    # descriptive, read nothing from these
    res['by_run'] = {r: {a: share(K, V, arm(a, lambda k: k['run'] == r)) for a in ARMS} for r in ('missing_wide', 'missing_rest', 'missing_watch')}
    res['english_only'] = {a: share(K, V, arm(a, lambda k: k['english'])) for a in ARMS}
    res['english_only']['PAGE_minus_RERANK'] = diff(K, V, 'PAGE', 'RERANK', random.Random(SEED + 2), lambda k: k['english'])
    res['by_rank'] = {a: {'1-5': share(K, V, [c for c in arm(a) if K[c]['arms'][a] <= 5]),
                          '6-10': share(K, V, [c for c in arm(a) if K[c]['arms'][a] > 5])} for a in ARMS}
    res['by_doc'] = {doc: {a: share(K, V, arm(a, lambda k: k['doc'] == doc)) for a in ARMS}
                     for doc in sorted({k['doc'] for k in K.values()})}
    res['by_folder'] = {x: {a: share(K, V, arm(a, lambda k: k['folder'] == x)) for a in ARMS} for x in FOLDERS}
    res['verdict_counts'] = dict(collections.Counter(V[c]['verdict'] for c in K))
    with open(RESULT, 'w', encoding='utf-8') as f: json.dump(res, f, indent=1, ensure_ascii=False)
    print(json.dumps({k: res[k] for k in ('random_yes', 'random_n', 'valid', 'precision_at_10', 'PAGE_minus_RERANK',
                                          'reading_page', 'reading_compare', 'english_only', 'by_rank')}, indent=1))


if __name__ == '__main__':
    {'cards': cards, 'score': score}[sys.argv[1]]()
