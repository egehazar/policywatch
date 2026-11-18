# Stops the server whose PID start_kev_np1v3.ps1 wrote, after checking it really is a llama-server, and checks it is gone.
$pw = 'C:\Users\egeha\projects\policywatch'
$id = [int](Get-Content "$pw\bench\out\kev_np1v3.pid")
$p = Get-Process -Id $id -ErrorAction SilentlyContinue
if ($p -and $p.ProcessName -eq 'llama-server') { Stop-Process -Id $id -Force -Confirm:$false; Start-Sleep 2 } else { "no llama-server with PID $id"; exit }
if (Get-CimInstance Win32_Process -Filter "ProcessId=$id") { "still running $id" } else { "stopped $id" }
