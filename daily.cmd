@echo off
rem The daily stale-evidence watch, all collections, for Windows Task Scheduler. Not scheduled: that is the owner's call.
rem   schtasks /Create /TN policywatch-daily /SC DAILY /ST 06:00 /TR "cmd /c C:\Users\egeha\projects\policywatch\daily.cmd"
rem Each step fast-forwards an archive clone, so do not run it while an evaluation reads one (part D's eval asserts the
rem contrib clone has not moved since its draw). Logs: stale\live\daily.log, stale\wide\live\daily.log.
rem Suggestions: Kev's when the server on port 9995 answers (cached, so a day costs only the changed documents), else
rem word match.
cd /d %~dp0
py -m stale.daily ..\decision-serving\data\pga-versions >> stale\live\daily.log 2>&1
py -m stale.daily_suggest ..\decision-serving\data\pga-versions kev >> stale\live\daily.log 2>&1 || py -m stale.daily_suggest ..\decision-serving\data\pga-versions bm25 >> stale\live\daily.log 2>&1
if not exist stale\wide\live mkdir stale\wide\live
for %%c in (contrib genai-contrib dating) do py -m stale.wide_daily %%c >> stale\wide\live\daily.log 2>&1
