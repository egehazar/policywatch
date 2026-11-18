"""Export the relocation test's 602 points (three pre-registered samples) as a standalone dataset for inspect_eval/.

Reads the frozen draws in stale/out/ (reloc_docs.json, heldout_docs.json, contrib_docs.json) and writes
inspect_eval/data/points.jsonl and documents.jsonl. Standard library only.
Usage  py -m inspect_eval.export
"""
import hashlib, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'stale', 'out'); DATA = os.path.join(ROOT, 'inspect_eval', 'data')
# sample -> (frozen draw, number of points taken from its fixed order; None = every item, as in that sample's test)
SAMPLES = {'A': ('reloc_docs.json', 200), 'B': ('heldout_docs.json', None), 'D': ('contrib_docs.json', None)}


def psha(P):          # the same digest as stale.relocate.psha
    return hashlib.sha256('\x00'.join(P).encode('utf-8')).hexdigest()[:16]


def export():
    points, docs = [], []
    for s, (fname, n) in SAMPLES.items():
        D = json.load(open(os.path.join(OUT, fname), encoding='utf-8'))
        order = D['order'][:n] if n else D['order']; rank = {p: i for i, p in enumerate(order)}
        rows = []
        for d in D['docs']:
            key = f"{s}:{d['doc']}"; used = False
            for it in d['items']:
                if it['point'] not in rank: continue
                used = True
                rows.append({'id': f"{s}-{it['point']}", 'sample': s, 'rank': rank[it['point']], 'point': it['point'],
                             'service': d.get('service') or it['platform'], 'document': key, 'n_passages': len(d['pieces']),
                             'case_title': it['case_title'], 'question': it['question'], 'gold': it['gold']})
            if used: docs.append({'document': key, 'passages_sha': psha(d['pieces']), 'passages': d['pieces']})
        assert len(rows) == len(order), (s, len(rows), len(order))
        points += sorted(rows, key=lambda r: r['rank'])
    os.makedirs(DATA, exist_ok=True)
    for name, rows in (('points', points), ('documents', docs)):
        with open(os.path.join(DATA, f'{name}.jsonl'), 'w', encoding='utf-8', newline='\n') as f:
            for r in rows: f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print({s: sum(p['sample'] == s for p in points) for s in SAMPLES}, len(docs), 'documents')


if __name__ == '__main__':
    export()
