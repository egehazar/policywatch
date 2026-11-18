"""Addendum 2 to stale/PLAN_multiq.md: Kev on a 1-slot server again, with the llama.cpp patch fixed for one slot
(stale/PLAN_multiq_addendum2.md).

Usage  py -m stale.multiq_np1v3 kev [port]   -> stale/out/multiq_kev_np1v3.json  (server: build-fix3, -np 1 -c 16384 -t 6)
       py -m stale.multiq_np1v3 result       -> stale/out/multiq_np1v3_result.json
"""
import json, os, statistics as st, sys, time
from stale.missing import save
from stale.missing2 import load
from stale.multiq import F as FM, cells
from stale.multiq_np1 import F as F1, MULTI_S_PER_Q
from stale.triage import TEMPLATE

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out')
F = {'kev': os.path.join(OUT, 'multiq_kev_np1v3.json'), 'result': os.path.join(OUT, 'multiq_np1v3_result.json')}


def kev(port='9998'):
    from policywatch.scorer import Server, qid
    S = Server(f'http://127.0.0.1:{port}'); assert S.served == 'Kev-4B-Q8_0.gguf', S.served
    out = load(F['kev']); t0 = time.time()
    for n, (doc, i, text, cs) in enumerate(cells(), 1):
        key = f'{doc}|{i}'
        if key in out: continue
        qs = [TEMPLATE.format(c) for c in cs]
        t = time.perf_counter(); ans = S.ask(text, {qid(q): q for q in qs}); sec = time.perf_counter() - t
        out[key] = {'sec': round(sec, 3), 'k': len(cs), 'p': {c: ans[qid(q)] for c, q in zip(cs, qs)}}
        save(F['kev'], out)
        if n % 25 == 0: print(f'[kev np1v3 {n} {time.time() - t0:.0f}s]', flush=True)
    print('kev np1v3 done')


def result():
    K3, K1, K4 = load(F['kev']), load(F1['kev']), load(FM['kev'])
    keys = [f'{d}|{i}' for d, i, _, _ in cells()]
    assert all(k in K3 for k in keys), 'run incomplete'
    dp = lambda A: st.mean(abs(K3[k]['p'][c] - A[k]['p'][c]) for k in keys for c in A[k]['p'])
    flips = lambda A: sum((K3[k]['p'][c] > .5) != (A[k]['p'][c] > .5) for k in keys for c in A[k]['p'])
    q = sum(K3[k]['k'] for k in keys)
    spq = lambda A: sum(A[k]['sec'] for k in keys) / q
    k3, k1, k4 = spq(K3), spq(K1), spq(K4)
    S, R = k1 / k3, MULTI_S_PER_Q / k3
    agree = dp(K1)
    if agree > .01: reading = 'void'
    else: reading = "Kev's cost edge holds" if R >= 1.5 else 'edge gone' if R <= 1.0 else 'edge reduced'
    res = {'agreement_mean_abs_dp_vs_v2_1_slot': round(agree, 4), 'flips_vs_v2_1_slot': flips(K1),
           'mean_abs_dp_vs_v2_4_slots': round(dp(K4), 4), 'flips_vs_v2_4_slots': flips(K4), 'questions': q,
           'v3_1_slot_s_per_question': round(k3, 3), 'v2_1_slot_s_per_question': round(k1, 3),
           'v2_4_slots_s_per_question': round(k4, 3), 'S_speedup_v2_over_v3_1_slot': round(S, 2),
           'multi_s_per_question_main_run': MULTI_S_PER_Q, 'R_multi_over_v3_1_slot': round(R, 3),
           'patch_reading': 'speedup on the real workload' if agree <= .01 and S >= 2 else 'no clear speedup',
           'reading': reading}
    with open(F['result'], 'w', encoding='utf-8', newline='\n') as f: json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    {'kev': kev, 'result': result}[cmd](*sys.argv[2:])
