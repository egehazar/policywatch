# Relocation follow-up: result (2026-11-14)

Pre-registrations:
- `stale/PREREG_relocate2.md` (part A: the 200 points of the relocation test, on 20 platforms, and part C);
- `stale/PREREG_relocate2b.md` (part B: 202 held-out points from 41 other services);
- `stale/PREREG_relocate2_addendum1.md` (run order and the Qwen server's memory, written before any evaluation).

All three are hashed in `stale/PREREG_relocate2.sha256` and `stale/PREREG_relocate2b.sha256`. The result hashes were
appended by the run itself at 2026-11-14T20:34:26Z (part A) and 20:34:27Z (part B). The non-QWEN readings were looked at early, as
addendum 1 allows; the official evaluations gave the same numbers.

## Summary
| Question | Part A (200 points, 20 platforms) | Part B (202 points, 41 other services) | What the README may say |
|---|---|---|---|
| Does the win over retrieval replicate beyond the 20 platforms? | (the original test: Kev .620, BM25 .360, bge .295) | **REPLICATED**: Kev .752, BM25 .408, bge .431 | yes |
| Kev vs its base family (Qwen3.5-4B, the same question, one piece at a time) | NO DIFFERENCE SHOWN: .620 vs .600, +.020 [-.035, +.077] | NO DIFFERENCE SHOWN: .752 vs .738, +.015 [-.026, +.055] | the win was **not shown to come from decision-model training** |
| Kev vs a cross-encoder reranker (bge-reranker-v2-m3) | NO DIFFERENCE SHOWN: .620 vs .550, +.070 [-.011, +.158] | DECISION MODEL BETTER: .752 vs .653, +.099 [+.035, +.163] | neither (the parts disagree). Part A's rule applies: the README gives both arms' costs and says the decision model was not shown to beat a reranker |
| Short question layout (lower bound at least -.05) | fails by .003: -.025 [-.053, +.005] | holds: .000 [-.036, +.040] | the r20 wrapper stays: the pre-registration has no rule for this disagreement, and I kept the wrapper that passed on the 20 platforms the page serves |
| Proposed quote (part C) | **SHIPS**: 83% given the right passage, vs BM25 56% | (not run) | yes |

In plain words: asking a 4B language model "does this passage state the case?" for every passage finds the
curator's passage far more often than word matching or embeddings, and that holds on services the method was not
built on. Kev's base family, asked the same question, did about as well, so the win was not shown to come from Kev's
decision-model training. Nor is it settled that a language model is needed: a cross-encoder reranker, at a fifth to under a
third of Kev's CPU, was within the interval in part A and behind in part B. Against the instruct model, Kev's
advantage was cost: it reads a passage once for all of a document's questions, and used about a third of the instruct
model's CPU per cell in part A and about half in part B.

## Part A: the 200 points of the relocation test
| Arm | hit@1 | hit@3 | hit@5 | MRR |
|---|---|---|---|---|
| CASCADE_RERANK (Kev within the reranker's top 10; secondary) | .630 | .785 | .845 | .725 |
| KEV (Kev-4B, r20 wrapper; hashed scores from the first test) | **.620** | .800 | .860 | .730 |
| QWEN (Qwen3.5-4B instruct, log-odds of yes vs no) | .600 | .835 | .890 | .726 |
| KEV_SHORT (Kev-4B, short layout) | .595 | .810 | .865 | .720 |
| CASCADE_BM25 (Kev within BM25's top 10; secondary) | .590 | .755 | .790 | .684 |
| RERANK (bge-reranker-v2-m3, case title) | .550 | .760 | .805 | .670 |
| QNN (from the first test) | .465 | .675 | .770 | .598 |
| BM25 | .360 | .590 | .671 | .504 |
| BGE (bge-small) | .295 | .600 | .710 | .479 |
| RANDOM (expectation) | .040 | .116 | .182 | |

Paired differences in hit@1, 95% cluster bootstrap over the 29 documents (2,000 draws, seed 20261112):

| Reading | Difference | 95% interval | Result |
|---|---|---|---|
| R1: KEV - QWEN | +.020 | [-.035, +.077] | NO DIFFERENCE SHOWN |
| R2: KEV - RERANK | +.070 | [-.011, +.158] | NO DIFFERENCE SHOWN |
| R3: KEV_SHORT - KEV (bar: lower bound at least -.05) | -.025 | [-.053, +.005] | r20 wrapper kept |
| secondary: CASCADE_RERANK - KEV | +.010 | [-.024, +.040] | |
| secondary: CASCADE_BM25 - KEV | -.030 | [-.069, +.010] | |

**QWEN validity gate: passed.** None of the 8,386 cells lacked "yes" or "no" in the top 20 (the bar was at most 1%),
and the median yes+no mass was .979 (the bar was at least .5). The first token was "no" for 7,571 cells and "yes" for
815.

## Part B: 202 held-out points from 41 services, on ToS;DR's stored text
The points were drawn with a fixed seed from services ToS;DR has reviewed in full, outside the 22 platforms of the
archive. The text is ToS;DR's own stored copy of each document, not Open Terms Archive's. 71 documents, 1,456 pieces,
4,040 cells. The bootstrap resamples the 41 services.

| Arm | hit@1 | hit@3 | hit@5 | MRR |
|---|---|---|---|---|
| CASCADE_RERANK (exploratory; computed by my interim script, not by the official eval) | .757 | .916 | | .843 |
| KEV | **.752** | .926 | .975 | .847 |
| KEV_SHORT | .752 | .941 | .980 | .847 |
| QWEN | .738 | .921 | .965 | .837 |
| RERANK | .653 | .856 | .926 | .773 |
| BGE | .431 | .708 | .797 | .594 |
| BM25 | .408 | .713 | .788 | .579 |
| RANDOM (expectation) | .091 | .268 | .394 | |

| Reading | Difference | 95% interval | Result |
|---|---|---|---|
| B0: KEV - BM25 | +.345 | [+.260, +.430] | REPLICATED (both above 0) |
| B0: KEV - BGE | +.322 | [+.238, +.410] | |
| B1: KEV - QWEN | +.015 | [-.026, +.055] | NO DIFFERENCE SHOWN |
| B2: KEV - RERANK | +.099 | [+.035, +.163] | DECISION MODEL BETTER THAN THE RERANKER |
| B3: KEV_SHORT - KEV | .000 | [-.036, +.040] | holds |
| exploratory (interim script): CASCADE_RERANK - KEV | +.005 | [-.015, +.026] | |

QWEN validity gate: passed (0 of 4,040 cells without yes or no; median mass .981).

## Memorisation (exploratory)
Kev-4B is a LoRA adapter and a head on a frozen Qwen3.5-4B-Base, and its own training data has no ToS;DR text (its
model card lists the datasets). So the base model's pretraining is the only way it could know which passage a curator
quoted. `py -m stale.reloc_fresh` splits the official per-point rows by the point's creation date on ToS;DR.

- **Registered cut (part B only).** Part B pre-registered an exploratory look at the 47 points created on or after
  2025-07-01 (`heldout_result.json`, `created_after_2025_07`). On them: KEV .617, QWEN .681, KEV_SHORT .681, RERANK
  .596, BGE .362, BM25 .298. KEV - BM25 +.319 [+.146, +.500], KEV - BGE +.255 [+.082, +.441], KEV - RERANK +.021
  [-.122, +.160], KEV - QWEN -.064 [-.135, .000].
- **Post-hoc cut, chosen after the results: points created after the base model was published.** Qwen3.5-4B-Base was
  first published on the Hub on 2026-02-27 (its files were last modified on 2026-04-23). A point created on ToS;DR
  after the first date cannot be in pretraining data collected before it.

| Points created on ToS;DR | Part A n | KEV | QWEN | RERANK | BM25 | BGE | Part B n | KEV | QWEN | RERANK | BM25 | BGE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| before 2025-07-01 | 39 | .744 | .769 | .744 | .436 | .308 | 155 | .794 | .755 | .671 | .441 | .452 |
| from 2025-07-01 (part B's registered cut) | 161 | .590 | .559 | .503 | .342 | .292 | 47 | .617 | .681 | .596 | .298 | .362 |
| from 2026-02-28 (after first publication) | 157 | .605 | .561 | .516 | .350 | .299 | 37 | .622 | .676 | .541 | .270 | .351 |
| from 2026-04-24 (after the last modification) | 17 | .647 | .647 | .706 | .412 | .294 | 20 | .650 | .650 | .500 | .200 | .400 |

On the points created from 2026-02-28 (intervals over 21 documents in part A and 8 services in part B; the last row
has too few clusters for intervals):
- **KEV - BM25:** +.255 [+.176, +.323] and +.351 [+.162, +.550].
- **KEV - BGE:** +.306 [+.236, +.374] and +.270 [+.081, +.471].
- **KEV - RERANK:** +.089 [-.006, +.181] and +.081 [-.025, +.194]: not shown in either part.
- **KEV - QWEN:** +.045 [-.010, +.102] and -.054 [-.135, .000]. In part B the upper bound is exactly 0: QWEN is ahead
  on the newer points, at the edge of the interval.

**What this supports.** The lead over word matching and embeddings is about as large on points the base model cannot
have seen, in every cut, which is consistent with no memorisation behind it. It does not prove that: the cut is post
hoc, and creation dates cluster on single days (23 of the 157 part A points on 2026-04-06, 19 on 2026-03-14), which
looks like bulk annotation that may re-use older quotes. Kev's lead over the reranker in part B is not shown on the
newer points (+.081 or +.021, wide intervals), and no subgroup difference was tested.

## Part C: the proposed quote
Given Kev's top piece, every sentence or list item of it (8.8 per piece on average) is asked the point's question, and
the top one is the proposed quote. It matches the curator's quote if at least half of one's word 6-grams are in the
other.

| Rule, on the 124 points where Kev's top piece is gold | share matching |
|---|---|
| KEV | **.831** |
| BM25 (case title over the units) | .563 |
| RANDOM (expectation) | .200 |
| FIRST (first unit) | .194 |

KEV - BM25: +.268 [+.176, +.351]. Kev had no ties at the top. Over all 200 points, end to end, Kev's proposed quote
matches for 51.5%. The median proposed quote is 29 words; the median curator quote is 36.

**Shipping bar** (KEV at least .60 and the KEV - BM25 lower bound above 0): **met**. The curator page shows Kev's
proposed quote for each stale point, highlighted inside its top passage (`stale/propose.py`, built 2026-11-14).

**Changed after the result: navigation units are skipped.** 12 of the 141 quotes first shown on the page were a table
of contents or a row of links. Since 2026-11-14 ~21:30 UTC a unit with at least half of its words inside [link text]
ranks last unless every unit is one. On part C's data this changed 1 of 124 picks and left KEV at .831
(`py -m stale.propose_nav`, no model call). It is a display rule chosen after seeing the page, not a tested arm. The
first picks are kept in `stale/out/propose_kev.v1.jsonl`.

## Cost (seconds per piece-question cell, 6-core CPU, one model at a time unless noted)
| Arm | Part A | Part B |
|---|---|---|
| RERANK | 0.39 | 0.98 |
| KEV_SHORT | 1.45 | 3.05 |
| KEV | 1.94 (first test) | 3.52 |
| QWEN | 9.36 over all documents; 6.26 without the first 4 (addendum 1); 6.02 on documents 11-29 | 6.53 |

- **Why Kev is cheaper than QWEN.** Kev reads a piece once and answers all of the document's questions about it in the
  same request. QWEN gets one prompt per piece and question, and its hybrid recurrent architecture gives llama.cpp no
  prefix to reuse between them. Part A has 6.9 questions per document and part B 2.8, which fits Kev's advantage
  falling from about 3.1x (1.94 vs 6.02) to 1.9x (3.52 vs 6.53). It is not isolated: the reranker, which scores one
  pair at a time, also cost 2.5 times more per cell in part B, so part B's text costs more for every arm.
- Kev's part A figure is from the first test (a different run); the others are from this one.
- QWEN's slow start in part A (addendum 1) was its first document alone, at 92.8 s per cell; documents 2 to 4 ran at
  6.4-6.5. Documents 5 to 10 shared the CPU for 72 minutes with `stale/propose.py` (the curator page's quote step, not
  part C), so 6.02 on documents 11-29 is the cleanest figure.
- The short layout saved 25% of Kev's CPU in part A (0.75x), not the 43% measured on the review-queue test.
- Cost was not part of any reading.

## Prediction against result
| | predicted | result |
|---|---|---|
| A hit@1 QWEN | .50 | .600 |
| A hit@1 RERANK | .55 | .550 |
| A hit@1 KEV_SHORT | .60 | .595 |
| A hit@1 CASCADE_RERANK | .60 | .630 |
| Part C given a piece hit: BM25 / FIRST / RANDOM | .40 / .20 / .15 | .563 / .194 / .200 |
| P(R1 = decision model better than its base family) | 50% | no difference shown |
| P(R2 = decision model better than the reranker) | 30% | no difference shown |
| P(R3 = short layout used) | 70% | not used |
| Part C, KEV given a piece hit | .60 | .831 |
| P(proposed quote ships) | 50%, lowered to 30% after seeing BM25's .563 | ships |
| B hit@1 KEV / KEV_SHORT / QWEN / RERANK / BM25 / BGE | .62 / .60 / .48 / .58 / .45 / .40 | .752 / .752 / .738 / .653 / .408 / .431 |
| P(B0 replicated) | 70% | replicated |
| P(B1 = decision model better than its base family) | 45% | no difference shown |
| P(B2 = decision model better than the reranker) | 25% | decision model better |

I underrated the base family most: QWEN came in 10 points above my prediction in part A and 26 in part B. Part B was
easier than I expected for every model arm.

## What this changes
- **The claim.** The README's relocation claim becomes: Kev-4B beats word matching and embeddings at finding where a
  ToS;DR case is stated, on the 20 platforms and on 41 held-out services. As the pre-registration requires, it also
  says that the win was not shown to come from decision-model training (its base family did about as well), and that
  the decision model was not shown to beat a cross-encoder reranker (within the interval in part A, behind Kev in part
  B), with both arms' costs.
- **Why Kev stays on the page.** Its base family was not shown to do better, at about 2-3 times Kev's CPU per cell
  here, and Kev is the arm whose proposed quote was tested (part C). Nothing here says QWEN would not do as well with
  the quote step. The reranker is 3.6-5 times cheaper than Kev; a reranker-first cascade is the cheaper candidate (below).
- **The r20 wrapper stays** for relocation and suggestions: R3 failed on the 20 platforms the page serves, B3 held on
  the held-out services, and the pre-registration has no rule for the disagreement.
- **A cheaper pipeline.** Kev within the reranker's top 10 lost nothing in either part (+.010 and +.005) at about half
  of Kev's CPU on a 40-piece document. It is secondary here; adopting it needs its own test.

## What this does not show
- Every point here still has its quote, so the costly error cannot occur here: pointing a curator to a passage that
  does not state the case when nothing does. The stale-point test (`stale/RESULT_suggest.md`) covers that, and its
  result is provisional until a human checks 60 blind cards.
- QWEN was asked with one prompt. A better prompt, or all of a document's questions in one prompt, could change both
  its accuracy and its cost.
- The reranker was given the case title alone, as BM25 and bge were. Kev's and QWEN's question wraps the same title in
  a fixed template.
- Two parts, each with an interval half-width of about .06 to .09: differences under about .10 between the strong arms
  are not expected to be distinguishable.
