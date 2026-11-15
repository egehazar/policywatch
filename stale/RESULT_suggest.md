# Stale-point suggestions: result (2026-11-13, PROVISIONAL)

Pre-registration: `stale/PREREG_suggest.md` (hashes in `stale/PREREG_suggest.sha256`; the arm outputs' hashes were
appended by the run at 01:26 UTC). Scored with `py -m stale.suggest_eval` -> `stale/out/suggest_result.json`, at
archive HEAD b2ac8a9.

**Status: PROVISIONAL.** The gold is a model rater's (Claude Opus reading every piece of the current text). It becomes
final only when Ege's 60 blind cards (`audit/gate/`, drawn 01:27 UTC: 22 rater-cited pieces, 23 arm picks the rater did
not cite, 15 "none" cases) agree with the rater at kappa >= .6. If they do not, the reading is void.

**2026-11-15: Ege did not answer the cards and asked GPT and Fable to answer them instead** (plan written and hashed
before either ran: `stale/PREREG_gate_llm.md`). Both agreed with the grader above the .6 bar (GPT .67, Fable .82). That
is two more AI raters, not a person, so the result stays provisional. Details at the end.

## The population
- 141 ToS;DR points whose quote disappeared from the platform's text in a platform edit.
- The rater found the case still stated somewhere for 126 of them, and nowhere for 15.
- "Gone" (69 stated points, 22 documents): no part of the quote survives. "Partly" (57, 20): some of it does.

## 1. "This case may no longer be stated": the label does NOT ship
The label needed all five conditions. One failed and one is pending:

| Condition | Result | |
|---|---|---|
| Kev's AUROC (highest p(yes) in the document, stated vs none), lower bound >= .70 | .922 [.866, .967] | pass |
| The flag rule flags at least 8 points | 12 | pass |
| At least 75% of flagged points are "none" | 6 of 12 (50%) | **fail** |
| Rater control recall >= .85 | .932 (74 controls) | pass |
| Human gate | not answered (two AI raters stood in: both agree with the grader, see the end) | |

Kev ranks the 15 "none" points low (AUROC .92, against .78 for the quote-embedding arm), but its fixed flag
threshold catches as many stated points as none points. The page keeps making no verdict, as pre-registered. The
known ceiling held: a case often lives in one place, so when that place goes, the next-best piece can score low even
though the rater found it stated elsewhere.

## 2. Suggestions: the page leads with Kev
Precision@1 = the arm's top piece is one the rater cited. Primary summary: mean over documents, gone stratum.

| Arm (what it is given) | Gone: p@1 (doc mean) | Gone: p@1 (pooled) | Gone: found in top 3 | Partly: p@1 (doc mean) |
|---|---|---|---|---|
| **KEV** (case title) | **.741** | .696 | **.913** | .735 |
| QUOTE_BM25 (the old quote, BM25) | .771 | .609 | .783 | .855 |
| BGE (case title) | .486 | .420 | .638 | .374 |
| QUOTE (the old quote, bge windows) | .466 | .391 | .754 | .855 |
| BM25 (case title) | .399 | .348 | .478 | .344 |
| HUNK (the diff's replacement passage; abstains on 51 of 69) | .303 | .188 | .217 | .788 |

Paired differences on the gone stratum, arm minus KEV, 95% cluster bootstrap over documents:

| | point | 95% interval |
|---|---|---|
| QUOTE_BM25 - KEV | +.03 | [-.05, +.15] |
| BGE - KEV | -.26 | [-.45, -.07] |
| QUOTE - KEV | -.27 | [-.47, -.07] |
| BM25 - KEV | -.34 | [-.53, -.13] |
| HUNK - KEV | -.44 | [-.63, -.21] |

- No arm's interval is entirely above Kev's, so under the pre-registered rule the page leads with Kev's top 3.
- Given only the case title, Kev does as well as BM25 given the old quote, and better than every other title-only arm.
- On the partly stratum, where some of the quote survives, the quote-based arms lead (.86 against Kev's .74). The
  intervals include 0, but a curator should see the quote match first there. The page already shows QUOTE and HUNK
  beside Kev.
- The pre-registration says the comparison is descriptive: with about 70 points in 22 documents, differences under
  about .25 were not expected to be distinguishable.

## Prediction (hashed before the arms ran)
Precision@1 on gone points: KEV .50, HUNK .55 where it answers, QUOTE .45, QUOTE_BM25 .40, BM25 .30, BGE .25.
P(the label ships) = 10%. Kev did better than predicted (.74), and so did QUOTE_BM25 (.77). HUNK, where it answers,
was close (.72 on 18 points). The label did not ship.

## Rater quality
- Opus: 552 quotes checked, all verbatim in the text; control recall .932 on 74 control cases.
- Sonnet cross-check on 3 batches: control recall .833 on 12. On the 16 shared cases the two agreed on stated / none
  15 times; kappa is uninformative there because almost every case was "stated".
- The human gate is the real check. It was not answered; GPT and Fable answered its 60 cards instead (below).

## What this means for the system
- The curator page (`out/site/stale.html`, rebuilt with Kev at 01:26 UTC) shows Kev's top 3 for each stale point, with
  the old-quote match and the diff passage beside it. It makes no "no longer stated" verdict.
- Kev's ranking of "none" points is good enough to sort a queue (most likely gone first), not to label one.

## The 60 gate cards, answered by GPT and Fable instead of a person (2026-11-15)
Plan: `stale/PREREG_gate_llm.md` (hashed 10:24 UTC, before either rater ran). Scored with `py -m stale.gate_llm score`
-> `stale/out/fullread/gate_llm.json`. Raw replies: `gate_raw_gpt.txt` (Codex CLI 0.154.0, gpt-6-astra, reasoning
xhigh, read-only sandbox, empty folder), `gate_raw_fable.json` (Claude Fable 5.2 subagent; its log shows it opened only
the cards file and wrote only its answers file). Both saw the page's instructions and the 60 cards, nothing else.

| | Cards answered yes/no | Agree with the grader | Kappa vs the grader |
|---|---|---|---|
| GPT | 60 | 51 | .674 |
| Fable | 59 (1 can't tell) | 54 | .817 |
| GPT vs Fable | 59 | 52 | .744 |

| Stratum | Cards | Grader yes | GPT yes | Fable yes |
|---|---|---|---|---|
| Pieces the grader cited | 22 | 22 | 17 | 19 |
| Arm picks the grader did not cite | 23 | 0 | 4 | 3 |
| Kev's top piece where the grader found none | 15 | 0 | 0 | 0 |

**Reading (fixed in the plan): TWO OTHER AI RATERS AGREE WITH THE GRADER.** Still provisional: not a human check.

What it means:
- The 15 "none" cards are the cleanest part: neither rater found the case in Kev's top piece for any of them, so the
  grader's "no longer stated anywhere" calls hold up for those pieces.
- Both raters disagreed with the grader on 3 cards: 2 arm picks the grader did not cite that both call evidence (g10,
  g29), and 1 cited piece both call not enough (g23). Each rater alone disagreed on a few more (GPT 6, Fable 2);
  three of GPT's are cited advertising passages it read more strictly than the other two.
- The errors run both ways (cited pieces called not enough, uncited picks called evidence), so this does not say
  whether Kev's .74 is high or low; it says the grading it rests on is roughly how two other models read the cards.

