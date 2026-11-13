# Starts the Qwen3.5-4B baseline server on port 9996 and writes its PID to bench\qwen.pid (no stdout to inherit).
param([int]$Threads = 6, [int]$CacheRam = 8192)   # -CacheRam 0 turns llama.cpp's host prompt cache off (no effect on scores when no prefix is reused)
$ds = 'C:\Users\egeha\projects\decision-serving'
$pw = 'C:\Users\egeha\projects\policywatch'
$p = Start-Process -FilePath "$ds\llama.cpp\build-fix\bin\llama-server.exe" `
  -ArgumentList '-m','models\qwen35-4b\Qwen3.5-4B-Q8_0.gguf','--port','9996','-np','1','-c','16384','-t',"$Threads",'--jinja','--cache-ram',"$CacheRam" `
  -WorkingDirectory $ds -WindowStyle Hidden `
  -RedirectStandardOutput "$pw\bench\qwen_server.log" -RedirectStandardError "$pw\bench\qwen_server.err" -PassThru
Set-Content -Path "$pw\bench\qwen.pid" -Value $p.Id -Encoding ascii
