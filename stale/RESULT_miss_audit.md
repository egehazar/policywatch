# Exploratory result: Kev's "misses" often state the case anyway

Plan: `stale/PLAN_miss_audit.md` (written after parts A and B were final, before any card existed). The plan, code,
70 cards and answer key were hashed at 02:02 UTC on 2026-11-15, before rating, and the verdicts before scoring
(`stale/PLAN_miss_audit.sha256`). Scores: `stale/out/miss_audit_result.json` (`py -m stale.miss_audit score`).
Exploratory: it changes no pre-registered reading.

The rater was a Claude subagent (Opus 5.5) that saw only the case and one passage per card, blind to where the
passage came from. This is an LLM rater's reading, not a person's.

## Result
| Cards | n | YES | PARTLY | NO | YES share |
|---|---|---|---|---|---|
| MISS: Kev's best passage that the curator did not quote, on points Kev missed | 40 | 23 | 9 | 8 | .58 (Wilson 95% [.42, .72]) |
| GOLD control: the curator's passage, on points Kev found | 15 | 12 | 3 | 0 | .80 |
| RANDOM control: a passage outside Kev's top 5 | 15 | 0 | 1 | 14 | .00 |

- The controls pass the plan's bar (GOLD at least .80, RANDOM at most .20), GOLD only just. The rater was strict: the
  3 gold passages it rated PARTLY state a narrower version of the case (for example, child sexual abuse material
  forbidden, for the case "harming minors is prohibited").
- By part: 13 of 20 MISS cards YES in part A, 10 of 20 in part B.
- **Estimate (exploratory, LLM-rated):** the share of points where Kev's top passage states the case, whether or not
  the curator quoted it, is about .87 in part A (hit@1 .620) and .88 in part B (hit@1 .752). With 20 cards per part
  the uncertainty is wide: with each part's own Wilson interval for the MISS share, about .79-.93 for A and .83-.93
  for B.

## What the misses were
- **Another passage stating the case (23 of 40, YES).** Policies repeat themselves: a summary and the full clause, a
  general section and a regional one. The curator quoted one; Kev ranked another first.
- **A narrower statement (9, PARTLY).** For example a liability disclaimer that covers only third-party sites, or a
  ban on explicit content only in private messages.
- **Wrong passages (8, NO).** Two are navigation: a table of contents and a website menu, whose headings share the
  case's words. The proposed-quote step already skips navigation units (11-14); the passage ranking does not.
  Checked afterwards on the saved scores: ranking navigation pieces last (propose.py's rule: half the words are link
  text) moves part A's hit@1 from .620 to .625 (one point) and leaves part B's at .752, because ToS;DR's stored text
  has no link markup, so its menu passage is not caught. Too small to change the ranking for.

## What this does and does not change
- It does not change any comparison between arms. Only Kev's misses were rated. BM25's and the reranker's misses
  could state the case too, so the adjusted figure must not be set against the other arms' plain hit@1.
- It says hit@1 against the curator's own quote understates how often Kev sends a curator to a passage that states
  the case, by roughly 12-25 points, and that ranking navigation passages first is one of the few clear failure kinds.
- Follow-up, run and pre-registered: `stale/RESULT_states_case.md` rates every arm's top passage on 60 points. Its
  rater found 17 of Kev's 27 non-curator top passages stating the case (63%, close to the 58% here), but it was
  stricter on the curator's own passages (42 of 53 YES). The estimate above counts every hit as stating the case,
  so read .87/.88 as an upper figure. Across all the LLM-rated Kev misses (this audit and the 120-point test, 85 in
  all) about half state the case (47 of 85); the 120-point test alone gives 24 of 45.
