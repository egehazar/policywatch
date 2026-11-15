# Missing points pilot: which ToS;DR cases does a document state that ToS;DR has no point for? (pre-registered)

Written 2026-11-15 ~11:05 UTC, before any score of this pilot exists. Code: `stale/missing.py`.

## Why
Everything measured so far says Kev-4B's decision-model training adds no accuracy over its base family on
policywatch's tasks; what it adds is cost, and only when one text is asked many questions (Kev reads a passage once
for all its questions; an instruct model pays per question). The curator pages ask 1-7 questions per document, where
that edge is small. Finding *missing* points asks every plausible case of a document: the decision-model-native
workload. This pilot asks whether that job works at all, and which method does it best.

## Documents (fixed rule, applied to `stale/out/reloc_docs.json`, the relocation tests' cut of the 20 platforms)
- Type from the archive file name: privacy (Privacy / Data Policy) or terms (Terms).
- Known positives P_d: the distinct cases of the document's approved points whose quote is present in it (>= 6
  words, at least one gold piece: the relocation tests' rule).
- Eligible: at most 30 pieces. Ranked by |P_d| (then name); taken in that order while the type has fewer than 2
  and the platform is not already taken. This gives Bluesky Privacy Policy, X Privacy Policy, Pinterest Terms of
  Service, YouTube Terms of Service (105 pieces).

## Candidate cases
- C_d: every case with at least 10 approved points on documents of the same type across all points pulled
  (the 20 platforms plus the contrib, genai-contrib and dating collections), plus P_d.
- Excluded E_d: other cases with an approved point on the same platform (on another document, or on this one with a
  quote that is gone, partly gone, short or not found): ambiguous, neither positive nor negative.
- Negatives N_d = C_d minus P_d minus E_d (no approved point for the service; some may in fact be stated: that is
  what the pilot looks for, so every score below is a lower bound for every arm alike).
- Question: `Does the text state or clearly imply the following: <case title>?` (the relocation template).

## Arms (a case's score in a document = its best piece's score)
- KEV: p(yes) from Kev-4B Q8 (port 9995), all candidate questions of the document in one request per piece
  (cached cells reused).
- RERANK: bge-reranker-v2-m3 (the relocation tests' revision and max_length), case title vs piece.
- BM25: case title vs pieces (the relocation tests' parameters).
- The instruct model (Qwen3.5-4B) is not run: at about 6.6 s per piece-question it would take about 15 h for these
  four documents; its cost is the comparison, taken from the clean cost benchmark.

## Measures
1. **Known positives first (primary):** per document, AUROC of P_d against N_d by case score; mean over the four
   documents. KEV - RERANK and KEV - BM25 with a 95% interval from 2,000 draws resampling positives and negatives
   within each document (seed 20261121). Reading per comparison: KEV better / no difference shown / KEV worse.
2. Recall@20: share of P_d in the top 20 of C_d minus E_d; mean over documents (descriptive).
3. **New suggestions:** each arm's top 10 of N_d per document, with that arm's best piece, become blind cards (case
   and passage only; deduplicated over document, case and piece), plus 10 random controls (a random negative case
   with a random piece). Rated YES / PARTLY / NO with the states-the-case instructions (`stale/audit_states/README.md`)
   by a fresh Claude Opus subagent that reads only its folder; GPT (Codex) rates the same cards as a second rater
   if its usage allows (reported, not read). Precision@10 = share of an arm's 40 cards rated YES, with a Wilson 95%
   interval. Valid only if at most 2 of the 10 random controls are rated YES.
4. Cost: Kev's measured seconds per piece in this run (and how many cells came from the cache), beside the
   instruct model's cost for the same cells from the cost benchmark.

## Readings (fixed now)
- **Worth building** if Kev's precision@10 is at least .30 and its Wilson lower bound at least .15 (a curator
  reading 10 suggestions finds about 3 real candidates), and measure 1 reads KEV better than BM25.
- **Not worth building as is** otherwise.
- Which method to build it on: Kev only if measure 1 reads KEV better than RERANK and Kev's precision@10 is at least
  the reranker's; otherwise the cheaper reranker is the default and Kev's role is stated as not shown.
- This is a four-document pilot: whatever it shows is a reason to run a larger pre-registered test, not a result to
  quote as general.

## Predictions
AUROC KEV .85-.92, RERANK .80-.88, BM25 .70-.80; KEV - RERANK about +.03, no difference shown; precision@10 KEV
.30-.50, RERANK .25-.40, BM25 .15-.30. P(worth building) = 55%.

## Schedule
After the clean cost benchmark (the CPU must be idle for it) and before the scanner backfill: KEV, then RERANK; BM25
and the card build need no model.

## Disclosure before hashing
Testing `measures` on stand-in scores used the real BM25 scores, so BM25's measure 1 figure was seen before this
file was hashed: mean AUROC .541 (below the .70-.80 predicted above). The predictions and readings were written
before that and are left as they were. No Kev or reranker score exists yet. Prep's output: Bluesky Privacy Policy
(27 pieces, 41 positives, 22 negatives), X Privacy Policy (30, 38, 24), Pinterest Terms of Service (23, 29, 37),
YouTube Terms of Service (25, 27, 51); 7,029 piece-question cells.
