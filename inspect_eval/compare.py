"""Port check: the Inspect task's per-passage scores against the repo's own harness, same model, same points.

Repo scores: stale/out/reloc_qwen.json (sample A, Qwen3.5-4B, stale/relocate2.py qwen). Readings are fixed in
inspect_eval/PLAN_port_check.md.
Usage  <inspect venv python> -m inspect_eval.compare <log.eval> [out.json]
"""
import json, os, statistics as st, sys

from inspect_ai.log import read_eval_log

from inspect_eval.relocation import _jsonl, hit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.join(ROOT, 'stale', 'out', 'reloc_qwen.json')
LINE = .05            # mean |log-odds difference| at or under this: the same computation (PLAN_port_check.md)


def compare(log_path, out_path=None):
    log = read_eval_log(log_path); Q = json.load(open(REPO, encoding='utf-8'))
    P = {p['id']: p for p in _jsonl('points.jsonl')}
    rows, diffs = [], []
    for s in log.samples:
        p = P[s.id]; doc = p['document'].split(':', 1)[1]
        lo_i = list(s.scores.values())[0].metadata['lo']
        lo_r = [cell[p['question']]['lo'] for cell in Q[doc]['scores']]
        assert len(lo_i) == len(lo_r), (s.id, len(lo_i), len(lo_r))
        d = [abs(a - b) for a, b in zip(lo_i, lo_r)]; diffs += d
        (hi, ri), (hr, rr) = hit(lo_i, p['gold']), hit(lo_r, p['gold'])
        rows.append({'id': s.id, 'cells': len(d), 'max_abs_dlo': round(max(d), 4), 'hit1': [hi[1], hr[1]], 'rr': [ri, rr],
                     'top_same': max(range(len(lo_i)), key=lo_i.__getitem__) == max(range(len(lo_r)), key=lo_r.__getitem__)})
    n = len(rows); m = lambda k, j: sum(r[k][j] for r in rows) / n
    res = {'log': os.path.basename(log_path), 'points': n, 'cells': len(diffs),
           'mean_abs_dlo': round(st.mean(diffs), 4), 'max_abs_dlo': round(max(diffs), 4),
           'top_passage_same': sum(r['top_same'] for r in rows),
           'inspect': {'hit1': round(m('hit1', 0), 3), 'mrr': round(m('rr', 0), 3)},
           'repo': {'hit1': round(m('hit1', 1), 3), 'mrr': round(m('rr', 1), 3)}}
    same = res['mean_abs_dlo'] <= LINE and abs(res['inspect']['hit1'] - res['repo']['hit1']) <= .01 \
        and abs(res['inspect']['mrr'] - res['repo']['mrr']) <= .01
    res['reading'] = 'port reproduces the repo' if same else 'port differs'
    res['rows'] = rows
    if out_path:
        with open(out_path, 'w', encoding='utf-8', newline='\n') as f: json.dump(res, f, indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != 'rows'}, indent=1))
    return res


if __name__ == '__main__':
    compare(*sys.argv[1:])
