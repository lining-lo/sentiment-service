$ErrorActionPreference = 'Stop'

$AppDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PidFile = Join-Path $AppDir '.user-frontend.pid'

if (-not (Test-Path $PidFile)) {
    Write-Host 'user-frontend is not running.'
    exit 0
}

$ProcessId = [int](Get-Content $PidFile | Select-Object -First 1)
$Process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue

if ($Process) {
    & taskkill.exe /PID $ProcessId /T /F | Out-Null
    Write-Host "user-frontend stopped (PID $ProcessId)."
} else {
    Write-Host "Process $ProcessId was not found."
}

Remove-Item $PidFile -Force