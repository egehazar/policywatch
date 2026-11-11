"""policywatch command line.

  python -m policywatch scan   --archive PATH [--since YYYY-MM-DD] [--until ...] [--server URL] [--out DIR]
  python -m policywatch report [--out DIR]
  python -m policywatch seed   --frozen DIR        (import the r20 test's Kev scores into the cache)
  python -m policywatch eval   --frozen DIR        (accuracy on the frozen r20 test -> OUT/eval.json)
"""
import argparse, json, os, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from . import archive, report, watch
from .scorer import Cache, Scorer, Server, qid

HERE = os.path.dirname(os.path.abspath(__file__))
DEF_BANK = os.path.join(HERE, '..', 'data', 'bank.json')


def main(argv=None):
    ap = argparse.ArgumentParser(prog='policywatch')
    ap.add_argument('cmd', choices=['scan', 'report', 'seed', 'eval'])
    ap.add_argument('--archive'); ap.add_argument('--since'); ap.add_argument('--until')
    ap.add_argument('--docs', default=','.join(archive.DEFAULT_DOCS)); ap.add_argument('--platforms')
    ap.add_argument('--server', default='http://127.0.0.1:9995'); ap.add_argument('--model-name', default='kev-4b-q8')
    ap.add_argument('--bank', default=DEF_BANK); ap.add_argument('--out', default='out')
    ap.add_argument('--tau', type=float, default=.3); ap.add_argument('--workers', type=int, default=2)
    ap.add_argument('--limit', type=int); ap.add_argument('--no-localize', action='store_true')
    ap.add_argument('--frozen'); ap.add_argument('--repo-url')
    a = ap.parse_args(argv)
    bank = watch.load_bank(a.bank)
    cache = Cache(os.path.join(a.out, 'cache.sqlite')); scorer = Scorer(Server(a.server, a.model_name), cache)

    if a.cmd == 'scan':
        us = archive.updates(a.archive, a.docs.split(','), a.since, a.until, a.platforms.split(',') if a.platforms else None)
        done = {os.path.splitext(f)[0] for f in os.listdir(os.path.join(a.out, 'updates'))} if os.path.isdir(os.path.join(a.out, 'updates')) else set()
        todo = [u for u in us if u.key not in done][:a.limit]
        print(f'{len(us)} updates, {len(us) - len(todo)} already done, {len(todo)} to scan', flush=True)
        t0 = time.time()

        def one(u):
            old, new = archive.texts(a.archive, u)
            if not old.strip() or not new.strip(): return u, None
            rec = watch.analyze(u, old, new, scorer, bank, a.tau, localize=not a.no_localize)
            watch.save(rec, a.out); return u, rec
        with ThreadPoolExecutor(a.workers) as ex:
            for n, fu in enumerate(as_completed([ex.submit(one, u) for u in todo]), 1):
                u, rec = fu.result()
                tag = 'skipped (missing side)' if rec is None else rec['kind'] + (f", {rec.get('n_flagged', 0)} flagged" if rec['kind'] == 'scored' else '')
                print(f'[{n}/{len(todo)} {time.time() - t0:.0f}s] {u.date} {u.platform} {u.doc}: {tag}', flush=True)
        print(f'questions asked {scorer.asked}, cache hits {scorer.hits}', flush=True)

    elif a.cmd == 'report':
        repo = a.repo_url or (archive.remote_url(a.archive) if a.archive else 'https://github.com/OpenTermsArchive/pga-versions')
        site, n = report.build(a.out, repo, len(bank)); print(f'{n} updates -> {site}')

    elif a.cmd == 'seed':
        pairs = [json.loads(l) for l in open(os.path.join(a.frozen, 'pairs.jsonl'), encoding='utf-8')]
        kev = {json.loads(l)['id']: json.loads(l)['p'] for l in open(os.path.join(a.frozen, 'kev.jsonl'), encoding='utf-8') if l.strip()}
        n = 0
        for p in pairs:
            for side in ('old', 'new'):
                ps = kev.get(f"{p['id']}|{side}")
                if ps: cache.put(scorer.server.id, p[side + '_region'], {qid(bank[int(k[1:])]['q']): v for k, v in ps.items()}); n += 1
        print(f'seeded {n} regions; cache rows {cache.count()}')

    elif a.cmd == 'eval':
        from .evaluate import run
        ev = run(a.frozen, a.tau); json.dump(ev, open(os.path.join(a.out, 'eval.json'), 'w', encoding='utf-8'), indent=1)
        print(json.dumps({k: v for k, v in ev.items() if k != 'html'}, indent=1))


if __name__ == '__main__':
    sys.exit(main())
