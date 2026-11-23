@echo off
rem JIFUNZE AI - double-click to run on LAN (phone)
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run.ps1" -Lan %*
if errorlevel 1 pause
