# Pre-registration, part B: does the relocation win hold on services outside the 20 platforms?

Written 2026-11-12 22:30 UTC, before any part A arm (`stale/PREREG_relocate2.md`) has run, and before any model has
scored a held-out point. The arms and readings are fixed now, so part A's result cannot shape them.

## Why
The relocation test and part A use 29 documents from 20 large platforms, as captured by Open Terms Archive. A curator
tool for ToS;DR has to work on any service ToS;DR covers, on ToS;DR's own copy of the text. Part B asks whether the
result replicates there.

## Population (`stale/heldout.py`; network and string matching only)
- **Pool.** The services that ToS;DR's public list (fetched 2026-11-12, 10,292 services) marks comprehensively
  reviewed and rates A-E, minus the 22 pga-versions services: 478 services.
- **Draw.** The pool is shuffled with seed 20261113 and walked in that order.
  - For each service, its approved points are shuffled with seed "20261113-<service id>". Points are taken in that
    order until 5 are eligible or the service runs out.
  - The draw stops at 200 eligible points.
- **Eligible.** A point must meet all of these:
  - its quote has at least 6 words;
  - the quote is in ToS;DR's stored copy of its document (document/v1): at least .8 of its word 6-grams over the
    whole document;
  - the document is English (at least .2 of its words in a 24-word stopword list) and 2,000-150,000 characters long;
  - the quote falls in 1-3 pieces of 1,500 characters (at least .3 of its 6-grams), as in the relocation test.
- **Result of the draw.** It was run before this was written, with no model involved:
  - 202 points from 41 services (45 visited, 4 with no eligible point), in 71 documents;
  - 1,456 pieces and 4,040 piece-question cells;
  - 191 points have one gold piece and 11 have two;
  - 47 points were created on ToS;DR on or after 2025-07-01.
- **The stored text.** ToS;DR's stored HTML is cut at block tags (one block per line), with tags dropped and entities
  decoded, then cut into pieces as for the archive text.

## Arms (`stale/relocate_b.py`): the same settings as the relocation test and part A
- **KEV:** the r20 wrapper, all of a document's questions in one request per piece.
- **KEV_SHORT:** the short layout.
- **QWEN:** the part A prompt, log-odds score and validity gate.
- **RERANK:** bge-reranker-v2-m3, case title, max_length 1,024.
- **BM25 and BGE:** case title, as in the relocation test.
- QNN is not run: it needs other companies' approved quotes for the same case, which the held-out set lacks.

## Measures
- Measures are as in part A, with one change: the cluster bootstrap resamples **services** (41 clusters), because a
  service's documents share authors and templates.
- Only hit@1 can change a reading.

## Readings (fixed now)
- **B0, replication.** REPLICATED if both the KEV - BM25 and KEV - BGE hit@1 intervals are entirely above 0 (the
  relocation test's own reading). Otherwise NOT REPLICATED.
- **B1, base family; B2, reranker; B3, short layout.** These use the same rules as part A's R1, R2 and R3 (R3's
  margin is -.05), with the QWEN validity gate.
- **What the README may claim.**
  - A claim about the reranker or the base family enters the README's headline only if it holds in both part A and
    part B.
  - If the two parts disagree, the README reports both and claims neither.
  - If B0 is NOT REPLICATED, the README says the relocation win was not shown beyond the 20 platforms.
- **Failures.** As in part A: a failed arm is re-run unchanged and resumes per document.

## Exploratory, no reading
hit@1 per arm on the 47 points created on or after 2025-07-01, as a check on memorisation of ToS;DR's public data.

## Order of runs (`run_night.sh`)
- Part A's steps, copied verbatim from `run_reloc2.sh`.
- Then part B: the base arms (venv), QWEN on its own server, KEV, KEV_SHORT, then eval.
- Then the deferred steps of `run_stale.sh`.
- The only change from `run_reloc2.sh` is that part B is inserted before the deferred steps.

## Seen before hashing
- The population numbers above.
- A dry run of the evaluation on random synthetic scores, to test the code. No model has scored a held-out point.

## My prediction
- hit@1: KEV .62, KEV_SHORT .60, RERANK .58, QWEN .48, BM25 .45, BGE .40.
- The documents are shorter (median 18 pieces, against about 40 in the relocation test), so chance is higher.
- P(B0 REPLICATED) = 70%.
- P(B2 = DECISION MODEL BETTER THAN THE RERANKER) = 25%.
- P(B1 = DECISION MODEL BETTER THAN ITS BASE FAMILY) = 45%.
