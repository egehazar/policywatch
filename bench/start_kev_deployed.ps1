# Starts the deployed Kev-4B server on port 9995 with the command it ran with since 2026-11-11 (RUN.md: build-fix, -np 4,
# -c 16384, -t 6, --no-mmproj, working directory decision-serving). Writes its PID to bench\out\kev_deployed.pid.
$ds = 'C:\Users\egeha\projects\decision-serving'
$pw = 'C:\Users\egeha\projects\policywatch'
New-Item -ItemType Directory -Force "$pw\bench\out" | Out-Null
$p = Start-Process -FilePath "$ds\llama.cpp\build-fix\bin\llama-server.exe" `
  -ArgumentList '-m','models/Kev-4B-Q8_0.gguf','--host','127.0.0.1','--port','9995','-np','4','-c','16384','-t','6','--no-mmproj' `
  -WorkingDirectory $ds -WindowStyle Hidden `
  -RedirectStandardOutput "$pw\bench\kev_deployed_server.log" -RedirectStandardError "$pw\bench\kev_deployed_server.err" -PassThru
Set-Content -Path "$pw\bench\out\kev_deployed.pid" -Value $p.Id -Encoding ascii
