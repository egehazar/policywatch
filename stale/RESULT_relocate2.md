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
| Kev vs a cross-encoder reranker (bge-reranker-v2-m3) | NO DIFFERENCE SHOWN: .620 vs .550, +.070 [-.011, +.158] | DECISION MODEL BETTER: .752 vs .653, +.099 [+.035, +.163] | neither (the parts disagree) |
| Short question layout (lower bound at least -.05) | fails by .003: -.025 [-.053, +.005] | holds: .000 [-.036, +.040] | the r20 wrapper stays |
| Proposed quote (part C) | **SHIPS**: 83% given the right passage, vs BM25 56% | (not run) | yes |

In plain words: asking a 4B language model "does this passage state the case?" for every passage finds the
curator's passage far more often than word matching or embeddings, and that holds on services the method was not
built on. Kev's decision-model training is not what wins: its own base family, asked the same question, does about as
well. What Kev adds here is cost. It reads a passage once for all of a document's questions, and was 3.2 times
cheaper per cell than the instruct model in part A and 1.9 times in part B.

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

## Memorisation (exploratory, not pre-registered)
Kev-4B is a LoRA adapter and a head on a frozen Qwen3.5-4B-Base, and its own training data has no ToS;DR text (its
model card lists the datasets). The only way it could know which passage a curator quoted is the base model's
pretraining. Qwen3.5-4B-Base was first published on 2026-02-27, so a point created on ToS;DR after that date cannot be
in it. `py -m stale.reloc_fresh` splits the official per-point rows by the point's creation date.

| Points created on ToS;DR | Part A n | KEV | QWEN | RERANK | BM25 | BGE | Part B n | KEV | QWEN | RERANK | BM25 | BGE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| before 2025-07-01 | 39 | .744 | .769 | .744 | .436 | .308 | 155 | .794 | .755 | .671 | .441 | .452 |
| from 2026-02-28 (after the base model was published) | 157 | .605 | .561 | .516 | .350 | .299 | 37 | .622 | .676 | .541 | .270 | .351 |

On the points created after the base model was published:
- **KEV - BM25:** +.255 [+.176, +.323] in part A (21 documents) and +.351 [+.162, +.550] in part B (8 services).
- **KEV - BGE:** +.306 [+.236, +.374] and +.270 [+.081, +.471].
- **KEV - RERANK:** +.089 [-.006, +.181] and +.081 [-.025, +.194]. No difference is shown in either part.
- **KEV - QWEN:** +.045 [-.010, +.102] and -.054 [-.135, .000]. No difference is shown in either part.

So the win over retrieval is not memorisation: it holds, about as large, on points the base model cannot have seen.
Part B's win over the reranker comes from the older points (+.123 [+.058, +.192] before 2025-07-01). That fits
memorisation by the shared base as well as it fits older points being easier for language models, and this check
cannot tell the two apart.

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

## Cost (seconds per piece-question cell, 6-core CPU, one model at a time unless noted)
| Arm | Part A | Part B |
|---|---|---|
| RERANK | 0.39 | 0.98 |
| KEV_SHORT | 1.45 | 3.05 |
| KEV | 1.94 (first test) | 3.52 |
| QWEN | 9.36 over all documents; 6.26 without the first 4 | 6.53 |

- **Why Kev is cheaper than QWEN.** Kev reads a piece once and answers all of the document's questions about it in the
  same request. QWEN gets one prompt per piece and question, and its hybrid recurrent architecture gives llama.cpp no
  prefix to reuse between them. Part A has 6.9 questions per document and part B 2.8, which fits Kev's advantage
  falling from 3.2x (1.94 vs 6.26) to 1.9x (3.52 vs 6.53).
- QWEN's first 4 documents in part A ran under memory pressure (addendum 1) at 21.8 s per cell. Documents 5 to 10 also
  shared the CPU with the proposed-quote step for 72 minutes, so 6.26 is an upper bound on its unhindered cost.
- The short layout saved 25% of Kev's CPU in part A (0.75x), not the 43% measured on the review-queue test.
- Cost was not part of any reading.

## Prediction against result
| | predicted | result |
|---|---|---|
| A hit@1 QWEN | .50 | .600 |
| A hit@1 RERANK | .55 | .550 |
| A hit@1 KEV_SHORT | .60 | .595 |
| A hit@1 CASCADE_RERANK | .60 | .630 |
| P(R1 = decision model better than its base family) | 50% | no difference shown |
| P(R2 = decision model better than the reranker) | 30% | no difference shown |
| P(R3 = short layout used) | 70% | not used |
| Part C, KEV given a piece hit | .60 | .831 |
| P(proposed quote ships) | 50%, lowered to 30% after seeing BM25's .563 | ships |
| B hit@1 KEV / QWEN / RERANK / BM25 / BGE | .62 / .48 / .58 / .45 / .40 | .752 / .738 / .653 / .408 / .431 |
| P(B0 replicated) | 70% | replicated |
| P(B1 = decision model better than its base family) | 45% | no difference shown |
| P(B2 = decision model better than the reranker) | 25% | decision model better |

I underrated the base family most: QWEN came in 10 points above my prediction in part A and 26 in part B.

## What this changes
- **The claim.** The README's relocation claim becomes: an LLM asked a yes/no question per passage beats retrieval at
  finding where a ToS;DR case is stated, on the 20 platforms and on 41 held-out services. It also says, as the
  pre-registration requires, that the win was not shown to come from decision-model training, and that a cross-encoder
  reranker was within the interval in part A and behind in part B.
- **Why Kev stays on the page.** It matches its base family's accuracy at 1.9-3.2 times less CPU per cell here, and it
  is the arm whose proposed quote was tested (part C). Nothing here says QWEN would not do as well with the quote step.
- **The r20 wrapper stays** for relocation and suggestions (R3).
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
