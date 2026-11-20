"""Was a verified grant sentence really new? Checks each deciding sentence against the document's full archived history.

  py -m aiwatch.history ledger  -> out/ledger/doc_check.json, out/ledger/first_appearance.json (phase-1 verified rows)
  py -m aiwatch.history recall  -> out/ledger/recall_history.json (the recall sample's verified rows)

A card shows only the changed passage, so raters cannot see the same sentence elsewhere in the old document, or a
capture that dropped a section and restored it later. Exploratory (found after the phase-1 tally; RESULT_ledger.md).

Matching. The first version (an inline script, 2026-11-20) matched the raters' quote fuzzily: two-thirds of its
60-character pieces. That called a sentence old when it had just GAINED its AI phrase (DeepSeek's "foundation model
training and optimization", Honkai's "including to train the model(s)", a new AWS service added to a training
clause), found by Fable 5.2 checking the email links. Now: take the sentence of the alerting version that best
matches the quote (raters' quotes are not always verbatim), and call it old only if that exact sentence, ignoring
case, spaces and punctuation, is in an older version. A changed sentence counts as new even when an older one
granted the same right; that kind of overcount is the full-document review's job, not this check's.
"""
import collections, difflib, json, os, re, sys
from policywatch.archive import git
from aiwatch.backtest import Blobs, DATA
from aiwatch.ledger import LED

norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())
SPLIT = re.compile(r'(?<=[.!?;])\s+|\n|\s\|\s')


def deciding(text, quote):
    """The run of 1-4 consecutive sentences, list items or table cells of `text` closest to the raters' quote,
    normalised (a quoted clause is often a list spread over several lines)."""
    q = quote.replace('…', ' ')
    F = [s.strip() for s in SPLIT.split(text) if s.strip()]
    C = [' '.join(F[i:i + k]) for k in (1, 2, 3, 4) for i in range(len(F) - k + 1)]
    C = [c for c in C if len(norm(c)) >= 20] or [text]
    sm = lambda c: difflib.SequenceMatcher(None, c, q, autojunk=False)
    top = sorted(C, key=lambda c: sm(c).quick_ratio(), reverse=True)[:40]
    return norm(max(top, key=lambda c: sm(c).ratio()))


def has(t, q):
    return q in t


def doc_check(rows):
    """-> [(row, verdict)]: 'short quote', 'in parent document', 'in an earlier version' or 'new to the document'."""
    out = []
    for r in rows:
        repo = os.path.join(DATA, r['coll']); path = f"{r['svc']}/{r['doc']}.md"
        q = deciding(git(repo, 'show', f"{r['commit']}:{path}"), r['quote_1'])
        if len(q) < 40: out.append((r, 'short quote')); continue
        try: parent = norm(git(repo, 'show', f"{r['commit']}^:{path}"))
        except Exception: parent = ''
        if has(parent, q): out.append((r, 'in parent document')); continue
        seen = None
        for h in git(repo, 'log', '--format=%H', f"{r['commit']}^", '--', path).split()[:400]:
            try:
                if has(norm(git(repo, 'show', f'{h}:{path}')), q): seen = h; break
            except Exception: pass
        out.append((r, 'in an earlier version' if seen else 'new to the document'))
    return out


def first_appearance(rows):
    """-> {card: oldest archived version of the document that contains the sentence, and how many versions do}."""
    B, res = {}, {}
    for r in rows:
        repo = os.path.join(DATA, r['coll']); path = f"{r['svc']}/{r['doc']}.md"
        b = B.setdefault(repo, Blobs(repo))
        q = deciding(b.get(f"{r['commit']}:{path}"), r['quote_1'])
        log = [l.split('\t') for l in git(repo, 'log', '--format=%H%x09%ad', '--date=short', r['commit'], '--', path).splitlines()]
        first, n_in = None, 0
        for h, d in log:                      # newest -> oldest; keep the oldest version containing the sentence
            if len(q) >= 40 and has(norm(b.get(f'{h}:{path}')), q): first = (h, d); n_in += 1
        res[r['card']] = {'svc': r['svc'], 'doc': r['doc'], 'alert_date': r['date'],
                          'first_commit': first[0] if first else None, 'first_date': first[1] if first else None,
                          'versions_with_it': n_in, 'versions_total': len(log)}
    return res


def ledger():
    V = [json.loads(l) for l in open(os.path.join(LED, 'verified.jsonl'), encoding='utf-8')]
    rows = doc_check(V)
    json.dump([{'card': r['card'], 'svc': r['svc'], 'date': r['date'], 'doc_check': c} for r, c in rows],
              open(os.path.join(LED, 'doc_check.json'), 'w', encoding='utf-8'), indent=0)
    json.dump(first_appearance(V), open(os.path.join(LED, 'first_appearance.json'), 'w', encoding='utf-8'), indent=0)
    print(dict(collections.Counter(c for _, c in rows)))


def recall():
    T = json.load(open(os.path.join(LED, 'recall_tally.json'), encoding='utf-8'))
    V = [dict(c, quote_1=c['quote']) for c in T['verified_in_sample_cards']]
    chk, fa = dict((r['card'], c) for r, c in doc_check(V)), first_appearance(V)
    out = [{'card': r['card'], 'svc': r['svc'], 'doc': r['doc'], 'date': r['date'], 'doc_check': chk[r['card']],
            'first_date': fa[r['card']]['first_date']} for r in V]
    json.dump(out, open(os.path.join(LED, 'recall_history.json'), 'w', encoding='utf-8'), indent=0)
    print(dict(collections.Counter(o['doc_check'] for o in out)))
    for o in out: print(f"{o['doc_check']:22} {o['date']} first {o['first_date']}  {o['svc']}")


if __name__ == '__main__':
    {'ledger': ledger, 'recall': recall}[sys.argv[1]]()
