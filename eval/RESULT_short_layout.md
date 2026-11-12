# Short question layout for Kev: result (2026-11-12)

Pre-registration: `eval/PREREG_short_layout.md`, hashed 14:56:55Z before any short-layout request. The result hashes
were appended by the run at 20:08:34Z (`eval/PREREG_short_layout.sha256`).

## Rule 1: ADOPT
KEV-SHORT drops the two option descriptions ("Yes, this is true of the text." / "No, this is not true of the text.")
so Kev's template shows bare "yes" / "no". Same server, same 70 questions and instructions, same 35 updates, one
request in flight, nothing else on the CPU.

| | KEV (r20 wrapper) | KEV-SHORT |
|---|---|---|
| Changes found within 182 reviews (of 25) | 20 | **21** |
| within 25 / 50 / 100 | 12 / 14 / 16 | 12 / 14 / 18 |
| Ambiguous counted as changes, within 182 (of 56) | 24 | 26 |
| CPU seconds per update (both sides) | 179.8 | **102.8** (0.57x) |
| Input tokens per state (server count) | 31,617 | 30,147 |

- **Adopt rule met.** The rule required recall@182 of at least 19 and CPU no more than 0.7x.
- **Rankings agree.** The two layouts' |dp| rankings correlate at Spearman .82.
- **The token count is not the cost.** The server's count fell 5% while time fell 43%, so that count does not measure
  the per-question work.

**Prediction (hashed).** About 95 s per update, recall 18-21, P(adopt) 55%.

## Rule 2: the bench reading, applied to KEV-SHORT (a second test, designed after the first result)
- **Against LLM-DIFF, the pre-registered comparator: NO CLEAR WINNER.** KEV-SHORT finds 19 more changes, but its CPU
  is 2.09x LLM-DIFF's 49.1 s. The rule allows 2x, so it misses by 4.6 s per update. LLM-DIFF was degenerate: it
  answered "none" on 32 of 35 updates.
- **Against LLM-QA (Qwen3.5-4B answering every question yes/no): not at least as good on both.** KEV-SHORT finds 21
  changes to LLM-QA's 12, but uses 102.8 s of CPU to its 81.7 s.

## What changes
- **policywatch adopts the short layout** for new scans as a new wrapper id, so cached scores of the two layouts
  never mix.
- **Two in-flight runs keep the r20 wrapper they were measured or registered with:**
  - the stale-point Kev arm of `stale/PREREG_suggest.md`, which names the relocation test's configuration;
  - the memo check and backfill queued in `run_stale.sh`.
  The switch happens after that chain.
- **The decision model is now 1.26x Qwen's CPU** on this bench (102.8 s vs 81.7 s), not 2.2x, and finds 21 changes
  to Qwen's 12.
