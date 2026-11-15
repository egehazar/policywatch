"""Which ToS;DR documents to re-crawl first: one row per stored document behind the listed stale points.

String matching only, no model. Reads the stored-copy checks (stale/phoenix.py) of the 20 platforms
(stale/out/phoenix.jsonl) and of the wider collections (stale/wide/<collection>/out/phoenix.jsonl), keeps the points
listed on the pages (dropped in an edit by the platform itself), and groups them by ToS;DR document. A point "breaks
on re-crawl" when the stored copy still holds its quote (coverage at least .8, as the pages count it) while the
archive's current text does not; it is "already lost" when the stored copy no longer holds it either.
Rows are sorted by the points that break on re-crawl, then by the age of the stored copy.
Usage  py -m stale.recrawl   -> stale/out/recrawl_priority.csv
"""
import csv, glob, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'out')
HOLDS = .8


def sources():
    yield 'pga-versions', os.path.join(OUT, 'phoenix.jsonl')
    for f in sorted(glob.glob(os.path.join(HERE, 'wide', '*', 'out', 'phoenix.jsonl'))):
        yield os.path.basename(os.path.dirname(os.path.dirname(f))), f


def rows():
    by = {}
    for coll, f in sources():
        for r in map(json.loads, open(f, encoding='utf-8')):
            if r.get('drop_kind') != 'platform edit': continue
            k = (coll, r['phoenix_doc'] if r.get('phoenix_doc') is not None else r['doc'])
            d = by.setdefault(k, {'collection': coll, 'service': r['platform'], 'archive_document': r['doc'],
                                  'tosdr_document_id': r.get('phoenix_doc'), 'tosdr_copy_updated': r.get('phoenix_doc_updated_at'),
                                  'tosdr_copy_matches_archive_of': r.get('phoenix_closest_version'),
                                  'breaks_on_recrawl': [], 'already_lost': [], 'no_stored_text': [], 'dropped': []})
            q = r.get('quote_in_phoenix')
            (d['no_stored_text'] if q is None else d['breaks_on_recrawl'] if q >= HOLDS else d['already_lost']).append(r['point'])
            d['dropped'].append(r['dropped'])
    out = []
    for d in by.values():
        ds = sorted(x for x in d.pop('dropped') if x)
        out.append({**{k: v for k, v in d.items() if not isinstance(v, list)},
                    'points_break_on_recrawl': len(d['breaks_on_recrawl']), 'points_already_lost': len(d['already_lost']),
                    'points_no_stored_text': len(d['no_stored_text']), 'first_drop': ds[0] if ds else '', 'last_drop': ds[-1] if ds else '',
                    'point_ids': ' '.join(map(str, sorted(d['breaks_on_recrawl'] + d['already_lost'] + d['no_stored_text'])))})
    out.sort(key=lambda r: (-r['points_break_on_recrawl'], r['tosdr_copy_matches_archive_of'] or '9999', r['service']))
    return out


def main():
    R = rows()
    with open(os.path.join(OUT, 'recrawl_priority.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(R[0])); w.writeheader(); w.writerows(R)
    tot = sum(r['points_break_on_recrawl'] for r in R); cum = 0
    print(f'{len(R)} documents; {tot} points break on re-crawl, {sum(r["points_already_lost"] for r in R)} already lost, '
          f'{sum(r["points_no_stored_text"] for r in R)} with no stored text')
    for n in (10, 20, 40):
        print(f'  the first {n} documents hold {sum(r["points_break_on_recrawl"] for r in R[:n])} of the {tot}')
    for r in R[:12]:
        cum += r['points_break_on_recrawl']
        print(f'  {r["points_break_on_recrawl"]:3d}  {r["service"]} / {os.path.basename(r["archive_document"])[:-3]} '
              f'(ToS;DR document {r["tosdr_document_id"]}, copy matches the archive of {r["tosdr_copy_matches_archive_of"]})')


if __name__ == '__main__':
    main()
