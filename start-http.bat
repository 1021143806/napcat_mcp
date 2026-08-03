@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [NapCat MCP] Creating virtual environment...
    py -3.12 -m venv .venv 2>nul || py -3 -m venv .venv
    if errorlevel 1 goto :error
)

".venv\Scripts\python.exe" -c "import napcat_mcp" >nul 2>&1
if errorlevel 1 (
    echo [NapCat MCP] Installing dependencies...
    ".venv\Scripts\python.exe" -m pip install -e .
    if errorlevel 1 goto :error
)

if not exist ".env" (
    echo [NapCat MCP] ERROR: .env not found.
    echo Copy .env.example to .env and configure it first.
    exit /b 1
)

".venv\Scripts\python.exe" -m napcat_mcp --transport streamable-http
exit /b %errorlevel%

:error
echo [NapCat MCP] Startup failed.
exit /b 1
