#!/usr/bin/env bash
# stale/PLAN_multiq.md, then what run_contrib_kev.sh had left (it was stopped by PID when this started):
#   1. Kev re-timed on the missing2 cascade cells with no score cache, alone on the CPU;
#   2. the instruct model (Qwen3.5-4B, its own server, prompt cache off) with all of a passage's questions in one prompt;
#   3. the result and the output hashes;
#   4. the scanner backfill's last slice (2025-11-11), the deferred memo check, the daily watch once.
# Usage: bash run_multiq.sh   (the plan and code must already be hashed in stale/PLAN_multiq.sha256)
cd /c/Users/egeha/projects/policywatch
PGA=../decision-serving/data/pga-versions; PW="py -m policywatch"
up() { curl -s -m 15 -o /dev/null -w '%{http_code}' http://127.0.0.1:${1:-9995}/health | grep -q 200; }
grep -E '^[0-9a-f]{64} ' stale/PLAN_multiq.sha256 | sha256sum -c --quiet || { echo "HASH MISMATCH: not run"; exit 1; }
echo "multiq start $(date -u +%T) UTC"
if up; then py -m stale.multiq kev >> stale/out/multiq.log 2>&1; echo "multiq kev exit $? at $(date -u +%T) UTC"; else echo "KEV SERVER DOWN"; exit 1; fi
up 9996 || { powershell.exe -NoProfile -File bench/start_qwen.ps1 -CacheRam 0; for i in $(seq 60); do up 9996 && break; sleep 5; done; }
if up 9996; then py -m stale.multiq qwen >> stale/out/multiq.log 2>&1; echo "multiq qwen exit $? at $(date -u +%T) UTC"; else echo "QWEN SERVER DID NOT START"; fi
powershell.exe -NoProfile -File bench/stop_qwen.ps1
py -m stale.multiq result > stale/out/multiq_result.log 2>&1; echo "multiq result exit $? at $(date -u +%T) UTC"; tail -30 stale/out/multiq_result.log
{ echo "outputs $(date -u +%FT%TZ)"; sha256sum stale/out/multiq_kev.json stale/out/multiq_qwen.json stale/out/multiq_result.json | sed 's/  / */'; } >> stale/PLAN_multiq.sha256
echo "multiq all done at $(date -u +%T) UTC"
if up; then
  $PW scan --archive $PGA --since 2025-11-11 --out out >> out/scan.log 2>&1; echo "slice since 2025-11-11 exit $? at $(date -u +%T) UTC"
  $PW report --archive $PGA --out out
  echo "backfill all done at $(date -u +%T) UTC"
  $PW memocheck --archive $PGA --out out > out/memocheck.log 2>&1; echo "memocheck exit $? at $(date -u +%T) UTC"; tail -16 out/memocheck.log
  cmd.exe //c daily.cmd; echo "daily exit $? at $(date -u +%T) UTC"; tail -5 stale/live/daily.log
else echo "KEV SERVER DOWN at $(date -u +%T) UTC: backfill, memo check and daily not run"; fi
echo "chain all done at $(date -u +%T) UTC"
