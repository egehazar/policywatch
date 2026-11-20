# Result: AI-training clause watch, the kill test (r39)

Plan: `PLAN_aiwatch.md`, hashed with its code and the gold incident list on 2026-11-19 at 16:15 UTC, before any
score (`PLAN_aiwatch.sha256`; every hash still matches). Kev-4B scored 5,170 distinct texts from 2026-11-19 16:27
to 2026-11-20 17:18 UTC, pausing overnight while the PC slept. The output hashes were appended to the same file.
`out/result.json` is the result. `py -m aiwatch.backtest result` recomputes it from the committed outputs
(`out/candidates.jsonl`, `out/kev_cache.sqlite`). The hashed code reads the gold list from the author's notes folder.
A byte-identical copy is in `gold/` (same SHA-256 as in `PLAN_aiwatch.sha256`), so point `GOLD` in `backtest.py` at
it.

## Reading: "keyword ties: stopped"
The plan's rule: the keyword rule ties if its recall is at least Kev's and it raises at most twice Kev's alerts. Its
recall is the same as Kev's, and it raises fewer than half as many alerts. "PASS" also fails on two of its three
bars.

| | Kev-4B (p(grant) rises by 0.2 or more) | Keyword rule |
|---|---|---|
| Eligible GRANT incidents flagged | 10 of 14 (71%) | 10 of 14 (71%), **the same 10** |
| Flagged 7 or more days before the first report | 2 (Zoom +127 days, X privacy 2023 +8) | the same 2 |
| Alerting updates, Jan 2023 to Nov 2026 | 392 (8.4 a month) | 172 (3.7 a month) |
| Kev's alerts at the keyword rule's recall | 307 (cut 0.292) | 172 |
| No grant alert on a promise-not-to-train or ban incident | 5 of 5 | 4 of 5 |

PASS bars: Kev recall of at least 70% (met, 71%); at least 3 flagged incidents 7 days ahead (missed, 2); at the
matched point, Kev raising at most half the keyword rule's alerts (missed, 307 against at most 86).

## Against my predictions (written before any score)
- **Eligible GRANT incidents: 4-8, "too thin" 45%.** Wrong: 14. The gold list's agent found more eligible
  incidents than I expected.
- **Kev recall about 75%, keyword about 70%.** Both 71%.
- **A lead of 7 days or more for 2 incidents (Zoom, X's privacy policy).** Right: exactly those two.
- **"PASS" 15%, cut to 3% once the gold list was in.** Not PASS. The failures I named as most likely, the lead bar
  and then keyword ties, both happened.

## Why both arms missed the same four (exploratory, after the result; `py -m aiwatch.incidents`)
- **Meta EU and Meta's UK notice (2024).** The archive tracks both pages in French. No changed passage has English AI
  vocabulary, so neither arm saw any text (ruling 4 kept them in as misses).
- **Google (2023-06-29).** The old policy already said Google may use public information "to help train Google's
  language models"; the new one says "AI models" and names Bard and Cloud AI. Kev's p(grant) went from .90 to .92,
  and the count of keyword sentences did not change. The change widened a right that was already there, and both
  arms only look for a new one.
- **Atlassian (2026-04-17).** The training sentence had been in the policy since 2025-09-06. Both arms alerted on
  that earlier change, seven months before the press (reported as information only, ruling 2). On the reported
  change Kev's p(grant) stayed at .95.

So the four misses come from the gold, not from either arm misreading a sentence: two pages neither arm could read,
and two reported events whose training text was not new on that day.

The one direction difference: on X's Developer Terms (2025-06-04), a ban on developers training models on X data,
the keyword rule raised a grant alert. Kev's p(grant) rose by 0.198, just under the cut, and its ban score rose
most.

## What it means
- **On the incidents the press reported, a 4B model reading meaning adds nothing over a careful keyword rule.** Same
  10 incidents, same leads, 2.3 times the alerts.
- **The "ahead of the press" story is thin.** In this archive the clause is usually recorded the same day as the
  press or later, because companies announce and then publish. Zoom is the one large lead.
- **Per the plan: stop.** No replay page or daily monitor is built on Kev.

## What this cannot show
- **Whether Kev's extra alerts are real.** The kill test counts alerts; no one judged them. Kev raised 262 alerts the
  keyword rule did not, and missed 42 of its alerts. The ledger's recall sample found the keyword rule misses about
  half of all grants (`RESULT_ledger.md`), so some of Kev's extra alerts may be grants. Its phase 2, which rates
  every Kev-only alert with the same two AI raters, answers this. That is an exploratory follow-up, not this test.
- The plan's other limits stand: the topic was chosen in hindsight, and the archive covers mostly consumer services.
