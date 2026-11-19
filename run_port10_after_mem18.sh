#!/usr/bin/env bash
# Runs the 10-point port check (run_inspect_port10.sh, inspect_eval/PLAN_port_check_addendum1.md) once at least 18 GB of
# RAM is free. Replaces run_port10_after_np1v4.sh, whose 14 GB gate (the plan's minimum) was too low: the Qwen server
# with its 8 GB prompt cache reaches 12.7 GB, which would leave about 1.3 GB, and the 2026-11-19 reap came at 4.2 GB
# free. 18 GB still meets the plan's "at least 14 GB". Addendum 3 (the Kev re-timing) ended at 14:34:04 UTC.
cd /c/Users/egeha/projects/policywatch
free() { powershell.exe -NoProfile -Command "[int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1024)" | tr -d '\r'; }
until [ "$(free)" -ge 18432 ]; do echo "waiting for 18 GB free (now $(free) MB) $(date -u +%T)"; sleep 600; done
echo "port restart $(date -u +%T) UTC, free $(free) MB"
bash run_inspect_port10.sh
