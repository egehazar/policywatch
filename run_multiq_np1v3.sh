#!/usr/bin/env bash
# stale/PLAN_multiq_addendum2.md: Kev re-timed on a 1-slot server built from decision checkpoints v3 (port 9998).
# Waits for the daily watch queued after the Inspect port check, so nothing else of mine is on the CPU, and runs only
# if the v3 checks on the test model read "v3 fixes the one-slot case".
# Usage: bash run_multiq_np1v3.sh   (plan and code must already be hashed in stale/PLAN_multiq_addendum2.sha256)
cd /c/Users/egeha/projects/policywatch
V3=/c/Users/egeha/projects/decision-serving/validation-20261118-v3
up() { curl -s -m 15 -o /dev/null -w '%{http_code}' http://127.0.0.1:9998/health | grep -q 200; }
until grep -q "daily all done" stale/live/daily_after_chain.log 2>/dev/null; do sleep 120; done
until [ -f "$V3/reading.json" ]; do sleep 120; done
grep -q '"reading": "v3 fixes the one-slot case"' "$V3/reading.json" || { echo "v3 checks did not pass: not run"; exit 1; }
grep -E '^[0-9a-f]{64} ' stale/PLAN_multiq_addendum2.sha256 | sha256sum -c --quiet || { echo "HASH MISMATCH: not run"; exit 1; }
echo "np1v3 start $(date -u +%T) UTC"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File bench/start_kev_np1v3.ps1
for i in $(seq 90); do up && break; sleep 5; done
if up; then py -m stale.multiq_np1v3 kev 9998 >> stale/out/multiq_np1v3.log 2>&1; echo "np1v3 kev exit $? at $(date -u +%T) UTC"; else echo "NP1V3 SERVER DID NOT START"; fi
powershell.exe -NoProfile -ExecutionPolicy Bypass -File bench/stop_kev_np1v3.ps1
py -m stale.multiq_np1v3 result > stale/out/multiq_np1v3_result.log 2>&1; echo "np1v3 result exit $? at $(date -u +%T) UTC"; cat stale/out/multiq_np1v3_result.log
{ echo "outputs $(date -u +%FT%TZ)"; sha256sum stale/out/multiq_kev_np1v3.json stale/out/multiq_np1v3_result.json | sed 's/  / */'; } >> stale/PLAN_multiq_addendum2.sha256
echo "np1v3 all done at $(date -u +%T) UTC"
