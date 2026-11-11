#!/usr/bin/env bash
# Overnight, resumable (rerun any time):
#   1. wait for the r20 Kev scorer (PID $1), then run its PRE-REGISTERED evaluation unchanged and hash the result
#   2. seed policywatch's cache from the r20 scores, write the accuracy page, scan the memo-matched updates
#   3. backfill ToS/Privacy updates newest-first in slices, rebuilding the site after each
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
for since in 2026-10-01 2026-08-01 2026-05-01 2025-11-11; do
  if ! curl -s -m 15 -o /dev/null -w '%{http_code}' http://127.0.0.1:9995/health | grep -q 200; then
    echo "MODEL SERVER DOWN at $(date -u +%T) UTC: stopping before slice $since"; break; fi
  $PW scan --archive $PGA --since $since --out out >> out/scan.log 2>&1; rc=$?
  echo "slice since $since exit $rc at $(date -u +%T) UTC"
  $PW report --archive $PGA --out out
done
