#!/usr/bin/env bash
# Replaces run_wide.sh (stopped before it did anything, 2026-11-14 21:30 UTC) after an independent code review:
# the draw now runs only on a complete pull and a successful match, from freshly built files.
# After the first ToS;DR pull: the pull again for the corrected mapping (resumes; retried until complete), match,
# part D's draw (hashed before any model call), the no-model page steps, part D's arms, eval and addendum-1 margin,
# then Kev's suggestions for the wider pages (the cascade only if part D adopted it). Shares Kev with run_resume.sh.
# Usage: bash run_wide2.sh <file whose content shows the first pull finished>
PULL_DONE=$1
VENV=/c/Users/egeha/projects/dedupe-research/.venv/Scripts/python.exe     # sentence-transformers + the reranker cached
COLS="contrib genai-contrib dating user-rights"
cd /c/Users/egeha/projects/policywatch
up() { curl -s -m 15 -o /dev/null -w '%{http_code}' http://127.0.0.1:9995/health | grep -q 200; }
echo "wide2 start $(date -u +%T) UTC; waiting for the first pull"
until grep -q 'pull user-rights exit' "$PULL_DONE" 2>/dev/null; do sleep 60; done
echo "first pull finished $(date -u +%T) UTC"; grep 'pull .* exit' "$PULL_DONE"

# the pull for the corrected mapping, until every mapped folder has its data (3 tries)
for c in $COLS; do
  for try in 1 2 3; do
    py -m stale.wide pull $c >> stale/wide/pull2.log 2>&1; echo "pull2 $c try $try exit $? at $(date -u +%T) UTC"
    if py -m stale.wide complete $c; then break; fi
  done
done
if ! py -m stale.wide complete contrib; then echo "CONTRIB PULL INCOMPLETE at $(date -u +%T) UTC: no draw"; exit 2; fi

# match from scratch (the dry-run files are removed first)
for c in $COLS; do
  rm -rf stale/wide/$c/raw stale/wide/$c/out
  py -m stale.wide match $c > stale/wide/match_$c.log 2>&1; rc=$?; echo "match $c exit $rc at $(date -u +%T) UTC"; tail -1 stale/wide/match_$c.log
  if [ $c = contrib ] && [ $rc -ne 0 ]; then echo "CONTRIB MATCH FAILED: no draw"; exit 2; fi
done

# part D: the draw, hashed before any model call
rm -f stale/out/contrib_docs.json
py -m stale.relocate_d prep > stale/out/contrib_prep.log 2>&1; rc=$?; echo "part D prep exit $rc at $(date -u +%T) UTC"; cat stale/out/contrib_prep.log
if [ $rc -ne 0 ] || [ ! -s stale/out/contrib_docs.json ]; then echo "PART D PREP FAILED: stopping"; exit 2; fi
{ echo "# draw $(date -u +%Y-%m-%dT%H:%M:%SZ) contrib HEAD $(git -C ../decision-serving/data/contrib-versions rev-parse HEAD)"
  sha256sum stale/out/contrib_docs.json stale/wide/contrib/out/points.jsonl stale/wide/contrib/map.json; } >> stale/PREREG_relocate_d.sha256

# no model: passages, ToS;DR's stored copy, BM25 suggestions, pages
for c in $COLS; do
  py -m stale.wide cheap $c > stale/wide/cheap_$c.log 2>&1; echo "cheap $c exit $? at $(date -u +%T) UTC"; tail -2 stale/wide/cheap_$c.log
done

# part D arms, eval, addendum-1 margin
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 $VENV -m stale.relocate_d base > stale/out/contrib_base.log 2>&1; echo "part D base exit $? at $(date -u +%T) UTC"
if ! up; then echo "KEV SERVER DOWN at $(date -u +%T) UTC"; exit 2; fi
py -m stale.relocate_d kev 9995 > stale/out/contrib_kev.log 2>&1; echo "part D kev exit $? at $(date -u +%T) UTC"
py -m stale.relocate_d eval > stale/out/contrib_eval.log 2>&1; echo "part D eval exit $? at $(date -u +%T) UTC"
py -m stale.reloc_margin > stale/out/contrib_margin.log 2>&1; echo "part D margin (addendum 1) exit $? at $(date -u +%T) UTC"; tail -1 stale/out/contrib_margin.log
{ echo "# result $(date -u +%Y-%m-%dT%H:%M:%SZ)"; sha256sum stale/out/contrib_kev.json stale/out/contrib_base.json stale/out/contrib_result.json stale/out/contrib_margin.json; } >> stale/PREREG_relocate_d.sha256
echo "part D done at $(date -u +%T) UTC"; grep -A4 '"reading"' stale/out/contrib_eval.log

# Kev's suggestions and proposed quotes for the wider pages: the reranker-first cascade if part D adopted it (D1),
# otherwise Kev on every piece (stale/cascade.py, stale/wide.py kev)
if py -m stale.cascade adopted contrib; then MODE=cascade; else MODE=full; fi; echo "wide suggestions mode: $MODE"
for c in $COLS; do
  if ! up; then echo "KEV SERVER DOWN at $(date -u +%T) UTC: stopping before $c"; break; fi
  if [ "$MODE" = cascade ]; then
    HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 $VENV -m stale.cascade rerank $c > stale/wide/rerank_$c.log 2>&1; echo "wide rerank $c exit $? at $(date -u +%T) UTC"
    py -m stale.cascade kev $c 9995 > stale/wide/kev_$c.log 2>&1; echo "wide cascade kev $c exit $? at $(date -u +%T) UTC"
  else
    py -m stale.wide kev $c 9995 > stale/wide/kev_$c.log 2>&1; echo "wide kev $c exit $? at $(date -u +%T) UTC"
  fi
  tail -2 stale/wide/kev_$c.log
done
echo "wide all done at $(date -u +%T) UTC"
