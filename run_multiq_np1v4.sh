#!/usr/bin/env bash
# stale/PLAN_multiq_addendum3.md: Kev re-timed on a 1-slot server built from decision checkpoints v4 (port 9998).
# Waits for the daily watch queued after the Inspect port check and for addendum 2's chain to end (it was gated on v3,
# which failed, so it exits without running), so nothing else of mine is on the CPU; runs only if the v4 checks on the
# test models read "v4 fixes the one-slot case".
# Usage: bash run_multiq_np1v4.sh   (plan and code must already be hashed in stale/PLAN_multiq_addendum3.sha256)
cd /c/Users/egeha/projects/policywatch
V4=/c/Users/egeha/projects/decision-serving/validation-20261119-v4
up() { curl -s -m 15 -o /dev/null -w '%{http_code}' http://127.0.0.1:9998/health | grep -q 200; }
until grep -q "daily all done" stale/live/daily_after_chain.log 2>/dev/null; do sleep 120; done
until grep -q -E "not run|np1v3 all done" stale/out/multiq_np1v3_chain.log 2>/dev/null; do sleep 60; done
until [ -f "$V4/reading.json" ]; do sleep 120; done
grep -q '"reading": "v4 fixes the one-slot case"' "$V4/reading.json" || { echo "v4 checks did not pass: not run"; exit 1; }
grep -E '^[0-9a-f]{64} ' stale/PLAN_multiq_addendum3.sha256 | sha256sum -c --quiet || { echo "HASH MISMATCH: not run"; exit 1; }
echo "np1v4 start $(date -u +%T) UTC"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File bench/start_kev_np1v4.ps1
for i in $(seq 90); do up && break; sleep 5; done
if up; then py -m stale.multiq_np1v4 kev 9998 >> stale/out/multiq_np1v4.log 2>&1; echo "np1v4 kev exit $? at $(date -u +%T) UTC"; else echo "NP1V4 SERVER DID NOT START"; fi
powershell.exe -NoProfile -ExecutionPolicy Bypass -File bench/stop_kev_np1v4.ps1
py -m stale.multiq_np1v4 result > stale/out/multiq_np1v4_result.log 2>&1; echo "np1v4 result exit $? at $(date -u +%T) UTC"; cat stale/out/multiq_np1v4_result.log
{ echo "outputs $(date -u +%FT%TZ)"; sha256sum stale/out/multiq_kev_np1v4.json stale/out/multiq_np1v4_result.json | sed 's/  / */'; } >> stale/PLAN_multiq_addendum3.sha256
echo "np1v4 all done at $(date -u +%T) UTC"
