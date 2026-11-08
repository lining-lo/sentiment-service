$ErrorActionPreference = 'Stop'

$AppDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PidFile = Join-Path $AppDir '.user-frontend.pid'
$StdoutLog = Join-Path $AppDir 'user-frontend.log'
$StderrLog = Join-Path $AppDir 'user-frontend.error.log'

if (Test-Path $PidFile) {
    $ExistingPid = [int](Get-Content $PidFile | Select-Object -First 1)
    if (Get-Process -Id $ExistingPid -ErrorAction SilentlyContinue) {
        Write-Host "user-frontend is already running (PID $ExistingPid)."
        exit 0
    }
    Remove-Item $PidFile -Force
}

$Process = Start-Process `
    -FilePath 'cmd.exe' `
    -ArgumentList @('/d', '/c', "npm run dev -- --host 0.0.0.0 > `"$StdoutLog`" 2> `"$StderrLog`"") `
    -WorkingDirectory $AppDir `
    -WindowStyle Hidden `
    -PassThru

$Process.Id | Set-Content -Path $PidFile -Encoding utf8
Write-Host "user-frontend started (PID $($Process.Id))."
Write-Host 'URL: http://localhost:3000'