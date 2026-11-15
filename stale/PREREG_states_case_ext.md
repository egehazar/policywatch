# Pre-registration: states-the-case comparison, extension to 120 points (the final look)

Written 2026-11-15 ~02:12 UTC, after `stale/RESULT_states_case.md` (60 points: KEV - RERANK +.133 [.000, +.258], no
difference shown, at the edge) and before any card of the extension was built. Hashed with the code, cards and key
in `stale/PREREG_states_case_ext.sha256` before rating.

## Why, and the risk it carries
The first 60 points left KEV against the reranker at the edge of the interval. A second look raises the chance of a
false "better" (looking until it shows is a forking path), so this is fixed in advance as the **only** further look:
one extension, then a pooled reading, then this measure is closed whatever it says.

## Points and cards (`stale/states_case.py ext`, seed 20261119)
- 60 new points: 30 from part A and 30 from part B, drawn the same way, excluding the first 60.
- Cards exactly as before (each arm's top passage, one card per distinct (point, passage), 10 RANDOM controls),
  shuffled, case and passage only, in `stale/audit_states2/`.
- A fresh Claude subagent (Opus 5.5) rates them with the same README.

## Readings
- The extension alone: states@1 per arm and the paired differences, as in the first test (reported, not called on
  its own).
- **Pooled, 120 points (final):** KEV - RERANK and KEV - BM25, 95% cluster bootstrap over documents (2,000 draws).
  Called only when the pooled interval excludes 0 **and** the extension's own point estimate has the same sign.
  Otherwise "no difference shown".
- Validity: more than 2 of the extension's 10 RANDOM cards rated YES makes the extension unreliable; then the first
  test's reading stands and nothing is pooled.
- Both raters are LLMs; the pooled reading sits beside the pre-registered hit@1 results, not in place of them.

## Predictions
Extension states@1: KEV .70, RERANK .60, BM25 .42. Pooled KEV - RERANK: +.11, about even odds of "KEV better".
Pooled KEV - BM25: KEV better.
