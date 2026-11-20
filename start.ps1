$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
Write-Host "JIFUNZE AI starting on http://127.0.0.1:8000 ..." -ForegroundColor Cyan
& ".\venv\Scripts\python.exe" manage.py runserver
