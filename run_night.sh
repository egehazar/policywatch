#!/usr/bin/env bash
# Overnight, resumable (rerun any time):
#   1. wait for the r20 Kev scorer (PID $1), then run its PRE-REGISTERED evaluation unchanged and hash the result
#   2. seed policywatch's cache from the r20 scores, write the accuracy page, scan the memo-matched updates
#   3. decision model vs ordinary LLM benchmark (pre-registered), then
#   4. backfill ToS/Privacy updates newest-first in slices, rebuilding the site after each
# Not `py -I -m`: isolated mode drops the cwd, so the package is not importable.
RQ=/c/Users/egeha/projects/decision-serving/play/reviewq
F=$RQ/out
PGA=../decision-serving/data/pga-versions
PW="py -m policywatch"
while tasklist //FI "PID eq $1" 2>/dev/null | grep -qi "py"; do sleep 30; done
n=$(grep -c . $F/kev.jsonl)
echo "r20 scorer exited at $(date -u +%T) UTC with $n/70"
if [ "$n" -lt 70 ]; then echo "NOT STARTING: r20 incomplete"; exit 1; fi

# 1. pre-registered verdict (rq.py and blind_check.py are hashed in PREREG_rq.sha256; neither is changed here)
( cd $RQ && py -I rq.py eval out > out/result.json && py -I blind_check.py out > out/blind_check.json
  { echo "# result $(date -u +%Y-%m-%dT%H:%M:%SZ) (rq.py eval, unchanged; full run 70/70)"; sha256sum out/result.json out/blind_check.json out/kev.jsonl rq.py blind_check.py; } >> PREREG_rq.sha256 )
echo "r20 verdict: $(grep -o '"verdict": "[^"]*"' $F/result.json)"

cd /c/Users/egeha/projects/policywatch
if ! curl -s -m 15 -o /dev/null -w '%{http_code}' http://127.0.0.1:9995/health | grep -q 200; then
  echo "MODEL SERVER DOWN at $(date -u +%T) UTC: not scanning"; exit 2; fi
$PW seed --frozen $F --out out || exit 3
$PW eval --frozen $F --out out > out/eval.log 2>&1
$PW memocheck --archive $PGA --out out > out/memocheck.log 2>&1; rc=$?
echo "memocheck exit $rc at $(date -u +%T) UTC"; tail -16 out/memocheck.log
$PW report --archive $PGA --out out

# 4. decision model vs ordinary LLM (eval/PREREG_kev_vs_llm.md, frozen 22:38:03Z), each server alone on the CPU
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

for since in 2026-10-01 2026-08-01 2026-05-01 2025-11-11; do
  if ! curl -s -m 15 -o /dev/null -w '%{http_code}' http://127.0.0.1:9995/health | grep -q 200; then
    echo "MODEL SERVER DOWN at $(date -u +%T) UTC: stopping before slice $since"; break; fi
  $PW scan --archive $PGA --since $since --out out >> out/scan.log 2>&1; rc=$?
  echo "slice since $since exit $rc at $(date -u +%T) UTC"
  $PW report --archive $PGA --out out
done
