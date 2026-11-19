# policywatch: results in detail

The README has the summary. This file has every test, its reading and its numbers; each row links to its result file in `stale/`, `eval/` or `bench/`.

## Summary by part
- **Stale evidence finder (`stale/`, working).**
  - *What it finds.* Checks every approved ToS;DR quote against every archived version and lists the points whose
    quote disappeared in an edit by the platform itself, with the archive commit (and, for 78 of the 141, the passage
    that replaced it): 141 on 18 of the 20 platforms and 538 more on 69 other services (snapshots of 11-12 and
    11-14). Of the 679, 483 have no part of the quote left and 196 only part of it; 39 are "date of the last update"
    points, whose quote is the date line itself and drops with every update. For 656 of the 679, ToS;DR's own stored
    copy still holds the quote. On the 20 platforms all 133 such copies are closest to an archived version from before
    the drop, although ToS;DR's document record shows a later update date for 110 of them (so that date is not when
    the text was fetched). A re-crawl would mark these points approved-not-found. ToS;DR announced in December 2023 that
    it would source document text from Open Terms Archive; nothing public says quotes are re-anchored or curators
    alerted. 10 of ToS;DR's documents hold 257 of the 656. A blind audit (an LLM rater) found 27 of 30 sampled contrib drops, and 8 of 10 on the
    20 platforms, to be real edits. A daily watch (built, run by hand three times so far: 11-12, 11-15, 11-19; not scheduled) lists new ones: its
    2026-11-15 run found Pinterest's rewrite (effective 12 November, recorded by the archive on 14 November).
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
    (`stale/RESULT_missing2.md`; departures from the plan are disclosed there). Two checks after the fact
    (exploratory, `py -m stale.prior_check`): a ranking that never reads the document, by how often curators approve
    each case on other services, scores AUROC .63, about the reranker's .65 (Kev .72); and the AUROC interval
    resampled cases within these 10 documents, while resampling documents instead puts Kev - reranker at +.07
    [.00, +.14]. So "Kev better" holds for these documents. For 43 of Kev's 69, an AI check of the titles found nothing close among the
    service's approved cases (exploratory; no person has checked a suggestion).
    20 more privacy policies and terms of the 20 platforms (with the tests' 14, the 34 of the 40 that have a matched
    ToS;DR point) ran through the cascade (the reranker's top 3 passages per case, then Kev; 8.1 h, against about 18 h
    estimated for Kev on every passage): on the 7
    with 10 or more known positives (approved cases whose quote is still in the text) Kev on the shortlist ranked
    those cases above unapproved ones better than the reranker, .771 to .693 (+.078 [+.034,
    +.121], fixed in advance; `stale/RESULT_missing_wide.md`). That interval resamples cases within the 7 documents;
    resampling documents gives [-.009, +.164], and the text-blind ranking scores .671 (both after the fact). The last 6 (no matched point, so nothing to check them against) went through the same cascade
    afterwards: the page covers all 40, and re-scores a document when the archive records a new version of it
    (Pinterest's two, after the rewrite). A third blind check (pre-registered) then rated the suggestions on
    those 28 documents: 190 of the page's 280 rated YES (.68 [.62, .73], predicted .55-.75) against 150 for the
    reranker's own top 10, +.14 [+.075, +.21]; 1 of 20 random controls YES; GPT as second rater 203 against 150, kappa
    .72 (`stale/RESULT_wide_rate.md`; departures from the plan are disclosed there). Exploratory,
    after scoring: the page is weakest on documents with many known positives (X's terms 2 of 10), and Kev's printed
    p(yes) sorts its suggestions: 149 of the 179 at 0.90 or more were rated YES. For 100 of the 190 YES, an AI check of
    the titles found nothing close among the service's approved cases (17 variants, 73 close).
  - *What the decision model adds.* Its base family's ordinary 4B instruct model, asked the same yes/no question,
    showed no difference from Kev on either measure (hit@1 on the curator's passage in relocation parts A and B; LLM-rated
    "states the case"), and Kev's probabilities were not shown to be better calibrated (exploratory). The larger
    missing-points test ran it on the same shortlisted passages as Kev: again no difference shown (AUROC .721 against
    .715; rated YES 73 against 70). It was not run on the other tests.
    What the decision-model endpoint appeared to add was cost: it reads a passage once for all its questions, while the instruct
    model, asked one question per request, took 1.9x (part B, 202 held-out points) to 3.1x (part A, 200 points on the
    20 platforms) as long per passage and question, growing with the number of
    questions per document; with one question per document Kev is the slower one. On the missing-points pilot (62-78
    questions per passage) Kev took 1.8 h where the instruct model would need about 10 h (5.7x, estimated); in the
    larger test the instruct model, measured, took 6.05 s per question against Kev's 1.11 s (5.4x). The setups were
    not equal: Kev's server ran 4 parallel slots and the instruct model's 1.
    Then the obvious question was measured (pre-registered, `stale/RESULT_multiq.md`): asked all of a passage's
    questions in one grammar-forced prompt, the instruct model read each passage once too and took 1.79 s per question
    against Kev's 2.01 s on the same 2,043 questions, with no difference in accuracy (AUROC .733 vs .721). The cost
    edge is gone. Nothing measured in policywatch comes from the decision model: its results are those of a 4B LLM
    reading each passage.
- **Meaning-diff scanner (`policywatch/`, the original goal, failed its tests).** Asks a decision model a fixed bank of
  questions about the old and new text of every update and lists the answers whose score moved. It did not find real
  changes well enough; the results are below.

Everything runs on a desktop CPU with no API key: Kev-4B (Q8) served by the `/v1/systemone` endpoint of a custom
llama.cpp build. "pga-versions" is Open Terms Archive's Platform Governance Archive collection of large platforms'
documents (see Credits); "the 20 platforms" are its services that have approved ToS;DR points with a quote.

## Pre-registered results so far
Each test was hashed before scoring. All results are reported, including failures. The hashes and their times are
in this repository's commit history only; nothing timestamps them publicly. Each plan was written knowing the
earlier results, mostly on the same 20 platforms and the same rubric, and no correction is made for the number of
tests.

### Stale evidence finder
| Test | Reading | Key numbers | Details |
|---|---|---|---|
| Are the listed drops real platform edits? (blind audit, an LLM rater) | **Mostly** | 27 of 30 sampled contrib drops are real edits (.90 [.74, .97]), 8 of 10 on the 20 platforms; the misses are the archive saving another language or region of the page, or losing a page header. The guard's 10 sampled set-asides were all broken captures. | `stale/RESULT_drop_audit.md` |
| Find where a ToS;DR case is stated in a platform's current text (part A: 200 points on the 20 platforms) | **Kev-4B better** than BM25 and bge (the plan's reading "DECISION MODEL BETTER"; an ordinary 4B instruct model of the same family did as well, two rows down) | Top-1 on 200 points: Kev-4B 62%, BM25 36%, bge-small 30%. Gold is the curators' own quotes. | [Stale evidence](#stale-evidence-for-tosdr-points-stale) |
| Same, on 202 held-out points from 41 other services (part B) | **Replicated** | Kev 75%, BM25 41%, bge 43%, on ToS;DR's own stored text. | `stale/RESULT_relocate2.md` |
| Same, a third time: 200 points from 47 services on Open Terms Archive's contrib collection (part D) | **Replicated** | Kev 62.5%, BM25 34.5%, bge 34%; Kev - BM25 +.28 [+.20, +.36], Kev - bge +.29 [+.21, +.36]. | `stale/RESULT_relocate_d.md` |
| Kev vs its base family (Qwen3.5-4B asked the same yes/no question) | **No difference shown**, in both parts | 62% vs 60% and 75% vs 74%. The win was not shown to come from decision-model training. Qwen, asked one question per request, took 1.9-3.1x Kev's time per passage-question; asked all of a passage's questions in one prompt it was as cheap (`stale/RESULT_multiq.md`). | `stale/RESULT_relocate2.md` |
| Kev vs a cross-encoder reranker (bge-reranker-v2-m3) | **Not shown to beat it** (one of three parts says Kev better) | 62% vs 55% (no difference shown); 75% vs 65% (Kev better); part D 62.5% vs 56.5%, +.06 [-.005, +.13] (no difference shown). The reranker took 0.39, 0.98 and 0.64 s per passage-question, Kev 1.94, 3.52 and 3.08 (wall clock, same CPU; part D's reranker shared it with another job, its Kev arm almost not). Pooled over all three (exploratory, after the results; `stale/pool_rerank.py`): +.08 [+.04, +.12] on 602 points, and Kev - base family +.02 [-.02, +.05] on 402. | `stale/RESULT_relocate2.md`, `stale/RESULT_relocate_d.md` |
| Does the top passage state the case, curator's or not? (120 points, blind LLM raters, pre-registered with one extension) | **KEV better than the reranker and BM25; its base family, no different from KEV, also better than the reranker** (by LLM raters) | States the case @1: KEV .73, RERANK .61, BM25 .42 (hit@1 on the same points .63 / .54 / .37). KEV - RERANK +.12 [+.03, +.20]; KEV - BM25 +.31 [+.21, +.41]. Kev's misses state the case more often (24 of 45, against 19 of 55 for the reranker). Kev's base family (Qwen3.5-4B): .73, no difference shown from KEV (-.01 [-.06, +.04]; 82 of its 120 top passages are Kev's), QWEN - RERANK +.13 [+.05, +.21]: the lead belongs to an LLM per passage, not shown to come from decision-model training. The first pre-registered look (60 points) alone read KEV - RERANK +.13 [.00, +.26], no difference shown; the pooled interval is not adjusted for the two looks, and a Pocock-style check afterwards, [+.03, +.21], still excludes 0. Raters are Claude models, not people; GPT re-rated all 337 cards blind (exploratory, plan hashed before it rated) and every conclusion held (KEV .74, RERANK .60, BM25 .48; KEV - RERANK +.14 [+.05, +.23]; KEV - QWEN -.01; card agreement with the Claude raters kappa .77). | `stale/RESULT_states_case.md`, `stale/RESULT_miss_audit.md` |
| Reranker shortlists each case's top 10 passages, Kev ranks only those (part D) | **Adopted** for the wider pages | 63.0% vs Kev alone 62.5%: +.005 [-.021, +.031], inside the bar (lower bound at least -.03). Kev is asked 27% of the cells but still reads 48% of the passages: about 62% of full Kev's time with the reranker's (an estimate, worked out after the result). | `stale/RESULT_relocate_d.md` |
| Mark a Kev suggestion "Clear" when its top passage leads the next by at least .30 (part D, addendum 1) | **Shipped** | 53 of 200 points clear, 50 of them right (.94 [.88, 1.00]; bar .85, lower bound .75); the other 147 right 51% at the top, 78% in the top 3. On the cascade (exploratory, checked after the result): 59 of 62. On the 141 real stale points (exploratory, LLM rater's answer key): all 16 Clear ones right, none on the 15 points whose case the rater found no longer stated. | `stale/RESULT_relocate_d.md` |
| Propose the sentence to quote, from the top passage | **Shipped** | When the passage was right, Kev's sentence matched the curator's quote 83% of the time; BM25's 56%. | `stale/RESULT_relocate2.md` |
| Kev's short question layout for relocation | **Not adopted** | 20 platforms: -2.5 points [-5.3, +0.5], failing the bar (lower bound at least -5). Held-out services: 0.0 [-3.6, +4.0], passing. No rule for the disagreement; the page keeps the original layout, since the short one failed on the page's own platforms. | `stale/RESULT_relocate2.md` |
| Suggest where a stale point's case is now stated (141 points) | **Page leads with Kev** (provisional) | Top-1 on the 69 of the 82 gone-quote points whose case the rater found still stated, averaged over documents: Kev 74%, BM25 with the old quote 77% (no difference shown), bge 49%, BM25 40%. Pooled over points the first two swap (Kev .70, BM25 with the old quote .61). Gold is a model rater's (Claude Opus); no person has checked it; a second whole key built by GPT from the same texts (exploratory, plan hashed before GPT ran) gives Kev 78%, still ahead of BM25 (34%) and bge (43%). | `stale/RESULT_suggest.md` |
| Missing points pilot: cases a document states that ToS;DR has no approved point for (4 documents, blind LLM raters) | **Worth building, on Kev** | Known positives ranked above negatives, AUROC: Kev .76, reranker .67, BM25 .54 (Kev - reranker +.08 [+.01, +.16], Kev better; Kev - BM25 +.22 [+.12, +.31]). New suggestions rated YES among each method's top 10 per document: Kev 18 of 40 (.45 [.31, .60]), reranker 9, BM25 6; GPT as second rater: 20, 9, 5 (kappa .72); 0 of 10 random controls YES. Kev 1.8 h, instruct model about 10.4 h (estimate), reranker 0.7 h. Base family not run here, so the lead is not shown to come from decision-model training (it was run in the larger test, next row, and matched Kev). The 10.4 h estimate is for one question per request. After the fact: a ranking that never reads the text (how often curators approve each case elsewhere) scores .65, which the reranker was not shown to beat. | `stale/RESULT_missing.md` |
| Missing points, larger test: 10 more documents, and Kev against its base family on the same passages (blind LLM raters) | **Replicated; Kev better than the reranker; no difference from the base family** | AUROC: Kev .72, reranker .65, BM25 .56 (Kev - reranker +.07 [+.03, +.12]; Kev - BM25 +.16 [+.10, +.22]); Kev and Qwen3.5-4B on the reranker's top 3 passages per case .721 and .715 (+.006 [-.018, +.027]). Rated YES among the top 10: Kev 69 of 100 [.59, .77], reranker 46, Kev on the shortlist 73, Qwen on the shortlist 70; GPT 73, 49, 76, 72 (kappa .79); 2 of 20 random controls YES. Kev 5.4 h; Qwen asked one question per request 6.05 s per question (5.4x Kev, measured; asked all of a passage's questions in one prompt, 1.79 s against Kev's 2.01 s, `stale/RESULT_multiq.md`); reranker 1.7 h. After the fact: the text-blind ranking scores .63, which the reranker was not shown to beat (Kev +.09 [+.03, +.15] over it); resampling documents, Kev - reranker is +.07 [.00, +.14]. | `stale/RESULT_missing2.md` |
| Missing points on 20 more documents of the 20 platforms (those with a matched ToS;DR point; the last 6 added later: all 40 covered), through the cascade (the reranker's top 3 passages per case, then Kev); a build, with one check fixed in advance | **Kev on the shortlist better than the reranker** | On the 7 documents with 10 or more known positives: AUROC Kev on the shortlist .771, reranker on every passage .693 (+.078 [+.034, +.121]); Kev higher on 6 of 7, two of them near ties (not on Facebook's 146-passage privacy policy, where Kev on every passage did worse still, .656: the shortlist was not the reason; exploratory, one document). Their suggestions were rated in the next row. Reranker 5.9 h, Kev 2.2 h (about 18 h estimated for Kev on every passage). After the fact: the text-blind ranking scores .67; resampling documents, Kev on the shortlist - reranker is +.08 [-.01, +.16]. | `stale/RESULT_missing_wide.md` |
| The page's suggestions on those 28 documents (the 20, the last 6, and Pinterest's two on their new text), rated blind against the reranker's own top 10 | **Page precision in the predicted range; page better than the reranker** | Rated YES: page 190 of 280 (.68 [.62, .73]; predicted .55-.75), reranker 150 of 280; page - reranker +.14 [+.075, +.21] over 28 documents; 1 of 20 random controls YES. Top 5 per document .77, ranks 6-10 .59. Exploratory, after scoring: weakest on documents with many known positives (45 of 90 on the 9 with 19 or more, 145 of 190 on the rest). Two Claude Opus raters, each on half the cards; GPT as second rater 203 vs 150 (kappa .72). | `stale/RESULT_wide_rate.md` |
| Missing points beyond the 20 platforms: 20 documents of 20 services from the contrib collection, drawn at random before any model ran (one per service); the page against the reranker's own top 10, and the printed p(yes) >= 0.90 as a label (two blind Claude Opus raters, each in its own folder) | **In the predicted range; page better; label adopted** | Rated YES: page 139 of 200 (.695 [.63, .76]; predicted .60-.80), reranker 99 of 200; page - reranker +.20 [+.14, +.27] over 20 documents (predicted +.05 to +.25); 2 of 20 random controls YES. Printed p(yes) 0.90 or more: 114 of 133 rated YES (.86 [.79, .91]; predicted .75-.90), the rest 25 of 67 (.37), so the page marks them. Exploratory: AUROC on the 10 documents with 5+ known positives, page .744, reranker .668, text-blind .635 (page - reranker +.08 [+.04, +.12] resampling documents). Kev 1.84 s per asked cell (19 documents; the 20th's time includes 11.4 h of PC sleep). GPT second rating queued (usage limit). | `stale/RESULT_missing_contrib.md` |
| Does the decision model's cost edge survive asking the instruct model all of a passage's questions in one prompt? (the larger test's 275 shortlisted passages, 2,043 questions, pre-registered) | **Edge gone; accuracy no difference shown** | Kev 2.01 s per question, the instruct model in one prompt 1.79 s (ratio 0.89, "edge gone" at 1.0 or less); no question count where Kev was cheaper (0.87-0.92 by count, exploratory). AUROC .721 vs .733, KEV - MULTI -.012 [-.057, +.032] over 10 documents; one question per request .715. 0 of 2,043 cells failed to parse under the grammar. | `stale/RESULT_multiq.md` |
| Label a stale point "case no longer stated" | **Not shipped** (provisional) | Kev ranks the 15 no-longer-stated points low (AUROC .92), but its flag was right for 6 of 12 flagged; the bar was 75%. | `stale/RESULT_suggest.md` |

### Meaning-diff scanner
| Test | Reading | Key numbers | Details |
|---|---|---|---|
| Catch the changes Open Terms Archive's editors wrote memos about (10 memos) | **Failed** | Caught 1 of 10; a random ranking would catch about 2. | [Accuracy](SCANNER.md#accuracy), item 2 |
| Rank which answers an update changed (35 updates) | **Failed** | The bar was 24 of 25 changes in 182 reviews; the tool needed 684. | [Accuracy](SCANNER.md#accuracy), item 1 |
| Same ranking, Kev-4B vs Qwen3.5-4B on the same CPU | **No clear winner** | The pre-registered comparator (Qwen listing the changed questions) found 2 of 25. Against Qwen answering every question yes/no, an ablation with no verdict attached, Kev found 20 vs 12 within 182 reviews at 2.2x the CPU. | [Accuracy](SCANNER.md#accuracy), item 4 |
| Kev with bare yes/no options (cost fix) | **Adopted** | 21 of 25 changes at 0.57x Kev's CPU, now 1.26x Qwen's. | [Accuracy](SCANNER.md#accuracy), item 4 |

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
    changed (recorded by the archive on 11-14; "Effective date: 12 November 2026"), and 8 approved points lost their
    quote, 4 fully. One Pinterest quote came back. For example, the arbitration point's quote is gone because the
    section was rewritten; read by hand, arbitration moved from AAA to JAMS, batched arbitration became mass-filing
    rules and the notice of dispute became mutual, so the case still holds, in new words. No ToS;DR point was new or
    edited in those three days.
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
    679 listed points sit in 124 ToS;DR documents; the 656 still held by ToS;DR's stored copies sit in 115 of them, and
    10 documents hold 257 of those (20 hold 390). The largest: Crunchyroll's terms 43, Netflix's privacy policy 39, Zoom's terms 25, Alibaba.com's privacy
    policy 24, W3Schools' terms 23.
  - Older captures fail in ways the archive files as edits: a page collapsed to a title, a login wall saved under
    two documents. 74 such drops on contrib (and 2 on genai-contrib) are set aside as broken captures, not listed.
  - A blind audit (`stale/RESULT_drop_audit.md`, pre-registered, rated by a Claude subagent) found 27 of 30 sampled
    listed contrib drops to be real edits. The 3 others, and 2 of 10 on the 20 platforms, were the archive saving
    another language or region of the page, or losing a page header. All 10 sampled set-asides were broken captures.
  - `stale/wide_daily.py` is the daily watch for these collections (built, not scheduled). A dry run on the snapshot's
    own archive and ToS;DR data (no fetch) reproduced it exactly: 0 events on contrib, genai-contrib and dating (seen
    in the console on 11-15; the run's files were not kept).
    `daily.cmd` runs every daily step in one command for Windows Task Scheduler.
- **Where the decision model would come in: relocation.** When a quote is gone, a curator has to find the passage that
  now states the case, or decline the point. A pre-registered test (`stale/PREREG_relocate.md`, hashed before any
  arm was scored) asks whether Kev-4B finds the curator's own quoted passage among a document's 1,500-character pieces
  better than bge-small and BM25. It uses the points whose quote is still present, so the curator's quote is the
  answer key.
  - **Result (2026-11-12): Kev-4B better than BM25 and bge** (the plan's reading "DECISION MODEL BETTER"; the
    follow-up below found its base family's instruct model as good; `stale/RESULT_relocate.md`). On 200 points in 29 documents,
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
      and the instruct model, asked one question per request, took 1.9-3.1x its time per piece-question here (wall clock on
      the same CPU; one prompt with all the questions was as cheap as Kev, `stale/RESULT_multiq.md`).
    - The decision model was not shown to beat a cross-encoder reranker (bge-reranker-v2-m3): 55% against Kev's 62% in
      part A (no difference shown) and 65% against 75% in part B (Kev better). The reranker is 3.6-5x cheaper than Kev
      (0.39 and 0.98 s per piece-question, against 1.94 and 3.52; wall clock on the same CPU).
    - Memorisation (exploratory): Kev's fine-tuning data has no ToS;DR text. On points whose ToS;DR record postdates
      the base model's first release (some may re-use older quotes: creation dates cluster on single days), Kev still
      leads BM25 by 26 and 35 points, consistent with no memorisation behind the win over retrieval. That cut was
      chosen after the results.
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
    9 min for seven (80 s a point). On part D's documents the cascade took roughly 62% of full Kev's time on average
    (an estimate; with few questions per document the shortlists touch fewer passages and the share is smaller).
  - Where the decision model's cost comes from (measured on an idle CPU, 60 passages of about 1,400 characters,
    `bench/RESULT_cost_curve.md`): Kev takes 7.4 s to read a passage plus 0.93 s per question asked of it (7.0 s and
    0.95 s without five early calls slowed by other work on the machine); the
    instruct model takes 6.3 s per passage and question, and its later questions on a passage cost the same as the
    first (.99), so it reads the passage again for each one (likely because llama.cpp cannot reuse a hybrid recurrent
    model's state for a shared prefix; the effect is measured, the cause is not). So Kev is slower with one question
    per passage (0.83x) and cheaper from two on: 1.4x at 2, 2.4x at 4, 3.4x at 8, 4.7x at 16, toward a limit of 6.8x.
    A curator page asks a few questions of most documents (median 3 on contrib; at most 18 on the 20 platforms, 43 on contrib);
    a tool asking a whole question bank of every document is where it pays, against an instruct model asked one
    question per request. Against the same model asked all of a passage's questions in one prompt it does not pay at
    any question count: 0.87-0.92x (`stale/RESULT_multiq.md`).
  - It covers points whose case is still stated. Whether Kev can tell that a case is no longer stated was tested on
    the 141 stale points: it ranks those points low (AUROC .92), but its flag was right 6 times in 12, under the 75%
    bar, so the page makes no such claim (`stale/RESULT_suggest.md`, provisional).
  - The page's suggestions for the 141 stale points now lead with Kev (`stale/RESULT_suggest.md`, provisional: graded
    by an LLM rater; a person did not check the 60 blind cards, GPT and a Claude Fable 5.2 subagent answered them instead and agreed with
    the grader, kappa .67 and .82; GPT also built a whole second answer key, which puts Kev's first suggestion right for
    78% of the gone points against Opus's 74%).
