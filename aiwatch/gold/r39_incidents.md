# r39 gold list: AI-training changes to terms and policies (2023-01-01 to 2026-11-19)

Machine-readable copy: `r39_incidents.json` (same 47 rows, same order).

**Counts.** 47 incidents in total: 28 GRANT, 7 PROMISE_NOT and 12 BAN_USERS. In 35 of them the service and document are present in a local OTA clone. 22 are ELIGIBLE: 15 GRANT, 2 PROMISE_NOT and 5 BAN_USERS.

Eligibility rule as given: the document was tracked at least 90 days before the first public report, AND the AI-training text change is visible in an archived version (found by reading `git show` diffs).

Lead time = archive commit date minus first report date. A negative lead means the archive recorded the change after the first report.

## Full table

| # | Service | Document | Dir | First report (date, outlet, type) | Verified | OTA (collection, first version) | >=90d | Change commit (date) | Eligible | Reason / note |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Zoom | Terms of Service | GRANT | 2023-08-06 Stack Diary (press) | yes | contrib, 2021-08-16 | yes | 6cee2e467 (2023-04-01) | **YES** | ML/AI clause new in 2023-04-01 version; lead +127 d |
| 2 | Zoom | Terms of Service | PROMISE_NOT | 2023-08-07 CNBC / Zoom blog (press) | yes | contrib, 2021-08-16 | yes | 99ab2d06d (2023-08-07) | **YES** | same day (OTA 18:49 UTC, after CNBC); Aug 11 rewrite 894baaa7a |
| 3 | Google | Privacy Policy | GRANT | 2023-07-03 9to5Google, credits Gizmodo (press) | yes | contrib, 2020-07-29 | yes | 1ee400fac (2023-06-29) | **YES** | "language models" became "AI models ... Bard"; lead +4 d |
| 4 | X (Twitter) | Privacy Policy | GRANT | 2023-08-31 Fortune (press) | yes | contrib, 2020-07-29 | yes | 193f9b02c (2023-08-23) | **YES** | upcoming version shown on page; flaps 08-24 and 08-30; lead +8 d |
| 5 | X (Twitter) | Terms of Service | BAN_USERS | 2023-09-08 TechCrunch (press) | yes | contrib, 2020-07-29 | yes | e86910a3b (2023-08-23) | **YES** | scraping ban (text does not say AI); lead +16 d |
| 6 | Microsoft | Services Agreement (ToS) | BAN_USERS | 2023-08-11 VentureBeat (press) | yes | contrib, 2020-12-08 | yes | 9f7ff463d (2023-09-30) | **YES** | visible only on effective date; lead -50 d |
| 7 | New York Times | Terms of Service | BAN_USERS | 2023-08-14 Gizmodo, credits Adweek (press) | yes | contrib, 2020-12-08 | yes* | d8394dee2 (2025-05-19) | no | archive gap 2022-07 to 2025-05; clause surfaces 21 months late |
| 8 | Reddit | Data API / Developer Terms | BAN_USERS | 2023-04-18 The Register (press) | yes | pga Developer Terms, 2026-07-14 | no | - | no | dev terms untracked then; user agreement only changed "consent" to "written consent" |
| 9 | Medium | Terms of Service | BAN_USERS | 2023-09-28 Medium blog (company) | no | not tracked | - | - | no | not in OTA |
| 10 | Tumblr / WordPress.com | settings / privacy | GRANT | 2024-02-27 404 Media (press) | yes | contrib, 2013-06-19 | yes | - | no | opt-out setting and blog; no policy text change |
| 11 | Reddit | Public Content Policy | BAN_USERS | 2024-05-09 TechCrunch (press) | yes | not tracked | - | - | no | separate document, untracked |
| 12 | Slack | Privacy Principles | GRANT | 2024-05-17 TechCrunch (press) | yes | not tracked | - | - | no | not in OTA |
| 13 | Slack | Privacy Principles | PROMISE_NOT | 2024-05-19 StackAware (press) | yes | not tracked | - | - | no | not in OTA |
| 14 | Meta (Facebook, EU) | Privacy Policy (fr-fr) | GRANT | 2024-05-30 Euronews (press) | yes | contrib, 2020-07-29 | yes | 16114b44f (2024-05-21) | **YES** | banner a day before Meta's notices; purpose row 2024-06-26 (de5b690ab); lead +9 d |
| 15 | Adobe | General Terms of Use | GRANT | 2024-06-06 Android Authority (press) | yes | not tracked | - | - | no | perceived grant; not in OTA |
| 16 | Adobe | General Terms of Use | PROMISE_NOT | 2024-06-10 Adobe blog (company) | yes | not tracked | - | - | no | not in OTA |
| 17 | Figma | AI terms / settings | GRANT | 2024-06-26 Figma (company) | no | not tracked | - | - | no | not in OTA; no dated press found |
| 18 | X (Twitter) | settings (Grok) | GRANT | 2024-07-26 TechCrunch / MacRumors (press) | no | pga, 2024-02-21 | yes | - | no | default-on setting, no document change |
| 19 | Microsoft (consumer Copilot) | Copilot Privacy Policy | GRANT | 2024-08-16 Microsoft blog (company) | yes | genai, 2024-02-09 | yes | 547db9af (2025-02-05) | no | text surfaces only in a selector-upgrade commit 6 months later |
| 20 | LinkedIn | Privacy Policy | GRANT | 2024-09-18 404 Media (press) | yes | pga, 2022-07-11 | yes | 0bb97299 (2024-09-19) | **YES** | lead -1 d (training began before the policy changed) |
| 21 | Meta (UK notice) | Privacy Policy (fr-fr) | GRANT | 2024-09-13 TechCrunch (press) | yes | contrib, 2020-07-29 | yes | 7775bb22d (2024-09-19) | **YES** | CAUTION: UK-style banner on fr-fr page; lead -6 d |
| 22 | X (Twitter) | Terms of Service | GRANT | 2024-10-16 X Privacy Center (company) | no | pga, 2024-02-21 | yes | 190ca8ff (2024-10-17) | **YES** | AI-training licence; verified press: Social Media Today 10-17 |
| 23 | X (Twitter) | Terms of Service | BAN_USERS | 2024-10-17 TechCrunch (press) | yes | pga, 2024-02-21 | yes | 190ca8ff (2024-10-17) | **YES** | liquidated damages for scraping; AI link is press framing (peripheral) |
| 24 | X (Twitter) | Privacy Policy | GRANT | 2024-10-17 TechCrunch (press) | yes | pga, 2024-02-21 | yes | 32b88003 (2024-10-17) | **YES** | third-party collaborators may train AI; OTA 00:36 UTC, about 21 h before TechCrunch |
| 25 | Bandcamp | Terms of Service | PROMISE_NOT | 2024-11-11 in-document change log (company) | yes | contrib, 2022-11-01 | yes | 38129e12e (2024-11-12) | **YES** | CIRCULAR: no outside report found |
| 26 | Strava | API Agreement | BAN_USERS | 2024-11-19 DC Rainmaker (press) | yes | not tracked | - | - | no | not in OTA |
| 27 | Firefox (Mozilla) | Terms of Use | GRANT | 2025-02-28 TechCrunch (press) | yes | contrib, 2025-02-28 | no | 2b4fb20ca (2025-02-28) | no | new document; text never says AI (perceived) |
| 28 | Pinterest | Privacy Policy | GRANT | 2025-03-10 PetaPixel (press) | no | contrib, 2020-07-29 | yes | d11795837 (2025-04-30) | **YES** | generic banner 03-06; AI text only on effective date; lead -51 d |
| 29 | Meta (EU 2025) | Privacy Policy (fr-fr) | GRANT | 2025-04-14 Fortune/AP (press) | yes | contrib, 2020-07-29 | yes | - | no | notification campaign only; text already present since 2024 |
| 30 | Meta (Ray-Ban glasses) | AI glasses privacy notice | GRANT | 2025-04-30 TechCrunch (press) | yes | not tracked | - | - | no | not in OTA |
| 31 | SoundCloud | Terms of Service | GRANT | 2025-05-09 TechCrunch (press) | yes | contrib, 2025-05-27 | no | - | no | tracking began after the report; change was Feb 2024 |
| 32 | SoundCloud | Terms of Service | PROMISE_NOT | 2025-05-14 TechCrunch (press) | yes | contrib, 2025-05-27 | no | 032f85fba (2025-09-10) | no | tracking began 13 d after the report |
| 33 | Slack (Salesforce) | API Terms | BAN_USERS | 2025-05-29 Salesforce statement (company) | no | not tracked | - | - | no | not in OTA |
| 34 | X (Twitter) | Developer Terms | BAN_USERS | 2025-06-05 TechCrunch (press) | yes | pga, 2024-02-21 | yes | 5453af28 (2025-06-04) | **YES** | foundation/frontier-model training ban; lead +1 d |
| 35 | Mastodon | Terms of Service | BAN_USERS | 2025-06-18 The Register (press) | yes | pga, 2026-09-17 | no | - | no | tracked only from 2026 |
| 36 | Slack | Privacy Principles | PROMISE_NOT | 2025-07-04 StackAware (press) | yes | not tracked | - | - | no | promise reworded and narrowed; not in OTA |
| 37 | WeTransfer | Terms of Service | GRANT | 2025-07-16 The Next Web (press) | yes | contrib, 2025-07-17 | no | - | no | ML clause gone before first record |
| 38 | WeTransfer | Terms of Service | PROMISE_NOT | 2025-07-15 WeTransfer statement (company) | yes | contrib, 2025-07-17 | no | b349194fb (2025-07-23) | no | tracking began 2 d after the statement |
| 39 | Google (Gemini Apps) | Gemini privacy hub / settings | GRANT | 2025-08-13 PCWorld (press) | yes | not tracked | - | - | no | Gemini privacy notice untracked |
| 40 | Claude.ai (Anthropic) | Privacy Policy (+ToS) | GRANT | 2025-08-28 Anthropic (company) | yes | genai, 2025-08-01 | no | e59bf71c (2025-08-29) | no | tracked only 27 d before the report |
| 41 | LinkedIn | Privacy Policy (EU-facing) | GRANT | 2025-09-18 Social Media Today (press) | yes | pga, 2022-07-11 | yes | 326007fd (2025-09-18) | **YES** | same day; full table 2025-11-04 (bc7d59e9) |
| 42 | Meta (Instagram/Facebook) | Privacy Policy | GRANT | 2025-10-01 Meta newsroom (company) | yes | contrib, 2020-07-29 | yes | 9dc2b5be3 (2025-10-07) | **YES** | ads-first change; "Developing and improving AI at Meta" text 2025-12-17 |
| 43 | X (Twitter) | Terms of Service | GRANT | 2025-12-17 CryptoSlate (press) | yes | pga, 2024-02-21 | yes | 4217afb7 (2025-12-17) | **YES** | Content now includes AI prompts and outputs; OTA about 10 h before press |
| 44 | Starlink | Privacy Policy | GRANT | 2026-01-16 OTA memo (watchdog) | yes | contrib, 2025-04-09 | yes | 8010e734a (2026-01-16) | **YES** | CIRCULAR first report; Reuters 2026-01-30 |
| 45 | Telegram | Developer Terms + ToS | BAN_USERS | 2026-02-03 OTA memo (watchdog) | yes | contrib, 2020-12-09 | yes | ace242672 (2026-02-03) | **YES** | CIRCULAR first report; no press found |
| 46 | Atlassian | Privacy Policy | GRANT | 2026-04-18 The Register (press) | yes | contrib, 2021-08-03 | yes | 25879f6e5 (2025-09-06) | **YES** | two candidate commits; 052858628 (2026-04-17) adds data-contribution wording |
| 47 | Pinterest | Privacy Policy | GRANT | 2026-11-08 PPC Land (press) | yes | contrib, 2020-07-29 | yes | 6c204569e (2026-11-13) | **YES** | generic banner 09-02; AI text on effective date; lead -5 d |

\* NYT: the document is nominally tracked from 2020, but no version was recorded between 2022-07-25 and 2025-05-19. It is marked not eligible. A scorer that accepts any visible version would count it as tracked, visible and detected late.

## Eligible list with the archived sentence

1. **Zoom ToS, GRANT.** Commit 6cee2e467, 2023-04-01: "machine learning or artificial intelligence (including for the purposes of training and tuning of algorithms and models)"
2. **Zoom ToS, PROMISE_NOT.** Commit 99ab2d06d, 2023-08-07: "Notwithstanding the above, Zoom will not use audio, video or chat Customer Content to train our artificial intelligence models without your consent."
3. **Google Privacy Policy, GRANT.** Commit 1ee400fac, 2023-06-29: "we may collect information that's publicly available online or from other public sources to help train Google's AI models"
4. **X Privacy Policy 2023, GRANT.** Commit 193f9b02c, 2023-08-23: "We may use the information we collect and publicly available information to help train our machine learning or artificial intelligence models"
5. **X ToS 2023, BAN_USERS.** Commit e86910a3b, 2023-08-23: "NOTE: crawling or scraping the Services in any form, for any purpose without our prior written consent is expressly prohibited"
6. **Microsoft Services Agreement, BAN_USERS.** Commit 9f7ff463d, 2023-09-30: "You may not use the AI services, or data from the AI services, to create, train or improve (directly or indirectly) any other AI service."
7. **Meta EU Privacy Policy 2024, GRANT.** Commit 16114b44f, 2024-05-21: "Nous mettons à jour la Politique de confidentialité en incluant la manière dont nous utilisons vos informations pour l'IA chez Meta"
8. **LinkedIn Privacy Policy 2024, GRANT.** Commit 0bb97299, 2024-09-19: "We may use your personal data to improve, develop, and provide products and Services, develop and train artificial intelligence (AI) models"
9. **Meta UK notice, GRANT.** Commit 7775bb22d, 2024-09-19: "Nous ferons cela afin de développer et d'améliorer les modèles d'IA générative destinés aux fonctionnalités et expériences de l'IA de Meta."
10. **X ToS 2024, GRANT.** Commit 190ca8ff, 2024-10-17: "including, for example, for use with and training of our machine learning and artificial intelligence models, whether generative or another type"
11. **X ToS 2024 liquidated damages, BAN_USERS.** Commit 190ca8ff, 2024-10-17: "you will be jointly and severally liable to us for liquidated damages as follows for requesting, viewing, or accessing more than 1,000,000 posts"
12. **X Privacy Policy 2024, GRANT.** Commit 32b88003, 2024-10-17: "If you do not opt out, in some instances the recipients of the information may use it ... to train their artificial intelligence models"
13. **Bandcamp ToS, PROMISE_NOT.** Commit 38129e12e, 2024-11-12: "Bandcamp will not use, and will not permit others to use, any Artist's Music to train models to generate sound recordings"
14. **Pinterest Privacy Policy 2025, GRANT.** Commit d11795837, 2025-04-30: "using information to train, develop and improve our technology such as our machine learning models, regardless of when Pins were posted"
15. **X Developer Terms, BAN_USERS.** Commit 5453af28, 2025-06-04: "use the X API or X Content to fine-tune or train a foundation or frontier model"
16. **LinkedIn Privacy Policy 2025, GRANT.** Commit 326007fd, 2025-09-18: "we are updating this notice to provide information about our reliance on Legitimate Interests as the legal basis for training content-generating AI models"
17. **Meta Instagram Privacy Policy, GRANT.** Commit 9dc2b5be3, 2025-10-07: "We'll start using interactions with AIs to personalize experiences and ads. This update goes into effect on December 16, 2025."
18. **X ToS Dec 2025, GRANT.** Commit 4217afb7, 2025-12-17: "including any inputs, prompts, outputs, and/or information obtained or created through the Services"
19. **Starlink Privacy Policy, GRANT.** Commit 8010e734a, 2026-01-16: "To train our machine learning or artificial intelligence models for the purposes outlined in this policy;"
20. **Telegram Developer Terms, BAN_USERS.** Commit ace242672, 2026-02-03: "you are prohibited from using, accessing or aggregating data obtained from the Telegram platform to train, fine-tune or otherwise engage in the development"
21. **Atlassian Privacy Policy, GRANT.** Commit 25879f6e5, 2025-09-06: "to repair and improve the Services, including for development, training, or fine-tuning of machine learning and artificial intelligence models"
22. **Pinterest Privacy Policy 2026, GRANT.** Commit 6c204569e, 2026-11-13: "to train, develop and improve our technology such as our machine learning models and our generative artificial intelligence models"

## Flags the scorer must settle before scoring

- **Circular first reports.** The first report for Starlink (#44) and Telegram (#45) is an Open Terms Archive memo, which is derived from the same archive. Bandcamp's (#25) is the change log inside the document itself. These three have zero lead time by construction. Starlink's first independent press report is Reuters on 2026-01-30. For Telegram and Bandcamp no outside report was found.
- **Peripheral AI link.** X's 2023 scraping ban (#5) and the 2024 liquidated-damages clause (#23) never mention AI. Only the press tied them to AI. Meta's December 2025 change (#42) was reported mainly as an ads change. X's December 2025 change (#43) widens a definition, while the training sentence itself is unchanged.
- **Two candidate commits for Atlassian (#46).** Commit 2025-09-06 is the first AI-training grant in the policy, 7 months before press. Commit 2026-04-17 is the data-contribution wording, 1 day before press. Pre-register which one the scorer uses.
- **Jurisdiction (#21).** The UK-style banner appears on the French-language Facebook page.
- **Flapping records.** X pages show both the current and the upcoming version, so the X records flip back and forth: 2023-08-23 to 08-30, and 2024-10/11. The first appearance is what is recorded here.
- **Language.** contrib Facebook/Privacy Policy is French, so English regexes miss it. Search for "intelligence artificielle", "IA chez Meta" and "IA générative".
- **Effective date versus announcement.** Several sites publish the upcoming text on an untracked preview page: Pinterest, Microsoft, and Meta (EU, 2024). In those cases the archive only shows the text on the effective date, after the press.

## Methods

**Incident sources searched (human-written only, no model judgments of documents).**
- The Visualping vendor policy-changes timeline.
- Open Terms Archive: the January 16, 2026 publication "Trends in AI data collection by Big Tech and regulatory responses", and the full memo list, read from the OpenTermsArchive/opentermsarchive.org GitHub repository `content/memos`, with the AI-related memos read in full.
- Web searches across TechCrunch, The Verge, 404 Media, The Register, Ars Technica, Gizmodo, Wired, Bloomberg, Stack Diary, PetaPixel, Social Media Today and others.
- Company blogs from Zoom, Adobe, Anthropic, Meta, Microsoft, Medium and Bandcamp.

The candidate list given in the brief was checked, not trusted. The task's Bandcamp example matches a Nov 2024 terms promise found in the archive; no outside report of it was found.

**Checking each first-report date.** Dates were checked by opening the source wherever possible. `date_verified` is false where the page could not be opened (403 errors or redirects) and the date rests on search snippets or a URL. That applies to 6 rows: X's Oct 16, 2024 privacy blog, PetaPixel (Pinterest), the Medium blog, the Figma announcement, X's Grok setting reports, and the Slack API statement. Gizmodo's July 3, 2023 Google story, Adweek's NYT story and Neowin's Microsoft story could not be opened or are undated, so a dated article that credits them is used instead.

**OTA checks.** For each service and document, the work was done with read-only `git log`, `git log -G<regex>` and `git show` on the four local clones: contrib, genai-contrib, pga and user-rights. Each candidate diff was read to confirm that the AI sentence is new in that commit and absent from the prior version. Commits labelled "Apply technical or declaration upgrade" or "Refilter" were not accepted as document changes.

**Not included, and why.**
- **Dropbox, December 2023.** The setting sent data to OpenAI for features. It was not about training and not a document change.
- **YouTube, December 2024.** A creator opt-in setting for third-party training, not a document change.
- **Gmail "smart features", November 2025.** A rumour that was later corrected; there was no policy change.
- **CapCut, June 2025.** The AI-training claim comes only from commentary; the licence text does not show it.
- **Bandcamp, January 2026.** The ban covers AI-generated uploads, not training.
- **TikTok US privacy policy, January 2026.** It collects AI interactions but has no training clause.
- **Apple App Review Guidelines, November 2025.** About sharing data with third-party AI, not training.
- **Archive-only AI changes with no outside report found.** Quora ToS July 2023 (pga c24c90dc, a ban on AI training), Stack Overflow Acceptable Use Policy November 2025 (d195b50e0, a generative-AI scraping ban), and Spotify privacy policy May 2025 (ML training purpose). These could be added if archive-only events are wanted as negatives or controls.

**Could not verify.** The exact first-report time for most same-day cases; the publication timestamps of OTA memos beyond their RSS date; and whether earlier press than that listed exists for WeTransfer (BBC/Guardian, July 15–16), Microsoft (Neowin) and Atlassian (Atlassian's own announcement). Lead-time signs are fragile when the absolute lead is 1 day or less (#2, #20, #24, #34, #41, #43) and should be scored with a stated tie rule.
