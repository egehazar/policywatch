# Pre-registration, part D: relocation on Open Terms Archive's contrib collection, and the reranker-first cascade

Written 2026-11-14 ~20:50 UTC, after parts A and B (`stale/RESULT_relocate2.md`) and before any model has scored a
contrib point. The population is drawn by code fixed here, after the ToS;DR pull for the contrib services finishes.

## Why
- **Replication where the tool now runs.** `stale/wide.py` extends the curator page to every Open Terms Archive
  contrib service that ToS;DR reviews. Its suggestions rank the archive's current text, as in part A, but on about 150
  other services. Part B replicated on ToS;DR's own stored text; part D asks the same question on the archive text
  the wider page uses.
- **A cheaper pipeline.** In parts A and B, Kev asked only about the reranker's top 10 pieces (CASCADE_RERANK) lost
  nothing: +.010 [-.024, +.040] and +.005 [-.015, +.026]. The cascade was secondary there. Part D decides whether the
  wider pages adopt it.

## Population (`stale/relocate_d.py prep`; no model)
- **Source.** `stale/wide/contrib/out/points.jsonl`, built by `stale/wide.py` (map, pull, match, dedupe) from:
  - the contrib-versions clone at its HEAD when the draw runs, recorded in `contrib_docs.json` and checked unchanged
    at eval;
  - ToS;DR's approved points as pulled on 2026-11-14 and 15 (the pull runs past midnight UTC).
- **Mapping.** OTA folders holding a pga platform's own documents (contrib's Facebook, YouTube, WeChat Open Platform
  and others, `stale/wide.py pga_folder`) are left out, so the 20 platforms are outside part D.
- **Eligible.** A point must meet all of these:
  - status present: at least .8 of its quote's word 6-grams are in the current text of its home document;
  - its quote has at least 6 words;
  - its ToS;DR service is not one of the 45 services part B's draw visited (41 of them gave points);
  - its home document's current text (paragraphs joined, as `stale/suggest.py` and `stale/relocate.py` read it) is
    2,000-150,000 characters, and at least .2 of its words are in part B's stopword list (28 words,
    `stale/heldout.py`; part B's pre-registration called it a 24-word list);
  - the quote falls in 1-3 pieces of 1,500 characters (at least .3 of its 6-grams), as in every part.
- **Draw.** Eligibility is computed for every point first. The ToS;DR services with at least one eligible point
  (sorted by id) are shuffled with seed 20261115 and walked in that order. For each service, all of its points in
  `points.jsonl` (any status, sorted by id) are shuffled with seed "20261115-<service id>", and the eligible ones are
  taken in that order until 5 are taken or the service runs out. The draw stops once at least 200 points are taken.
- **Documents.** Each drawn point's home document is asked only the drawn points' case questions, as in part B.

## Arms (part B's code, unchanged: `stale/relocate_b.py` pointed at `stale/out/contrib_docs.json`)
- **KEV:** Kev-4B Q8, the r20 wrapper, all of a document's questions in one request per piece.
- **RERANK, BGE and BM25:** bge-reranker-v2-m3 (max_length 1,024), bge-small and BM25, each given the case title.
- **CASCADE_RERANK:** Kev's scores restricted to the reranker's top 10 pieces per case question (pieces tied with the
  10th stay in); other pieces rank last. It is computed from the KEV and RERANK scores on disk.
- QWEN and KEV_SHORT are not run.

## Measures
- hit@1, 3 and 5 and MRR per arm, ties broken in expectation (`relocate.hit`).
- Paired hit@1 differences with a 95% cluster bootstrap over ToS;DR services (2,000 draws, seed 20261112, as in
  `relocate2.boot`).
- Cost: seconds per piece-question cell for KEV and RERANK. For the cascade, the share of Kev's cells it would ask.
- Only hit@1 can change a reading.

## Readings (fixed now)
- **D0, replication.** REPLICATED if both the KEV - BM25 and KEV - BGE intervals are entirely above 0. Otherwise NOT
  REPLICATED.
- **D1, cascade.** If the lower bound of CASCADE_RERANK - KEV is at least -.03: CASCADE ADOPTED.
  - Then the wider pages' Kev suggestions (`stale/wide.py kev`) and later daily runs ask Kev only about the reranker's
    top 10 pieces per case.
  - Otherwise KEV KEPT.
  - The 20-platform page, already built, is not re-run.
- **D2, reranker.** The rule of R2 and B2 for KEV - RERANK: DECISION MODEL BETTER THAN THE RERANKER, RERANKER BETTER,
  or NO DIFFERENCE SHOWN. D2 is reported beside parts A and B. It does not change the README's reranker line on its
  own: that line keeps the rule of parts A and B, and gains the third result.
- **Consequences.**
  - The README gets one row per reading.
  - If D0 is NOT REPLICATED, the wider pages say that the relocation win was not shown on the archive's contrib text.
- **Failures.** A failed arm is re-run unchanged and resumes per document. Nothing in this file, the arms or the
  readings is edited after hashing.

## Seen before hashing
- A dry run of prep and eval on the first 30 pulled contrib folders, with random synthetic scores, written to a
  scratch folder, to test the code: 43 points, 9 services, 10 documents. No model has scored any contrib point.
- While building `stale/wide.py` I looked at the dropped points of the first 30 folders (Apple Game Center, Airbnb,
  Netflix), not at any present point's text or gold.

## Changes before the draw (2026-11-14 ~21:35 UTC, after an independent code review; no draw had run)
- The draw code shuffled services with any present 6-word point and, per service, only those points; it now follows
  the text above (eligibility first; all of a service's points shuffled).
- `run_wide.sh` now stops unless the pull and the match succeeded and every mapped folder has its data, and the
  dry-run files are removed first.
- The archive HEAD is recorded at the draw and checked at eval, not read at eval.
- The mapping: subdomains on shared hosts no longer map to the host's owner (contrib's Tumblr had mapped to
  WaniKani), code hosts need the service's name in the folder's (SponsorBlock had mapped to GitHub), and pga
  platforms' own folders are left out. The pull for the new mapping resumes before the draw.
- Wording: the stopword list has 28 words; part B visited 45 services; the pull spans two dates.
- `stale/reloc_margin.py` compares the unrounded clear hit@1 with the .85 bar.

## Order of runs
1. Finish the contrib pull, then `stale.wide match contrib` (with dedupe and the broken-capture guard).
2. `py -m stale.relocate_d prep`; append the hashes of `contrib_docs.json` and `stale/wide/contrib/out/points.jsonl`
   to `stale/PREREG_relocate_d.sha256` before any model call.
3. `<venv python> -m stale.relocate_d base`, then `py -m stale.relocate_d kev`. These may share the CPU with the
   deferred steps of `run_resume.sh` and with the wider pages' Kev suggestions: cost is reported with that noted.
4. `py -m stale.relocate_d eval`, with the result hashes appended.

## My prediction
- hit@1: KEV .65, CASCADE_RERANK .64, RERANK .58, BM25 .40, BGE .38.
- P(D0 REPLICATED) = 85%.
- P(D1 CASCADE ADOPTED) = 75%.
- P(D2 = DECISION MODEL BETTER THAN THE RERANKER) = 35%.
