# Result: the AI-training clause ledger (r40, exploratory). INTERIM: keyword rule only

Plan: `PLAN_ledger.md` (hashed with `ledger.py` and `recall.py`; addenda 1-3). Started 2026-11-19 while the kill test
(`PLAN_aiwatch.md`) was still scoring. This file covers the keyword rule: its alerts (phase 1) and a recall sample of
what it did not flag. Kev's alerts (phase 2) and the kill test's reading are added when they finish. Marked PENDING
below.

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

## Kev-4B (PENDING: scoring, then phase 2)
## The kill test's reading (PENDING)

## Trackers
Public trackers of AI-training clauses exist (TOSTracker, Is It Training on Me?, ConductAtlas), as does a 2026 study
(PolicyForge). Their coverage of the verified rows was checked on their own sites (addenda 1 and 3).
Those results stay out of this repository until Ege has written to the trackers privately.
