@echo off
REM NapCat Group Info MCP Server - 快速测试脚本

echo ========================================
echo NapCat Group Info MCP Server - 快速测试
echo ========================================
echo.

REM 设置环境变量
set NAPCAT_HOST=http://localhost:3000
set NAPCAT_TOKEN=
set ALLOWED_GROUPS=628101497

echo 配置信息:
echo   NAPCAT_HOST: %NAPCAT_HOST%
echo   NAPCAT_TOKEN: %NAPCAT_TOKEN%
echo   ALLOWED_GROUPS: %ALLOWED_GROUPS%
echo.

echo 启动 MCP 服务器...
echo 按 Ctrl+C 停止
echo.

python run_direct.py

pause