@echo off
REM NapCat Group Info MCP Server - Windows 启动脚本

echo ========================================
echo NapCat Group Info MCP Server
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

REM 检查是否在虚拟环境中
if not defined VIRTUAL_ENV (
    echo 提示: 建议在虚拟环境中运行
    echo 创建虚拟环境: python -m venv venv
    echo 激活虚拟环境: venv\Scripts\activate
    echo.
)

REM 检查依赖是否安装
python -c "import mcp" >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装依赖...
    pip install -e .
    if %errorlevel% neq 0 (
        echo 错误: 依赖安装失败
        pause
        exit /b 1
    )
)

REM 检查环境变量
if not exist .env (
    echo 警告: 未找到 .env 文件
    echo 请复制 .env.example 为 .env 并配置 NapCat 服务器地址
    echo.
)

REM 启动 MCP 服务器
echo 启动 MCP 服务器...
echo.
python -m napcat_group_info_mcp

pause