# Stops the server whose PID start_qwen.ps1 wrote, after checking it really is a llama-server.
$pw = 'C:\Users\egeha\projects\policywatch'
$id = [int](Get-Content "$pw\bench\qwen.pid")
$p = Get-Process -Id $id -ErrorAction SilentlyContinue
if ($p -and $p.ProcessName -eq 'llama-server') { Stop-Process -Id $id -Force -Confirm:$false; "stopped $id" } else { "no llama-server with PID $id" }
