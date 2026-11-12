# Pre-registration: can a decision model re-find the evidence for approved ToS;DR points?

Written before any arm (Kev, bge, BM25) has scored a single piece of these documents. Code: `stale/relocate.py`
(hashed with this file in `PREREG_relocate.sha256`, together with stale/match.py, stale/triage.py, policywatch/watch.py,
`policywatch/diffing.py`, stale/out/points.jsonl and stale/out/reloc_docs.json, which fixes the pieces, gold and order).
An independent code review (11-12) found and I fixed, before this hash: tag and list-number normalization that hid
present quotes, the home-document choice, tie handling in hit@k, short-quote gold, and unguarded partial runs.

## Why this test
The r20 test's answer key came from two LLM raters. This one uses human labels: ToS;DR curators approved each point
with a quote from the document. Where that quote is still in the platform's current text, the quote marks a place
where the curator says the case is stated. A tool that keeps approved answers current has to do exactly this when a
quote disappears: find where the case is now stated, or report that it no longer is.

Prior art and the need: ToS;DR's own platform already marks an approved point "approved-not-found" when a recrawl
cannot find its quote, and curators then search the new text by hand. Its December 2020 recrawl did this to 1,589
points (forum post "Recrawled all documents", tosdr.community/t/415). Detecting a missing quote is therefore not new;
this test is about the manual step after it.

## Data
- ToS;DR approved points (api.tosdr.org, pulled 2026-11-12) for the 22 Open Terms Archive pga-versions platforms
  that ToS;DR covers. `stale/data/`.
- Each point's home document: the archive document whose recorded versions best contain its quote (`stale/match.py`,
  word 6-gram coverage). Points whose quote is in no archived version are left out.
- The current version (archive HEAD, 2026-11-11) of each home document, cut into pieces of at most 1,500 characters
  at paragraph boundaries.
- Counts (from `prep`, before any scoring): 1,114 approved points with a quote on the 20 platforms that have any
  (Threads and WeChat have none); 757 quotes still present in the current text, 83 partly, 97 gone, 177 in no
  archived version. 48 home documents, 1,851 pieces, 2.39M characters.
- Twitter/: the archive stopped updating this folder in 2023-24 (X/ holds the current text). It is used as history
  only, never as a point's current home.
- Eligible points: present, quote of at least 6 words (shorter quotes are mostly headings and match many pieces),
  and 1-3 gold pieces (more means boilerplate repeated across the document): 726 points.

## Arms (each ranks a document's pieces for one point's case question)
- KEV: Kev-4B Q8 (llama.cpp /v1/systemone, the policywatch wrapper) answers "Does the text state or clearly imply the
  following: <case title>?" on each piece; rank by p(yes). The case questions of a document's sampled points go in one request per piece.
- BGE: bge-small-en-v1.5 cosine, query = its retrieval instruction + case title.
- BM25: case title words (minus a fixed stop list) against the document's pieces.
- RANDOM: expectation.

## Gold and metric
- Gold pieces of a point: pieces holding >= .3 of its quote's word 6-grams.
- Sample: the eligible points in a fixed random order (seed 20261112, stored in reloc_docs.json). A run scores the
  first N. N is the largest of 100, 150, 200, 300, 400, 500, 726 whose Kev cost fits 6 CPU hours, estimated from the
  Kev timing of the Kev-vs-Qwen benchmark (bench/out/kev_timing.jsonl, kev_scale.jsonl) before any piece here is
  scored. If Kev is later run further down the same order, every N is reported, the first one as primary.
- Each document gets the case questions of its sampled points; BGE and BM25 score every question (cheap), but only
  sampled points are evaluated.
- Primary: hit@1 (the top-ranked piece is a gold piece), ties broken in expectation. Also hit@3, hit@5, MRR.
- Uncertainty: 95% interval of KEV minus each baseline, cluster bootstrap over documents (2,000 draws, seed 20261112).

## Reading (fixed now)
- DECISION MODEL BETTER: KEV hit@1 minus BGE hit@1 AND KEV minus BM25 both have a 95% interval above 0.
- BASELINE BETTER: either interval is entirely below 0.
- Otherwise NO CLEAR DIFFERENCE.
- Cost is not part of this reading: the CPU is shared with other jobs while this runs. The Kev-vs-Qwen benchmark
  measures cost on an idle CPU.

## Known limits (stated now)
- A case is often stated in more than one place; the quote marks one. Hit rates are lower bounds for every arm.
- Curators may have picked quotes with help from ToS;DR's own ML suggestions (DocBot), which could favour
  retrieval-like arms.
- Case titles are ToS;DR's wording; some are vague or broad ("Your personal information is used for many different
  purposes").
- One model and quantization; one piece size; current versions only.

## Not part of the reading
- For points whose quote is gone or partly gone, each arm's top piece is the "the point may now be stated here"
  suggestion. Whether those suggestions are right needs a person (or disclosed LLM raters) and is reported apart.

## My prediction (before scoring)
hit@1 about KEV .45, BGE .35, BM25 .30. P(DECISION MODEL BETTER) = 50%. P(BASELINE BETTER) = 10%.
