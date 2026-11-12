# Pre-registration: does the relocation win survive a strong reranker and Kev's own base family, and can Kev propose the quote?

Written 2026-11-12, after the relocation result (`stale/RESULT_relocate.md`: Kev-4B hit@1 .62, BM25 .36, bge-small
.295, all intervals above 0). Revised once, before hashing, after an independent review (a subagent with file access;
its six fixes are applied below). No new arm has been run on the 200 points except the format checks listed under
"Seen before hashing".

## Why
The relocation test compared Kev-4B with a 33M-parameter embedding model and BM25. Two objections follow:
1. **Any cross-encoder might do this.** A reranker reads the query and the passage together, as Kev does. If a
   standard open reranker matches Kev, the win is "cross-encoders beat bi-encoders", not a decision-model result.
2. **Any 4B instruct LLM might do this.** If Qwen3.5-4B, from the same model family as Kev and asked the same
   question, matches Kev, the decision-model training is not what wins.

A curator also needs a quote to paste, not a 1,500-character piece. Part C measures that step.

## Population and gold: unchanged
- The first 200 points of the fixed order in `stale/out/reloc_docs.json` (hashed in `stale/PREREG_relocate.sha256`).
- 29 documents, 1,149 pieces of at most 1,500 characters at paragraph boundaries, 200 questions, 8,386
  piece-question cells.
- Gold: the pieces holding at least .3 of the curator's quote's word 6-grams (1-3 pieces per point).
- KEV, BM25, BGE and QNN keep their hashed scores (`stale/out/reloc_kev.json`, `reloc_base.json`) and are not re-run.

## New arms (`stale/relocate2.py`)
- **QWEN.** Qwen3.5-4B, instruct, Q8_0 (the GGUF already used in `bench/`), on the same llama.cpp build with
  `--jinja`, 6 threads.
  - One zero-shot prompt, thinking off, temperature 0, one output token:
    `TEXT:\n<piece>\n\nQuestion: <the relocation question>\nAnswer yes or no.`
  - The relocation question is `Does the text state or clearly imply the following: <case title>?`.
  - Score: log P(yes) - log P(no) over the first answer token's top-20 logprobs, matching stripped, lower-cased
    tokens. A side absent from the top 20 gets the 20th logprob, which is an upper bound on its probability.
  - Each cell's yes+no mass and top token are stored.
  - It is one prompt, not a prompt search, so a better prompt could do better. That limits R1.
- **RERANK.** The bge-reranker-v2-m3 cross-encoder (BAAI, Apache-2.0, revision 953dc6f), via sentence-transformers
  6.1.0 on CPU.
  - Score: the raw logit for (case title, piece), with max_length 1,024.
  - The longest pair is 599 tokens, so nothing is cut. At 512, 52 pairs would have been cut.
  - The title is used as the query, as in the BGE and BM25 arms.
- **KEV_SHORT.** Kev-4B with the short question layout adopted in `eval/RESULT_short_layout.md`: the same
  instructions with no option descriptions. All of a document's questions go in one request per piece, as for KEV.

## Measures
- hit@1, @3 and @5 and MRR per arm, with ties broken in expectation (`relocate.hit`).
- Paired hit@1 differences, each with a 95% cluster bootstrap over the 29 documents: 2,000 draws from a fresh
  `random.Random(20261112)` per comparison. Readings use the unrounded bounds.
- Only hit@1 can change a reading. MRR and hit@3/5 are reported and never change one.
- Cost: seconds per piece-question cell, with one model process at a time on the 6-core CPU. KEV's 1.94 s per cell
  is from the first test (16,013 s for the 8,270 cells it asked).

## Readings (fixed now)
- **QWEN validity gate.** QWEN is valid only if both hold:
  - at most 1% of cells have neither "yes" nor "no" in the top 20;
  - the median yes+no mass is at least .5.

  Otherwise R1 is INVALID (a broken prompt or template), not a Kev win.
- **R1, base family.** If the KEV - QWEN interval is entirely above 0: DECISION MODEL BETTER THAN ITS BASE FAMILY
  (with this prompt). Entirely below 0: BASE LLM BETTER. Otherwise: NO DIFFERENCE SHOWN.
- **R2, reranker.** The same rule for KEV - RERANK: DECISION MODEL BETTER THAN THE RERANKER, RERANKER BETTER, or NO
  DIFFERENCE SHOWN.
- **R3, short layout.** If the lower bound of KEV_SHORT - KEV is at least -.05, the stale suggestions use KEV_SHORT
  from now on, under a new wrapper id. Otherwise the r20 wrapper stays.
  - This accepts losing up to 5 points of hit@1 for 0.57x the CPU.
  - The arms are paired and correlated, so the interval is narrow. A layout whose whole interval lies a little below
    0 can still pass, and that trade is intended.
- **Consequences, fixed now.**
  - If R2 is RERANKER BETTER, the curator page leads with the reranker, and the README says the decision model lost
    to it.
  - If R2 is NO DIFFERENCE SHOWN, the README reports both arms with their costs. It says the decision model was not
    shown to beat a reranker.
  - If R1 is not DECISION MODEL BETTER, the README says the win was not shown to come from decision-model training.
  - The README's results table gets one row per reading, whatever it is.
- **Failures.** If an arm fails part-way, it is re-run unchanged and resumes per document. Its prompt, model, scoring
  or configuration is never edited after hashing. A code fix that leaves the arm's definition unchanged is logged in
  the result.
- **Power.** The first test's intervals had a half-width of about .065. Differences under about .10 are not expected
  to be distinguishable.

## Secondary, no reading and no consequence
- **CASCADE_RERANK and CASCADE_BM25.**
  - What it is: Kev's scores, restricted to that arm's top 10 pieces (every piece tied with the 10th stays in); other
    pieces rank last.
  - It is computed from scores on disk and reported with its interval against KEV.
  - It shows what a cheaper pipeline would lose. Adopting a cascade would need its own test.

## Part C: the proposed quote (descriptive, with a shipping bar)
- **Units.** Kev's top piece for each point (the earliest piece on ties) is cut into units: lines, then sentences.
  A unit under 5 words joins the next one.
- **Scoring.** Kev with the r20 wrapper, as in KEV, is asked the point's question of every unit. The top unit is the
  proposed quote. Ties at the top are scored in expectation: the mean match over the tied units. The same rule
  applies to BM25.
- **Match.** A unit matches the curator's quote if either holds:
  - at least .5 of the quote's word 6-grams are in the unit;
  - at least .5 of the unit's word 6-grams are in the quote.

  Texts under 6 words count only if found whole.
- **Check without a model.** All 200 curator quotes match some unit of one of their gold pieces under this rule.
- **Reported.**
  - On the 124 points where Kev's top piece is gold: the share whose proposed unit matches, for four rules:
    - KEV;
    - BM25 (the case title over the piece's units);
    - FIRST (the first unit);
    - RANDOM (in expectation).
  - The count of Kev ties at the top.
  - The end-to-end share over all 200 points.
  - The KEV - BM25 interval, using the bootstrap above.
- **Shipping bar.** The page highlights Kev's proposed quote only if both hold:
  - KEV's share, given a piece hit, is at least .60;
  - the KEV - BM25 lower bound is above 0.

  Otherwise it shows the piece alone.
- **Wrapper.** If the quote ships, the quote step keeps the r20 wrapper it was tested with, whatever R3 says.
- **Cost.** 172 distinct top pieces and 1,766 unit-question cells.

## Order of runs (`run_reloc2.sh`)
1. The stale-point chain (`run_stale.sh`) is stopped after Kev's stale arm and the page rebuild.
2. Then RERANK, QWEN (its own server on port 9996, Kev's server idle), KEV_SHORT, Part C and eval.
3. Then the deferred steps of `run_stale.sh` (triage hints, memo check, backfill), still with the r20 wrapper.

## Seen before hashing
- **Format checks.** These were run beside the stale Kev arm, only to check formats:
  - QWEN: 3 pairs, the first 3 pieces of `Facebook/Trackers Policy.md` for "First-party cookies are used" (gold:
    piece 0). They got p(yes) .161, .543 and .431, and the first tokens were lower-case "no"/"yes".
  - RERANK: the same 3 pairs, ranked 2, 1, 0.
- **Computed from on-disk scores without any new model call (the reviewer's checks and my dry run of the eval):**
  - Part C baselines on the 124 points, with ties in expectation: BM25 .563, FIRST .194, RANDOM .20. My prediction
    below (BM25 .40) was written before I saw this.
  - CASCADE_BM25 hit@1: .59, against KEV's .62, a difference of -.03 [-.069, +.010]. It is secondary and has no
    reading.
- No other output of any new arm has been seen.

## My prediction (written before any of the above was seen)
- hit@1: QWEN .50, RERANK .55, KEV_SHORT .60, CASCADE_RERANK .60.
- P(R1 = DECISION MODEL BETTER THAN ITS BASE FAMILY) = 50%.
- P(R2 = DECISION MODEL BETTER THAN THE RERANKER) = 30%.
- P(R3 = KEV_SHORT used) = 70%.
- Part C, given a piece hit: KEV .60, BM25 .40, FIRST .20, RANDOM .15. P(the proposed quote ships) = 50%.
  - After seeing BM25's .563, I lower P(ships) to 30%: Kev needs a share above about .65 to clear BM25's interval.
