"""Native Streamable HTTP transport for NapCat MCP."""

from __future__ import annotations

import contextlib
import hmac
import logging
from collections.abc import AsyncIterator

import uvicorn
from mcp.server.auth.middleware.bearer_auth import AuthenticatedUser
from mcp.server.auth.provider import AccessToken
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.server.transport_security import TransportSecuritySettings
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Route
from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger(__name__)


class StreamableHTTPASGIApp:
    """Adapt a session manager to a Starlette ASGI endpoint."""

    def __init__(self, session_manager: StreamableHTTPSessionManager):
        self.session_manager = session_manager

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self.session_manager.handle_request(scope, receive, send)


class StaticBearerAuthMiddleware:
    """Require one static bearer token for the MCP endpoint.

    RikkaHub and other remote MCP clients can send this through a custom
    ``Authorization`` header. Health checks intentionally remain unauthenticated.
    """

    def __init__(self, app: ASGIApp, token: str, protected_path: str):
        self.app = app
        self.token = token
        self.protected_path = protected_path.rstrip("/") or "/"

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        path = scope.get("path", "").rstrip("/") or "/"
        if scope["type"] == "http" and path == self.protected_path:
            headers = {key.lower(): value for key, value in scope.get("headers", [])}
            authorization = headers.get(b"authorization", b"").decode("latin-1")
            scheme, _, credential = authorization.partition(" ")
            if scheme.lower() != "bearer" or not hmac.compare_digest(credential, self.token):
                response = PlainTextResponse(
                    "Unauthorized",
                    status_code=401,
                    headers={"WWW-Authenticate": "Bearer"},
                )
                await response(scope, receive, send)
                return

            # The MCP session manager records credential ownership for stateful
            # sessions. Populate the same ASGI auth object used by the SDK.
            scope["user"] = AuthenticatedUser(
                AccessToken(token=credential, client_id="static-bearer", scopes=[])
            )
        await self.app(scope, receive, send)


def _normalise_path(path: str) -> str:
    path = path.strip() or "/mcp"
    return path if path.startswith("/") else f"/{path}"


def _security_settings(allowed_hosts: list[str], allowed_origins: list[str]) -> TransportSecuritySettings:
    return TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=allowed_hosts,
        allowed_origins=allowed_origins,
    )


def create_streamable_http_app(
    server,
    *,
    path: str = "/mcp",
    bearer_token: str = "",
    allowed_hosts: list[str] | None = None,
    allowed_origins: list[str] | None = None,
    stateless: bool = False,
    json_response: bool = False,
) -> ASGIApp:
    """Create the native Streamable HTTP ASGI application."""
    path = _normalise_path(path)
    session_manager = StreamableHTTPSessionManager(
        app=server,
        stateless=stateless,
        json_response=json_response,
        security_settings=_security_settings(
            allowed_hosts or ["127.0.0.1:*", "localhost:*", "[::1]:*"],
            allowed_origins or ["http://127.0.0.1:*", "http://localhost:*", "http://[::1]:*"],
        ),
        session_idle_timeout=None if stateless else 1800,
    )

    async def health(_: Request) -> JSONResponse:
        return JSONResponse({"status": "ok", "transport": "streamable-http", "endpoint": path})

    @contextlib.asynccontextmanager
    async def lifespan(_: Starlette) -> AsyncIterator[None]:
        async with session_manager.run():
            yield

    starlette_app: ASGIApp = Starlette(
        routes=[
            Route("/healthz", endpoint=health, methods=["GET"]),
            Route(path, endpoint=StreamableHTTPASGIApp(session_manager)),
        ],
        lifespan=lifespan,
    )
    if bearer_token:
        starlette_app = StaticBearerAuthMiddleware(starlette_app, bearer_token, path)
    return starlette_app


def run_streamable_http(
    server,
    *,
    host: str,
    port: int,
    path: str,
    bearer_token: str,
    allowed_hosts: list[str],
    allowed_origins: list[str],
    stateless: bool,
    json_response: bool,
    log_level: str,
) -> None:
    """Run the MCP server using native Streamable HTTP."""
    application = create_streamable_http_app(
        server,
        path=path,
        bearer_token=bearer_token,
        allowed_hosts=allowed_hosts,
        allowed_origins=allowed_origins,
        stateless=stateless,
        json_response=json_response,
    )
    uvicorn.run(application, host=host, port=port, log_level=log_level)
