#!/usr/bin/env bash
# After the scanner backfill: the deferred memo check, the daily watch once (daily.cmd, last run 2026-11-15), then the
# contrib missing-points run (stale/PLAN_missing_contrib.md): the reranker on every cell, then Kev on its shortlist, and
# the outputs' hashes appended to the plan's hash file. One job at a time on the CPU.
# Usage: bash run_contrib.sh [file to wait for] [line it must contain] ...  (pairs; waits for each before starting)
cd /c/Users/egeha/projects/policywatch
PGA=../decision-serving/data/pga-versions; PW="py -m policywatch"
up() { curl -s -m 15 -o /dev/null -w '%{http_code}' http://127.0.0.1:${1:-9995}/health | grep -q 200; }
while [ $# -ge 2 ]; do until grep -qE "$2" "$1" 2>/dev/null; do sleep 60; done; echo "saw '$2' at $(date -u +%T) UTC"; shift 2; done
if up; then
  $PW memocheck --archive $PGA --out out > out/memocheck.log 2>&1; echo "memocheck exit $? at $(date -u +%T) UTC"; tail -16 out/memocheck.log
else echo "KEV SERVER DOWN at $(date -u +%T) UTC: no memo check"; fi
cmd.exe //c daily.cmd; echo "daily exit $? at $(date -u +%T) UTC"; tail -5 stale/live/daily.log
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 /c/Users/egeha/projects/dedupe-research/.venv/Scripts/python.exe -m stale.missing_contrib rerank >> stale/out/missing_contrib_rerank.log 2>&1
echo "contrib rerank exit $? at $(date -u +%T) UTC"
if up; then
  py -m stale.missing_contrib kev >> stale/out/missing_contrib_kev.log 2>&1; echo "contrib kev exit $? at $(date -u +%T) UTC"
  { echo "outputs $(date -u +%FT%TZ)"; sha256sum stale/out/missing_contrib_rerank.json stale/out/missing_contrib_kev.json | sed 's/  / */'; } >> stale/PLAN_missing_contrib.sha256
else echo "KEV SERVER DOWN at $(date -u +%T) UTC: contrib kev not run"; fi
echo "contrib all done at $(date -u +%T) UTC"
