param(
    [int]$Port = 8000,
    [switch]$Lan,
    [switch]$NoBrowser,
    [switch]$SkipInstall,
    [switch]$Check
)
$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot
$venvPy = Join-Path $PSScriptRoot "venv\Scripts\python.exe"
function Test-PortBusy([int]$p) {
    try {
        $c = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue
        if ($c) { return $true }
    } catch {}
    $n = netstat -ano | Select-String (":" + $p + "\s+.*LISTENING")
    return [bool]$n
}
if (-not (Test-Path -LiteralPath $venvPy)) {
    Write-Host "[jifunze] creating virtual environment..." -ForegroundColor Cyan
    $made = $false
    foreach ($cmd in @("py -3.12", "py -3", "python")) {
        $parts = $cmd.Split(" ")
        $exe = $parts[0]
        $pre = @()
        if ($parts.Length -gt 1) { $pre = $parts[1..($parts.Length - 1)] }
        if (Get-Command $exe -ErrorAction SilentlyContinue) {
            & $exe @pre -m venv venv
            if ($LASTEXITCODE -eq 0 -and (Test-Path -LiteralPath $venvPy)) { $made = $true; break }
        }
    }
    if (-not $made) { throw "Python 3.12 not found. Install Python 3.12 or create the venv manually." }
}
if (-not $SkipInstall) {
    Write-Host "[jifunze] installing dependencies..." -ForegroundColor Cyan
    if (Test-Path -LiteralPath "requirements.txt") {
        & $venvPy -m pip install -r requirements.txt --quiet --disable-pip-version-check
    } else {
        & $venvPy -m pip install --quiet --disable-pip-version-check django djangorestframework django-cors-headers pymupdf python-docx
    }
}
Write-Host "[jifunze] applying migrations..." -ForegroundColor Cyan
& $venvPy manage.py migrate --noinput
& $venvPy manage.py check
if ($Check) { Write-Host "[jifunze] check OK" -ForegroundColor Green; exit 0 }
while (Test-PortBusy $Port) {
    Write-Host "[jifunze] port $Port busy, trying $($Port + 1)" -ForegroundColor Yellow
    $Port++
}
$bind = "127.0.0.1"
if ($Lan) { $bind = "0.0.0.0" }
$url = "http://127.0.0.1:$Port/"
$lan = ""
if ($Lan) {
    $ip = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
        Where-Object { $_.IPAddress -like "192.168.*" -or $_.IPAddress -like "10.*" -or $_.IPAddress -like "172.*" } |
        Select-Object -First 1
    if ($ip) { $lan = "http://" + $ip.IPAddress + ":$Port/"
}
}
Write-Host ""
Write-Host "  JIFUNZE AI is starting" -ForegroundColor Green
Write-Host ("  local : " + $url) -ForegroundColor White
if ($lan) { Write-Host ("  phone : " + $lan) -ForegroundColor White }
Write-Host "  stop  : Ctrl+C" -ForegroundColor DarkGray
Write-Host ""
$job = $null
if (-not $NoBrowser) {
    $job = Start-Job -ArgumentList $url -ScriptBlock {
        param($u)
        for ($i = 0; $i -lt 80; $i++) {
            try {
                Invoke-WebRequest -Uri $u -UseBasicParsing -TimeoutSec 1 | Out-Null
                Start-Process $u
                return
            } catch { Start-Sleep -Milliseconds 500 }
        }
    }
}
try {
    & $venvPy manage.py runserver ($bind + ":" + $Port)
} finally {
    if ($job) {
        Stop-Job $job -ErrorAction SilentlyContinue
        Remove-Job $job -Force -ErrorAction SilentlyContinue
    }
}
