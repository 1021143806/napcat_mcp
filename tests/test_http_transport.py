import asyncio
import os
import socket
import subprocess
import sys
import time
from contextlib import closing

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


def _free_port() -> int:
    with closing(socket.socket()) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _wait_for_health(url: str, process: subprocess.Popen, timeout: float = 15.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            raise AssertionError(f"server exited early\nstdout={stdout}\nstderr={stderr}")
        try:
            response = httpx.get(url, timeout=0.5)
            if response.status_code == 200:
                return
        except httpx.HTTPError:
            pass
        time.sleep(0.1)
    raise AssertionError("server did not become healthy")


async def _list_tools(url: str, token: str | None = None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    async with httpx.AsyncClient(headers=headers) as client:
        async with streamable_http_client(url, http_client=client) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return await session.list_tools()


def test_native_streamable_http_lists_tools_with_bearer_auth():
    port = _free_port()
    token = "test-secret-token"
    command = [
        sys.executable,
        "-m",
        "napcat_mcp",
        "--transport",
        "streamable-http",
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
        "--log-level",
        "warning",
    ]
    environment = os.environ.copy()
    environment["MCP_BEARER_TOKEN"] = token
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=environment,
    )
    try:
        _wait_for_health(f"http://127.0.0.1:{port}/healthz", process)
        unauthorized = httpx.post(
            f"http://127.0.0.1:{port}/mcp",
            headers={"Accept": "application/json, text/event-stream"},
            json={"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        )
        assert unauthorized.status_code == 401

        tools = asyncio.run(_list_tools(f"http://127.0.0.1:{port}/mcp", token))
        names = {tool.name for tool in tools.tools}
        assert "get_status" in names
        assert "read_group_messages" in names
        assert len(names) == 57
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def test_remote_http_refuses_to_start_without_token():
    process = subprocess.run(
        [
            sys.executable,
            "-m",
            "napcat_mcp",
            "--transport",
            "streamable-http",
            "--host",
            "192.0.2.10",
            "--port",
            "18080",
        ],
        capture_output=True,
        text=True,
        timeout=10,
        env={key: value for key, value in os.environ.items() if key != "MCP_BEARER_TOKEN"},
    )
    assert process.returncode != 0
    assert "MCP_BEARER_TOKEN" in process.stderr
