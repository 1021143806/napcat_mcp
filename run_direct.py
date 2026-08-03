"""Run NapCat MCP directly from a source checkout without installation."""

import sys
from importlib import import_module
from pathlib import Path

src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

main = import_module("napcat_mcp.server").main


if __name__ == "__main__":
    main()
