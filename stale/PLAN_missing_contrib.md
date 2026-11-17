# Plan: missing points beyond the 20 platforms, and the printed p(yes) as a label

Written 2026-11-17, before any document is drawn. Code: `stale/missing_contrib.py`. Hashes of this plan and the code go
in `stale/PLAN_missing_contrib.sha256` before the draw; the drawn document list's hash is appended before any model
scores it, and the cards' hashes before any rater starts.

## Why
The private curator page suggests missing points for all 40 privacy policies and terms of the 20 platforms, and every
suggestion on it has a blind AI rating. Two questions are open:
1. Does the method carry beyond the 20 platforms? ToS;DR covers hundreds of other services, most with fewer points.
   Open Terms Archive's contrib collection holds 408 English privacy policies and terms of services mapped to ToS;DR.
2. Does the p(yes) the page prints tell a curator which suggestions to trust? After the last rating was scored I
   looked (exploratory, bands chosen after the result): 149 of the 179 suggestions printed at 0.90 or more were rated
   YES, against 41 of 101 below (`stale/wide_rate_explore.py`). This run tests that on new documents, as a label
   decided in advance.

## Documents (the draw)
- Population: every `Privacy Policy.md` and `Terms of Service.md` at the contrib clone's HEAD (recorded in the output)
  whose service is mapped to ToS;DR in `stale/wide/contrib/map.json` (the 20 platforms are not mapped there), with 1 to
  80 passages as part D cuts them, in English by `stale.missing_page.english`: 377 documents on 2026-11-17. The 31
  English documents over 80 passages (8%) are left out to bound the reranker's time; the result applies to the rest.
- Draw (seed 20261118): the population's services in a seeded random order; from each, one document of a type still
  short of 10 (a seeded coin flip when both are open and the service has both), until there are 10 privacy policies
  and 10 terms. One document per service.
- Candidate cases per document, as on the page: the cases ToS;DR approved at least 10 times on documents of that type
  (`stale.missing.all_points`, all collections), minus every case with an approved point on the service (the
  2026-11-14 snapshot in `stale/wide/contrib/data/`, any quote length). Known positives (approved points whose quote
  is still in this document's current text, `stale/wide/contrib/out/points.jsonl`) are scored too but never
  suggested.

## Arms (the page's own method, unchanged)
- PAGE: the cascade. bge-reranker-v2-m3 scores every passage-case cell; Kev-4B (Q8, `/v1/systemone`) reads only the
  reranker's top 3 passages per case; a case's score is its best shortlisted p(yes), with that passage. Top 10.
- RERANK: the reranker on every passage, its best passage. Top 10.

## Cards and raters
- A card is (document, case, passage); one picked by both arms is rated once and counts for both. Plus 20 random
  controls (a random candidate case of a random drawn document, with a random passage of it).
- Shuffled (seed 20261119), cut in two halves: `stale/audit_contrib_a/`, `stale/audit_contrib_b/`, each with the
  instructions every earlier rating used (`stale/audit_states/README.md`, unchanged) and an empty `verdicts.json`.
- One fresh Claude Opus subagent per folder. It reads only its folder, sees case and passage only (no arm, no score, no
  document name), answers YES / PARTLY / NO with a short reason, and keeps any helper file in its own scratch
  subfolder, named in its prompt. (Last time the two raters shared one scratch folder and one opened the other's
  finished verdicts file; `stale/RESULT_wide_rate.md`.) Each verdicts file is hashed as soon as its rater finishes.
- GPT (Codex) rates the same cards as a second rater: reported beside the first, never read.

## Readings (fixed now)
- Validity: at most 3 of the 20 random controls rated YES. If more, every reading is NOT VALID.
- Page precision: the YES share of the PAGE cards, Wilson 95% interval. Predicted .60-.80 (in, below or above).
- PAGE against RERANK: PAGE YES share minus RERANK YES share, 95% interval from 2,000 draws resampling the 20 documents
  (seed 20261120). "PAGE better" if above 0, "RERANK better" if below, otherwise "no difference shown". Predicted
  +.05 to +.25; I put P(PAGE better) at 65%.
- The label: among PAGE cards, the YES share of those whose p(yes) prints as 0.90 or more ("high", two decimals, as
  the page shows it) and of the rest. Predicted high .75-.90, rest .30-.55. **Adopted** if the high share's Wilson 95%
  lower bound is at least .70 and high minus rest has a 95% interval above 0 (2,000 draws resampling documents, seed
  20261121; draws where either group is empty are dropped and counted). I put P(adopted) at 70%.

## What the page does with the result (fixed now)
- The 20 documents join the curator page as a second part, "Other services", each suggestion with its verdict, and
  the part states its measured precision, whatever it is.
- Label adopted: every suggestion on the page printed at 0.90 or more gets a mark that says how often such suggestions
  were rated as stating the case in this test. Not adopted: no mark, and the page's exploratory sentence about p(yes)
  is replaced by this result.

## Descriptive only (nothing is read from these)
Both arms by type, by rank (1-5 against 6-10), by known positives (0-4 against 5 or more: the last rating's exploratory
finding was that the page is weakest where ToS;DR has approved the most), by document and by folder; YES-or-PARTLY
shares; verdict counts; reranker and Kev time per cell.

## What it can and cannot show
- The raters are Claude models (GPT as a second), not people and not ToS;DR's curators.
- It rates the passage an arm picked, not the document: a NO can be a right case with the wrong passage.
- "No point" means no approved point in a snapshot a few days old; ToS;DR's public data does not show pending or
  declined points.
- The label's threshold (0.90) and the page's method come from earlier results on the 20 platforms; this run is the
  first look at both on these documents.
