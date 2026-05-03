"""
NapCat MCP Server - 直接运行脚本
无需安装，直接运行此脚本即可启动 MCP 服务器
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加 miniconda3 的 site-packages 路径
miniconda_path = "/home/a1/miniconda3/lib/python3.12/site-packages"
if miniconda_path not in sys.path:
    sys.path.insert(0, miniconda_path)

# 添加 src 目录到 Python 路径
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from napcat_mcp.server import main

if __name__ == "__main__":
    asyncio.run(main())