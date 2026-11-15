#!/usr/bin/env bash
# After the wider pages' suggestions (run_wide2.sh): the cost-curve benchmark on an idle CPU (bench/PLAN_cost_curve.md),
# then the scanner backfill (run_backfill.sh, unchanged). Replaces the bare backfill waiter, 2026-11-15 ~07:55 UTC.
# Usage: bash run_after_wide.sh <run_wide2 output file>
W=$1
cd /c/Users/egeha/projects/policywatch
up() { curl -s -m 15 -o /dev/null -w '%{http_code}' http://127.0.0.1:$1/health | grep -q 200; }
echo "after-wide waiter start $(date -u +%T) UTC"
until grep -qE 'wide all done|PREP FAILED|INCOMPLETE|MATCH FAILED|KEV SERVER DOWN' "$W" 2>/dev/null; do sleep 120; done
echo "wide chain ended $(date -u +%T) UTC: $(grep -E 'wide all done|FAILED|INCOMPLETE|DOWN' "$W" | tail -1)"
if up 9995; then
  py -m bench.cost_curve kev 9995 > bench/out/cost_kev.log 2>&1; echo "cost kev exit $? at $(date -u +%T) UTC"
  powershell -NoProfile -File bench/start_qwen.ps1 -Threads 6 -CacheRam 0
  for i in $(seq 1 60); do up 9996 && break; sleep 5; done
  if up 9996; then py -m bench.cost_curve qwen 9996 > bench/out/cost_qwen.log 2>&1; echo "cost qwen exit $? at $(date -u +%T) UTC"
  else echo "QWEN SERVER DID NOT START at $(date -u +%T) UTC"; fi
  powershell -NoProfile -File bench/stop_qwen.ps1
  py -m bench.cost_curve result > bench/out/cost_result.log 2>&1; echo "cost result exit $? at $(date -u +%T) UTC"
  { echo "# result $(date -u +%Y-%m-%dT%H:%M:%SZ)"; sha256sum bench/out/cost_kev.jsonl bench/out/cost_qwen.jsonl bench/out/cost_result.json; } >> bench/PLAN_cost_curve.sha256
  echo "cost curve done at $(date -u +%T) UTC"
else echo "KEV SERVER DOWN at $(date -u +%T) UTC: no cost curve"; fi
bash run_backfill.sh "$W"
