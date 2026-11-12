# Pre-registration: on the real stale points, can the decision model tell that a case is no longer stated, and how good are the suggestions?

Written 2026-11-12, after the relocation result (`stale/RESULT_relocate.md`) and after Fable 5.2's round-27 critique
of a first draft (pooled gold; notes/fable_r27_brief.md). No arm below has been run on the stale points except BM25
(run earlier for the curator page; never judged). The full-read rater batches were built (`stale/fullread.py prep`)
before hashing; no rater has seen them.

## Why
The relocation test used survivors: points whose quote is still in the current text. It could not produce the costly
error: re-anchoring a point to a passage that does not state the case, or keeping a point that no longer holds.
The points a curator actually has to fix are the 141 whose quote dropped in a platform edit (82 gone, 59 partly).
On the 200 survivors (all positives; inspected before this was written), Kev's best non-gold piece scored >= .5 for
65% of points. So Kev's score alone may not say "not stated any more". Only judged negatives can show it.

## Population
The 141 points of the curator page (`stale/out/points.jsonl`, status gone or partly, drop_kind "platform edit"),
in 32 documents, on archive HEAD b2ac8a9367544a3591bd88d96f0581c9cef6121c. Strata: 82 gone (primary for the
suggestions), 59 partly.

## Gold: full read, arm-independent (`stale/fullread.py`)
- **What raters see.** Each rater reads whole current documents, cut into the same 1,500-character pieces as the
  arms and labelled P1..Pn in document order. Each document has a list of cases: title, ToS;DR description (API
  case/v3, fetched 11-12) and classification. Raters see no old quote and no arm output.
- **What raters do.** For every case, they quote every passage (up to 5) that states or clearly implies it, with its
  piece label, or answer none.
- **Verification.** A quote counts only if it is found in the text: at least .8 of its word 6-grams in the cited
  piece, else in a neighbouring piece, else anywhere in the document. Unverified quotes are dropped and counted.
- **Batches.** 12 batches of up to 200,000 characters, whole documents only (`key.json`): 32 documents, 141 stale
  cases (no two stale points share a case in one document) and 74 control cases. 15 of the 174 cases have no ToS;DR
  description and are shown with "(none)". Every rater gets the same prompt (`stale/RATER_PROMPT.md`).
- **Positive controls.** Up to 3 control cases per document are mixed in, unmarked: cases whose approved ToS;DR
  quote is still in 1-3 current pieces, with no stale case shared. Rater recall on controls is the share of control
  cases where the rater cites at least one of the gold pieces.
- **Raters** are two models from one vendor:
  - Claude Opus 5.5 (primary) reads every batch.
  - Claude Sonnet 5.5 also reads batches 3, 8 and 11 (`random.Random(20261112).sample(range(12), 3)`), for
    agreement on stated / none per case.
  - Both run as separate subagents and never see each other's answers.
- **Labels.** A stale case is "stated" if the primary rater gives at least one verified quote, and "none"
  otherwise. Its gold pieces are the pieces holding a verified quote.
- **Human gate.** Ege labels about 60 items blind: (case, piece) pairs drawn after the arms run, stratified over
  rater-cited pieces, arm top pieces the rater did not cite, and "none" cases with Kev's top piece.
  - If Ege's agreement with the primary rater has kappa < .6, the reading is void.
  - Until Ege's labels are in, every result here is PROVISIONAL.

## Arms (`stale/suggest.py`; each ranks the current pieces)
- KEV: Kev-4B p(yes) for "Does the text state or clearly imply the following: <case title>?" (relocation wrapper).
- QUOTE: bge-small cosine between the old quote (HTML removed) and the best quote-length window of each piece.
- QUOTE_BM25: BM25 with the old quote as the query.
- HUNK: the new side of the edit that removed the quote (aligned passage, `stale/triage.py`), located in the current
  text. It abstains when the edit left no similar passage (61 of 141), when no passage was aligned (2), or when the
  passage is no longer in the current text.
- BM25 and BGE: the case title, as in the relocation test.

## Measures
1. **The "not stated any more" question (pre-registered reading).**
   - AUROC of Kev's highest p(yes) over the document, stated vs none, over the 141 points.
   - Interval: 95% cluster bootstrap over documents (2,000 draws, seed 20261112).
   - Reported beside it:
     - QUOTE's highest window cosine (AUROC);
     - HUNK's abstention used as a "none" rule (precision and recall);
     - Kev's flag rule: flag when the highest p(yes) < T = 0.3578. T is the 5th percentile of the 200 survivors'
       highest p(yes), computed with `statistics.quantiles(n=20, method='inclusive')[0]`.
   - Ceiling known now: for 37 of the 200 survivors (18.5%), the best non-gold piece is below T. If a case was
     stated in one place and that place were deleted, the flag would fire about one time in five.
2. **Suggestions (descriptive).**
   - Precision@1 per arm on stated points: the arm's top piece is a gold piece. Also found@3. An abstaining arm
     counts as a miss, and is also reported on the points where it answers.
   - Primary summary: the mean over documents of per-document precision@1 on the gone stratum. Also reported:
     pooled over points, leave-one-document-out range, and the partly stratum.
   - Paired KEV-minus-arm intervals use the cluster bootstrap above.
   - Minimum detectable difference: with about 50 stated gone points in about 20 documents, a paired difference
     under about .25 is not expected to be distinguishable. The comparison is therefore descriptive.
3. **Rater quality.**
   - Control recall per rater.
   - Verified-quote share.
   - Agreement between the two models on stated / none (Cohen's kappa) on the shared batches.

## Reading (fixed now)
- **The "may no longer be stated" label ships only if all five hold:**
  1. Kev's AUROC 95% interval has a lower bound of at least .70.
  2. The flag rule flags at least 8 points.
  3. At least 75% of flagged points are "none".
  4. Primary-rater control recall is at least .85.
  5. The human gate passes.

  Otherwise the page keeps making no verdict, and the README says the decision model has not been shown to tell.
- **The page's suggestions** show Kev's top 3, and beside them QUOTE's top piece and the HUNK passage when it does not
  abstain. The page leads with another arm instead of Kev only if that arm's per-document precision@1 minus Kev's has
  a 95% interval entirely above 0 on the gone stratum.

## Known limits
- The raters are LLMs from one vendor and are not curators. LLM judges are reported to favour LLM-based rankers.
  The human gate is the check on that.
- A full read can miss passages, which is why control recall is reported. "None" means the primary rater found none.
- The old quote is hidden from raters. A curator would have it. No second pass with the quote is run, to save cost.
- One model and quantization, one piece size, one archive HEAD.

## My prediction (before any arm except BM25 has been run on these points)
- Primary rater: 60% of gone cases stated, 85% of partly cases stated; control recall .90.
- Precision@1 on stated gone points: KEV .50, HUNK .55 where it answers, QUOTE .45, QUOTE_BM25 .40, BM25 .30,
  BGE .25.
- AUROC: Kev's highest p(yes) about .65, QUOTE's highest cosine about .70.
- P(the label ships) = 10%.
