param([Parameter(ValueFromRemainingArguments=$true)]$Commands)
Set-Location $PSScriptRoot
$py = Join-Path $PSScriptRoot "venv\Scripts\python.exe"
if (!(Test-Path $py)) { Write-Host "Error: Virtual environment not found." -ForegroundColor Red; exit 1 }
& $py manage.py @Commands
