#!/usr/bin/env bash
# The scanner backfill slices run_missing_wide.sh had left (2026-05-01, paused at 63 of 126 updates on 2026-11-17
# because its large requests starved the page jobs, and 2025-11-11). Answers already given are served from out/cache.sqlite.
# Usage: bash run_backfill_rest.sh [file to wait for] [line it must contain] ...  (pairs; waits for each before starting)
cd /c/Users/egeha/projects/policywatch
PGA=../decision-serving/data/pga-versions; PW="py -m policywatch"
up() { curl -s -m 15 -o /dev/null -w '%{http_code}' http://127.0.0.1:${1:-9995}/health | grep -q 200; }
while [ $# -ge 2 ]; do until grep -qE "$2" "$1" 2>/dev/null; do sleep 60; done; echo "saw '$2' at $(date -u +%T) UTC"; shift 2; done
for since in 2026-05-01 2025-11-11; do
  if ! up; then echo "KEV SERVER DOWN at $(date -u +%T) UTC: stopping before slice $since"; break; fi
  $PW scan --archive $PGA --since $since --out out >> out/scan.log 2>&1; echo "slice since $since exit $? at $(date -u +%T) UTC"
  $PW report --archive $PGA --out out
done
echo "backfill all done at $(date -u +%T) UTC"
