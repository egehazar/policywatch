"""GPT's full-read answer key for the stale points (stale/PREREG_fullread_gpt.md).

ingest <dir>: <dir>/out/gpt_batch_<k>.txt (GPT's final replies) -> stale/out/fullread/gpt_batch_<k>.json, checking each
  reply is one JSON object that covers the batch's documents; then run  py -m stale.fullread verify <pga> gpt.
combine: gold_opus.json + gold_gpt.json -> gold_union.json (a piece counts if either grader cited it) and
  gold_both.json (only if both did); descriptive, for  py -m stale.suggest_eval --primary union|both.

Usage  py -m stale.fullread_gpt ingest <dir>  |  py -m stale.fullread_gpt combine
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); FDIR = os.path.join(HERE, 'out', 'fullread')


def parse(raw):
    a, b = raw.index('{'), raw.rindex('}')
    return json.loads(raw[a:b + 1])


def ingest(src):
    key = json.load(open(os.path.join(FDIR, 'key.json'), encoding='utf-8'))
    report = {}
    for B in key['batches']:
        k = B['batch']; path = os.path.join(src, 'out', f'gpt_batch_{k}.txt')
        if not os.path.exists(path): report[k] = 'NO REPLY'; continue
        try: A = parse(open(path, encoding='utf-8').read())
        except (ValueError, json.JSONDecodeError) as e: report[k] = f'NOT JSON ({e.__class__.__name__})'; continue
        docs = set(B['docs']); miss_d = sorted(docs - set(A))
        miss_c = sum(1 for dl, d in B['docs'].items() for it in key['plan'][d] if dl in A and it['label'] not in A[dl])
        report[k] = 'ok' if not miss_d and not miss_c else f'missing documents {miss_d}, cases {miss_c}'
        with open(os.path.join(FDIR, f'gpt_batch_{k}.json'), 'w', encoding='utf-8') as f: json.dump(A, f, indent=1, ensure_ascii=False)
    print(json.dumps(report, indent=1))


def combine():
    O = json.load(open(os.path.join(FDIR, 'gold_opus.json'), encoding='utf-8'))
    P = json.load(open(os.path.join(FDIR, 'gold_gpt.json'), encoding='utf-8'))
    for name, op in (('union', lambda a, b: a | b), ('both', lambda a, b: a & b)):
        gold = {d: {l: sorted(op(set(O['gold'][d][l]), set(P['gold'].get(d, {}).get(l, [])))) for l in O['gold'][d]} for d in O['gold']}
        with open(os.path.join(FDIR, f'gold_{name}.json'), 'w', encoding='utf-8') as f:
            json.dump({'stats': {'combined_from': ['opus', 'gpt'], 'rule': name}, 'gold': gold}, f, indent=1)
        print(name, sum(bool(v) for d in gold.values() for v in d.values()), 'cases with at least one piece')


if __name__ == '__main__':
    if sys.argv[1] == 'ingest': ingest(sys.argv[2])
    elif sys.argv[1] == 'combine': combine()
