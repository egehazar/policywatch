#!/usr/bin/env bash
# Reordered 11-12 10:40 UTC (run_night.sh stalled in the memo check: two copies of it had shared the CPU for 10 h).
#   0. wait until the Kev server has no request in flight (the killed memo check may leave tasks behind)
#   1. decision model vs ordinary LLM benchmark (eval/PREREG_kev_vs_llm.md), each server alone on the CPU
#   2. memo check (resumable; scored pieces are cached), report
#   3. backfill ToS/Privacy updates newest-first in slices, rebuilding the site after each
# Steps and commands are the ones in run_night.sh; only the order changed.
F=/c/Users/egeha/projects/decision-serving/play/reviewq/out
PGA=../decision-serving/data/pga-versions
PW="py -m policywatch"
cd /c/Users/egeha/projects/policywatch

busy() { curl -s -m 10 http://127.0.0.1:9995/slots | py -c "import sys,json; print(sum(1 for s in json.load(sys.stdin) if s.get('is_processing')))"; }
idle=0
while [ $idle -lt 3 ]; do
  if [ "$(busy)" = "0" ]; then idle=$((idle+1)); else idle=0; fi
  sleep 20
done
echo "kev server idle at $(date -u +%T) UTC"
$PW report --archive $PGA --out out

# 1. decision model vs ordinary LLM (eval/PREREG_kev_vs_llm.md, frozen 22:38:03Z)
powershell -NoProfile -ExecutionPolicy Bypass -File bench/start_qwen.ps1 -Threads 6 > /dev/null 2>&1
echo "qwen server PID $(cat bench/qwen.pid) started at $(date -u +%T) UTC"
for i in $(seq 1 60); do curl -s -m 5 -o /dev/null -w '%{http_code}' http://127.0.0.1:9996/health | grep -q 200 && break; sleep 2; done
py -m bench.kev_vs_llm run-llm 9996 $F >> bench/run.log 2>&1; echo "llm arms exit $? at $(date -u +%T) UTC"
powershell -NoProfile -ExecutionPolicy Bypass -File bench/stop_qwen.ps1
py -m bench.kev_vs_llm time-kev 9995 $F >> bench/run.log 2>&1; echo "kev timing exit $? at $(date -u +%T) UTC"
py -m bench.kev_vs_llm scale-kev 9995 $F >> bench/run.log 2>&1; echo "kev scaling exit $? at $(date -u +%T) UTC"
py -m bench.kev_vs_llm eval $F > bench/out/eval.log 2>&1
{ echo "# bench result $(date -u +%Y-%m-%dT%H:%M:%SZ)"; sha256sum bench/out/*.jsonl bench/out/result.json; } >> eval/PREREG_kev_vs_llm.sha256
echo "bench reading: $(grep -o '"reading": "[^"]*"' bench/out/result.json)"

# 2. memo check
if ! curl -s -m 15 -o /dev/null -w '%{http_code}' http://127.0.0.1:9995/health | grep -q 200; then
  echo "MODEL SERVER DOWN at $(date -u +%T) UTC: no memo check"; exit 2; fi
$PW memocheck --archive $PGA --out out > out/memocheck.log 2>&1; rc=$?
echo "memocheck exit $rc at $(date -u +%T) UTC"; tail -16 out/memocheck.log
$PW report --archive $PGA --out out

# 3. backfill
for since in 2026-10-01 2026-08-01 2026-05-01 2025-11-11; do
  if ! curl -s -m 15 -o /dev/null -w '%{http_code}' http://127.0.0.1:9995/health | grep -q 200; then
    echo "MODEL SERVER DOWN at $(date -u +%T) UTC: stopping before slice $since"; break; fi
  $PW scan --archive $PGA --since $since --out out >> out/scan.log 2>&1; rc=$?
  echo "slice since $since exit $rc at $(date -u +%T) UTC"
  $PW report --archive $PGA --out out
done
