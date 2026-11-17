#!/usr/bin/env bash
# The contrib missing-points run (stale/PLAN_missing_contrib.md) around the scanner backfill:
#   1. the reranker on every cell, now: it needs no model server, so it shares the CPU with the backfill (its timing is
#      therefore not an idle-CPU figure);
#   2. wait for the backfill to finish, then the deferred memo check and the daily watch once (daily.cmd, last run
#      2026-11-15);
#   3. Kev on the reranker's shortlist, alone on the server (the backfill's large requests starve other clients), and
#      the outputs' hashes appended to the plan's hash file.
# Usage: bash run_contrib.sh [file to wait for] [line it must contain] ...  (pairs; step 2 waits for each)
cd /c/Users/egeha/projects/policywatch
PGA=../decision-serving/data/pga-versions; PW="py -m policywatch"
up() { curl -s -m 15 -o /dev/null -w '%{http_code}' http://127.0.0.1:${1:-9995}/health | grep -q 200; }
echo "contrib rerank start $(date -u +%T) UTC"
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 /c/Users/egeha/projects/dedupe-research/.venv/Scripts/python.exe -m stale.missing_contrib rerank >> stale/out/missing_contrib_rerank.log 2>&1
echo "contrib rerank exit $? at $(date -u +%T) UTC"
while [ $# -ge 2 ]; do until grep -qE "$2" "$1" 2>/dev/null; do sleep 60; done; echo "saw '$2' at $(date -u +%T) UTC"; shift 2; done
if up; then
  $PW memocheck --archive $PGA --out out > out/memocheck.log 2>&1; echo "memocheck exit $? at $(date -u +%T) UTC"; tail -16 out/memocheck.log
else echo "KEV SERVER DOWN at $(date -u +%T) UTC: no memo check"; fi
cmd.exe //c daily.cmd; echo "daily exit $? at $(date -u +%T) UTC"; tail -5 stale/live/daily.log
if up; then
  py -m stale.missing_contrib kev >> stale/out/missing_contrib_kev.log 2>&1; echo "contrib kev exit $? at $(date -u +%T) UTC"
  { echo "outputs $(date -u +%FT%TZ)"; sha256sum stale/out/missing_contrib_rerank.json stale/out/missing_contrib_kev.json | sed 's/  / */'; } >> stale/PLAN_missing_contrib.sha256
else echo "KEV SERVER DOWN at $(date -u +%T) UTC: contrib kev not run"; fi
echo "contrib all done at $(date -u +%T) UTC"
