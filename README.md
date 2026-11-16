# policywatch

[Open Terms Archive](https://opentermsarchive.org) records every version of platforms' terms and privacy policies.
[ToS;DR](https://tosdr.org)'s volunteer curators rate services from "points": a case ("You waive your right to a class
action") backed by a quote from those documents.
policywatch watches the archive for the moment a curator's evidence stops being there.

- **Stale evidence finder (`stale/`, working).**
  - *What it finds.* Checks every approved ToS;DR quote against every archived version and lists the points whose
    quote disappeared in an edit by the platform itself, with the archive commit and the passage that replaced it:
    141 on 18 of the 20 platforms and 538 more on 69 other services. For 656 of the 679, ToS;DR's own stored copy
    still holds the quote, so ToS;DR does not know yet; 10 of its documents hold 257 of those. A blind audit (an LLM
    rater) found 27 of 30 sampled drops to be real edits. A daily watch (built, run twice so far, not scheduled) lists
    new ones: its 2026-11-15 run found Pinterest's rewrite of 12 November.
  - *What the model does.* For each stale point it suggests the passages of the current text where the case may be
    stated now, and a sentence to quote. On test points whose answer is the curator's own quote, Kev-4B ranks the
    right passage first 62-75% of the time in three pre-registered samples, against 30-43% for BM25 and bge-small. A
    cross-encoder reranker, at a fraction of the CPU, was not shown to be worse in two of the three samples (Kev led by
    6-10 points in each, with the interval clear of zero in one; about 8 pooled after the fact, exploratory). On whether the top passage states the case
    at all (blind LLM raters, 120 points) Kev is ahead of the reranker, 73% to 61%. A suggestion whose top passage
    clearly leads is marked Clear (right 50 times in 53 in a held-out test). Letting the reranker shortlist 10 passages
    per case lost at most about 2 points, so the wider pages' 538 points were done that way (544 suggestions: six GitHub
    points sit under both GitHub's and GitHub Copilot's documents). 130 are marked Clear; on shortlisted suggestions
    that label was checked only after the test (59 of 62, exploratory). A pre-registered four-document pilot asked
    the reverse question, which cases a document states that ToS;DR has no approved point for on the service: 18 of
    Kev's 40 top-10 suggestions stated one (blind LLM raters; GPT 20), against 9 for the reranker and 6 for BM25.
    Reading: worth building, on Kev (`stale/RESULT_missing.md`; a pilot, not a general result). A larger
    pre-registered test on 10 more documents replicated it: 69 of Kev's 100 top-10 suggestions rated YES (GPT 73)
    against the reranker's 46, Kev better than the reranker on both measures, 2 of 20 random controls YES
    (`stale/RESULT_missing2.md`). For 43 of Kev's 69, an AI check of the titles found nothing close among the
    service's approved cases (exploratory; no person has checked a suggestion).
    The other 20 privacy policies and terms of the 20 platforms ran through the cascade (the reranker's top 3
    passages per case, then Kev; 8.1 h instead of about 18 h): on the 7 with 10 or more approved points Kev on the
    shortlist ranked approved cases above unapproved ones better than the reranker, .771 to .693 (+.078 [+.034,
    +.121], fixed in advance; `stale/RESULT_missing_wide.md`). Their 200 suggestions are on the page, not rated.
  - *What the decision model adds.* Its base family's ordinary 4B instruct model, asked the same yes/no question,
    showed no difference from Kev on either measure, and Kev's probabilities were not shown to be better calibrated
    (exploratory). The larger missing-points test ran it on the same shortlisted passages as Kev: again no difference
    shown (AUROC .721 against .715; rated YES 73 against 70).
    What the decision-model endpoint added is cost: it reads a passage once for all its questions, so it took 1.9x
    (part B) to 3.1x (part A) less time per passage and question than the instruct model, growing with the number of
    questions per document; with one question per document Kev is the slower one. On the missing-points pilot (62-78
    questions per passage) Kev took 1.8 h where the instruct model would need about 10 h (5.7x, estimated); in the
    larger test the instruct model, measured, took 6.05 s per question against Kev's 1.11 s (5.4x).
- **Meaning-diff scanner (`policywatch/`, the original goal, failed its tests).** Asks a decision model a fixed bank of
  questions about the old and new text of every update and lists the answers whose score moved. It did not find real
  changes well enough; the results are below.

Everything runs on a desktop CPU with no API key: Kev-4B (Q8) served by llama.cpp's `/v1/systemone` endpoint.

## Pre-registered results so far
Each test was hashed before scoring. All results are reported, including failures.

### Stale evidence finder
| Test | Reading | Key numbers | Details |
|---|---|---|---|
| Are the listed drops real platform edits? (blind audit, an LLM rater) | **Mostly** | 27 of 30 sampled contrib drops are real edits (.90 [.74, .97]), 8 of 10 on the 20 platforms; the misses are the archive saving another language or region of the page, or losing a page header. The guard's 10 sampled set-asides were all broken captures. | `stale/RESULT_drop_audit.md` |
| Find where a ToS;DR case is stated in a platform's current text | **Decision model better** than BM25 and bge | Top-1 on 200 points: Kev-4B 62%, BM25 36%, bge-small 30%. Gold is the curators' own quotes. | [Stale evidence](#stale-evidence-for-tosdr-points-stale) |
| Same, on 202 held-out points from 41 other services | **Replicated** | Kev 75%, BM25 41%, bge 43%, on ToS;DR's own stored text. | `stale/RESULT_relocate2.md` |
| Same, a third time: 200 points from 47 services on Open Terms Archive's contrib collection (part D) | **Replicated** | Kev 62.5%, BM25 34.5%, bge 34%; Kev - BM25 +.28 [+.20, +.36], Kev - bge +.29 [+.21, +.36]. | `stale/RESULT_relocate_d.md` |
| Kev vs its base family (Qwen3.5-4B asked the same yes/no question) | **No difference shown**, in both parts | 62% vs 60% and 75% vs 74%. The win was not shown to come from decision-model training. Qwen took 1.9-3.1x Kev's time per passage-question. | `stale/RESULT_relocate2.md` |
| Kev vs a cross-encoder reranker (bge-reranker-v2-m3) | **Not shown to beat it** (one of three parts says Kev better) | 62% vs 55% (no difference shown); 75% vs 65% (Kev better); part D 62.5% vs 56.5%, +.06 [-.005, +.13] (no difference shown). The reranker took 0.39, 0.98 and 0.64 s per passage-question, Kev 1.94, 3.52 and 3.08 (wall clock, same CPU; part D's reranker shared it with another job, its Kev arm almost not). Pooled over all three (exploratory, after the results; `stale/pool_rerank.py`): +.08 [+.04, +.12] on 602 points, and Kev - base family +.02 [-.02, +.05] on 402. | `stale/RESULT_relocate2.md`, `stale/RESULT_relocate_d.md` |
| Does the top passage state the case, curator's or not? (120 points, blind LLM raters, pre-registered with one extension) | **KEV better than the reranker and BM25; its base family, no different from KEV, also better than the reranker** (by LLM raters) | States the case @1: KEV .73, RERANK .61, BM25 .42 (hit@1 on the same points .63 / .54 / .37). KEV - RERANK +.12 [+.03, +.20]; KEV - BM25 +.31 [+.21, +.41]. Kev's misses state the case more often (24 of 45, against 19 of 55 for the reranker). Kev's base family (Qwen3.5-4B): .73, no difference shown from KEV (-.01 [-.06, +.04]; 82 of its 120 top passages are Kev's), QWEN - RERANK +.13 [+.05, +.21]: the lead belongs to an LLM per passage, not shown to come from decision-model training. Raters are Claude models, not people; GPT re-rated all 337 cards blind (exploratory, plan hashed before it rated) and every conclusion held (KEV .74, RERANK .60, BM25 .48; KEV - RERANK +.14 [+.05, +.23]; KEV - QWEN -.01; card agreement with the Claude raters kappa .77). | `stale/RESULT_states_case.md`, `stale/RESULT_miss_audit.md` |
| Reranker shortlists each case's top 10 passages, Kev ranks only those (part D) | **Adopted** for the wider pages | 63.0% vs Kev alone 62.5%: +.005 [-.021, +.031], inside the bar (lower bound at least -.03). Kev is asked 27% of the cells but still reads 48% of the passages: about 62% of full Kev's time with the reranker's (an estimate). | `stale/RESULT_relocate_d.md` |
| Mark a Kev suggestion "Clear" when its top passage leads the next by at least .30 (part D, addendum 1) | **Shipped** | 53 of 200 points clear, 50 of them right (.94 [.88, 1.00]; bar .85, lower bound .75); the other 147 right 51% at the top, 78% in the top 3. On the cascade (exploratory, checked after the result): 59 of 62. On the 141 real stale points (exploratory, LLM rater's answer key): all 16 Clear ones right, none on a point whose case is gone. | `stale/RESULT_relocate_d.md` |
| Propose the sentence to quote, from the top passage | **Shipped** | When the passage was right, Kev's sentence matched the curator's quote 83% of the time; BM25's 56%. | `stale/RESULT_relocate2.md` |
| Kev's short question layout for relocation | **Not adopted** | 20 platforms: -2.5 points [-5.3, +0.5], failing the bar (lower bound at least -5). Held-out services: 0.0 [-3.6, +4.0], passing. No rule for the disagreement; the page keeps the layout that passed on its own platforms. | `stale/RESULT_relocate2.md` |
| Suggest where a stale point's case is now stated (141 points) | **Page leads with Kev** (provisional) | Top-1 on 69 points whose quote is gone, averaged over documents: Kev 74%, BM25 with the old quote 77% (no difference shown), bge 49%, BM25 40%. Pooled over points the first two swap (Kev .70, BM25 with the old quote .61). Gold is a model rater's (Claude Opus) until a human check; a second whole key built by GPT from the same texts (exploratory, plan hashed before GPT ran) gives Kev 78%, still ahead of BM25 (34%) and bge (43%). | `stale/RESULT_suggest.md` |
| Missing points pilot: cases a document states that ToS;DR has no approved point for (4 documents, blind LLM raters) | **Worth building, on Kev** | Known positives ranked above negatives, AUROC: Kev .76, reranker .67, BM25 .54 (Kev - reranker +.08 [+.01, +.16], Kev better; Kev - BM25 +.22 [+.12, +.31]). New suggestions rated YES among each method's top 10 per document: Kev 18 of 40 (.45 [.31, .60]), reranker 9, BM25 6; GPT as second rater: 20, 9, 5 (kappa .72); 0 of 10 random controls YES. Kev 1.8 h, instruct model about 10.4 h (estimate), reranker 0.7 h. Base family not run, so the lead is not shown to come from decision-model training. | `stale/RESULT_missing.md` |
| Missing points, larger test: 10 more documents, and Kev against its base family on the same passages (blind LLM raters) | **Replicated; Kev better than the reranker; no difference from the base family** | AUROC: Kev .72, reranker .65, BM25 .56 (Kev - reranker +.07 [+.03, +.12]; Kev - BM25 +.16 [+.10, +.22]); Kev and Qwen3.5-4B on the reranker's top 3 passages per case .721 and .715 (+.006 [-.018, +.027]). Rated YES among the top 10: Kev 69 of 100 [.59, .77], reranker 46, Kev on the shortlist 73, Qwen on the shortlist 70; GPT 73, 49, 76, 72 (kappa .79); 2 of 20 random controls YES. Kev 5.4 h; Qwen 6.05 s per question (5.4x Kev, measured); reranker 1.7 h. | `stale/RESULT_missing2.md` |
| Missing points on the remaining 20 documents of the 20 platforms, through the cascade (the reranker's top 3 passages per case, then Kev); a build, with one check fixed in advance | **Kev on the shortlist better than the reranker** | On the 7 documents with 10 or more approved points: AUROC Kev on the shortlist .771, reranker on every passage .693 (+.078 [+.034, +.121]); Kev higher on 6 of 7 (not on Facebook's 146-passage privacy policy). The 200 suggestions are not rated. Reranker 5.9 h, Kev 2.2 h (about 18 h estimated for Kev on every passage). | `stale/RESULT_missing_wide.md` |
| Label a stale point "case no longer stated" | **Not shipped** (provisional) | Kev ranks the 15 no-longer-stated points low (AUROC .92), but its flag was right for 6 of 12 flagged; the bar was 75%. | `stale/RESULT_suggest.md` |

### Meaning-diff scanner
| Test | Reading | Key numbers | Details |
|---|---|---|---|
| Catch the changes Open Terms Archive's editors wrote memos about (10 memos) | **Failed** | Caught 1 of 10; a random ranking would catch about 2. | [Accuracy](#accuracy), item 2 |
| Rank which answers an update changed (35 updates) | **Failed** | The bar was 24 of 25 changes in 182 reviews; the tool needed 684. | [Accuracy](#accuracy), item 1 |
| Same ranking, Kev-4B vs Qwen3.5-4B on the same CPU | **No clear winner** | The pre-registered comparator (Qwen listing the changed questions) found 2 of 25. Against Qwen answering every question yes/no, an ablation with no verdict attached, Kev found 20 vs 12 within 182 reviews at 2.2x the CPU. | Item 4 |
| Kev with bare yes/no options (cost fix) | **Adopted** | 21 of 25 changes at 0.57x Kev's CPU, now 1.26x Qwen's. | Item 4 |

## Stale evidence for ToS;DR points (`stale/`)
ToS;DR approves each point with a quote from the platform's document. When the platform rewrites that passage, the
point keeps pointing at text that is no longer there. `stale/` checks every approved quote against every recorded
version of the platform's documents in Open Terms Archive. This part is string matching only: no model decides
anything.

- **Snapshot 2026-11-12.** 22 pga-versions platforms are on ToS;DR; 20 have approved points with a quote, 1,114 in
  all.
  - 757 quotes are in the current text, 83 partly and 97 gone. 177 are in no archived version: the document is not
    tracked, or the quote is older than the archive.
  - 141 quotes dropped in an edit by the platform itself (82 gone, 59 partly), each with the archive commit where
    it dropped. 39 more dropped at an archive extraction change or have no single drop version, and are not listed.
  - For 133 of the 141, ToS;DR's own stored copy of the document still holds the quote: the copy predates the edit,
    and a re-crawl would mark them "approved-not-found". For 8, the stored copy no longer holds the quote, yet the
    point is approved (`stale/phoenix.py`).
- **Prior art.** ToS;DR already marks a point "approved-not-found" when a re-crawl misses its quote. Curators then
  re-find the quote by hand (their Dec 2020 re-crawl did this to 1,589 points). What this adds: when the quote dropped,
  whether the platform or the archive changed, and the passage that replaced it.
- **Curator page.** `py -m stale.report <repo> kev` writes `out/site/stale.html`: each point with the old passage, the
  most similar new passage (or "no similar passage"), the drop commit, the three passages of the current text most
  likely to state the case, and a suggested quote from the first of them (`stale/propose.py`; rows of links and tables
  of contents are skipped). `py -m stale.export` writes the same as one CSV row per point
  (`stale/out/stale_points_suggested.csv`); `stale/out/stale_points.csv` is the frozen 11-12 list.
- **Daily.** `py -m stale.daily <pga-versions>` fast-forwards the archive, refreshes ToS;DR's approved points
  incrementally (one request per platform, plus one per new or edited point) and lists what changed since the last run:
  new drops, new points, recovered quotes. Output goes to `stale/live/` (`digest.html`, one JSON per run). The
  snapshot above is never rewritten.
  - Run 2026-11-15 (11 new archive versions since 11-12): Pinterest's terms, privacy policy and community guidelines
    changed on 11-14 ("Effective date: 12 November 2026"), and 8 approved points lost their quote, 4 fully. One
    Pinterest quote came back. For example, the arbitration point's quote is gone because the section was rewritten
    (arbitration moved from AAA to JAMS, batched arbitration became mass-filing rules, the notice of dispute became
    mutual); the case still holds, in new words. No ToS;DR point was new or edited in those three days.
- **Beyond the 20 platforms (`stale/wide.py`, 2026-11-14).** The same string matching over four more Open Terms
  Archive collections, mapped to 212 ToS;DR services by name or web domain. Folders holding the 20 platforms' own
  documents are left out.
  - contrib: 196 ToS;DR services mapped, 147 of them with approved quoted points: 4,447 points, 2,494 still in the
    current text.
  - 521 quotes dropped in an edit by the platform itself, in 65 services (a blind audit rated 27 of 30 sampled ones
    real edits; see below). The largest are Netflix 48, Crunchyroll 43, NordVPN 41, W3Schools 39, Yahoo 39.
    genai-contrib adds 20 and dating 3: 544 on 69 services in all, 538 distinct ToS;DR points (six GitHub points sit
    under both GitHub's and GitHub Copilot's archived documents).
  - For 507 of the 521, ToS;DR's stored copy still holds the quote (re-crawl pending); for 14 it does not. For 63 of
    the 78 documents behind those 507, the stored copy is closest to an archived version more than 3 years old
    (most from 2020-21); on the 20 platforms, 13 of 29 documents.
  - Re-crawl priority (`py -m stale.recrawl` -> `stale/out/recrawl_priority.csv`, one row per ToS;DR document): the
    656 points still held by ToS;DR's stored copies sit in 124 documents, and 10 documents hold 257 of them (20 hold
    390). The largest: Crunchyroll's terms 43, Netflix's privacy policy 39, Zoom's terms 25, Alibaba.com's privacy
    policy 24, W3Schools' terms 23.
  - Older captures fail in ways the archive files as edits: a page collapsed to a title, a login wall saved under
    two documents. 74 such drops on contrib (and 2 on genai-contrib) are set aside as broken captures, not listed.
  - A blind audit (`stale/RESULT_drop_audit.md`, pre-registered, rated by a Claude subagent) found 27 of 30 sampled
    listed contrib drops to be real edits. The 3 others, and 2 of 10 on the 20 platforms, were the archive saving
    another language or region of the page, or losing a page header. All 10 sampled set-asides were broken captures.
  - `stale/wide_daily.py` is the daily watch for these collections (built, not scheduled). A dry run on the snapshot's
    own archive and ToS;DR data (no fetch) reproduces it exactly: 0 events on contrib, genai-contrib and dating.
    `daily.cmd` runs every daily step in one command for Windows Task Scheduler.
- **Where the decision model would come in: relocation.** When a quote is gone, a curator has to find the passage that
  now states the case, or decline the point. A pre-registered test (`stale/PREREG_relocate.md`, hashed before any
  arm was scored) asks whether Kev-4B finds the curator's own quoted passage among a document's 1,500-character pieces
  better than bge-small and BM25. It uses the points whose quote is still present, so the curator's quote is the
  answer key.
  - **Result (2026-11-12): DECISION MODEL BETTER** (`stale/RESULT_relocate.md`). On 200 points in 29 documents,
    Kev ranks a curator-quoted piece first for 62% of points: BM25 36%, bge 30%, and 47% for a stronger embedding
    arm that matches other companies' approved quotes for the same case.
  - Paired 95% intervals over documents: Kev minus bge [+.26, +.39], minus BM25 [+.18, +.32], minus the quote arm
    [+.05, +.26].
  - Checks after the result (exploratory): asked another point's question, Kev's top piece is the right one 6% of the
    time (chance 4%), so it reads the question; the intervals stay above 0 when resampling cases instead of documents.
  - **Follow-up (2026-11-14, `stale/RESULT_relocate2.md`, pre-registered).**
    - Replicated on 202 held-out points from 41 services outside the 20 platforms, on ToS;DR's own stored text: Kev
      75%, BM25 41%, bge 43%.
    - Kev's base family, Qwen3.5-4B, asked the same yes/no question one piece at a time, did about as well: 60% vs 62%
      and 74% vs 75%, no difference shown in either part. So the win was not shown to come from decision-model
      training. Against that model Kev's advantage was cost: it reads a piece once for all of a document's questions,
      and the instruct model took 1.9-3.1x its time per piece-question here (wall clock on the same CPU).
    - The decision model was not shown to beat a cross-encoder reranker (bge-reranker-v2-m3): 55% against Kev's 62% in
      part A (no difference shown) and 65% against 75% in part B (Kev better). The reranker is 3.6-5x cheaper than Kev
      (0.39 and 0.98 s per piece-question, against 1.94 and 3.52; wall clock on the same CPU).
    - Memorisation (exploratory): Kev's fine-tuning data has no ToS;DR text. On points created after its base model
      was first published, which that model's pretraining cannot contain, Kev still leads BM25 by 26 and 35 points,
      consistent with no memorisation behind the win over retrieval. That cut was chosen after the results.
    - Proposed quote: within its top passage, Kev picks the sentence to quote. When the passage was right, that sentence
      matched the curator's quote 83% of the time, against 56% for BM25. The curator page shows it.
  - **Part D (2026-11-15, `stale/RESULT_relocate_d.md`, pre-registered, with one addendum written before the draw).** 200 points
    from 47 services on the contrib collection, drawn and hashed before any model call.
    - Replicated a third time: Kev 62.5%, BM25 34.5%, bge 34%.
    - Kev against the reranker: 62.5% vs 56.5%, no difference shown (+.06 [-.005, +.13]). Over the three parts Kev's
      lead is +.07, +.10 and +.06, and only part B's interval excludes zero. Pooled after the fact (exploratory,
      `stale/pool_rerank.py`): +.08 [+.04, +.12] on 602 points; its base family's lead over the reranker on parts A and
      B is about the same (+.07 [+.02, +.12]), so this too belongs to an LLM per passage.
    - Calibration (exploratory, `stale/calib.py`): on the 307 passages the blind raters judged, Kev's p(yes) was not
      better calibrated than the instruct model's yes/no log-odds (Brier .140 vs .135, difference +.004 [-.013,
      +.021]; AUROC .90 vs .91). The decision-model training was not shown to add calibration either.
    - The cascade: the reranker shortlists each case's top 10 passages and Kev ranks only those. 63.0% against Kev
      alone 62.5%, inside the pre-registered bar (it lost at most about 2 points), so the wider pages' suggestions were
      computed with it (done 11-15 16:59 UTC; on contrib the reranker took 2.7 h, then Kev, asked 24% of the cells, 4.4 h). Kev still reads about half the passages (it reads a passage once for all its
      questions), so the estimated saving is about 38% of the time, not the 73% of cells it skips.
    - The label: a suggestion whose top passage leads the next by at least .30 (a cut chosen on parts A and B) is
      marked Clear. 53 of 200 were clear and 50 of those right; the rest are marked Close (51% right at the top, 78%
      in the top 3). On the 20 platforms' stale points 16 of 141 are Clear. For the cascade's suggestions the same
      rule was checked after the result (59 of 62 right), and the page says so.
  - Cost, from the measured figures below: on a 40-piece document Kev takes about 5.5 min for one stale point and about
    9 min for seven (80 s a point); the cascade cuts that to roughly 62% (an estimate).
  - Where the decision model's cost comes from (measured on an idle CPU, 60 passages of about 1,400 characters,
    `bench/RESULT_cost_curve.md`): Kev takes 7.4 s to read a passage plus 0.93 s per question asked of it (7.0 s and
    0.95 s without five early calls slowed by other work on the machine); the
    instruct model takes 6.3 s per passage and question, and its later questions on a passage cost the same as the
    first (.99), so it reads the passage again for each one (likely because llama.cpp cannot reuse a hybrid recurrent
    model's state for a shared prefix; the effect is measured, the cause is not). So Kev is slower with one question
    per passage (0.83x) and cheaper from two on: 1.4x at 2, 2.4x at 4, 3.4x at 8, 4.7x at 16, toward a limit of 6.8x.
    A curator page asks a few questions of most documents (median 3 on contrib; at most 18 on the 20 platforms, 43 on contrib);
    a tool asking a whole question bank of every document is where it pays.
  - It covers points whose case is still stated. Whether Kev can tell that a case is no longer stated was tested on
    the 141 stale points: it ranks those points low (AUROC .92), but its flag was right 6 times in 12, under the 75%
    bar, so the page makes no such claim (`stale/RESULT_suggest.md`, provisional).
  - The page's suggestions for the 141 stale points now lead with Kev (`stale/RESULT_suggest.md`, provisional: graded
    by an LLM rater; a person did not check the 60 blind cards, GPT and Fable answered them instead and agreed with
    the grader, kappa .67 and .82; GPT also built a whole second answer key, which puts Kev's first suggestion right for
    78% of the gone points against Opus's 74%).

## The meaning-diff scanner (`policywatch/`)
The original goal, kept with its results: it failed its pre-registered tests as a detector of real changes.

### Why
Measured on 35 real Terms of Service and Privacy Policy updates (Open Terms Archive, 2,450 update x question pairs).
Two independent LLM raters (not humans) judged each question on the changed excerpt only, not the whole document.
- In 25 of the 2,450 cases both raters' answer flipped, and in 31 more one rater's did. Most real edits are cosmetic
  or structural.
- A common shortcut (re-check every answer whose top-5 retrieved paragraphs, by bge-small, touch a changed
  paragraph) re-read 365 answers. 96% of those had not changed, and it missed 12 of the 25 changes, which sat outside
  the retrieved paragraphs.
- This shows what one retriever misses on one test. It does not show that dependency tracking cannot work.

### How it works
1. **Diff.** Paragraph diff of the two versions, with link targets and whitespace normalized away. Each changed
   block is read together with one unchanged paragraph on either side.
2. **Ask.** One decision-model request per side answers every question in the bank over the same text. Scores are
   cached in SQLite by (model, text hash, question), so no text is read twice.
3. **Rank.** Questions are ranked by |p_new - p_old|. The model is used as a comparator (the same question on two
   versions), never as an oracle: in earlier tests its ranking was reliable while its 0.5 cut-off was not.
4. **Localize.** For each flagged question, the question is re-asked of each changed block alone, and the block
   that moved it most is shown as evidence.
5. **Numbers and links by rule.** Two kinds of change are listed separately, whatever the model says:
   - a paragraph whose number or date tokens changed ("30 days" -> "14 days")
   - a paragraph whose text is unchanged but whose link now points elsewhere (the linked document can carry
     obligations)
6. **Report.** A static HTML site: one page per update, with word-level diffs, linked to the source commit.
7. **Capture noise is labelled, not scored.** In 2026 so far, 267 of the archive's 835 recorded "changes" (32%) are
   not edits.
   - Either the text returned to a recent version, a recurrence (TikTok's UK-ads banner flips on and off between
     captures), or the new capture was cut off part-way (Reddit's privacy policy, cut at a table about every other
     capture).
   - A recurrence can also be a platform retracting and reinstating a change, so recurrences are labelled and shown
     with their diff, never hidden.
   - Across the whole archive it is 426 of 2,672 (`eval/noise_stats.json`).
   - A return to an older version (more than 6 captures or 45 days back) is scored as a real rollback.
   - After a cut-off capture, the next version is compared with the last full one.
8. **Human review.** `python -m policywatch serve` serves the site with buttons to mark each flagged answer changed,
   not changed or unsure, and to record a change the tool missed. Verdicts go to an append-only file, and the index
   shows running precision and audited misses as counts.

More than 80 changed paragraphs counts as a rewrite: the report says "review everything" and scores nothing.

### Questions
`data/bank.json` has 101 yes/no questions made from ToS;DR case titles: the 70 cases approved on at least 100
services, plus every bad or blocker case approved on 30-99. The second group was added after the first 70 turned out
to have no question about AI training, which would have hidden Twitch's 2026-08-12 privacy update. Because that
update motivated the added questions, it is excluded from every accuracy claim; results with the 70 original
questions are reported separately. See `data/BANK.md`.

What this measures: whether a model's answers to generic case questions move between two versions of the changed
text. It does not show that a specific approved answer for that service became wrong. Tying the questions to a
service's actual approved answers (for example its ToS;DR points) is future work.

### Accuracy
Four measurements; the first three are shown on the site's "How it works" page:
1. **Frozen test** (`python -m policywatch eval`): the pre-registered verdict of that test (quoted, never
   recomputed), then recall at k and precision/recall at the flag threshold on the 35 updates above. One-rater items
   are counted both ways. n = 25 real changes, LLM raters, one model.
   - **Result (2026-11-12): the pre-registered test FAILED.** The bar was 24 of the 25 changes within 182 reviewed
     answers, half of the shortcut's 365. The tool's ranked list needed 684.
   - The tool still ranks usefully. At 182 reviews it holds 19 of the 25 changes (20 without the number/date rule);
     the shortcut re-reads 365 and holds 13. But it is not near-complete, and for this job a missed broken answer is
     the costly error.
   - Most of its late misses are updates where the model already misread the old text.
   - A blind human check of the LLM raters' answer key is in progress (`audit/`, `eval/PREREG_human_audit.md`).
2. **Human write-ups** (`python -m policywatch memocheck`): Open Terms Archive memos about these documents. Each memo
   was mapped to the questions a correct tool should move before anything was scored (`eval/memo_targets.json`,
   hashes in `eval/MEMO_TARGETS.sha256`).
   - A memo counts as caught if one of those questions is flagged or in the update's top 5. A rewrite counts as
     missed.
   - Shown alongside:
     - the count a random ranking would catch
     - a stricter count (a target must be flagged)
     - the original 70-question bank
     - a second rater's mapping
   - 8 of the 19 memos have no recorded update within 10 days and are left out.
   - **Result (2026-11-15): failed.** Caught 1 of 10 judged memos (TikTok's 2026 US rewrite); a random ranking would
     catch about 2. The stricter count is 0 of 9, and the 70-question bank and the second rater's mapping also
     catch 1. One memo has no bank question that fits. The scanner does not find what the archive's editors wrote
     up.
3. **Running human record** (`serve`): precision of flags and audited misses, as counts.
4. **Decision model vs an ordinary LLM** (`bench/`, `eval/PREREG_kev_vs_llm.md`, result in
   `eval/RESULT_kev_vs_llm.md`). Same 35 updates and CPU, against Qwen3.5-4B (Kev's base family, instruct, Q8_0).
   - Pre-registered reading: **no clear winner**. Kev finds more, but at more than the 2x CPU the rule allowed.
   - Changes found within 182 reviews, of 25:
     - Kev: 20, at 180 s of CPU per update
     - Qwen answering all 70 questions yes/no on each side: 12, at 82 s
     - Qwen asked to list the changed questions (the pre-registered comparator): 2, at 49 s. It answered "none" on
       32 of 35 updates.
   - Kev's cost is about 1.1 s per question whatever the text length: 80 s for 70 questions, 580 s for 500.
   - **Follow-up, pre-registered before it ran (`eval/RESULT_short_layout.md`).** The question wrapper's two option
     descriptions were dropped, so the template shows bare "yes"/"no".
     - Recall 21 of 25 at 102.8 s per update (0.57x), so it was adopted under its rule.
     - Against Qwen's yes/no arm: 21 vs 12 changes at 1.26x the CPU. It is still "no clear winner" under the bench
       rule.

## Run
```
llama-server -m kev-4b-q8.gguf --port 9995 -np 4 -c 16384      # a llama.cpp build with /v1/systemone
python -m policywatch scan   --archive path/to/pga-versions --since 2026-10-01
python -m policywatch report --archive path/to/pga-versions
python -m policywatch serve                                    # review at http://127.0.0.1:8787
python -m unittest discover -s tests
```
Stale evidence, 20 platforms (network: api.tosdr.org, about one request per 0.6 s):
```
python -m stale.pull                                   # ToS;DR's approved points -> stale/data/
python -m stale.match   path/to/pga-versions           # quote coverage in every version -> stale/out/points.jsonl
python -m stale.triage  prep path/to/pga-versions      # old and new passage of each drop
python -m stale.phoenix path/to/pga-versions           # does ToS;DR's stored copy still hold the quote?
python -m stale.suggest path/to/pga-versions kev       # top 3 passages of the current text per stale point (Kev)
python -m stale.propose                                # the sentence to quote from the top passage (Kev)
python -m stale.report  https://github.com/OpenTermsArchive/pga-versions kev   # out/site/stale.html
python -m stale.export                                 # the same as a CSV
python -m stale.daily   path/to/pga-versions           # what changed since the last run
python -m stale.daily_suggest path/to/pga-versions kev # Kev's suggestions for the new drops in the daily digest
python -m stale.recrawl                                # which ToS;DR documents to re-crawl first (all collections)
```
The same for other Open Terms Archive collections (`stale/wide.py`; clone `<collection>-versions` and
`<collection>-declarations` next to pga-versions): `python -m stale.wide map|pull|match|cheap|kev <collection>`.
The cheaper suggestions adopted in part D: `<sentence-transformers python> -m stale.cascade rerank <collection>`,
then `python -m stale.cascade kev <collection>`. `daily.cmd` chains the daily steps for Windows Task Scheduler.
Python 3.12+ (tested on 3.14). The core is standard library only; the bge and reranker arms need
sentence-transformers.

## Credits
- Documents: Open Terms Archive, pga-versions (Platform Governance Archive, University of Bremen), ODC-BY 1.0.
- Questions: case titles from ToS;DR (tosdr.org).
- The re-asking mechanic follows jev-why (github.com/Mahad-007/jev-why).
