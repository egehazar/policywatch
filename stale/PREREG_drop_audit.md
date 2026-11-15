# Pre-registration: are the listed drops real platform edits? (a blind audit)

Written 2026-11-15 ~01:15 UTC, before any case card was built or read. Hashed in `stale/PREREG_drop_audit.sha256`
together with the case cards and the answer key, before any rating.

## Why
The curator pages list a point when its approved quote "dropped in an edit by the platform itself": 141 on the 20
platforms (`stale/out/points.jsonl`) and 521 on the contrib collection (`stale/wide/contrib/out/points.jsonl`). That
is string matching between two archived captures. A capture can also change because the archive saved a broken page
(a title only, a login or cookie wall, an error page, another language or region). On contrib, a guard
(`stale/wide.py guard`) sets aside 74 such drops as broken captures; the 20-platform list was built before the guard
and never had it. Nobody has checked either list against the captures by eye.

## Populations and draw
- **P**: the 141 listed drops on the 20 platforms (status gone or partly, drop kind "platform edit").
- **L**: the 521 listed drops on contrib (same rule).
- **G**: the 74 contrib drops the guard set aside as "broken capture".
- Draw: each population's points sorted by point id, `random.Random("20261116-<P|L|G>").sample`: 10 from P, 30 from L,
  10 from G. The 50 cases are shuffled together with `random.Random(20261116)` and numbered C01-C50. The card does
  not show the population, the drop kind, ToS;DR's status or anything the pipeline decided.

## The card (built by `stale/drop_audit.py`, the same code for every case)
- Service, document, the drop's two archive dates (last version holding the quote, first version without it).
- The quote (HTML tags removed).
- The passage of the earlier capture that best matches the quote, and the passage of the later capture most similar
  to it (word-triple overlap), each up to 1,500 characters.
- Both captures' lengths in characters, and the first 600 characters of the later capture.
- Both full captures as files next to the cards, for the rater to open when the card is not enough.

## The rater and the question
An independent Claude subagent (Opus 5.5) that has not seen the pipeline's code or this session's results reads only
`stale/audit_drops/`. For each case it answers one question:

> Between these two captures, did the service change the document's own text so that the quoted wording is no longer
> there? **GENUINE**: yes, the later capture is a real version of the document and the wording was removed or
> rewritten. **CAPTURE**: no, the later capture is not a faithful copy of the document (truncated, a title or menu
> only, a login, cookie or error page, another page, another language or region). **UNSURE**: the card and files do
> not settle it.

The rater is an LLM, not a person. The result is reported as an LLM rater's reading.

## Readings (all reported, none of them gates anything)
- **Precision of the contrib list (L):** GENUINE / (30 - UNSURE), with a Wilson 95% interval. The README's "521
  dropped in a platform edit" gets this number next to it, whatever it is.
- **Precision of the 20-platform list (P):** the same over 10 (small: an interval, not a verdict).
- **The guard's set-asides (G):** the share rated CAPTURE. If 5 or more of G are rated GENUINE, the guard is too
  eager, and that is said.
- If L's precision is below .80, the contrib page gets a line saying how many listed drops the audit found to be
  capture problems, and the guard is revisited as an exploratory change (reported as such, the list re-counted).

## Predictions (mine, before the cards exist)
L: 26 of 30 GENUINE, 1 UNSURE. P: 9 of 10 GENUINE. G: 8 of 10 CAPTURE.
