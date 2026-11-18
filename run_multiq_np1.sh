#!/usr/bin/env bash
# stale/PLAN_multiq_addendum1.md: Kev re-timed on a 1-slot server (port 9997), after the main chain (run_multiq.sh) ends.
# Usage: bash run_multiq_np1.sh   (plan and code must already be hashed in stale/PLAN_multiq_addendum1.sha256)
cd /c/Users/egeha/projects/policywatch
up() { curl -s -m 15 -o /dev/null -w '%{http_code}' http://127.0.0.1:9997/health | grep -q 200; }
until grep -q "chain all done" stale/out/multiq_chain.log; do sleep 120; done
grep -E '^[0-9a-f]{64} ' stale/PLAN_multiq_addendum1.sha256 | sha256sum -c --quiet || { echo "HASH MISMATCH: not run"; exit 1; }
echo "np1 start $(date -u +%T) UTC"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File bench/start_kev_np1.ps1
for i in $(seq 90); do up && break; sleep 5; done
if up; then py -m stale.multiq_np1 kev 9997 >> stale/out/multiq_np1.log 2>&1; echo "np1 kev exit $? at $(date -u +%T) UTC"; else echo "NP1 SERVER DID NOT START"; fi
powershell.exe -NoProfile -ExecutionPolicy Bypass -File bench/stop_kev_np1.ps1
py -m stale.multiq_np1 result > stale/out/multiq_np1_result.log 2>&1; echo "np1 result exit $? at $(date -u +%T) UTC"; cat stale/out/multiq_np1_result.log
{ echo "outputs $(date -u +%FT%TZ)"; sha256sum stale/out/multiq_kev_np1.json stale/out/multiq_np1_result.json | sed 's/  / */'; } >> stale/PLAN_multiq_addendum1.sha256
echo "np1 all done at $(date -u +%T) UTC"
