"""Held-out services for the relocation test: ToS;DR points on services outside the 22 pga-versions platforms, on
ToS;DR's own stored copy of each document (no Open Terms Archive text). Network and string matching only; no model.

pool    comprehensively reviewed services rated A-E in stale/data/services_list.json (fetched 2026-11-12), minus the
        22 pga-versions services, in a fixed random order (seed 20261113)
pull    walks the pool in that order. For each service: its approved points (service/v3) in a fixed random order; each
        point's quote (point/v1) and its document's stored text (document/v1), until PER_SERVICE eligible points are
        found or the service runs out. Stops at TARGET eligible points. Writes stale/data/heldout/<service>.json.
eligible  an approved point whose quote has >= 6 words and is in the stored text (coverage >= .8 over the whole
        document), whose document is English (>= .2 of its words in a small stopword list), 2,000-150,000 characters,
        and whose quote falls in 1-3 pieces of 1,500 characters (>= .3 of its 6-grams, as in stale/relocate.py)
prep    -> stale/out/heldout_docs.json in the format of reloc_docs.json (order = all eligible points)

Usage  py -m stale.heldout pull   |   py -m stale.heldout prep
"""
import html, json, os, random, re, sys, time, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(HERE, 'out')
DATA = os.path.join(HERE, 'data', 'heldout'); sys.path.insert(0, ROOT)
from policywatch.watch import pieces
from stale.match import words, grams, coverage
from stale.pull import SERVICES
from stale.relocate import PIECE, GOLD_MIN, GOLD_MAX, psha
from stale.triage import TEMPLATE

SEED = 20261113; PER_SERVICE = 5; TARGET = 200
API = 'https://api.tosdr.org'; UA = {'User-Agent': 'policywatch-research (local, low-rate)'}
EN = set('the of and to in a is that for you we or by be this are with as on your may our any not it from at us'.split())


def get(path, tries=4):
    for i in range(tries):
        try:
            r = json.loads(urllib.request.urlopen(urllib.request.Request(API + path, headers=UA), timeout=90).read())
            time.sleep(0.6); return r.get('parameters', r) if isinstance(r, dict) else r
        except Exception:
            if i == tries - 1: raise
            time.sleep(5 * (i + 1))


def pool():
    S = json.load(open(os.path.join(HERE, 'data', 'services_list.json'), encoding='utf-8'))['services']
    pga = set(SERVICES.values())
    ids = sorted(s['id'] for s in S if s['is_comprehensively_reviewed'] and s['rating'] in 'ABCDE' and len(s['rating']) == 1 and s['id'] not in pga)
    random.Random(SEED).shuffle(ids); return ids


def paragraphs(stored_html):
    """ToS;DR's stored text is HTML with one block per line: tags dropped, entities decoded, empty lines skipped."""
    out = []
    for line in (stored_html or '').split('\n'):
        t = html.unescape(re.sub(r'<[^<>]*>', ' ', line)); t = re.sub(r'\s+', ' ', t).strip()
        if t: out.append(t)
    return out


def qcov(quote, text_ws):
    qw = words(quote, quote=True)
    return coverage(qw, grams(qw), ' ' + ' '.join(text_ws) + ' ', grams(text_ws))


def check(quote, P, doc_ws):
    """None if the point is not eligible, else its gold pieces."""
    if len(words(quote, quote=True)) < 6 or qcov(quote, doc_ws) < .8: return None
    gold = [i for i, p in enumerate(P) if qcov(quote, words(p)) >= GOLD_MIN]
    return gold if 1 <= len(gold) <= GOLD_MAX else None


def doc_ok(text, ws):
    return 2000 <= len(text) <= 150_000 and ws and sum(w in EN for w in ws) / len(ws) >= .2


def pull():
    os.makedirs(DATA, exist_ok=True); total = 0; docs_cache = {}
    for sid in pool():
        path = os.path.join(DATA, f'{sid}.json')
        if os.path.exists(path):
            total += len(json.load(open(path, encoding='utf-8'))['points'])
        else:
            s = get(f'/service/v3/?id={sid}')
            pts = [p for p in s.get('points', []) if p.get('status') == 'approved']
            random.Random(f'{SEED}-{sid}').shuffle(pts)
            keep, docs, tried = [], {}, 0
            for p in pts:
                if len(keep) >= PER_SERVICE: break
                d = get(f"/point/v1/?id={p['id']}"); tried += 1; did = d.get('document_id'); q = d.get('quote_text') or ''
                if not did or len(words(q, quote=True)) < 6: continue
                if did not in docs:
                    dd = get(f'/document/v1?id={did}'); text = '\n\n'.join(paragraphs(dd.get('text')))
                    docs[did] = {'id': did, 'name': dd.get('name'), 'url': dd.get('url'), 'updated_at': dd.get('updated_at'), 'text': text}
                text = docs[did]['text']; ws = words(text)
                if not doc_ok(text, ws): continue
                P = [x for x in pieces(text, PIECE) if x.strip()]
                gold = check(q, P, ws)
                if gold is None: continue
                c = d.get('case') or {}
                keep.append({'point': d['id'], 'service': sid, 'service_name': s.get('name'), 'document_id': did,
                             'case_id': c.get('id'), 'case_title': c.get('title'), 'quote': q, 'created_at': d.get('created_at'),
                             'gold_preview': gold})
            used = {k['document_id'] for k in keep}
            with open(path, 'w', encoding='utf-8') as f:
                json.dump({'service': sid, 'name': s.get('name'), 'approved': len(pts), 'tried': tried, 'points': keep,
                           'documents': [docs[i] for i in sorted(used)]}, f, ensure_ascii=False)
            total += len(keep)
            print(f'{s.get("name")} ({sid}): {len(keep)} eligible of {tried} tried; total {total}', flush=True)
        if total >= TARGET: break
    print('done', total)


def prep():
    order, out = [], []
    for sid in pool():
        path = os.path.join(DATA, f'{sid}.json')
        if not os.path.exists(path): break
        S = json.load(open(path, encoding='utf-8'))
        for doc in S['documents']:
            P = [x for x in pieces(doc['text'], PIECE) if x.strip()]
            pts = [p for p in S['points'] if p['document_id'] == doc['id']]
            cases = sorted({p['case_title'] for p in pts}); items = []
            for p in pts:
                gold = [i for i, x in enumerate(P) if qcov(p['quote'], words(x)) >= GOLD_MIN]
                assert gold == p['gold_preview'], (p['point'], gold, p['gold_preview'])
                items.append({'point': p['point'], 'platform': S['name'], 'case_title': p['case_title'], 'status': 'present',
                              'question': TEMPLATE.format(p['case_title']), 'gold': gold})
                order.append(p['point'])
            out.append({'doc': f"{S['name']}/{doc['name']} [{doc['id']}]", 'service': sid, 'chars': sum(len(x) for x in P), 'pieces': P,
                        'questions': [TEMPLATE.format(c) for c in cases], 'cases': cases, 'items': items, 'pieces_sha': psha(P)})
    with open(os.path.join(OUT, 'heldout_docs.json'), 'w', encoding='utf-8') as f: json.dump({'order': order, 'docs': out}, f, ensure_ascii=False)
    print(len(order), 'points,', len(out), 'documents,', sum(len(d['pieces']) for d in out), 'pieces,',
          sum(len(d['pieces']) * len(d['questions']) for d in out), 'cells')


if __name__ == '__main__':
    {'pull': pull, 'prep': prep}[sys.argv[1]]()
