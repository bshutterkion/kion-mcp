"""Proxy authentication for remote MCP hosting behind the Kion proxy."""

import logging
import os
from typing import Optional

from fastmcp.server.auth.auth import AccessToken, RemoteAuthProvider, TokenVerifier
from mcp.server.auth.middleware.auth_context import get_access_token
from pydantic import AnyHttpUrl


class KionProxyTokenVerifier(TokenVerifier):
    """Token verifier that trusts tokens pre-validated by the Kion proxy.

    When kion-mcp runs behind the Kion MCP proxy, the proxy's JWT middleware
    has already validated the Bearer token. This verifier simply passes the
    raw token through so it can be used for downstream Kion API calls.
    """

    async def verify_token(self, token: str) -> Optional[AccessToken]:
        if not token:
            return None
        return AccessToken(token=token, client_id="kion-proxy", scopes=[])


def build_remote_auth_provider(kion_server_url: str, mcp_base_url: str) -> RemoteAuthProvider:
    """Build a RemoteAuthProvider that advertises Kion as the authorization server.

    This tells MCP clients (Claude Desktop, etc.) where to do OAuth — they
    discover Kion's authorization server via the well-known metadata endpoint
    and handle the OAuth flow themselves.

    Args:
        kion_server_url: The Kion instance URL (e.g. https://kion.example.com/api)
        mcp_base_url: The public URL of this MCP server (e.g. https://kion.example.com/mcp)
    """
    # The authorization server is the Kion instance (strip /api if present)
    auth_server = kion_server_url.rstrip("/")
    if auth_server.endswith("/api"):
        auth_server = auth_server[:-4]

    return RemoteAuthProvider(
        token_verifier=KionProxyTokenVerifier(),
        authorization_servers=[AnyHttpUrl(auth_server)],
        base_url=AnyHttpUrl(mcp_base_url),
        resource_name="Kion MCP Server",
    )


def get_request_token() -> Optional[str]:
    """Get the per-request Bearer token from the HTTP auth context.

    Returns the raw token string if running in HTTP mode behind the proxy,
    or None if no per-request token is available (stdio mode).
    """
    access_token = get_access_token()
    if access_token and access_token.token:
        return access_token.token
    return None
