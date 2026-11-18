# Keeps the PC from sleeping while a long run is going, without changing any power setting: the process asks Windows
# for "system required" (SetThreadExecutionState), which lapses when this process exits. It exits when the given file
# contains the given line, or after MaxHours.
# Usage: powershell -File bench\keep_awake.ps1 -File <log> -Line '<regex>' [-MaxHours 14]
param([string]$File, [string]$Line, [double]$MaxHours = 14)
Add-Type -Namespace W -Name P -MemberDefinition '[DllImport("kernel32.dll")] public static extern uint SetThreadExecutionState(uint f);'
$null = [W.P]::SetThreadExecutionState(0x80000001)   # ES_CONTINUOUS | ES_SYSTEM_REQUIRED
$end = (Get-Date).AddHours($MaxHours)
while ((Get-Date) -lt $end) {
  if ((Test-Path $File) -and (Select-String -Path $File -Pattern $Line -Quiet)) { break }
  Start-Sleep -Seconds 60
}
$null = [W.P]::SetThreadExecutionState(0x80000000)   # ES_CONTINUOUS: back to normal
"keep_awake ended $(Get-Date -Format o)"
