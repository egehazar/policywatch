"""AI-training clause watch: replay Open Terms Archive history and ask, for every recorded change of a tracked
terms of service or privacy policy, whether it newly lets the company train AI on users' content or data.
Plan: aiwatch/PLAN_aiwatch.md (hashed with this file before any Kev score).

Two arms see exactly the same changed blocks (a block = changed paragraphs plus one unchanged paragraph each side,
policywatch.diffing). Both only look at blocks whose changed paragraphs mention AI vocabulary (BROAD), so the
comparison is about judging the change, not finding AI words.
- REGEX arm: counts "grant sentences" (training + AI/model words in one sentence, with no negation and no ban on
  users) in the old and new changed paragraphs; alerts if the new side has more.
- KEV arm: Kev-4B (deployed llama.cpp server, /v1/systemone) asked three yes/no questions of the old and the new block
  text; alerts if p(grant) rises by at least DELTA (0.2, the cut from the r19 meaning-diff test, fixed before this).

Usage (from the policywatch folder):
  py -m aiwatch.backtest prep            -> aiwatch/out/candidates.jsonl (+ regex arm), counts
  py -m aiwatch.backtest score [port]    -> Kev scores into aiwatch/out/kev_cache.sqlite (resumable)
  py -m aiwatch.backtest result          -> aiwatch/out/result.json (needs the hashed gold, notes/r39_incidents.json)
"""
import concurrent.futures as cf, datetime, json, os, re, sys
from policywatch.archive import History, git
from policywatch.diffing import diff, SEP
from policywatch.scorer import Server, Cache, qid

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out')
DATA = r'C:\Users\egeha\projects\decision-serving\data'
COLLS = ['contrib-versions', 'genai-contrib-versions', 'pga-versions', 'user-rights-versions']
GOLD = r'C:\Users\egeha\projects\decision-serving\notes\r39_incidents.json'
SINCE, UNTIL = '2023-01-01', '2026-11-19'
BASE_DOCS = ('Terms of Service', 'Privacy Policy')
DELTA = 0.2

BROAD = re.compile(r'(?i)(artificial intelligence|machine learning|generative|\bmodels?\b|algorithm|large language|'
                   r'neural|\btrain|\bLLMs?\b)|\bAI\b')
TRAIN = re.compile(r'(?i)\b(train\w*|fine[- ]?tun\w*|retrain\w*)\b')
AIW = re.compile(r'(?i)(artificial intelligence|machine learning|generative|\bmodels?\b|algorithms?|large language|'
                 r'neural|\bLLMs?\b)|\bAI\b')
NEG = re.compile(r"(?i)\b(not|never|no longer|won't|cannot|can't|neither|nor|without your (?:prior )?(?:consent|permission|"
                 r"authori[sz]ation))\b")
BAN = re.compile(r'(?i)\b(you (?:may|must|shall|will|agree|should) not|you agree not to|prohibit\w*|not permitted|'
                 r'not allowed|forbid\w*|scrap\w*|crawl\w*)\b')
SENT = re.compile(r'(?<=[.!?;])\s+')

Q = {'grant': 'Does this text allow the company to use its users\' content or personal data to train artificial '
              'intelligence or machine learning models?',
     'promise': 'Does this text promise that the company will not use its users\' content or personal data to train '
                'artificial intelligence models?',
     'ban': 'Does this text forbid users or others from using the service\'s content to train artificial intelligence '
            'models?'}


def grant_sentences(paragraphs):
    n = 0
    for p in paragraphs:
        for s in SENT.split(p):
            if TRAIN.search(s) and AIW.search(s) and not NEG.search(s) and not BAN.search(s): n += 1
    return n


# Rulings fixed after the gold list and before any Kev score (PLAN_aiwatch.md, addendum 1). Indexes are positions in
# notes/r39_incidents.json, which is hashed with this file.
EXTRA_DOCS = ('Developer Terms',)        # the only other eligible document type (X and Telegram developer terms)
OVERRIDE = {45: {'change_commit': '052858628', 'change_date': '2026-04-17'}}   # Atlassian: the change the press reported
EXCLUDE = {41: 'not a training change at the recorded commit (reported as an ads change; training text came 2025-12-17)'}
NO_AI_WORDS = {4, 22}                    # BAN_USERS clauses with no AI words: left out of the direction tallies


def doc_types():
    """Terms of Service and Privacy Policy, plus the other document type named by eligible gold incidents."""
    return tuple(sorted(set(BASE_DOCS) | set(EXTRA_DOCS)))


def gold():
    G = json.load(open(GOLD, encoding='utf-8'))
    out = []
    for i, g in enumerate(G):
        if not g.get('eligible') or i in EXCLUDE: continue
        g = dict(g, **OVERRIDE.get(i, {}), idx=i)
        out.append(g)
    return out


class Blobs:
    """One persistent `git cat-file --batch` per repo: reading a version costs no new process (git show did)."""
    def __init__(self, repo):
        import subprocess
        self.p = subprocess.Popen(['git', '-C', repo, 'cat-file', '--batch'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def get(self, spec):
        self.p.stdin.write((spec + '\n').encode('utf-8')); self.p.stdin.flush()
        header = self.p.stdout.readline().decode('utf-8', 'replace')
        if header.rstrip().endswith('missing') or len(header.split()) < 3: return ''
        data = self.p.stdout.read(int(header.split()[2])); self.p.stdout.read(1)
        return data.decode('utf-8', 'replace')


class FastHistory(History):
    """policywatch.archive.History (noise rules unchanged), reading versions through Blobs."""
    def __init__(self, archive, path, blobs):
        super().__init__(archive, path); self.blobs = blobs

    def text_at(self, h):
        if h not in self._t: self._t[h] = self.blobs.get(f'{h}:{self.path}')
        return self._t[h]


_BLOBS = {}


def prep_service(job):
    """All candidate blocks of one service's tracked documents -> (rows, counts)."""
    coll, svc, docs = job
    repo = os.path.join(DATA, coll)
    blobs = _BLOBS.setdefault(repo, Blobs(repo))
    rows, n = [], {'updates': 0, 'noise_skipped': 0, 'blocks': 0, 'candidate_blocks': 0}
    for doc in docs:
        path = f'{svc}/{doc}.md'
        if not os.path.exists(os.path.join(repo, path)): continue
        hist = None
        for line in git(repo, 'log', '--format=%H%x09%ad%x09%s', '--date=short', '--', path).splitlines():
            h, d, s = line.split('\t', 2)
            if not (SINCE <= d <= UNTIL): continue
            if not (s.startswith('Record new changes') or s.startswith('Update ')): continue
            hist = hist or FastHistory(repo, path, blobs)
            new, old = hist.text_at(h), blobs.get(f'{h}^:{path}')
            if not old.strip() or not new.strip(): continue
            n['updates'] += 1
            if hist.classify(h, old, new): n['noise_skipped'] += 1; continue
            old, _ = hist.clean_parent(h, old)
            for i, b in enumerate(diff(old, new).blocks):
                n['blocks'] += 1
                if not BROAD.search('\n'.join(b.old + b.new)): continue
                n['candidate_blocks'] += 1
                go, gn = grant_sentences(b.old), grant_sentences(b.new)
                # What Kev reads: the block's changed paragraphs that mention AI vocabulary, between its unchanged
                # context paragraphs. A large rewrite would otherwise hide its AI clause past any length cap.
                ao, an = [p for p in b.old if BROAD.search(p)], [p for p in b.new if BROAD.search(p)]
                rows.append({'coll': coll, 'svc': svc, 'doc': doc, 'commit': h, 'date': d, 'block': i,
                             'old_text': ('\n\n'.join(b.before + ao + b.after) or '(no text)')[:8000],
                             'new_text': ('\n\n'.join(b.before + an + b.after) or '(no text)')[:8000],
                             'regex_old': go, 'regex_new': gn, 'regex_alert': gn > go})
    return rows, n


def prep(workers='5'):
    import multiprocessing as mp
    os.makedirs(OUT, exist_ok=True)
    docs = doc_types()
    jobs = [(coll, svc, docs) for coll in COLLS for svc in sorted(os.listdir(os.path.join(DATA, coll)))
            if not svc.startswith('.') and os.path.isdir(os.path.join(DATA, coll, svc))]
    total = {'updates': 0, 'noise_skipped': 0, 'blocks': 0, 'candidate_blocks': 0}
    with mp.Pool(int(workers)) as pool, open(os.path.join(OUT, 'candidates.jsonl'), 'w', encoding='utf-8', newline='\n') as f:
        for k, (rows, n) in enumerate(pool.imap(prep_service, jobs), 1):     # imap keeps the job order
            for r in rows: f.write(json.dumps(r, ensure_ascii=False) + '\n')
            for key in total: total[key] += n[key]
            if k % 50 == 0: print(f'[prep {k}/{len(jobs)} services {datetime.datetime.utcnow():%H:%M:%S}] {total}', flush=True)
    counts = dict(total, doc_types=list(docs), services=len(jobs))
    json.dump(counts, open(os.path.join(OUT, 'prep_counts.json'), 'w'), indent=1)
    print(json.dumps(counts, indent=1))


def cands():
    return [json.loads(l) for l in open(os.path.join(OUT, 'candidates.jsonl'), encoding='utf-8')]


def score(port='9995'):
    S = Server(f'http://127.0.0.1:{port}'); assert S.served == 'Kev-4B-Q8_0.gguf', S.served
    C = Cache(os.path.join(OUT, 'kev_cache.sqlite'))
    texts = sorted({t for c in cands() for t in (c['old_text'], c['new_text'])})
    qs = {qid(v): v for v in Q.values()}
    todo = [t for t in texts if len(C.get(S.id, t, list(qs))) < len(qs)]
    print(f'{len(texts)} distinct texts, {len(todo)} to score', flush=True)

    def one(t): return t, S.ask(t, qs)
    done = 0
    with cf.ThreadPoolExecutor(4) as ex:
        for t, ps in ex.map(one, todo):
            C.put(S.id, t, ps); done += 1
            if done % 50 == 0: print(f'[score {done}/{len(todo)} {datetime.datetime.utcnow():%H:%M:%S}]', flush=True)
    C.close(); print('score done', flush=True)


def kev_table():
    import sqlite3
    path = os.path.join(OUT, 'kev_cache.sqlite')
    ids = [r[0] for r in sqlite3.connect(path).execute('select distinct scorer from scores')]
    assert len(ids) == 1, ids
    S_id, C = ids[0], Cache(path)
    qs = {k: qid(v) for k, v in Q.items()}
    out = []
    for c in cands():
        po, pn = C.get(S_id, c['old_text'], list(qs.values())), C.get(S_id, c['new_text'], list(qs.values()))
        if len(po) < len(qs) or len(pn) < len(qs): raise SystemExit('scores incomplete')
        c['kev'] = {k: (po[q], pn[q]) for k, q in qs.items()}
        out.append(c)
    return out


def months():
    a, b = datetime.date.fromisoformat(SINCE), datetime.date.fromisoformat(UNTIL)
    return (b - a).days / 30.44


def result():
    C = kev_table()
    G = gold()
    grant = [g for g in G if g['direction'] == 'GRANT']
    other = [g for g in G if g['direction'] in ('PROMISE_NOT', 'BAN_USERS') and g['idx'] not in NO_AI_WORDS]

    def alerts_kev(delta):    # update key -> True
        return {(c['coll'], c['svc'], c['doc'], c['commit']) for c in C if c['kev']['grant'][1] - c['kev']['grant'][0] >= delta}
    regex = {(c['coll'], c['svc'], c['doc'], c['commit']) for c in C if c['regex_alert']}

    def hit(alerts, g):       # gold names services for people ("X (Twitter)"), so match the archive commit instead
        return any(k[0] == g['ota_collection'] and k[3].startswith(g['change_commit'][:8]) for k in alerts)

    def volume(alerts):       # alerting updates; an update whose AI blocks are identical to another's counts once
        ident = {}
        for c in C:
            k = (c['coll'], c['svc'], c['doc'], c['commit'])
            if k in alerts: ident.setdefault(k, set()).add((c['old_text'], c['new_text']))
        return len({frozenset(v) for v in ident.values()})

    def lead(g):
        return (datetime.date.fromisoformat(g['first_report_date'][:10]) - datetime.date.fromisoformat(g['change_date'][:10])).days

    def arm(alerts):
        name = lambda g: f"{g['service']} {g['document']} {g['change_date']}"
        hits = [g for g in grant if hit(alerts, g)]
        return {'recall': round(len(hits) / len(grant), 3) if grant else None, 'flagged': [name(g) for g in hits],
                'missed': [name(g) for g in grant if not hit(alerts, g)],
                'lead_ge_7': sum(lead(g) >= 7 for g in hits), 'leads': {name(g): lead(g) for g in hits},
                'alert_changes': volume(alerts), 'alerts_per_month': round(volume(alerts) / months(), 2),
                'grant_alert_on_other_direction': [name(g) for g in other if hit(alerts, g)],
                'info_atlassian_2025_09_06_alert': any(k[0] == 'contrib-versions' and k[3].startswith('25879f6e5') for k in alerts)}
    K, R = arm(alerts_kev(DELTA)), arm(regex)
    # matched operating point: the highest delta at which Kev's recall reaches the regex arm's
    deltas = sorted({round(c['kev']['grant'][1] - c['kev']['grant'][0], 4) for c in C if c['kev']['grant'][1] > c['kev']['grant'][0]}, reverse=True)
    matched = None
    for dl in deltas:
        a = alerts_kev(dl)
        if grant and sum(hit(a, g) for g in grant) / len(grant) >= (R['recall'] or 0):
            matched = {'delta': dl, 'alert_changes': volume(a)}; break
    # direction on non-grant incidents: Kev right if no grant alert and the matching question rose most
    def kev_dir(g):
        rows = [c for c in C if c['coll'] == g['ota_collection'] and c['commit'].startswith(g['change_commit'][:8])]
        if not rows: return None
        d = {k: max(c['kev'][k][1] - c['kev'][k][0] for c in rows) for k in Q}
        want = 'promise' if g['direction'] == 'PROMISE_NOT' else 'ban'
        return max(d, key=d.get) == want and d['grant'] < DELTA
    dir_kev = [kev_dir(g) for g in other]
    res = {'eligible_grant': len(grant), 'eligible_other': len(other), 'kev_delta_0.2': K, 'regex': R,
           'kev_matched_to_regex_recall': matched,
           'direction_kev_right': sum(x is True for x in dir_kev), 'direction_kev_unscored': sum(x is None for x in dir_kev),
           'direction_regex_right': sum(not hit(regex, g) for g in other)}
    thin = len(grant) < 6
    passes = (not thin and K['recall'] >= .7 and K['lead_ge_7'] >= 3 and matched is not None
              and matched['alert_changes'] * 2 <= R['alert_changes'])
    tie = R['recall'] is not None and R['recall'] >= K['recall'] and R['alert_changes'] <= 2 * K['alert_changes']
    res['reading'] = 'too thin: stopped' if thin else 'PASS' if passes else 'keyword ties: stopped' if tie else 'FAIL'
    json.dump(res, open(os.path.join(OUT, 'result.json'), 'w', encoding='utf-8', newline='\n'), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    {'prep': prep, 'score': score, 'result': result}[cmd](*sys.argv[2:])
