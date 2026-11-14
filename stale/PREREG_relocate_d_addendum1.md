# Addendum 1 to part D (`stale/PREREG_relocate_d.md`): a "clear" label for suggestions

Written 2026-11-14 ~21:10 UTC, before part D's draw and before any model scored a contrib point. It adds one secondary
rule. It changes no arm, measure or reading of part D.

## Why
After parts A and B, I looked at how Kev's top score relates to whether its top piece is gold (`stale/reloc_conf.py`,
exploratory). Kev's raw top p(yes) says little (AUROC .63 and .57), but its margin over the second piece says more
(AUROC .70 and .77). I then cut the margin at .30, after seeing the bands, so these figures are not evidence for that
cut:
- part A: 45 of 200 points clear, hit@1 .933 [.861, 1.0]; the rest .529;
- part B: 71 of 202 clear, hit@1 .958 [.908, 1.0]; the rest .641.

Part D's points are held out from that choice.

## Rule (`stale/reloc_margin.py`)
- **margin:** Kev's highest p(yes) over the point's document pieces, minus the second highest.
- **clear:** margin at least .30.
- **LABEL ADOPTED** if all three hold on part D's points:
  - at least 30 points are clear;
  - their hit@1, with ties in expectation, is at least .85;
  - the lower bound of its 95% cluster bootstrap over services is at least .75.

  Otherwise NO LABEL.
- **If adopted.** The curator pages mark a suggestion whose margin is at least .30 as clear: in testing, its top
  passage held the curator's quote about 9 times in 10. The others are marked "close: check the next passages too".
- **If not.** The pages show no confidence label.
- `py -m stale.reloc_margin` runs after part D's eval and appends nothing to part D's result. Its output is
  `stale/out/contrib_margin.json`, hashed with part D's result.

## Prediction
P(LABEL ADOPTED) = 65%. Clear share about 30%, clear hit@1 about .88.
