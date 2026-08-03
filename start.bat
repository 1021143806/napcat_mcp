@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    py -3.12 -m venv .venv 2>nul || py -3 -m venv .venv
    if errorlevel 1 exit /b 1
)

".venv\Scripts\python.exe" -c "import napcat_mcp" >nul 2>&1
if errorlevel 1 ".venv\Scripts\python.exe" -m pip install -e .
if errorlevel 1 exit /b 1

".venv\Scripts\python.exe" -m napcat_mcp
