# Plan: the AI-training clause ledger (r40, exploratory)

Drafted 2026-11-19 ~19:45 UTC; revised ~19:55 UTC after Fable 5.2's round-40 reply
(`decision-serving/notes/fable_r40_reply.md`). Written while the kill test (PLAN_aiwatch.md) was still scoring,
before any Kev result of it and before any rating. Hashed with `aiwatch/ledger.py` (`aiwatch/PLAN_ledger.sha256`)
before the first rater sees a card. GPT-6's round-40 reply was still pending (Codex usage limit); anything it
changes goes in a dated addendum and applies only to steps not yet run.

## Why a second question, and what it is not
- The kill test asks whether a monitor beats the press on clause changes the press reported. Its gold can only
  contain reported changes, so it cannot see the case a monitor exists for: a change nobody reported.
- After prep, and before any Kev result, the keyword arm's alert list showed 165 distinct updates on 76 services.
  Only 6 matched the 22 eligible reported incidents.
- **This is exploratory.** The idea came after the kill test's lead bar was seen to be out of reach, on a topic
  picked in hindsight. It does not change or rescue the kill test, whose reading stands as computed.
- **Already seen before this plan:** Fable press-checked 12 hand-picked keyword alerts (non-blind). 8 were clear
  grants. None had a press report within 30 days. 6 had no report of any kind.

## Question
Between 2023-01-01 and 2026-11-19, which recorded changes to the terms and privacy policies Open Terms Archive tracks
newly let the company train AI on its users' content or personal data, or clearly widened such a right? Which of
those were ever publicly reported, and when? How precise is each monitor arm, keywords against Kev?

## Units
- Every update on which either kill-test arm alerts: keyword grant sentences, or Kev's p(grant) rising by at least
  0.2.
- Updates whose AI blocks are identical (one Google policy under several services) are one card.
- A card shows the blocks that made an arm alert: BEFORE and AFTER, each side cut at 3,500 characters on a paragraph
  boundary.
- **The date is the date the archive first recorded the text, not the date the company introduced it.** It is
  always written that way.

## Rating (blind)
- **Blinding.** Cards are shuffled (seed 40) and carry a random id. Raters never get the service, the date, the arm
  or a score as fields; the policy text itself may name the company.
- **Phases.** Keyword-alert cards are rated first. Cards that only Kev alerts on are rated after Kev scoring ends,
  with the same instructions. A card rated in phase 1 is not rated again. Phase-1 cards show the blocks the
  keyword arm alerted on; phase-2 cards show the blocks Kev alerted on.
- **Raters:**
  - Rater 1: Claude subagents.
  - Rater 2: GPT-6 (Codex). If Codex usage limits block GPT for more than 12 hours, Fable 5.2 rates in its place,
    and this is reported.
- **The label** (`QUESTION` in ledger.py):
  - one of NEW, WIDER, SAME, NO, UNCLEAR;
  - a scope for NEW or WIDER: THIRD (shared for others to train), GENERAL (generative or general-purpose AI, or
    models with no narrow purpose), or NARROW (one operational purpose such as ads, recommendations, fraud or
    safety);
  - the deciding sentence.
- **A verified grant** is a card both raters label NEW or WIDER. Cohen's kappa on grant vs not is reported.
- **A person checks every published row.** Before anything is published, Ege reads the old and new text of every
  verified grant and may strike rows. Struck rows and reasons are listed. This is the first human rating in the
  project.

## Press check (after rating, blind to arms)
- **Searchers.** For each verified grant, two searchers independently look for the earliest report: a Fable subagent
  and GPT, or a Claude subagent with web search if GPT is blocked.
- **What they get:** the service, the document, the date first archived, the deciding sentence and the archive diff
  link. Never the arm or a score.
- **Classes** (`PRESS_Q` in ledger.py):
  - press: news, watchdog or advocacy group, law-firm or industry newsletter, independent blog;
  - company: its own announcement, email, help page or filing;
  - tracker: a machine-written tracker record such as ConductAtlas.
- **Only press counts as "reported".** Company and tracker mentions are separate columns.
- A row is **reported** if either searcher finds a press report, at any date, or one with an unknown date. Also
  counted: press within 30 days of the archive date.
- **Wording.** "None found" is never written as "unreported". The page says "no press report found by two documented
  searches" and lists the queries.

## Measures
- **Verified grants:** count, services, by year, by scope.
- **Precision of each arm:** verified grants among its alerts. Kev minus keywords, with a 95% interval resampling
  services.
- **Relative recall:** of all verified grants, the share each arm alerted on.
- **Press:** found at all, found within 30 days, none found (and of those, how many have only a company or tracker
  mention).
- **ConductAtlas:** "has a record for this clause today: yes/no" is a column, checked for each published row. It is
  reported, not read.

## Readings (fixed now)
- **"worth publishing"** if at least 15 verified grants, on at least 10 services, have no press report found by
  either searcher. Then: a CSV and one page of human-checked rows, with the precision table under it.
- **"thin"** otherwise. Then the rows go into policywatch's results with no headline.
- **The arm comparison is reported, not read.** "Kev more precise" is said only if its interval is above zero.

## Publication rules (Fable's)
- **Each row is phrased as:** "On [date first archived], the archived text of X's [document] added this sentence:
  '...'. Two searches (listed) found no press report of this change. The sentence describes a permitted use; it does
  not show that X does this."
- **Never:** "quietly", "secretly", "never reported", "trains on your data", "gave itself the right".
- **The headline** is "N we verified; M we found reported", never a claim about the press.
- **A corrections address and a dated changelog** go on the page.

## Predictions (mine, before any rating)
- **Cards:** about 250 once Kev's alerts are added.
- **Verified grants:** 50-90.
- **Precision:** keywords about 45%. Kev lower (it reads "AI features" as grants), about 30%.
- **Press:** no report found for about 60% of verified grants at companies that are not AI companies.
- **Reading:** "worth publishing" 70%.

## What this cannot show
- Grants phrased without the words either arm looks for: both arms only see blocks with AI vocabulary.
- Services Open Terms Archive does not track.
- That a change was never reported: only that two searches did not find a press report.
- That a company actually trains on users' data: a policy permits; it does not report practice.

## Addendum 1, 2026-11-19 ~20:40 UTC: prior work found; press check replaced by a tracker check
Written after rater 1 (Claude) had labelled all 172 phase-1 cards, while rater 2 (GPT) was running (2 of 7 batches
answered; none of its labels looked at), and before any press or tracker search.
The labels, raters, verified-grant rule and arm measures above are unchanged.

- **Why.** GPT-6's round-40 reply (`decision-serving/notes/gpt_r40_reply.md`) found three public trackers of AI-training
  clauses, all checked on their own pages the same day: TOSTracker (23 companies, 2026-07-02), Is It Training on Me?
  (261 apps, 455 recorded changes) and PolicyForge (575 policies, 2026-11). A public "N verified; M reported" page
  would repeat them, and "reported" would have to count their records anyway. Archive dates also lag: TOSTracker had
  PayPal's clause on 2026-01-31, the archive on 2026-05-06.
- **Dropped before it ran:** the two-searcher press check, the "worth publishing / thin" reading, the public page and
  its headline. `page.py build` is not used for a public page.
- **Instead, a tracker check.** For each verified grant, one searcher (a Claude subagent with web access, given the
  service, document, archive date and sentence, never an arm or a score) records, for each of Is It Training on Me?,
  TOSTracker and ConductAtlas:
  - whether it covers the service;
  - whether it records this training clause;
  - the earliest date it shows for it (capture or change).
- **Measures (reported, not read):**
  - verified grants per tracker: covered service / clause recorded / recorded no later than the archive;
  - the archive's lead or lag against each tracker's earliest date.
- **Use:** private notes Ege may send to each tracker, listing the changes on services it covers that it lacks or
  dates later than the archive. Nothing about a named company is published by this plan.
- **Ege still reads every row** that goes into such a note.

## Addendum 2, 2026-11-19 ~20:50 UTC: a recall sample
Written after both raters had labelled the 172 phase-1 cards (tally: 92 verified, keyword precision .535, kappa
.894), before any Kev result, before any card below was made or seen, and while the tracker check ran.

- **Why.** Precision alone is not an evaluation. As GPT-6 said in round 40, judging only the arms' alerts cannot show
  what both arms miss.
- **Population:** distinct AI-vocabulary updates of the kill test's prep with no keyword alert: 1,134 of 1,306.
- **Sample:** a simple random sample of 120 (seed 41, `aiwatch/recall.py`).
  - Each card shows all of the update's AI-vocabulary blocks, each side cut at 3,500 characters.
  - A card stops at 20,000 characters; passages past that are listed as not shown and counted.
  - Same question, same blinding, same two raters, ids starting with "R". A sampled update that Kev later alerts on
    is also rated in phase 2; both labels are kept, as a repeat-rating check.
- **Estimates (reported, not read):**
  - grants the keyword arm missed = (verified in sample / 120) x 1,134, with a Wilson 95% interval;
  - keyword recall = 92 / (92 + missed);
  - Kev recall (after phase 2, where every Kev alert is rated) = Kev's verified grants / (keyword verified + the
    larger of the estimate and Kev's count of verified grants without a keyword alert).
- **Limits.** Recall is only within updates whose changed passages use AI vocabulary. A grant worded without any of
  those words is outside both arms and this sample.
- **Prediction (mine):** 3-8 verified in the sample (about 30-75 missed), keyword recall 55-75%.

## Addendum 3, 2026-11-19 ~21:50 UTC: the row check is done by two AI reviewers, not by Ege
Ege's decision: Ege will not read the rows ("It is probably best if we leave the review to fable and gpt"). So:
- **No person has read any ledger row.** Every statement about this work says so; nothing claims a human check.
- **The 55 rows** (verified grants still in the current text that some tracker lacks) are read by Fable 5.2 and by
  GPT-6, separately.
  - Neither reviewer is blind: each sees the service, the full before/after text and the tracker status.
  - Each answers KEEP or STRIKE with a reason.
  - Fable also re-checks each "tracker lacks it" claim on the tracker's own pages.
- **A row goes into a tracker note only if** both reviewers keep it. A tracker claim is used only if Fable confirmed
  it on the tracker's site.
- The trackers' results and these reviews stay outside this repository until Ege has sent the notes.
