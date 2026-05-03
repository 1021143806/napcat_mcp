#!/bin/bash
# NapCat Group Info MCP Server - Linux/Mac 启动脚本

echo "========================================"
echo "NapCat Group Info MCP Server"
echo "========================================"
echo ""

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python，请先安装 Python 3.10+"
    exit 1
fi

# 检查是否在虚拟环境中
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "提示: 建议在虚拟环境中运行"
    echo "创建虚拟环境: python3 -m venv venv"
    echo "激活虚拟环境: source venv/bin/activate"
    echo ""
fi

# 检查依赖是否安装
python3 -c "import mcp" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "正在安装依赖..."
    pip install -e .
    if [ $? -ne 0 ]; then
        echo "错误: 依赖安装失败"
        exit 1
    fi
fi

# 检查环境变量
if [ ! -f .env ]; then
    echo "警告: 未找到 .env 文件"
    echo "请复制 .env.example 为 .env 并配置 NapCat 服务器地址"
    echo ""
fi

# 启动 MCP 服务器
echo "启动 MCP 服务器..."
echo ""
python3 -m napcat_group_info_mcp