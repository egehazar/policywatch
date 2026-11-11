# Question bank

- `bank_v1_r20.json`: the 70 questions of the frozen r20 test. These are the ToS;DR cases approved on at least 100
  services (case_counts.json, pulled 2026-11-04 from the ToS;DR API). The accuracy numbers apply to these only.
- `bank.json` (v2, 2026-11-11): v1 unchanged and in the same order, plus every "bad" or "blocker" case approved on
  30-99 services (31 cases), in descending order of approvals.
  - Added after the v1 bank turned out to have no question about AI training. Twitch's 2026-08-12 privacy update
    added "using data to develop or deploy our generative AI models"; the Platform Governance Archive wrote it up on
    2026-10-18.
  - The selection is mechanical; no case was hand-picked or reworded.
  - The added questions have no accuracy test yet.
- Template: "Does the text state or clearly imply the following: <case title>?"
