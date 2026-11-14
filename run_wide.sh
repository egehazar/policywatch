#!/usr/bin/env bash
# After the ToS;DR pull for the wider collections (stale/wide.py pull): match, part D's draw (hashed before any model
# call), the no-model page steps, part D's arms and eval (stale/PREREG_relocate_d.md), then Kev's suggestions and
# proposed quotes for the wider pages. Shares Kev's server with run_resume.sh's deferred steps.
# Usage: bash run_wide.sh <file whose content shows the pull finished>
PULL_DONE=$1
VENV=/c/Users/egeha/projects/dedupe-research/.venv/Scripts/python.exe     # sentence-transformers + the reranker cached
cd /c/Users/egeha/projects/policywatch
up() { curl -s -m 15 -o /dev/null -w '%{http_code}' http://127.0.0.1:9995/health | grep -q 200; }
echo "wide start $(date -u +%T) UTC; waiting for the pull"
until grep -q 'pull user-rights exit' "$PULL_DONE" 2>/dev/null; do sleep 60; done
echo "pull finished $(date -u +%T) UTC"; grep 'pull .* exit' "$PULL_DONE"

for c in contrib genai-contrib dating user-rights; do
  py -m stale.wide match $c > stale/wide/match_$c.log 2>&1; echo "match $c exit $? at $(date -u +%T) UTC"; tail -1 stale/wide/match_$c.log
done

# part D: the draw, hashed before any model call
py -m stale.relocate_d prep > stale/out/contrib_prep.log 2>&1; echo "part D prep exit $? at $(date -u +%T) UTC"; cat stale/out/contrib_prep.log
{ echo "# draw $(date -u +%Y-%m-%dT%H:%M:%SZ) contrib HEAD $(git -C ../decision-serving/data/contrib-versions rev-parse HEAD)"
  sha256sum stale/out/contrib_docs.json stale/wide/contrib/out/points.jsonl stale/wide/contrib/map.json; } >> stale/PREREG_relocate_d.sha256

# no model: passages, ToS;DR's stored copy, BM25 suggestions, pages
for c in contrib genai-contrib dating user-rights; do
  py -m stale.wide cheap $c > stale/wide/cheap_$c.log 2>&1; echo "cheap $c exit $? at $(date -u +%T) UTC"; tail -2 stale/wide/cheap_$c.log
done

# part D arms and eval
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 $VENV -m stale.relocate_d base > stale/out/contrib_base.log 2>&1; echo "part D base exit $? at $(date -u +%T) UTC"
if ! up; then echo "KEV SERVER DOWN at $(date -u +%T) UTC"; exit 2; fi
py -m stale.relocate_d kev 9995 > stale/out/contrib_kev.log 2>&1; echo "part D kev exit $? at $(date -u +%T) UTC"
py -m stale.relocate_d eval > stale/out/contrib_eval.log 2>&1; echo "part D eval exit $? at $(date -u +%T) UTC"
py -m stale.reloc_margin > stale/out/contrib_margin.log 2>&1; echo "part D margin (addendum 1) exit $? at $(date -u +%T) UTC"; tail -1 stale/out/contrib_margin.log
{ echo "# result $(date -u +%Y-%m-%dT%H:%M:%SZ)"; sha256sum stale/out/contrib_kev.json stale/out/contrib_base.json stale/out/contrib_result.json stale/out/contrib_margin.json; } >> stale/PREREG_relocate_d.sha256
echo "part D done at $(date -u +%T) UTC"; grep -A4 '"reading"' stale/out/contrib_eval.log

# Kev's suggestions and proposed quotes for the wider pages (full Kev: the cascade is adopted only by a later change)
for c in contrib genai-contrib dating user-rights; do
  if ! up; then echo "KEV SERVER DOWN at $(date -u +%T) UTC: stopping before $c"; break; fi
  py -m stale.wide kev $c 9995 > stale/wide/kev_$c.log 2>&1; echo "wide kev $c exit $? at $(date -u +%T) UTC"; tail -2 stale/wide/kev_$c.log
done
echo "wide all done at $(date -u +%T) UTC"
