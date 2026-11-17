#!/usr/bin/env bash
# The contrib run's second half (stale/PLAN_missing_contrib.md), reordered 2026-11-17 ~20:35 UTC.
# run_contrib.sh waited for the scanner backfill before Kev. The backfill was at 57 of 92 updates of slice 2025-11-11,
# about 22 min per update while it shared the CPU with the reranker. So it was paused (killed by PID; answers already
# given stay in out/cache.sqlite) and run_contrib.sh was stopped by PID while its reranker kept running.
# Now: wait for that reranker process to end; Kev on the shortlist alone on the server; output hashes appended to the
# plan's hash file; then the backfill's last slice; then the deferred memo check; then the daily watch once (it must
# not run before the backfill finishes).
# Usage: bash run_contrib_kev.sh <reranker python PID>
cd /c/Users/egeha/projects/policywatch
PGA=../decision-serving/data/pga-versions; PW="py -m policywatch"
up() { curl -s -m 15 -o /dev/null -w '%{http_code}' http://127.0.0.1:${1:-9995}/health | grep -q 200; }
RPID=${1:?reranker PID}
while tasklist //FI "PID eq $RPID" //NH 2>/dev/null | grep -qw "$RPID"; do sleep 60; done
echo "contrib rerank process ended at $(date -u +%T) UTC; log: $(tail -1 stale/out/missing_contrib_rerank.log)"
if [ "$(tail -1 stale/out/missing_contrib_rerank.log)" = "rerank done" ]; then
  if up; then
    py -m stale.missing_contrib kev >> stale/out/missing_contrib_kev.log 2>&1; echo "contrib kev exit $? at $(date -u +%T) UTC"
    { echo "outputs $(date -u +%FT%TZ)"; sha256sum stale/out/missing_contrib_rerank.json stale/out/missing_contrib_kev.json | sed 's/  / */'; } >> stale/PLAN_missing_contrib.sha256
  else echo "KEV SERVER DOWN at $(date -u +%T) UTC: contrib kev not run"; fi
else echo "RERANK DID NOT FINISH: contrib kev not run"; fi
echo "contrib kev step done at $(date -u +%T) UTC"
if up; then
  $PW scan --archive $PGA --since 2025-11-11 --out out >> out/scan.log 2>&1; echo "slice since 2025-11-11 exit $? at $(date -u +%T) UTC"
  $PW report --archive $PGA --out out
  echo "backfill all done at $(date -u +%T) UTC"
  if up; then
    $PW memocheck --archive $PGA --out out > out/memocheck.log 2>&1; echo "memocheck exit $? at $(date -u +%T) UTC"; tail -16 out/memocheck.log
  else echo "KEV SERVER DOWN at $(date -u +%T) UTC: no memo check"; fi
  cmd.exe //c daily.cmd; echo "daily exit $? at $(date -u +%T) UTC"; tail -5 stale/live/daily.log
else echo "KEV SERVER DOWN at $(date -u +%T) UTC: backfill, memo check and daily not run"; fi
echo "contrib chain all done at $(date -u +%T) UTC"
