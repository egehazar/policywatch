"""The blind audit of listed drops (stale/PREREG_drop_audit.md): are they real platform edits or broken captures?

build   draw 10 / 30 / 10 cases from the 20-platform list (P), the contrib list (L) and the contrib guard's set-asides
        (G); write one card per case and both full captures to stale/audit_drops/, the answer key to
        stale/out/drop_audit_key.json. The card shows nothing the pipeline decided.
score   read stale/audit_drops/verdicts.json (filled by the rater) -> stale/out/drop_audit_result.json
Usage   py -m stale.drop_audit build | score
"""
import json, math, os, random, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(HERE, 'out')
sys.path.insert(0, ROOT)
AUD = os.path.join(HERE, 'audit_drops')
KEY = os.path.join(OUT, 'drop_audit_key.json')
PGA = os.path.join(ROOT, '..', 'decision-serving', 'data', 'pga-versions')
SIZES = {'P': 10, 'L': 30, 'G': 10}; SEED = 20261116; CAP = 1500


def show(repo, commit, path):
    r = subprocess.run(['git', '-C', repo, 'show', f'{commit}:{path}'], capture_output=True)
    return r.stdout.decode('utf-8', 'replace')


def plain(q):
    q = re.sub(r'<[^<>]*>', ' ', q); q = re.sub(r'^\s*/?\w+>', ' ', q); q = re.sub(r'<\s*/?\w*\s*$', ' ', q)
    return re.sub(r'\s+', ' ', q).strip()


def tri(t):
    w = re.findall(r'\w+', t.lower())
    return {tuple(w[i:i + 3]) for i in range(len(w) - 2)} or ({tuple(w)} if w else set())


def paras(t):
    return [p.strip() for p in re.split(r'\n\s*\n', t) if p.strip()]


def window(ps, i, target):
    """Paragraph i, widened with its neighbours while under CAP characters; a long paragraph is cut around target."""
    p = ps[i]
    if len(p) > CAP:
        k = p.lower().find(target.lower()[:40]) if target else -1
        k = max(0, k - CAP // 3) if k >= 0 else 0
        return ('...' if k else '') + p[k:k + CAP] + '...'
    a = b = i
    while True:
        grew = False
        if a > 0 and len('\n\n'.join(ps[a - 1:b + 1])) <= CAP: a -= 1; grew = True
        if b < len(ps) - 1 and len('\n\n'.join(ps[a:b + 2])) <= CAP: b += 1; grew = True
        if not grew: return '\n\n'.join(ps[a:b + 1])


def best(ps, ref):
    R = tri(ref); sc = [len(R & tri(p)) for p in ps]
    i = max(range(len(ps)), key=lambda j: sc[j]) if ps else None
    return i, (sc[i] / len(R) if (i is not None and R) else 0.0)


def draw():
    P = [json.loads(l) for l in open(os.path.join(OUT, 'points.jsonl'), encoding='utf-8')]
    W = [json.loads(l) for l in open(os.path.join(HERE, 'wide', 'contrib', 'out', 'points.jsonl'), encoding='utf-8')]
    listed = lambda r: r['status'] in ('gone', 'partly') and r.get('drop_kind') == 'platform edit'
    pops = {'P': sorted((r for r in P if listed(r)), key=lambda r: r['point']),
            'L': sorted((r for r in W if listed(r)), key=lambda r: r['point']),
            'G': sorted((r for r in W if r.get('drop_kind') == 'broken capture'), key=lambda r: r['point'])}
    cases = [(k, r) for k in ('P', 'L', 'G') for r in random.Random(f'{SEED}-{k}').sample(pops[k], SIZES[k])]
    random.Random(SEED).shuffle(cases)
    return cases, {k: len(v) for k, v in pops.items()}


def build():
    from stale.wide import vdir
    cases, N = draw()
    os.makedirs(AUD, exist_ok=True)
    key, cards = {}, ['# Drop audit: 50 cases', '',
                      'For each case: did the service change the document\'s own text so that the quoted wording is no longer there?',
                      'Answer GENUINE, CAPTURE or UNSURE in verdicts.json (see README.md in this folder). Full captures: '
                      'Cxx_before.md (last capture holding the quote) and Cxx_after.md (first capture without it).', '']
    for n, (pop, r) in enumerate(cases, 1):
        cid = f'C{n:02d}'; repo = PGA if pop == 'P' else vdir('contrib')
        a, b = r['last_present'], r['dropped_at']
        old, new = show(repo, a['commit'], r['doc']), show(repo, b['commit'], r['doc'])
        for s, t in (('before', old), ('after', new)):
            with open(os.path.join(AUD, f'{cid}_{s}.md'), 'w', encoding='utf-8', newline='\n') as f: f.write(t)
        q = plain(r['quote']); po, pn = paras(old), paras(new)
        i, _ = best(po, q); op = window(po, i, q) if i is not None else '(empty capture)'
        j, sim = best(pn, po[i] if i is not None else q); np_ = window(pn, j, '') if j is not None else '(empty capture)'
        cards += [f'## {cid}: {r["platform"]}, {r["doc"].split("/", 1)[1][:-3]}',
                  f'- Earlier capture {a["date"]}: {len(old):,} characters. Later capture {b["date"]}: {len(new):,} characters.',
                  f'- Quote: "{q[:1200]}"', '', '**Earlier capture, the passage holding the quote:**', '', '```', op, '```', '',
                  f'**Later capture, the passage most like it ({sim:.0%} of its word triples shared):**', '', '```', np_, '```', '',
                  '**Later capture, first 600 characters:**', '', '```', new[:600], '```', '']
        key[cid] = {'population': pop, 'point': r['point'], 'platform': r['platform'], 'doc': r['doc'],
                    'last_present': a, 'dropped_at': b, 'drop_kind': r.get('drop_kind')}
    with open(os.path.join(AUD, 'cards.md'), 'w', encoding='utf-8', newline='\n') as f: f.write('\n'.join(cards) + '\n')
    with open(os.path.join(AUD, 'verdicts.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump({c: {'verdict': '', 'why': ''} for c in key}, f, indent=1)
    with open(KEY, 'w', encoding='utf-8') as f: json.dump({'populations': N, 'sizes': SIZES, 'cases': key}, f, indent=1)
    print(len(key), 'cases;', 'population sizes', N, '->', AUD)


def wilson(k, n, z=1.96):
    if not n: return [None, None]
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 3), round(c + h, 3)]


def score():
    K = json.load(open(KEY, encoding='utf-8'))['cases']; V = json.load(open(os.path.join(AUD, 'verdicts.json'), encoding='utf-8'))
    assert set(V) == set(K) and all(V[c]['verdict'] in ('GENUINE', 'CAPTURE', 'UNSURE') for c in V), 'every case needs a verdict'
    res = {}
    for pop in ('P', 'L', 'G'):
        cs = [c for c in K if K[c]['population'] == pop]; v = [V[c]['verdict'] for c in cs]
        g, cap, u = v.count('GENUINE'), v.count('CAPTURE'), v.count('UNSURE'); n = g + cap
        res[pop] = {'cases': len(cs), 'GENUINE': g, 'CAPTURE': cap, 'UNSURE': u,
                    'genuine_share': round(g / n, 3) if n else None, 'wilson95': wilson(g, n),
                    'disagree_cases': [{'case': c, 'point': K[c]['point'], 'platform': K[c]['platform'], 'doc': K[c]['doc'],
                                       'why': V[c]['why']} for c in cs if V[c]['verdict'] != ('CAPTURE' if pop == 'G' else 'GENUINE')]}
    res['reading'] = {'L_below_80': res['L']['genuine_share'] is not None and res['L']['genuine_share'] < .80,
                      'G_guard_too_eager': res['G']['GENUINE'] >= 5}
    with open(os.path.join(OUT, 'drop_audit_result.json'), 'w', encoding='utf-8') as f: json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    {'build': build, 'score': score}[sys.argv[1]]()
