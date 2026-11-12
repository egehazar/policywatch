"""Human gate for stale/PREREG_suggest.md: about 60 blind (case, passage) items for Ege, and the agreement score.

sample: 60 items, fixed by seed, from three strata over the 141 stale points:
  cited    pieces the primary rater (Opus) cited for a stale case                     (22)
  uncited  arm top-1 pieces the primary rater did not cite for that case, all arms    (23)
  none     the 'none' cases (primary rater found no passage) with Kev's top piece      (all, up to 15)
A short stratum is filled from the others in the order cited, uncited. Items are shuffled; ids say nothing.
Writes audit/gate/data.json (what Ege sees) and stale/out/fullread/gate_key.json (stratum, rater label).
score: reads stale/out/fullread/gate_answers.json ({id: {"v": "yes"|"no"|"unsure"}}, from the page's db) and writes
stale/out/fullread/human_gate.json: Cohen's kappa between Ege and the primary rater on yes/no answers.

Usage  py -m stale.gate sample <pga-versions>   |   py -m stale.gate score
"""
import json, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(HERE, 'out')
FDIR = os.path.join(OUT, 'fullread'); PAGE = os.path.join(ROOT, 'audit', 'gate', 'data.json')
sys.path.insert(0, ROOT)
from policywatch import archive
from policywatch.diffing import paras
from policywatch.watch import pieces
from stale.relocate import PIECE
from stale.suggest import drops
from stale.suggest_eval import ARMS, kappa

SEED = 20261112
SIZES = {'cited': 22, 'uncited': 23, 'none': 15}


def sample(arch):
    key = json.load(open(os.path.join(FDIR, 'key.json'), encoding='utf-8'))
    head = archive.git(arch, 'rev-parse', 'HEAD').strip(); assert head == key['archive_head'], 'archive moved'
    G = json.load(open(os.path.join(FDIR, 'gold_opus.json'), encoding='utf-8'))['gold']
    C = json.load(open(os.path.join(HERE, 'data', 'cases.json'), encoding='utf-8'))
    S = {a: {int(json.loads(l)['point']): json.loads(l) for l in open(os.path.join(OUT, f'suggest_{a}.jsonl'), encoding='utf-8')} for a in ARMS}
    R = {int(r['point']): r for r in drops()}
    lab = {}
    for d, items in key['plan'].items():
        for it in items:
            if it['kind'] == 'stale':
                for p in it['points']: lab[p] = (d, it['label'], it['case'])
    cited, uncited, none = [], [], []
    for p in sorted(R):
        d, l, c = lab[p]; g = set(G[d][l])
        for i in sorted(g): cited.append((d, l, c, i))
        if not g:
            if S['kev'][p]['top']: none.append((d, l, c, S['kev'][p]['top'][0]['piece']))
            continue
        for a in ARMS:
            t = S[a][p]['top']
            if t and t[0]['piece'] not in g: uncited.append((d, l, c, t[0]['piece']))
    dedup = lambda xs: sorted(set(xs))
    cited, uncited, none = dedup(cited), dedup(uncited), dedup(none)
    rng = random.Random(SEED)
    pick = {'none': rng.sample(none, min(len(none), SIZES['none']))}
    short = SIZES['none'] - len(pick['none'])
    pick['cited'] = rng.sample(cited, min(len(cited), SIZES['cited'] + short))
    taken = set(pick['none']) | set(pick['cited'])
    pool = [x for x in uncited if x not in taken]
    pick['uncited'] = rng.sample(pool, min(len(pool), 60 - len(pick['none']) - len(pick['cited'])))
    allx = [(s, x) for s in ('cited', 'uncited', 'none') for x in pick[s]]
    rng.shuffle(allx)
    text = {}
    for d in {x[0] for _, x in allx}:
        text[d] = [q for q in pieces('\n\n'.join(paras(archive.git(arch, 'show', f'HEAD:{d}'))), PIECE) if q.strip()]
        assert len(text[d]) == key['n_pieces'][d], f'pieces changed for {d}'
    items, gk = [], {}
    for k, (s, (d, l, c, i)) in enumerate(allx):
        gid = f'g{k + 1:02d}'; plat, name = d.split('/', 1); cs = C[str(c)]
        items.append({'id': gid, 'platform': plat, 'doc': name.removesuffix('.md'), 'case': cs['title'],
                      'desc': (cs.get('description') or '').strip(), 'text': text[d][i].strip()})
        gk[gid] = {'doc': d, 'label': l, 'case': c, 'piece': i, 'stratum': s, 'opus_yes': i in set(G[d][l])}
    os.makedirs(os.path.dirname(PAGE), exist_ok=True)
    with open(PAGE, 'w', encoding='utf-8') as f: json.dump({'items': items}, f, ensure_ascii=False, indent=0)
    with open(os.path.join(FDIR, 'gate_key.json'), 'w', encoding='utf-8') as f: json.dump(gk, f, indent=1)
    print(len(items), 'items:', {s: len(pick[s]) for s in pick}, '| candidates', {'cited': len(cited), 'uncited': len(uncited), 'none': len(none)})


def score():
    gk = json.load(open(os.path.join(FDIR, 'gate_key.json'), encoding='utf-8'))
    A = json.load(open(os.path.join(FDIR, 'gate_answers.json'), encoding='utf-8'))
    pairs = [(A[i]['v'] == 'yes', gk[i]['opus_yes'], gk[i]['stratum']) for i in gk if i in A and A[i].get('v') in ('yes', 'no')]
    k = kappa([a for a, _, _ in pairs], [b for _, b, _ in pairs])
    res = {'items': len(gk), 'answered_yes_no': len(pairs), 'unsure': sum(1 for i in gk if i in A and A[i].get('v') == 'unsure'),
           'agree': sum(a == b for a, b, _ in pairs), 'kappa': round(k, 3) if k is not None else None,
           'by_stratum': {s: {'n': sum(1 for *_, t in pairs if t == s), 'ege_yes': sum(a for a, _, t in pairs if t == s),
                              'opus_yes': sum(b for _, b, t in pairs if t == s)} for s in ('cited', 'uncited', 'none')}}
    with open(os.path.join(FDIR, 'human_gate.json'), 'w', encoding='utf-8') as f: json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    if sys.argv[1] == 'sample': sample(sys.argv[2])
    elif sys.argv[1] == 'score': score()
