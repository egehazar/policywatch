# Result: which arm's top passage states the case? (blind, LLM-rated)

Pre-registration: `stale/PREREG_states_case.md` (02:07 UTC, 2026-11-15). Code, cards and key hashed before rating;
one code revision before any card existed (a short document had no passage for a random control; logged in
`stale/PREREG_states_case.sha256`); verdicts hashed before scoring. Scores: `stale/out/states_case_result.json`.

One Claude subagent (Opus 5.5) rated 150 cards blind (case and passage only). This is one LLM rater on 60 points, not
a person: it sits beside the pre-registered hit@1 results, not in place of them.

## Readings
| | KEV | RERANK | BM25 |
|---|---|---|---|
| States the case @1 (top passage rated YES) | **.717** | .583 | .417 |
| YES or PARTLY @1 | .917 | .767 | .667 |
| hit@1 (the curator's passage) on the same 60 points | .550 | .467 | .306 |

- **KEV - BM25: +.300 [+.167, +.418], KEV better.**
- **KEV - RERANK: +.133 [.000, +.258], no difference shown** (the lower bound sits exactly at 0).
- Validity: 0 of 10 random control passages rated YES, so the comparison is called.

## What it adds
- The order holds and the gaps widen slightly when "right" means "states the case" instead of "the passage the
  curator quoted". When an arm's top passage was not the curator's, the rater still found it stating the case 17
  times in 27 for Kev, 13 in 32 for the reranker and 10 in 42 for BM25: Kev's misses are more often near-misses.
- Kev against the reranker is still not shown, now on a second measure, at the edge of the interval.
- The rater was strict: it rated 42 of 53 curator-quoted passages YES (9 PARTLY, 2 NO). So the absolute rates are
  lower than a lenient reader would give, and in part B Kev's states@1 (.633) is below its hit@1 (.667). The
  comparison between arms, all judged by the same rater, is the meaningful part.

## Prediction against result
| | predicted | result |
|---|---|---|
| States@1 KEV / RERANK / BM25 | .85 / .78 / .50 | .717 / .583 / .417 |
| KEV - RERANK | no difference shown | no difference shown |
| KEV - BM25 | KEV better | KEV better |

By part (30 points each), states@1: A KEV .80, RERANK .63, BM25 .47; B KEV .63, RERANK .53, BM25 .37.

## Final: the pre-registered extension and the pooled 120-point reading
`stale/PREREG_states_case_ext.md` (02:12 UTC), fixed in advance as the only further look: 60 new points (30 from each
part), the same protocol, a fresh rater, then a pooled reading called only if the pooled interval excludes 0 and the
extension points the same way. Hashes in `stale/PREREG_states_case_ext.sha256`; scores in
`stale/out/states_case_pooled.json` (`py -m stale.states_case_ext score`).

| | KEV | RERANK | BM25 |
|---|---|---|---|
| Extension (60 points): states the case @1 | .733 | .633 | .417 |
| **Pooled (120 points): states the case @1** | **.725** | .608 | .417 |
| Pooled: YES or PARTLY @1 | .900 | .758 | .650 |
| Pooled: hit@1 (the curator's passage) on the same points | .625 | .542 | .373 |

- Extension alone: KEV - RERANK +.100 [.000, +.208]; KEV - BM25 +.317 [+.196, +.452]. 0 of 10 random controls rated
  YES; the extension's rater rated 42 of 48 curator-quoted passages YES.
- **Pooled KEV - RERANK: +.117 [+.034, +.200]. Final reading: KEV better than the reranker** on this measure.
- **Pooled KEV - BM25: +.308 [+.206, +.407]. KEV better.**
- On the same 120 points, hit@1 KEV - RERANK is +.083 [-.020, +.183], no difference shown. The gap becomes a shown
  difference because Kev's misses state the case more often: 24 of 45 for Kev, 19 of 55 for the reranker, 14 of 76
  for BM25.
- Predicted: pooled +.11 with about even odds of "KEV better"; result +.117, KEV better.
- The 95% interval is not adjusted for the two looks (disclosed in the extension's pre-registration). Checked
  afterwards: a Pocock-style interval for two looks (about 97.1%, same bootstrap) is [+.029, +.211], still above 0.

## How far this goes
- All three raters (first test, extension, base family) are Claude models judging passages a language model ranked. A rater that shares a language model's
  sense of relevance could favour Kev's picks; nothing here rules that out. A person's ratings would.
- It does not overturn the pre-registered hit@1 results, where KEV and the reranker were not separated in part A and
  were in part B. It adds a second measure, closer to what a curator needs, on which Kev is ahead by about 12 points.
- The base family was rated next (below): no difference shown from Kev, so this lead is not shown to come from
  decision-model training; it belongs to asking a language model per passage.
- The reranker remains 3.6-5x cheaper; part D tests whether a reranker-first cascade keeps Kev's accuracy at a
  fraction of its cost.

## The base family on the same measure (pre-registered, `stale/PREREG_states_case_qwen.md`)
Qwen3.5-4B instruct, asked the same yes/no question per passage (scores on disk from parts A and B). Its top passage
was already rated for 95 of the 120 points (82 are Kev's own top passage); a fresh rater rated the other 25, plus 30
anchor cards re-rated blind and 10 random controls. Hashes in `stale/PREREG_states_case_qwen.sha256`; scores in
`stale/out/states_case_qwen.json` (`py -m stale.states_case_qwen score`).

- Rater checks: the anchors agreed with the earlier verdicts 30 of 30 (YES share unchanged); 0 of 10 random controls
  rated YES. Valid.
- States the case @1 on the 120 points: **QWEN .733**, KEV .725, RERANK .608, BM25 .417.
- **KEV - QWEN: -.008 [-.060, +.039], no difference shown.**
- **QWEN - RERANK: +.125 [+.051, +.206], QWEN better.**
- Predicted: QWEN .71; KEV - QWEN no difference; QWEN better than the reranker (about 60% likely). All three held.

So on both measures the picture is the same: a 4B language model asked about each passage beats BM25 and, on the
states-the-case measure, the reranker; Kev's decision-model training was not shown to add accuracy over its base
family (82 of the 120 top passages are the same, so only 38 points could differ). What Kev adds is cost: it reads a
passage once for all of a document's questions, 1.9x (part B) to 3.1x (part A; corrected 11-15 from 3.2x, see RESULT_relocate2.md) less time than the instruct model,
growing with the number of questions per document.

## Exploratory, 2026-11-15 ~08:00 UTC: are Kev's probabilities better calibrated? (`stale/calib.py`)
Not pre-registered. Kev-4B is trained to return calibrated p(yes); its base family's instruct model gives the log-odds
of "yes" against "no", read as a probability. Both scored every passage of parts A and B, so every passage the blind
raters judged above (anchors left out) has both scores: 307 passage-case pairs, 46% rated YES.

| | Brier | log loss | calibration error (10 bins) | AUROC |
|---|---|---|---|---|
| Kev-4B p(yes) | .140 | .444 | .116 | .903 |
| Qwen3.5-4B instruct, logistic(log-odds) | .135 | .455 | .105 | .909 |

Kev minus the instruct model on Brier: +.004 [-.013, +.021] (bootstrap over passages, not clustered): no difference
shown. With PARTLY left out (247 pairs): +.012 [-.005, +.027]. The shapes differ: the instruct model puts most
passages near 0 or 1 (212 of 307), and those extremes are about right; Kev spreads them out but runs high between .3
and .8 (e.g. passages it scored .6-.7 were rated YES 54% of the time). So on this task the decision-model training
was not shown to add calibration either. The labelled passages are mostly the methods' top picks, not a random
sample, and the raters are Claude models.

## The same cards re-rated by GPT (2026-11-15; exploratory, `stale/PREREG_states_case_gpt.md`)
The plan and scorer were hashed at 10:38 UTC, before GPT saw a card; fed the Claude raters' verdicts, the scorer
reproduces every figure above exactly. GPT (Codex CLI 0.154.0, gpt-6-astra, reasoning xhigh, read-only sandbox, an
empty folder, no web) rated the 337 cards of `audit_states`, `audit_states2` and `audit_states3` blind, one run per
folder, each given that folder's README and cards verbatim. The first attempts hit the Codex usage limit (no reply,
logged); each folder then ran once at 15:28-15:35 UTC. Raw replies and logs: `stale/out/states_gpt_raw/`; verdicts:
`stale/<folder>/verdicts_gpt.json`; scores: `stale/out/states_case_gpt.json`.

| 120 points | KEV | QWEN | RERANK | BM25 |
|---|---|---|---|---|
| States the case @1, Claude raters | .725 | .733 | .608 | .417 |
| States the case @1, GPT | .742 | .750 | .600 | .475 |
| YES or PARTLY @1, GPT | .908 | .950 | .775 | .683 |

- KEV - RERANK: +.142 [+.053, +.228], KEV better (Claude raters: +.117 [+.034, +.200]).
- KEV - BM25: +.267 [+.184, +.355], KEV better.
- KEV - QWEN: -.008 [-.053, +.035], no difference shown. QWEN - RERANK: +.150 [+.080, +.223], QWEN better.
- Checks: 1 of 30 random controls rated YES (valid; the bar was at most 3). The 30 anchor passages, rated twice in two
  folders, got the same YES / not-YES call both times (30 of 30). Card by card, GPT and the Claude raters agree on 298
  of 337 (kappa .768); GPT said YES 165 times, Claude 156.

**Reading (fixed in the plan): HOLDS UNDER GPT.** All three conclusions survive a rater from another company: a
language model asked about each passage picks a passage that states the case more often than the reranker and BM25,
and Kev's decision-model training was not shown to add anything over its base family on this measure (KEV - QWEN
-.008 [-.053, +.035]). Predicted: KEV .65-.75 (.742),
RERANK .55-.65 (.600), BM25 .35-.45 (.475, above), KEV - RERANK +.05 to +.12 with even odds of clearing 0 (+.142,
above the range, cleared), kappa .55-.75 (.768, just above). GPT and the Claude raters are both language models, so the risk named
above (a rater that shares a model's sense of relevance) is narrowed, not removed.
