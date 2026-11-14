"""One CSV row per approved ToS;DR point whose quote dropped in a platform edit, for curators who work outside the page.

Columns as in stale/out/stale_points.csv (the frozen 11-12 file), plus the archive's latest capture of the document and
the suggestion shown on the page: the top passage's number and the proposed quote (Kev, when stale.propose has run;
otherwise the arm's top passage alone).
Usage  py -m stale.export [data dir] [csv path] [repo url] [arm]
       defaults: stale/out -> stale/out/stale_points_suggested.csv, pga-versions, kev
"""
import csv, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

COLS = ['tosdr_point', 'point_url', 'platform', 'case', 'classification', 'archive_document', 'quote_status',
        'current_coverage', 'quote_dropped_on', 'archive_commit', 'point_last_edited', 'tosdr_copy_holds_quote',
        'archive_latest_capture', 'new_passage', 'suggestion_arm', 'suggested_passage', 'suggested_quote']


def jl(p):
    return [json.loads(l) for l in open(p, encoding='utf-8')] if os.path.exists(p) else []


def rows(base, repo, arm='kev'):
    pts = jl(os.path.join(base, 'points.jsonl'))
    pas = {r['point']: r for r in jl(os.path.join(base, 'passages.jsonl'))}
    phx = {r['point']: r for r in jl(os.path.join(base, 'phoenix.jsonl'))}
    sug = {r['point']: r for r in jl(os.path.join(base, f'suggest_{arm}.jsonl'))}
    prop = {r['point']: r for r in jl(os.path.join(base, 'propose_kev.jsonl'))} if arm == 'kev' else {}
    out = []
    for r in pts:
        if r['status'] not in ('gone', 'partly') or r.get('drop_kind') != 'platform edit': continue
        ps = (pas.get(r['point']) or {}).get('passage') or {}
        new = '' if not ps else 'none similar' if ps.get('removed') else 'edited' if ps.get('similarity', 0) >= .6 else 'reworded'
        x = phx.get(r['point']) or {}; q = x.get('quote_in_phoenix')
        s = sug.get(r['point']) or {}; top = (s.get('top') or [None])[0]; p = prop.get(r['point'])
        out.append({'tosdr_point': r['point'], 'point_url': f'https://edit.tosdr.org/points/{r["point"]}', 'platform': r['platform'],
                    'case': r['case_title'], 'classification': r.get('classification') or '', 'archive_document': r['doc'],
                    'quote_status': r['status'], 'current_coverage': r['current_coverage'], 'quote_dropped_on': r['dropped_at']['date'],
                    'archive_commit': f'{repo}/commit/{r["dropped_at"]["commit"]}', 'point_last_edited': r['point_updated_at'],
                    'tosdr_copy_holds_quote': '' if q is None else 'yes' if q >= .8 else 'no',
                    'archive_latest_capture': r.get('latest_capture', ''), 'new_passage': new,
                    'suggestion_arm': arm if top else '', 'suggested_passage': f'{top["piece"] + 1} of {s["n_pieces"]}' if top else '',
                    'suggested_quote': re.sub(r'\s+', ' ', p['quote']).strip() if p else ''})
    return out


def write(base=os.path.join(HERE, 'out'), path=None, repo='https://github.com/OpenTermsArchive/pga-versions', arm='kev'):
    path = path or os.path.join(base, 'stale_points_suggested.csv')
    R = rows(base, repo, arm)
    with open(path, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, COLS); w.writeheader(); w.writerows(R)
    print(path, len(R), 'rows,', sum(1 for r in R if r['suggested_quote']), 'with a suggested quote')


if __name__ == '__main__':
    write(*sys.argv[1:])
