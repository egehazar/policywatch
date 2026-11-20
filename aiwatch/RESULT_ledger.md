# Result: the AI-training clause ledger (r40, exploratory)

Plan: `PLAN_ledger.md` (hashed with `ledger.py` and `recall.py`; addenda 1-3). Started 2026-11-19 while the kill test
(`PLAN_aiwatch.md`) was still scoring. It covers the keyword rule's alerts (phase 1), a recall sample of what the
rule did not flag, and Kev's alerts (phase 2, rated 2026-11-20 after the kill test ended).

**In short.** Over every AI-vocabulary change from 2023 to November 2026, Kev-4B found 135 grants and the keyword rule
92. Kev's alerts were right less often (34% against 54%). On the 14 grants the press reported, the two tied
(`RESULT_aiwatch.md`). So the model's gain is in the changes nobody reported, mostly worded "develop and improve"
rather than "train", and it costs 2.3 times the reading.

## What was measured
- **Changes:** every recorded change (2023-01 to 2026-11, four Open Terms Archive collections, 472 services) whose
  changed passages mention AI vocabulary: 1,306 distinct updates.
- **Detectors:** a keyword rule (training word + AI word in one sentence, no negation, no ban on users) and Kev-4B
  (p(grant) rising by at least 0.2).
- **Labels:** two AI raters from different companies (Claude subagents, GPT-6), blind to service, date, detector and
  score. Each change is NEW / WIDER / SAME / NO / UNCLEAR for "does the new text newly let the company train AI on
  users' content or personal data?". "Verified" = both say NEW or WIDER.
- **No person rated anything.** Ege delegated the row check to two more AI reviewers (addendum 3).

## Phase 1: the keyword rule's 172 alerts
| | |
|---|---|
| Alerts (distinct updates) | 172 |
| Verified grants (both raters) | 92, on 49 services |
| Agreement, grant vs not | kappa .894 |
| Keyword precision | .535 (prediction: about .45) |
| Rater 1 labels | NEW 79, WIDER 15, SAME 13, NO 41, UNCLEAR 24 |
| Rater 2 labels | NEW 80, WIDER 19, SAME 9, NO 42, UNCLEAR 22 |

## The labels overcount new grants (found after the tally; exploratory)
A card shows a changed passage with a little context, not the whole old document. Two things the raters could not
see:
- **The same sentence elsewhere in the old document.** A mechanical check against the full archived history
  (`py -m aiwatch.history ledger`) found 18 of the 92 deciding sentences already present, word for word, in an
  earlier version of the same document (20%). A first, fuzzy version of the check said 20; it wrongly counted
  sentences that had just gained their AI phrase as old (see `aiwatch/history.py`).
  - Archive captures that drop a section and restore it later produced repeat "new" events. Meta's "manual review
    ... to train our algorithms" sentence is in the archive from 2022-12-16 and was flagged five times.
  - Table rewrites repeated an existing purpose.
- **An equivalent right in other words.** Fable 5.2, reading full documents for 55 rows (addendum 3), struck 21. Most
  had a prior grant the card did not show; others were mislabelled documents or moved text.

So **92 is an upper bound on new grants**. The keyword rule's precision for "a new grant" is lower than .535, by
roughly a fifth to a third on this evidence. Labelling changes from diff snippets needs the whole prior document in
view. That is a lesson for any change-level evaluation, this one included.

## Recall: what the keyword rule misses (addendum 2)
A random sample (seed 41) of 120 of the 1,134 AI-vocabulary updates the keyword rule did not flag, rated blind by
the same two raters on the same question.

| | |
|---|---|
| Verified grants in the sample | 11 of 120 (prediction: 3-8) |
| Estimated grants the rule missed | 104 (95% CI 59-178) |
| Keyword recall, 92 / (92 + missed) | .47 (95% CI .34-.61; prediction: .55-.75) |

**The prediction failed on the low side:** the rule finds about half of the grants, not two-thirds. Why it missed
the 11 (checked mechanically against the rule's own patterns):
- **No training word (8).** Companies wrote "develop and improve" instead of "train". Examples: AWS's service terms,
  four times ("we may use ... AI Content to develop and improve ... machine-learning and artificial intelligence
  technologies"); Meta's "Develop and improve AI at Meta"; Snapchat's "Develop and improve our machine learning
  models"; Match's "machine learning development". Cursor's two rows describe collecting prompts and code when
  Privacy Mode is off, with no AI word in the sentence at all.
- **A training word but no AI word (1).** Wix: a licence to "train our software tools".
- **Both words, but no new matching sentence (1).** Spotify's new training sentence replaced one the rule already
  counted, so the count of matching sentences did not rise.

A rule could be widened for "develop and improve", but that would be fitted to this sample. The planned test of a
detector that reads meaning instead of words is Kev's phase 2.

**Counting only new sentences (exploratory, `py -m aiwatch.history recall`).** The sample labels come from cards
too. The same mechanical check against each document's full archived history finds 3 of the 11 sentences already in
an earlier version (27%; phase 1: 18 of 92, 20%). Counting only sentences new to the document on both sides (74
alerts, 8 in the sample): about 76 missed (95% CI 39-143), keyword recall .49 (.34-.66). The reading does not
change: the rule finds about half. The check catches the same sentence only, not an equivalent right in other
words, so both counts are still upper bounds.

## Kev-4B: phase 2
Kev scoring ended 2026-11-20 at 17:18 UTC. Kev raised 392 alerts, 130 of them on updates the keyword rule also
flagged. The 262 cards only Kev raised were generated at 20:12 UTC and rated by 20:35 UTC by the same two raters,
with the same question and blinding (`py -m aiwatch.ledger tally`, `py -m aiwatch.recall tally`).

| | Keyword rule | Kev-4B (p(grant) up by 0.2 or more) |
|---|---|---|
| Alerts | 172 | 392 |
| Verified grants (both raters NEW or WIDER) | 92 | 135 |
| Precision | .535 | .344 |
| Verified grants only this arm found | 9 | 52 |
| Share of all 144 verified grants | .64 | .94 |
| Estimated recall over all AI-vocabulary changes (with the recall sample) | .47 (.34-.61) | .69 (.50-.90) |
| Counting only sentences new to the document: grants, precision | 74, .43 | 103, .26 |

- **Precision, Kev minus keywords:** -.19 (95% CI -.275 to -.112, resampling services). Kev is less precise. The
  plan allows "Kev more precise" only if the interval is above zero; it is below.
- **Agreement** over all 434 cards: kappa .89. In all, 144 verified grants on 63 services.
- **What Kev found that the keywords missed:** 52 grants on 25 services, led by AWS (8), Instagram (6), Wix (4),
  Facebook (4), Llama API (4), Mistral AI (3) and Bolt (3). These are the "develop and improve" wordings the recall
  section describes. 35 of the 52 sentences are new to their document (`py -m aiwatch.history ledger`, now over all
  144: 109 new, 35 already in an earlier version).
- **Repeat check:** 27 recall-sample updates were also Kev alerts and were rated again in phase 2 (that card shows
  only the blocks Kev alerted on). Verified or not agreed on 24 of 27. Kev alerted on 5 of the 11 grants in the
  recall sample.
- **Against my predictions (before any rating):** cards about 250 (434); verified grants 50-90 (144); precision,
  keywords about 45% (.535), Kev about 30% (.344).

**Reading it with the kill test.** On reported incidents the arms tie. Across all changes, Kev finds about half again
as many grants for 2.3 times the alerts: a reader of Kev's feed reads 392 changes to find 135 grants, against 172 for
92. Which is better depends on whether a missed grant or a wasted read costs more. A tracker that wants to be
complete would take Kev's feed; a quick alert feed would take the keywords.

**What this does not show.** That the gain comes from decision-model training. In policywatch, Kev tied its base
model family wherever both were run, and no base model was run here. The fair credit is "a 4B LLM reading each
change", not the decision model. Every label is an AI rater's; no person rated a card.

## The kill test's reading: "keyword ties: stopped"
Full write-up: `RESULT_aiwatch.md`. On the 14 reported incidents, Kev and the keyword rule flagged the same 10, with
the same leads, and Kev raised 392 alerts against 172. That test counted alerts and did not judge them. Phase 2,
above, judged them: 52 of Kev's extra alerts are grants the keyword rule missed.

## Trackers
Public trackers of AI-training clauses exist (TOSTracker, Is It Training on Me?, ConductAtlas), as does a 2026 study
(PolicyForge). Their coverage of the verified rows was checked on their own sites (addenda 1 and 3).
Those results stay out of this repository until Ege has written to the trackers privately.
