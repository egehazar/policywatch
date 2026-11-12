# Relocation test: result (2026-11-12)

Pre-registration: `stale/PREREG_relocate.md` (hashes in `stale/PREREG_relocate.sha256`; the N rule was fixed at
14:39:07Z, before any arm scored a piece; the result hashes were appended at 19:07:41Z by the run itself).

## Reading: DECISION MODEL BETTER
Both pre-registered intervals are above 0. Kev-4B puts a curator-quoted passage first for 62% of the 200 points,
against 36% for BM25 and 30% for bge-small.

| Arm | hit@1 | hit@3 | hit@5 | MRR |
|---|---|---|---|---|
| KEV (Kev-4B p(yes) for the case question) | **.620** | .800 | .860 | .730 |
| QNN (bge nearest neighbour to other companies' quotes for the case; secondary) | .465 | .675 | .770 | .598 |
| BM25 (case title words) | .360 | .590 | .671 | .504 |
| BGE (bge-small, case title) | .295 | .600 | .710 | .479 |
| RANDOM (expectation) | .040 | .116 | .182 | |

Paired difference in hit@1, 95% cluster bootstrap over the 29 documents (2,000 draws, seed 20261112):

| | point | 95% interval |
|---|---|---|
| KEV - BGE (reading) | +.325 | [+.262, +.392] |
| KEV - BM25 (reading) | +.260 | [+.184, +.320] |
| KEV - QNN (secondary) | +.155 | [+.053, +.256] |

Secondary measures from addendum 1. Hit@1 minus chance: KEV .58, QNN .425, BM25 .32, BGE .255. Hit@1 averaged within
each of the 111 cases and then across cases: KEV .614, QNN .496, BM25 .376, BGE .336. QNN fell back to the title for
8 points.

**Prediction (hashed before scoring).** Hit@1 about KEV .45, BGE .35, BM25 .30, with P(DECISION MODEL BETTER) = 50%.
Kev did better than predicted and bge worse.

**Cost.**
- Kev took 16,013 s for 8,270 piece-question cells, about 1.9 s per cell on the 6-core CPU (116 more were cache hits).
- That is about 80 s per point for a 40-piece document.
- BM25 and bge take seconds for the whole set.
- Cost was not part of the reading.

## Checks after the result (exploratory, not pre-registered)
`python stale/reloc_checks.py` looks for artifacts that could produce the gap.

**Not a few documents.** Kev's hit@1 beats the baseline's within most documents:

| Kev vs | Kev higher | equal | Kev lower |
|---|---|---|---|
| bge | 24 of 29 | 4 | 1 |
| BM25 | 18 | 8 | 3 |
| QNN | 19 | 5 | 5 |

**Not position, ties, length or one hub passage.**
- Position: Kev's top piece sits at a mean relative position of .47, and the gold pieces at .43. A first-piece baseline hits 1.5%.
- Ties: one point has a two-way tie at the top.
- Length: Kev's top pieces average 1,309 characters, against a document mean of 1,258.
- Hub: the piece Kev ranks first most often within a document is the top piece for 23% of that document's points.

**Probably not memorisation of ToS;DR's pairings.** Kev keeps its lead where its pretraining could not have seen the pairing:

| Subset | n | KEV | QNN | BM25 | BGE |
|---|---|---|---|---|---|
| Point created on ToS;DR on/after 2025-07-01 | 161 | .590 | .460 | .342 | .292 |
| Quote text first in the archive on/after 2025-07-01 | 22 | .682 | .455 | .318 | .409 |

Kev's training cutoff is not published, so this lowers the concern without removing it.

**Document size.**

| Pieces in the document | n | KEV | QNN | BM25 | BGE | chance |
|---|---|---|---|---|---|---|
| under 30 | 75 | .64 | .43 | .41 | .29 | .058 |
| 30-59 | 97 | .63 | .50 | .35 | .31 | .033 |
| 60 or more | 28 | .54 | .46 | .25 | .25 | .015 |

## What this does and does not show
**It shows:** given only a ToS;DR case title, the decision model finds the passage a curator quoted for it in the
platform's current text far more often than lexical or embedding retrieval. That is the step a curator does by hand
after "approved-not-found". The gold here is the curators' own quotes, not model raters.

**It does not show:**
- **Survivors only.** Every point here still has its quote, so the costly errors cannot occur: re-anchoring a
  point to a passage that does not state the case, or keeping a point that no longer holds. A "no passage states
  this any more" label needs its own test with negatives, pre-registered before it is scored.
- **No incumbent comparison.** DocBot, ToS;DR's per-case classifiers, was not compared; no local model was found.
- **Single passage per case.** A case is often stated in more than one place, so every hit rate is a lower bound.
- **One configuration.** One model and quantization, one piece size, current versions only.

## Consequence for the system
Following the plan fixed before the result (Fable 5.2 r26):
- The curator page's "the point may now be stated here" suggestions for the 141 stale points move from BM25 to Kev
  (`py -m stale.suggest <pga-versions> kev`, about 5 CPU hours, queued after the short-layout test).
- The page still offers no verdict.
- Before any "case no longer stated" label ships, a separate test with negatives is pre-registered.

## Independent review (subagent with file access, 11-12, after the result)
- **Recomputed, nothing wrong.** It recomputed hit@1 and MRR for all 200 points and four arms with its own formula
  and found no differences.
- **Gold matches.** It recomputed the gold pieces from the quotes with exact 6-gram sets: 0 differ.
- **Inputs match.** Every hashed file matches. Pieces are identical across arms, and questions line up with arm rows.
- **BM25 matches.** It recomputed BM25 for two documents: no difference.
- **Bootstrap is stable.** With a different seed the intervals move by at most .01.
- **Cosmetic bug.** `reloc_result.json` says `"N": 25`: `relocate.py` reuses `n` for a document's piece count. The
  sample is 200 (`points: 200`), and no metric is affected. The hashed files are left as they are.
- **Two small asymmetries, both concerning QNN, neither favouring Kev.** In 12 of 200 points another company's quote
  for the same case is boilerplate that overlaps this point's gold, which helps QNN. QNN's comparison quotes are
  reduced to bare lowercase words, which may hurt it a little.
