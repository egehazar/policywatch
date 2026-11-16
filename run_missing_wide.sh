#!/usr/bin/env bash
# Missing points on the remaining documents (stale/PLAN_missing_wide.md), then the scanner backfill slices it paused.
# Usage: bash run_missing_wide.sh
cd /c/Users/egeha/projects/policywatch
PGA=../decision-serving/data/pga-versions; PW="py -m policywatch"
up() { curl -s -m 15 -o /dev/null -w '%{http_code}' http://127.0.0.1:${1:-9995}/health | grep -q 200; }
echo "missing_wide start $(date -u +%T) UTC"
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 /c/Users/egeha/projects/dedupe-research/.venv/Scripts/python.exe -m stale.missing_wide rerank >> stale/out/missing_wide_rerank.log 2>&1; echo "missing_wide rerank exit $? at $(date -u +%T) UTC"
if up; then
  py -m stale.missing_wide kev >> stale/out/missing_wide_kev.log 2>&1; echo "missing_wide kev exit $? at $(date -u +%T) UTC"
  py -m stale.missing_wide measures > stale/out/missing_wide_measures.log 2>&1; echo "missing_wide measures exit $? at $(date -u +%T) UTC"
  { echo "# outputs $(date -u +%FT%TZ)"; sha256sum stale/out/missing_wide_rerank.json stale/out/missing_wide_kev.json stale/out/missing_wide_measures.json | sed 's/  / */'; } >> stale/PLAN_missing_wide.sha256
  py -m stale.missing_page > /dev/null 2>&1; echo "missing_wide done $(date -u +%T) UTC"
else echo "KEV SERVER DOWN at $(date -u +%T) UTC: missing_wide kev not run"; fi
for since in 2026-10-01 2026-08-01 2026-05-01 2025-11-11; do
  if ! up; then echo "KEV SERVER DOWN at $(date -u +%T) UTC: stopping before slice $since"; break; fi
  $PW scan --archive $PGA --since $since --out out >> out/scan.log 2>&1; echo "slice since $since exit $? at $(date -u +%T) UTC"
  $PW report --archive $PGA --out out
done
echo "backfill all done at $(date -u +%T) UTC"
