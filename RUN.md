# Running policywatch

```
llama-server -m kev-4b-q8.gguf --port 9995 -np 4 -c 16384      # a llama.cpp build with /v1/systemone
python -m policywatch scan   --archive path/to/pga-versions --since 2026-10-01
python -m policywatch report --archive path/to/pga-versions
python -m policywatch serve                                    # review at http://127.0.0.1:8787
python -m unittest discover -s tests
```
Stale evidence, 20 platforms (network: api.tosdr.org, about one request per 0.6 s):
```
python -m stale.pull                                   # ToS;DR's approved points -> stale/data/
python -m stale.match   path/to/pga-versions           # quote coverage in every version -> stale/out/points.jsonl
python -m stale.triage  prep path/to/pga-versions      # old and new passage of each drop
python -m stale.phoenix path/to/pga-versions           # does ToS;DR's stored copy still hold the quote?
python -m stale.suggest path/to/pga-versions kev       # top 3 passages of the current text per stale point (Kev)
python -m stale.propose                                # the sentence to quote from the top passage (Kev)
python -m stale.report  https://github.com/OpenTermsArchive/pga-versions kev   # out/site/stale.html
python -m stale.export                                 # the same as a CSV
python -m stale.daily   path/to/pga-versions           # what changed since the last run
python -m stale.daily_suggest path/to/pga-versions kev # Kev's suggestions for the new drops in the daily digest
python -m stale.missing_watch check path/to/pga-versions # missing-points documents whose text changed since scored
<sentence-transformers python> -m stale.missing_watch rerank; python -m stale.missing_watch kev; python -m stale.missing_page
python -m stale.recrawl                                # which ToS;DR documents to re-crawl first (all collections)
```
Missing points, a new set of documents through the cascade (the pattern of `stale/missing_wide.py`, `missing_rest.py`
and `missing_contrib.py`; the curator page is `out/site/missing.html`):
```
python -m stale.missing_contrib prep                   # draw the documents and their candidate cases (no model)
<sentence-transformers python> -m stale.missing_contrib rerank   # reranker on every passage-case cell
python -m stale.missing_contrib kev                    # Kev on the reranker's top 3 passages per case
python -m stale.missing_contrib cards                  # blind cards for raters; then `score` once they are filled
python -m stale.missing_page                           # rebuild the curator page
```
The same for other Open Terms Archive collections (`stale/wide.py`; clone `<collection>-versions` and
`<collection>-declarations` next to pga-versions): `python -m stale.wide map|pull|match|cheap|kev <collection>`.
The cheaper suggestions adopted in part D: `<sentence-transformers python> -m stale.cascade rerank <collection>`,
then `python -m stale.cascade kev <collection>`. `daily.cmd` chains the daily steps for Windows Task Scheduler.
Python 3.12+ (tested on 3.14). The core is standard library only; the bge and reranker arms need
sentence-transformers.
