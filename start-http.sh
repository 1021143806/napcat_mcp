#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"

if [ ! -x .venv/bin/python ]; then
    python3 -m venv .venv
fi

if ! .venv/bin/python -c 'import napcat_mcp' >/dev/null 2>&1; then
    .venv/bin/python -m pip install -e .
fi

if [ ! -f .env ]; then
    echo '[NapCat MCP] ERROR: .env not found. Copy .env.example to .env and configure it first.' >&2
    exit 1
fi

exec .venv/bin/python -m napcat_mcp --transport streamable-http
