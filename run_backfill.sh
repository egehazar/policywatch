#!/usr/bin/env bash
# The backfill slices of run_resume.sh, stopped at 01:20 UTC 2026-11-15 (one update into the first slice) so part D's
# Kev arm gets the CPU; restarted once run_wide2.sh prints "wide all done". `scan` skips updates already scanned.
# Usage: bash run_backfill.sh <run_wide2 output file>
W=$1; PGA=../decision-serving/data/pga-versions; PW="py -m policywatch"
cd /c/Users/egeha/projects/policywatch
up() { curl -s -m 15 -o /dev/null -w '%{http_code}' http://127.0.0.1:9995/health | grep -q 200; }
echo "backfill waiter start $(date -u +%T) UTC"
until grep -qE 'wide all done|PREP FAILED|INCOMPLETE|MATCH FAILED|KEV SERVER DOWN' "$W" 2>/dev/null; do sleep 120; done
echo "wide chain ended $(date -u +%T) UTC: $(grep -E 'wide all done|FAILED|INCOMPLETE|DOWN' "$W" | tail -1)"
# Missing points pilot first (stale/PREREG_missing.md, added 11:05 UTC 2026-11-15): Kev, then the reranker, then the cards.
if up; then
  echo "missing pilot start $(date -u +%T) UTC"
  py -m stale.missing kev >> stale/out/missing_kev.log 2>&1; echo "missing kev exit $? at $(date -u +%T) UTC"
  py -m stale.missing rerank >> stale/out/missing_rerank.log 2>&1; echo "missing rerank exit $? at $(date -u +%T) UTC"
  py -m stale.missing measures > stale/out/missing_measures.log 2>&1; echo "missing measures exit $? at $(date -u +%T) UTC"
  echo "missing pilot done $(date -u +%T) UTC"
else echo "KEV SERVER DOWN at $(date -u +%T) UTC: missing pilot not run"; fi
for since in 2026-10-01 2026-08-01 2026-05-01 2025-11-11; do
  if ! up; then echo "KEV SERVER DOWN at $(date -u +%T) UTC: stopping before slice $since"; break; fi
  $PW scan --archive $PGA --since $since --out out >> out/scan.log 2>&1; echo "slice since $since exit $? at $(date -u +%T) UTC"
  $PW report --archive $PGA --out out
done
echo "backfill all done at $(date -u +%T) UTC"
