"""AI-training clause ledger: which archived changes newly let a company train AI on its users' data, and was each
one ever reported? Plan: aiwatch/PLAN_ledger.md (hashed with this file before any rating).

Built on the kill test's prep (aiwatch/out/candidates.jsonl) and Kev scores (out/kev_cache.sqlite); the hashed kill
test itself (backtest.py) is not changed.

Usage (from the policywatch folder):
  py -m aiwatch.ledger cards      -> aiwatch/out/ledger/cards.jsonl + cards_key.jsonl + one text file per batch
  py -m aiwatch.ledger tally      -> aiwatch/out/ledger/tally.json (needs the raters' answer files)
"""
import collections, hashlib, json, os, random, re, sys
from aiwatch.backtest import OUT, DELTA, SENT, TRAIN, AIW, NEG, BAN, cands, kev_table

LED = os.path.join(OUT, 'ledger')
SEED = 40                 # card order and ids
BATCH = 25                # cards per rater batch
CARD_CAP = 3500           # characters per side of a card; longer sides are cut at a paragraph and marked

QUESTION = (
    'Each card shows the BEFORE and AFTER text of one change to a company\'s terms of service or privacy policy '
    '(only the changed passages that mention AI or models, with a little context). Read both and answer one label:\n'
    '- NEW: the AFTER text lets the company (or partners it shares data with) use its users\' content or personal '
    'data to train or improve AI / machine-learning models, and the BEFORE text did not.\n'
    '- WIDER: the BEFORE text already allowed that, and the AFTER text allows clearly more (more kinds of data, '
    'generative AI, new recipients, fewer limits, an opt-out removed).\n'
    '- SAME: both allow it to about the same extent (rewording, moving text, small clarifications).\n'
    '- NO: the AFTER text does not let the company train AI on users\' data (for example: a promise not to train, a '
    'ban on users training AI on the service, AI features or third-party models mentioned without training on '
    'users\' data, or training only on data that is not users\' own, such as public web data).\n'
    '- UNCLEAR: the passages shown are not enough to tell.\n'
    'For NEW or WIDER, also give the scope of the training use:\n'
    '- THIRD: users\' data is shared with other companies for THEM to train AI.\n'
    '- GENERAL: generative or general-purpose AI, or AI/ML models with no narrow purpose named.\n'
    '- NARROW: models for one named operational purpose only (ads, recommendations, fraud, safety, support, search).\n'
    '(If several apply, the first in this order.) For the other labels, scope is "-".\n'
    'Then quote the one AFTER sentence that decides it (or "-" for NO with nothing to quote).')


def norm(s):
    return re.sub(r'[^a-z0-9 ]', '', ' '.join(s.lower().split()))


def grant_sents(text):
    out = []
    for p in text.split('\n\n'):
        for s in SENT.split(p):
            if TRAIN.search(s) and AIW.search(s) and not NEG.search(s) and not BAN.search(s): out.append(norm(s))
    return out


def updates(kev=True):
    """Alerting updates of either arm -> list of dicts (one per distinct set of AI blocks)."""
    C = kev_table() if kev else cands()
    by = collections.OrderedDict()
    for c in C:
        by.setdefault((c['coll'], c['svc'], c['doc'], c['commit'], c['date']), []).append(c)
    seen, out = {}, []
    for k, blocks in by.items():
        r_al = any(b['regex_alert'] for b in blocks)
        k_d = max((b['kev']['grant'][1] - b['kev']['grant'][0] for b in blocks), default=0) if kev else None
        k_al = kev and k_d >= DELTA
        if not (r_al or k_al): continue
        ident = frozenset((b['old_text'], b['new_text']) for b in blocks)
        if ident in seen:                      # a shared policy (one Google text under several services): one card
            seen[ident]['also'].append({'coll': k[0], 'svc': k[1], 'doc': k[2], 'commit': k[3], 'date': k[4]})
            continue
        # what the card shows: the blocks that made either arm alert
        show = [b for b in blocks if b['regex_alert'] or (kev and b['kev']['grant'][1] - b['kev']['grant'][0] >= DELTA)]
        u = {'coll': k[0], 'svc': k[1], 'doc': k[2], 'commit': k[3], 'date': k[4], 'regex_alert': r_al,
             'kev_alert': bool(k_al), 'kev_delta': None if k_d is None else round(k_d, 4), 'also': [],
             'blocks': [(b['old_text'], b['new_text']) for b in show]}
        seen[ident] = u; out.append(u)
    return out


def cut(t):
    if len(t) <= CARD_CAP: return t
    keep, n = [], 0
    for p in t.split('\n\n'):
        if n + len(p) > CARD_CAP: break
        keep.append(p); n += len(p) + 2
    return '\n\n'.join(keep) + '\n\n[... cut ...]'


def cards(kev='1'):
    """kev='0': phase 1, keyword-alert cards (batch_p1_*). kev='1': phase 2, the union key; batch files (batch_p2_*)
    only for cards not already rated in phase 1."""
    os.makedirs(LED, exist_ok=True)
    phase = 'p2' if kev == '1' else 'p1'
    p1 = os.path.join(LED, 'cards_key_p1.jsonl')
    done = {json.loads(l)['card'] for l in open(p1, encoding='utf-8')} if phase == 'p2' and os.path.exists(p1) else set()
    U = updates(kev == '1')
    rnd = random.Random(SEED); rnd.shuffle(U)
    key, txt = [], []
    for u in U:
        cid = 'L' + hashlib.sha256(f'{SEED}|{u["coll"]}|{u["commit"]}|{u["doc"]}'.encode()).hexdigest()[:6]
        if cid in done: key.append(dict({k: v for k, v in u.items() if k != 'blocks'}, card=cid, phase='p1')); continue
        b = len(txt) // BATCH
        key.append(dict({k: v for k, v in u.items() if k != 'blocks'}, card=cid, phase=phase, batch=b))
        body = '\n\n'.join(f'BEFORE:\n{cut(o)}\n\nAFTER:\n{cut(n)}' for o, n in u['blocks'])
        txt.append((b, f'=== CARD {cid} ===\n{body}\n'))
    with open(os.path.join(LED, 'cards_key.jsonl'), 'w', encoding='utf-8', newline='\n') as f:
        for k in key: f.write(json.dumps(k, ensure_ascii=False) + '\n')
    if phase == 'p1':
        with open(p1, 'w', encoding='utf-8', newline='\n') as f:
            for k in key: f.write(json.dumps(k, ensure_ascii=False) + '\n')
    for b in sorted({b for b, _ in txt}):
        with open(os.path.join(LED, f'batch_{phase}_{b:02d}.txt'), 'w', encoding='utf-8', newline='\n') as f:
            f.write(QUESTION + '\n\nAnswer as JSON lines: {"card": "<id>", "label": "<NEW|WIDER|SAME|NO|UNCLEAR>", '
                    '"scope": "<THIRD|GENERAL|NARROW|->", "quote": "<sentence>"}\n\n')
            f.write('\n'.join(t for bb, t in txt if bb == b))
    n_r = sum(u['regex_alert'] for u in U); n_k = sum(u['kev_alert'] for u in U)
    print(f'{len(U)} cards ({n_r} regex alerts, {n_k} Kev alerts, {sum(u["regex_alert"] and u["kev_alert"] for u in U)} both), '
          f'{len({b for b, _ in txt})} batches -> {LED}')


GRANTISH = ('NEW', 'WIDER')


def answers(rater):
    """out/ledger/answers_<rater>_*.jsonl -> card -> label (the last answer for a card wins; unknown labels fail)."""
    out = {}
    for f in sorted(os.listdir(LED)):
        if not (f.startswith(f'answers_{rater}_') and f.endswith('.jsonl')): continue
        for line in open(os.path.join(LED, f), encoding='utf-8'):
            line = line.strip()
            if not line.startswith('{'): continue
            a = json.loads(line)
            lab = a['label'].strip().upper()
            assert lab in ('NEW', 'WIDER', 'SAME', 'NO', 'UNCLEAR'), a
            sc = (a.get('scope') or '-').strip().upper()
            assert sc in ('THIRD', 'GENERAL', 'NARROW', '-'), a
            out[a['card']] = {'label': lab, 'scope': sc, 'quote': a.get('quote', '')}
    return out


def kappa(x, y):
    n = len(x); po = sum(a == b for a, b in zip(x, y)) / n
    px, py = sum(x) / n, sum(y) / n
    pe = px * py + (1 - px) * (1 - py)
    return round((po - pe) / (1 - pe), 3) if pe < 1 else None


def tally(r1='claude', r2='gpt', boots='2000'):
    K = [json.loads(l) for l in open(os.path.join(LED, 'cards_key.jsonl'), encoding='utf-8')]
    A1, A2 = answers(r1), answers(r2)
    missing = [k['card'] for k in K if k['card'] not in A1 or k['card'] not in A2]
    if missing: raise SystemExit(f'{len(missing)} cards lack an answer, e.g. {missing[:5]}')
    g1 = [A1[k['card']]['label'] in GRANTISH for k in K]; g2 = [A2[k['card']]['label'] in GRANTISH for k in K]
    for k, a, b in zip(K, g1, g2): k['verified'] = a and b
    arms = {'regex': [k for k in K if k['regex_alert']], 'kev': [k for k in K if k['kev_alert']]}
    V = [k for k in K if k['verified']]

    def prec(rows): return round(sum(k['verified'] for k in rows) / len(rows), 3) if rows else None
    # document-resampled interval for Kev precision minus keyword precision (services resampled with replacement)
    svcs = sorted({k['svc'] for k in K}); by = collections.defaultdict(list)
    for k in K: by[k['svc']].append(k)
    rnd, diffs = random.Random(SEED), []
    for _ in range(int(boots)):
        rows = [k for s in (rnd.choice(svcs) for _ in svcs) for k in by[s]]
        pk, pr = prec([k for k in rows if k['kev_alert']]), prec([k for k in rows if k['regex_alert']])
        if pk is not None and pr is not None: diffs.append(pk - pr)
    diffs.sort()
    ci = [round(diffs[int(.025 * len(diffs))], 3), round(diffs[int(.975 * len(diffs)) - 1], 3)] if diffs else None
    res = {'cards': len(K), 'verified_grants': len(V), 'verified_services': len({k['svc'] for k in V}),
           'by_year': dict(collections.Counter(k['date'][:4] for k in V)),
           'scope_rater1': dict(collections.Counter(A1[k['card']]['scope'] for k in V)),
           'kappa_grant': kappa(g1, g2),
           'labels': {r1: dict(collections.Counter(A1[k['card']]['label'] for k in K)),
                      r2: dict(collections.Counter(A2[k['card']]['label'] for k in K))},
           'precision': {a: prec(rows) for a, rows in arms.items()},
           'alerts': {a: len(rows) for a, rows in arms.items()},
           'relative_recall': {a: round(sum(k['verified'] for k in rows) / len(V), 3) if V else None
                               for a, rows in arms.items()},
           'kev_minus_regex_precision_ci95': ci}
    with open(os.path.join(LED, 'verified.jsonl'), 'w', encoding='utf-8', newline='\n') as f:
        for k in sorted(V, key=lambda k: k['date']):
            f.write(json.dumps(dict(k, scope_1=A1[k['card']]['scope'], scope_2=A2[k['card']]['scope'],
                                    quote_1=A1[k['card']]['quote'], quote_2=A2[k['card']]['quote']),
                               ensure_ascii=False) + '\n')
    json.dump(res, open(os.path.join(LED, 'tally.json'), 'w', encoding='utf-8', newline='\n'), indent=1)
    print(json.dumps(res, indent=1))


PRESS_Q = (
    'For each item: a change archived by Open Terms Archive on the given date added the given sentence to the '
    'service\'s document. Find the EARLIEST public report of THIS change or of the AI-training use it describes for '
    'this service. Classes:\n'
    '- press: news media, a watchdog or advocacy group, a law firm or industry newsletter, an independent blog;\n'
    '- company: the company\'s own announcement, email, help page, blog or regulatory filing;\n'
    '- tracker: a machine-written record on a terms-tracking site (for example ConductAtlas, ToS;DR automated '
    'notes).\n'
    'General AI news about the company does not count. Give the earliest of each class you find (date, outlet, URL), '
    'and the queries you tried. Do not guess dates: write "unknown" if a page has none.\n'
    'Answer as JSON lines: {"item": "<id>", "press_date": "<YYYY-MM-DD|unknown|none>", "press_url": "", '
    '"press_outlet": "", "company_date": "", "company_url": "", "tracker_url": "", "queries": ["..."]}')


def diff_link(k):
    return f'https://github.com/OpenTermsArchive/{k["coll"]}/commit/{k["commit"]}'


def press_sheet():
    V = [json.loads(l) for l in open(os.path.join(LED, 'verified.jsonl'), encoding='utf-8')]
    os.makedirs(os.path.join(LED, 'press'), exist_ok=True)
    with open(os.path.join(LED, 'press', 'items.txt'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(PRESS_Q + '\n\n')
        for k in V:
            k['item'] = 'P' + k['card'][1:]
            also = ', '.join(sorted({a['svc'] for a in k['also']}))
            f.write(f'=== ITEM {k["item"]} ===\nservice: {k["svc"]}' + (f' (same text also under: {also})' if also else '')
                    + f'\ndocument: {k["doc"]}\ndate first archived: {k["date"]}\nsentence: {k["quote_1"]}\n'
                    f'archive diff: {diff_link(k)}\n\n')
    print(f'{len(V)} items -> {os.path.join(LED, "press", "items.txt")}')


def press_tally(s1='fable', s2='gpt'):
    V = [json.loads(l) for l in open(os.path.join(LED, 'verified.jsonl'), encoding='utf-8')]
    P = os.path.join(LED, 'press')

    def load(who):
        out = {}
        for f in sorted(os.listdir(P)):
            if f.startswith(f'answers_{who}') and f.endswith('.jsonl'):
                for line in open(os.path.join(P, f), encoding='utf-8'):
                    if line.strip().startswith('{'): a = json.loads(line); out[a['item']] = a
        return out
    S = [load(s1), load(s2)]
    rows = []
    for k in V:
        item = 'P' + k['card'][1:]
        found = [s[item] for s in S if item in s]
        if len(found) < 2: raise SystemExit(f'{item} lacks an answer from both searchers')
        dates = sorted(a['press_date'] for a in found if re.fullmatch(r'\d{4}-\d{2}-\d{2}', a['press_date'] or ''))
        any_press = bool(dates) or any((a['press_date'] or 'none') == 'unknown' for a in found)
        import datetime as dt
        lag = (dt.date.fromisoformat(dates[0]) - dt.date.fromisoformat(k['date'])).days if dates else None
        rows.append(dict(k, item=item, press_first=dates[0] if dates else None, press_any=any_press, press_lag_days=lag,
                         company=any(a.get('company_url') for a in found), tracker=any(a.get('tracker_url') for a in found),
                         searches=found, diff=diff_link(k)))
    none = [r for r in rows if not r['press_any']]
    res = {'verified': len(rows), 'press_found': sum(r['press_any'] for r in rows),
           'press_within_30d': sum(r['press_lag_days'] is not None and r['press_lag_days'] <= 30 for r in rows),
           'no_press_found': len(none), 'no_press_services': len({r['svc'] for r in none}),
           'no_press_but_company': sum(r['company'] for r in none), 'no_press_but_tracker': sum(r['tracker'] for r in none)}
    res['reading'] = 'worth publishing' if res['no_press_found'] >= 15 and res['no_press_services'] >= 10 else 'thin'
    with open(os.path.join(P, 'ledger_rows.jsonl'), 'w', encoding='utf-8', newline='\n') as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + '\n')
    json.dump(res, open(os.path.join(P, 'press_tally.json'), 'w', encoding='utf-8', newline='\n'), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    {'cards': cards, 'tally': tally, 'press_sheet': press_sheet, 'press_tally': press_tally}[cmd](*sys.argv[2:])
