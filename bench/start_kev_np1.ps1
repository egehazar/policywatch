# Starts a second Kev-4B server set up like the instruct model's (1 slot) on port 9997 for stale/PLAN_multiq_addendum1.md.
# Same flags as the deployed Kev server (port 9995) except -np 1; writes its PID to bench\out\kev_np1.pid.
$ds = 'C:\Users\egeha\projects\decision-serving'
$pw = 'C:\Users\egeha\projects\policywatch'
New-Item -ItemType Directory -Force "$pw\bench\out" | Out-Null
$p = Start-Process -FilePath "$ds\llama.cpp\build-fix\bin\llama-server.exe" `
  -ArgumentList '-m','models/Kev-4B-Q8_0.gguf','--host','127.0.0.1','--port','9997','-np','1','-c','16384','-t','6','--no-mmproj' `
  -WorkingDirectory $ds -WindowStyle Hidden `
  -RedirectStandardOutput "$pw\bench\kev_np1_server.log" -RedirectStandardError "$pw\bench\kev_np1_server.err" -PassThru
Set-Content -Path "$pw\bench\out\kev_np1.pid" -Value $p.Id -Encoding ascii
