"""Suggestions for the daily digest: where may a newly stale point's case be stated now?

stale.daily is string matching only. This optional step, run after it, ranks the pieces of each live drop's current
document for the point's case question (stale.suggest, unchanged, pointed at stale/live/out), proposes the sentence to
quote from the top piece when the arm is kev (stale.propose), and rebuilds the digest with the same suggestion block
as the curator pages. Kev's scores are cached by piece and question, so a day's run only pays for the documents that
changed.
Usage  py -m stale.daily_suggest <pga-versions> [bm25|kev] [port]
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from stale import daily


def jl(p):
    return {r['point']: r for r in map(json.loads, open(p, encoding='utf-8'))} if os.path.exists(p) else {}


def run(arch, arm='bm25', port='9995'):
    from stale import suggest, propose
    from policywatch import archive
    suggest.OUT = daily.OUT                       # drops() reads OUT/points.jsonl; the rows go to OUT/suggest_<arm>.jsonl
    suggest.run(arch, arm, f'http://127.0.0.1:{port}')
    if arm == 'kev': propose.run(port, daily.OUT)
    runs = []
    for f in sorted(os.listdir(daily.RUNS)):
        with open(os.path.join(daily.RUNS, f), encoding='utf-8') as fh: runs.append(json.load(fh))
    sug = jl(os.path.join(daily.OUT, f'suggest_{arm}.jsonl'))
    prop = jl(os.path.join(daily.OUT, 'propose_kev.jsonl')) if arm == 'kev' else {}
    daily.digest(runs, archive.remote_url(arch) or 'https://github.com/OpenTermsArchive/pga-versions', sug=sug, prop=prop, arm=arm)
    shown = sum(1 for e in runs[-1]['events'] if e['point'] in sug and e['status'] in ('gone', 'partly'))
    print('digest rebuilt with', arm, 'suggestions for', shown, 'of', len(runs[-1]['events']), 'events')


if __name__ == '__main__':
    run(*sys.argv[1:])
