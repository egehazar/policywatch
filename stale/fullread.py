"""Full-read gold for the stale points (stale/PREREG_suggest.md): raters read each whole current document once and,
for every case listed for it, quote every passage that states or clearly implies the case, or answer NONE.

The gold does not depend on any arm: raters see the document in its own order, cut into the same 1,500-character
pieces as stale/suggest.py and labelled P1..Pn in document order, plus a list of cases (title, ToS;DR description,
classification; no old quote). The list mixes the stale points' cases with up to CONTROLS cases per document whose
approved quote is still in the current text (known positives, not marked as such) to measure rater recall.

Usage  py -m stale.fullread cases                 -> stale/data/cases.json (ToS;DR case/v3, cached)
       py -m stale.fullread prep <pga-versions>   -> stale/out/fullread/batch_<k>.md, stale/out/fullread/key.json
       py -m stale.fullread verify <pga-versions> <family>  -> stale/out/fullread/gold_<family>.json (quotes checked)
Raters write stale/out/fullread/<family>_batch_<k>.json:
  {"<document label>": {"<case label>": [{"piece": "P12", "quote": "<verbatim text>"}, ...] or [], ...}, ...}
"""
import json, os, random, sys, time, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(HERE, 'out')
FDIR = os.path.join(OUT, 'fullread'); CASES = os.path.join(HERE, 'data', 'cases.json')
sys.path.insert(0, ROOT)
from policywatch import archive
from policywatch.diffing import paras
from policywatch.watch import pieces
from stale.relocate import PIECE
from stale.suggest import drops
from stale.triage import qcov
from stale.match import words

SEED = 20261112
CONTROLS = 3               # known-positive cases per document, when available
BATCH_CHARS = 200_000
SECOND_BATCHES = sorted(random.Random(SEED).sample(range(12), 3))     # the batches Sonnet 5.5 also reads
API = 'https://api.tosdr.org'; UA = {'User-Agent': 'policywatch-research (local, low-rate)'}

INSTRUCTIONS = """# Rating task: where does this policy state each case?

ToS;DR (Terms of Service; Didn't Read) summarises policies with "cases", for example "You must create an account to
use this service". Below are one or more platform documents in their CURRENT version, each cut into numbered pieces
(P1, P2, ...) in document order, followed by a list of cases for that document (C1, C2, ...). Each case has a title,
ToS;DR's description and its classification (good / neutral / bad / blocker: which way it cuts for users).

Read the whole document. For EACH listed case, find EVERY passage that states or clearly implies the case for this
platform, so that a ToS;DR curator could quote it as the evidence. A passage that is only on the same topic, states
the opposite, or needs another passage to make the case does not count. Some cases are stated in several places;
some are not stated at all in this version.

For each passage you find, give the piece label and a verbatim quote of the shortest span (usually one or two
sentences) that states the case, copied exactly from that piece. List at most 5 passages per case, the clearest
first. If the document does not state the case, give an empty list.

Write ONLY a JSON object to the output file named in your instructions, in this shape, covering every listed case of
every document:
  {{"D1": {{"C1": [{{"piece": "P12", "quote": "exact text"}}, ...], "C2": [], ...}}, "D2": {{...}}}}
"""


def get(path, tries=4):
    for i in range(tries):
        try:
            r = json.loads(urllib.request.urlopen(urllib.request.Request(API + path, headers=UA), timeout=60).read())
            time.sleep(0.6); return r
        except Exception:
            if i == tries - 1: raise
            time.sleep(5 * (i + 1))


def all_points():
    return [json.loads(l) for l in open(os.path.join(OUT, 'points.jsonl'), encoding='utf-8')]


def eligible_controls(P, docs):
    """Present points with a quote of 6+ words whose quote is in 1-3 current pieces (as the relocation test)."""
    out = {d: [] for d in docs}
    for r in P:
        if r['status'] != 'present' or r.get('doc') not in out or len(words(r['quote'], quote=True)) < 6: continue
        out[r['doc']].append(r)
    return out


def needed_cases():
    P = all_points(); R = drops(); docs = {r['doc'] for r in R}
    ids = {int(r['case_id']) for r in R} | {int(r['case_id']) for rs in eligible_controls(P, docs).values() for r in rs}
    return sorted(ids)


def cases():
    have = json.load(open(CASES, encoding='utf-8')) if os.path.exists(CASES) else {}
    for c in needed_cases():
        if str(c) in have: continue
        d = get(f'/case/v3/?id={c}')
        have[str(c)] = {k: d.get(k) for k in ('id', 'title', 'description', 'classification', 'updated_at')}
        with open(CASES, 'w', encoding='utf-8') as f: json.dump(have, f, indent=1, ensure_ascii=False)
    print(len(have), 'cases cached')


def prep(arch):
    head = archive.git(arch, 'rev-parse', 'HEAD').strip()
    C = json.load(open(CASES, encoding='utf-8')); P = all_points(); R = drops()
    docs = sorted({r['doc'] for r in R})
    text = {d: [p for p in pieces('\n\n'.join(paras(archive.git(arch, 'show', f'HEAD:{d}'))), PIECE) if p.strip()] for d in docs}
    ctrl = eligible_controls(P, docs); rng = random.Random(SEED)
    plan = {}
    for d in docs:
        stale_cases = sorted({int(r['case_id']) for r in R if r['doc'] == d})
        cands = []
        for r in sorted(ctrl[d], key=lambda r: int(r['point'])):
            if int(r['case_id']) in stale_cases: continue
            gold = [i for i, p in enumerate(text[d]) if qcov(r['quote'], p) >= .3]
            if 1 <= len(gold) <= 3: cands.append((int(r['case_id']), int(r['point']), gold))
        byc = {}
        for c, p, g in cands: byc.setdefault(c, (p, g))          # one control point per case
        picks = sorted(byc); rng.shuffle(picks); picks = sorted(picks[:CONTROLS])
        items = [{'case': c, 'kind': 'stale', 'points': sorted(int(r['point']) for r in R if r['doc'] == d and int(r['case_id']) == c)}
                 for c in stale_cases] + [{'case': c, 'kind': 'control', 'points': [byc[c][0]], 'gold': byc[c][1]} for c in picks]
        rng.shuffle(items)
        for k, it in enumerate(items): it['label'] = f'C{k + 1}'
        plan[d] = items
    size = {d: sum(map(len, text[d])) for d in docs}
    batches, cur, n = [], [], 0
    for d in docs:
        if cur and n + size[d] > BATCH_CHARS: batches.append(cur); cur, n = [], 0
        cur.append(d); n += size[d]
    if cur: batches.append(cur)
    os.makedirs(FDIR, exist_ok=True)
    key = {'archive_head': head, 'piece_chars': PIECE, 'batches': []}
    for b, ds in enumerate(batches):
        lines = [INSTRUCTIONS]; dk = {}
        for j, d in enumerate(ds):
            lab = f'D{j + 1}'; dk[lab] = d; plat, name = d.split('/', 1)
            lines.append(f'\n## {lab}: {plat}, {name.removesuffix(".md")} (current version, {len(text[d])} pieces)\n')
            for i, p in enumerate(text[d]): lines.append(f'### {lab} P{i + 1}\n{p.strip()}\n')
            lines.append(f'\n## Cases for {lab} ({plat}, {name.removesuffix(".md")})\n')
            for it in plan[d]:
                c = C[str(it['case'])]
                lines.append(f'- {it["label"]}. "{c["title"]}". Description: {(c.get("description") or "").strip() or "(none)"} '
                             f'Classification: {c.get("classification")}.')
        with open(os.path.join(FDIR, f'batch_{b}.md'), 'w', encoding='utf-8') as f: f.write('\n'.join(lines) + '\n')
        key['batches'].append({'batch': b, 'docs': dk, 'chars': sum(size[d] for d in ds)})
    key['plan'] = plan; key['n_pieces'] = {d: len(text[d]) for d in docs}
    with open(os.path.join(FDIR, 'key.json'), 'w', encoding='utf-8') as f: json.dump(key, f, indent=1)
    ns = sum(1 for d in docs for it in plan[d] if it['kind'] == 'stale'); nc = sum(1 for d in docs for it in plan[d] if it['kind'] == 'control')
    print(len(batches), 'batches', [k['chars'] for k in key['batches']], ';', len(docs), 'documents;', ns, 'stale cases (',
          len(R), 'points );', nc, 'control cases')


def verify(arch, family):
    """Check each quoted span against the cited piece (word 6-grams, or the whole quote if shorter): a quote holding
    >= .8 of its words' 6-grams in the cited piece is kept there; else it is looked up in the neighbouring pieces and
    then the whole document; else it is dropped and counted."""
    key = json.load(open(os.path.join(FDIR, 'key.json'), encoding='utf-8'))
    rev = key['archive_head']                       # the texts as prep cut them, even if the archive has moved on since
    text = {d: [p for p in pieces('\n\n'.join(paras(archive.git(arch, 'show', f'{rev}:{d}'))), PIECE) if p.strip()] for d in key['plan']}
    assert all(len(text[d]) == key['n_pieces'][d] for d in text), 'pieces changed since prep'
    gold, stats = {}, {'quotes': 0, 'kept': 0, 'moved': 0, 'dropped': 0, 'missing_cases': 0}
    stats['batches_read'] = []
    for B in key['batches']:
        path = os.path.join(FDIR, f'{family}_batch_{B["batch"]}.json')
        if not os.path.exists(path):
            assert family != 'opus', f'primary rater missing {path}'
            continue                                  # the second rater reads only SECOND_BATCHES
        A = json.load(open(path, encoding='utf-8')); stats['batches_read'].append(B['batch'])
        for dl, d in B['docs'].items():
            got = A.get(dl, {})
            for it in key['plan'][d]:
                ans = got.get(it['label'])
                if ans is None: stats['missing_cases'] += 1; ans = []
                found = set()
                for a in ans[:5]:
                    stats['quotes'] += 1; q = str(a.get('quote', '')); n = len(text[d])
                    try: i = int(str(a.get('piece', '')).split('P')[-1]) - 1
                    except ValueError: i = -1
                    ok = lambda j: 0 <= j < n and qcov(q, text[d][j]) >= .8
                    if ok(i): found.add(i); stats['kept'] += 1; continue
                    alt = [j for j in (i - 1, i + 1) if ok(j)] or [j for j in range(n) if ok(j)]
                    if alt: found.add(alt[0]); stats['moved'] += 1
                    else: stats['dropped'] += 1
                gold.setdefault(d, {})[it['label']] = sorted(found)
    with open(os.path.join(FDIR, f'gold_{family}.json'), 'w', encoding='utf-8') as f: json.dump({'stats': stats, 'gold': gold}, f, indent=1)
    print(family, stats)


if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'cases': cases()
    elif c == 'prep': prep(sys.argv[2])
    elif c == 'verify': verify(sys.argv[2], sys.argv[3])
