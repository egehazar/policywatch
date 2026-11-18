# Running policywatch

## Setup (the local models and build behind RESULTS.md)
- **Machine.** One desktop CPU (Intel Core i5-11600K, 6 cores), 32 GB RAM, no GPU. Servers run with `-t 6`.
- **Kev-4B.** `Kev-4B-Q8_0.gguf` from huggingface.co/ggml-org/Kev-4B-GGUF, revision f4624b6b, 4,483,801,504 bytes,
  sha256 7c2ebed90560522c2801389db482ac1dc4c36d828f201f6074c1d60e433948da (model: huggingface.co/jaredpalmer/kev-4b).
- **Instruct baseline.** `Qwen3.5-4B-Q8_0.gguf` from huggingface.co/unsloth/Qwen3.5-4B-GGUF (base Qwen/Qwen3.5-4B),
  sha256 10cc391b403021dd11c614679d2fd92f611c3681d29e29651b717316965d61e1.
- **Server.** llama.cpp (github.com/ggml-org/llama.cpp) at commit 954de24 (2026-11-06), which serves the decision
  endpoint `/v1/systemone`, plus one local patch, "server : checkpoint shared prefixes for decision tasks" (for
  llama.cpp issue #31475: without it a hybrid model recomputes the shared passage for every group of questions
  larger than the slot count). The patch changes what is recomputed, not what is computed; a stock build at 954de24
  should give the same scores up to small numeric differences, and may be slower on passages with more questions
  than slots. All timings were taken on the patched build.
  - Kev (as deployed): `llama-server -m Kev-4B-Q8_0.gguf --port 9995 -np 4 -c 16384 -t 6 --no-mmproj`
  - Instruct baseline: `llama-server -m Qwen3.5-4B-Q8_0.gguf --port 9996 -np 1 -c 16384 -t 6 --jinja`
    (bench/start_qwen.ps1)
- **Documents.** Clone github.com/OpenTermsArchive/pga-versions (and, for other collections,
  `<collection>-versions` and `<collection>-declarations` next to it).
- **Python.** 3.12+ (tested on 3.14). The core is standard library only; the bge and reranker arms need
  sentence-transformers (BAAI/bge-small-en-v1.5, BAAI/bge-reranker-v2-m3). `python -m pytest -q tests` runs without
  any model or archive; one test that compares against a frozen external file skips when that file is absent.

## Commands

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
