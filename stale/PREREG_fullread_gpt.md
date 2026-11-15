# A second full answer key from another company: GPT re-grades the 141 stale points (written before GPT runs)

Written 2026-11-15 ~10:50 UTC. Exploratory addition to `stale/PREREG_suggest.md`; it changes no reading there.

## Why
The stale-point suggestion result (`stale/RESULT_suggest.md`: Kev's first suggestion right for 74% of the 69 "gone"
points, by document) is graded against one answer key, Claude Opus reading every piece of every current document.
GPT and Fable agreed with that key on 60 sampled cards (`stale/PREREG_gate_llm.md`, kappa .67 and .82). This goes
further: a rater from another company builds a whole second answer key from the same inputs, and every arm is scored
against it. If the ranking of the methods and Kev's level hold, the result does not hinge on one grader.

## Rater
- GPT through Codex CLI 0.154.0 (`codex exec`), model gpt-6-astra, reasoning effort xhigh (Ege's config), read-only
  sandbox, an empty folder, no web. Up to 3 runs at a time.
- Input: the same 12 batch files the Opus grader read (`stale/out/fullread/batch_<k>.md`: whole current documents cut
  into the same pieces, the stale cases mixed with known-positive controls, no old quotes, no arm outputs), verbatim,
  preceded by the Opus prompt's rules adapted to a reply instead of a file: read all of it, judge from the text only,
  quote verbatim, cover every case, reply with only the JSON object.
- One run per batch; a batch is rerun once only if its reply is not parseable JSON or misses documents (said so).
- Quotes are checked exactly as for Opus (`py -m stale.fullread verify <pga> gpt` -> `gold_gpt.json`).

## What is computed
1. `py -m stale.suggest_eval --primary gpt` -> `stale/out/suggest_result_gpt.json`: the same statistics as the
   official run (stated/none counts, control recall, AUROC, top-1 by document and pooled, found in top 3, arm minus
   Kev intervals), with GPT's key in place of Opus's, and GPT vs Opus agreement on stated/none over all 141 cases.
2. Descriptive only: the same with a key that counts a piece if either grader cited it (`union`), and one that counts
   it only if both did (`both`).
The official `stale/out/suggest_result.json` (Opus key) is not changed.

## Reading (fixed now; on the "gone" points, top-1 by document)
- **HOLDS UNDER A SECOND GRADER** if, with GPT's key: Kev's top-1 is within .10 of .741, AND the bm25-minus-Kev and
  bge-minus-Kev intervals both lie below zero (Kev ahead of both, as with Opus's key).
- **DEPENDS ON THE GRADER** otherwise; then the 74% is quoted only together with GPT's figure.
- The quote_bm25 vs Kev comparison (no difference with Opus's key) is reported, not read.
- GPT's control recall is reported; if it is below .85 (the bar Opus had to pass), the reading above is marked as
  resting on a weaker key.

## Predictions
Kev top-1 on gone points with GPT's key .65-.80; GPT control recall .85-.95; GPT vs Opus stated/none agreement
80-90% of cases; Kev still ahead of BM25 and bge.
