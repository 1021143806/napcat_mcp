"""
NapCat MCP Server - Package Entry Point
封装 NapCat 所有 HTTP API 的 MCP 服务器
"""

import asyncio
from .server import main

if __name__ == "__main__":
    asyncio.run(main())