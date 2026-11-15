"""Exploratory: what the reranker-first cascade saves in time, not in cells.

Kev reads each passage once for all the questions asked of it, so its time is mostly per passage (part B's timings:
about 6.9 s per 1,500-character passage plus 1.05 s per question; the reranker about 0.67 s per passage-question on
part D). The cascade asks Kev only each case's reranker top 10, but a passage in any case's top 10 is still read.
This counts, on part D's documents, the share of passages Kev still reads and estimates the time of both pipelines
from that cost model. No model call: the reranker's scores are in stale/out/contrib_base.json.
Usage  py -m stale.cascade_cost   -> stale/out/cascade_cost.json
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out')
TOPK = 10; KEV_PIECE, KEV_Q, RERANK_CELL = 6.9, 1.05, 0.67


def main():
    D = json.load(open(os.path.join(OUT, 'contrib_docs.json'), encoding='utf-8'))['docs']
    B = json.load(open(os.path.join(OUT, 'contrib_base.json'), encoding='utf-8'))
    P = PR = C = CR = 0; full = casc = rr = 0.0
    for d in D:
        n, qs = len(d['pieces']), d['questions']; keep = {}
        for q in qs:
            s = B['RERANK'][d['doc']][q]; cut = sorted(s, reverse=True)[min(TOPK, n) - 1]
            keep[q] = {i for i, x in enumerate(s) if x >= cut}          # pieces tied with the 10th stay, as in eval
        union = set().union(*keep.values())
        P += n; PR += len(union); C += n * len(qs); CR += sum(len(v) for v in keep.values())
        full += n * (KEV_PIECE + KEV_Q * len(qs)); rr += n * len(qs) * RERANK_CELL
        casc += sum(KEV_PIECE + KEV_Q * sum(i in keep[q] for q in qs) for i in union)
    res = {'pieces': P, 'pieces_kev_reads': PR, 'piece_share': round(PR / P, 3), 'cells': C, 'cells_kev_asked': CR,
           'cell_share': round(CR / C, 3), 'est_hours_full_kev': round(full / 3600, 2), 'est_hours_cascade_kev': round(casc / 3600, 2),
           'est_hours_reranker': round(rr / 3600, 2), 'est_time_share': round((casc + rr) / full, 3),
           'cost_model': {'kev_per_piece_s': KEV_PIECE, 'kev_per_question_s': KEV_Q, 'rerank_per_cell_s': RERANK_CELL}}
    with open(os.path.join(OUT, 'cascade_cost.json'), 'w', encoding='utf-8') as f: json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
