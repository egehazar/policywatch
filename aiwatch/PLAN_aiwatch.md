# Plan: AI-training clause watch, a 2-day kill test (r39)

Written 2026-11-19 ~15:55 UTC, before any Kev score of this test. Hashed with its code (`aiwatch/PLAN_aiwatch.sha256`)
before scoring. The incident list (`decision-serving/notes/r39_incidents.json`) is hashed into the same file before
the result step. It was compiled by a separate agent from human-written sources; that agent never sees a model
score. Context: `decision-serving/notes/r39_converged.md` (Claude, Fable 5.2 and GPT-6 agreed this runs in
parallel with publishing and outreach, capped at 2 days, and stops if keywords tie or coverage is thin).

## Question
Replaying Open Terms Archive's history, would a monitor asking one question ("does this edit newly let the company
train AI on users' content or data?") have flagged the publicly reported AI-training clause changes, ahead of the
press, at an alert volume a person could read? And does a model do that better than a careful keyword rule?

## Data
- **Archive:** the four local OTA clones (contrib, genai-contrib, pga, user-rights). Every service's Terms of Service
  and Privacy Policy, plus any other document type named by an eligible incident.
- **Window:** 2023-01-01 to 2026-11-19.
- **Changes counted:**
  - Commits recorded as service changes ("Record new changes", or the older "Update ...").
  - Capture noise is skipped (cut-off captures and reverts, policywatch.archive, unchanged), and a cut-off parent is
    replaced by its last clean version.
- **Units:** changed blocks (policywatch.diffing). Both arms see only blocks whose changed paragraphs contain AI
  vocabulary (BROAD in backtest.py), so the test is about judging the change, not finding AI words.

## Gold (human sources only)
- Incidents 2023-2026 where a terms or privacy change about AI training was reported by press, the company, a
  watchdog or a human-written timeline.
- Each incident has:
  - a direction: GRANT, PROMISE_NOT or BAN_USERS;
  - its first public report date;
  - the archived commit where the text change appears, found by reading the diffs.
- **Eligible** if the document was tracked at least 90 days before the first report and the change is visible in an
  archived version (Fable's rule).

## Arms
- **REGEX:** a sentence is a "grant sentence" if it has a training word and an AI or model word, with no negation
  and no ban on users. An update alerts if any block's new side has more grant sentences than its old side.
  Checked on six hand-written cases before this plan (Zoom grant and promise, two bans, X grant, unrelated): all
  right.
- **KEV:**
  - Kev-4B on the deployed server (port 9995, 4 slots, build-fix). Kev rather than Qwen because it is already
    running and, in policywatch, it ties its base model.
  - Three yes/no questions (grant, promise not to train, ban users from training) on the old and new block text.
  - An update alerts if p(grant) rises by at least **0.2**, the cut from the r19 meaning-diff test, fixed before
    this test.

## Measures
- **Recall:** eligible GRANT incidents whose change commit the arm alerts on.
- **Lead:** first report date minus change date, for flagged incidents.
- **Alert volume:** alerting updates over the window (updates whose AI blocks are identical, as in shared Google
  policies, count once), and per month.
- **Matched operating point:** the highest Kev cut at which Kev's recall reaches the regex arm's, and Kev's alert
  volume there.
- **Direction:** on eligible PROMISE_NOT and BAN_USERS incidents, Kev is right if it raises no grant alert and the
  matching question rose most. Regex is right if it raises no grant alert.

## Readings (fixed now; `result()` computes them)
- **"too thin: stopped"** if fewer than 6 eligible GRANT incidents.
- **"PASS"** if all hold (Fable's bars):
  - Kev at 0.2 flags at least 70% of eligible GRANT incidents;
  - at least 3 flagged incidents have a lead of 7 days or more;
  - at the matched operating point, Kev's alert volume is at most half the regex arm's.
- **"keyword ties: stopped"** if regex recall is at least Kev's and its alert volume is at most twice Kev's.
- **Otherwise "FAIL".**
- **Direction is reported, not read.** There will be too few non-grant incidents for a bar.

After a PASS: the replay page, a daily ledger and the write-up (days 3-8 in r39_converged). After any other reading:
stop. Publishing and outreach go on as agreed.

## Predictions (mine, written before any score)
- Eligible GRANT incidents: 4-8. "too thin" 45%.
- If not thin:
  - Kev recall at 0.2 about 75%; regex about 70%;
  - lead of 7 days or more for 2 incidents (Zoom about 4 months; Twitter's privacy policy about 9 days if its dates
    hold; the rest near 0 or negative).
- "PASS" 15%. Most likely failure: the lead bar, then keyword ties.

## What this cannot show
- **Precision.** Alerts are counted, not judged: no rater reads them. Fewer alerts is a workload claim, not proof the
  extra alerts were wrong (GPT's round-2 point).
- **Topic.** It was picked in hindsight, after the famous incidents. Only a forward ledger answers that.
- **Coverage.** OTA tracks mostly consumer services; Adobe, Slack and Dropbox are not in these clones.

## Addendum 1, 2026-11-19 ~16:12 UTC: the gold list arrived; rulings fixed before any Kev score
- **Gold:** `decision-serving/notes/r39_incidents.json` and `.md`, compiled by a separate agent from human sources.
  47 incidents, 22 eligible (15 GRANT, 5 BAN_USERS, 2 PROMISE_NOT). 41 of 47 report dates opened and verified;
  6 rest on search snippets (pages returned 403).
- **Rulings (in backtest.py: EXTRA_DOCS, OVERRIDE, EXCLUDE, NO_AI_WORDS):**
  1. **Matching:** an incident is flagged if the arm alerts on the update in its OTA collection whose commit
     starts with the gold commit. Service names in the gold are for people and are not used.
  2. **Atlassian (#45):** scored on 052858628 (2026-04-17), the change the press reported (lead 1 day), not on
     25879f6e5 (2025-09-06, the first training sentence, unreported, lead 7 months). This is the harder choice for
     PASS. Whether an arm alerts on 25879f6e5 is reported as info only.
  3. **Meta Instagram/Facebook, 2025-10-07 (#41): excluded.** The press covered it as an ads change; the training
     text arrived 2025-12-17.
  4. **The two Meta pages tracked in French (#13 EU, #20 UK notice): kept.** Both arms use English vocabulary; a
     miss counts as a miss.
  5. **Leads** use the first human report recorded, including OTA's own memos (Starlink), not the later press. This
     is conservative.
  6. **Document types:** Terms of Service, Privacy Policy and Developer Terms (the only other eligible type).
  7. **Direction tallies** leave out the two X anti-scraping clauses (#4, #22), which contain no AI words.
- **After rulings:** 14 eligible GRANT incidents, so "too thin" does not apply.
- **Seen from the gold alone, before any score.** The leads (report minus change, in days) are:

  | Incident | Lead |
  |---|---:|
  | Zoom | +127 |
  | Google | +4 |
  | X privacy 2023 | +8 |
  | Meta EU (French) | +9 |
  | LinkedIn 2024 | -1 |
  | Meta UK | -6 |
  | X terms 2024 | -1 |
  | X privacy 2024 | 0 |
  | Pinterest 2025 | -51 |
  | LinkedIn 2025 | 0 |
  | X Dec 2025 | 0 |
  | Starlink | 0 |
  | Atlassian | +1 |
  | Pinterest 2026 | +5 |

  - Only 3 incidents can reach a lead of 7 days, so the lead bar needs all three flagged, including the French
    Meta EU page.
  - My PASS estimate drops from 15% to 3%.
  - The bars are not changed. The run still measures recall and alert volume, model against keywords, as fixed.
- **What the gold already shows:** in this archive the clause is usually recorded the same day as the press or later
  (companies announce, then publish). The "months before the press" moment exists once, for Zoom. Fable's round-1
  "biggest risk" (lead time mostly zero) holds before any model runs.
