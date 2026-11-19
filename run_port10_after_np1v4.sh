#!/usr/bin/env bash
# Runs the 10-point port check (run_inspect_port10.sh, PLAN_port_check_addendum1.md) after addendum 3's chain ends, and only once at least
# 14 GB of RAM is free: its Qwen server with the 8 GB prompt cache reached 12.7 GB, and the previous attempt was reaped
# for low memory (2026-11-19 ~09:50 UTC).
cd /c/Users/egeha/projects/policywatch
until grep -q -E "np1v4 all done|v4 checks did not pass|HASH MISMATCH|DID NOT START" stale/out/multiq_np1v4_chain.log; do sleep 120; done
free() { powershell.exe -NoProfile -Command "[int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1024)" | tr -d '\r'; }
until [ "$(free)" -ge 14336 ]; do echo "waiting for 14 GB free (now $(free) MB) $(date -u +%T)"; sleep 600; done
echo "port restart $(date -u +%T) UTC, free $(free) MB"
bash run_inspect_port10.sh
