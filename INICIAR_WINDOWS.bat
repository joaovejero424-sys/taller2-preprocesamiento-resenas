@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto :fin
.venv\Scripts\python.exe main.py --solo-preprocesar
:fin
pause
